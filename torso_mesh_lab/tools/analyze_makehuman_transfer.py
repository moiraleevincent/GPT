#!/usr/bin/env python3
"""Check transferability of MakeHuman hm08 breast firmness targets to our GLB.

This is diagnostic research, not a claim of exact topology correspondence.
Writes an analysis report, no model is modified.
"""
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.optimize import minimize

HERE=Path(__file__).resolve().parents[1]
OUT=HERE/"research"
OUT.mkdir(parents=True,exist_ok=True)
BASE_URL="https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/"
SOURCES={
  "base.obj":"data/3dobjs/base.obj",
  "maxfirmness.target":"data/targets/breast/female-young-averagemuscle-averageweight-maxcup-maxfirmness.target",
  "minfirmness.target":"data/targets/breast/female-young-averagemuscle-averageweight-maxcup-minfirmness.target",
  "volume-down.target":"data/targets/breast/breast-volume-vert-down.target",
  "point-decr.target":"data/targets/breast/breast-point-decr.target",
  "trans-down.target":"data/targets/breast/breast-trans-down.target"
}
for name, source in SOURCES.items():
    urlretrieve(BASE_URL+source, OUT/name)

source_vertices=[]
for line in (OUT/"base.obj").open():
    if line.startswith("v "):
        source_vertices.append([float(x) for x in line.split()[1:4]])
src=np.asarray(source_vertices,dtype=float)
glb=trimesh.load(HERE/"assets/female-base-mesh-base_female.glb",force="scene")
body=glb.geometry["base"]
dst=np.asarray(body.vertices,dtype=float)
tree=cKDTree(dst)

def read_target(name):
    result=np.zeros_like(src)
    ids=[]
    for row in (OUT/name).read_text().splitlines():
        cols=row.strip().split()
        if len(cols)==4 and cols[0].isdigit():
            idx=int(cols[0]);result[idx]=[float(x) for x in cols[1:]];ids.append(idx)
    return result,np.asarray(ids,dtype=int)
firm,ids_firm=read_target("maxfirmness.target")
soft,ids_soft=read_target("minfirmness.target")
shift=soft-firm
union=np.unique(np.concatenate([ids_firm,ids_soft]))
# Align neutral hm08 to adapted GLB at similar pose:
# same axis directions, uniform scale + Y/Z offset. This is an APPROXIMATION.
candidates=np.where((np.abs(src[:,0])<2.8)&(src[:,1]>1.8)&(src[:,1]<6.2)&(src[:,2]>-1.5))[0]
idx=np.random.default_rng(21).choice(candidates,size=min(len(candidates),2500),replace=False)
sub=src[idx]
min_y,max_y=src[:,1].min(),src[:,1].max()
scale0=(dst[:,1].max()-dst[:,1].min())/(max_y-min_y)
y0=dst[:,1].min()-min_y*scale0
def loss(p):
    scale,ty,tz=p
    if not (0.06<scale<0.13 and 0.5<ty<1.1 and -0.15<tz<0.15):
        return 99
    points=sub*scale+[0,ty,tz]
    d=tree.query(points,k=1,workers=1)[0]
    # Trim large distances due to shape differences.
    return float(np.mean(np.minimum(d,0.075)**2))
fit=minimize(loss,[scale0,y0,0.0],method="Nelder-Mead",
             options={"maxiter":180,"xatol":1e-6,"fatol":1e-9})
scale,ty,tz=fit.x
mapped_src=src*scale+[0,ty,tz]
breast_match=tree.query(mapped_src[union],k=1)[0]
dall=tree.query(mapped_src[idx],k=1)[0]
def q(a):
    return [round(float(v),5) for v in np.quantile(a,[.5,.9,.99])]
# Important: MakeHuman target rows are in MakeHuman xyz axes, where Y is up.
# A downward translation target has negative second column.
firm_rows=np.linalg.norm(firm,axis=1)>0
soft_rows=np.linalg.norm(soft,axis=1)>0
moved=np.where(np.linalg.norm(shift,axis=1)>1e-5)[0]
norms=np.linalg.norm(shift[moved],axis=1)
report=f"""# MakeHuman firmness target transfer — diagnostic

Input source: MakeHuman community hm08 CC0 base.obj and CC0 breast targets.
Destination: Innerscene adapted female GLB, \`torso_mesh_lab/assets/\`.

## Vertex correspondence
- Original MakeHuman source vertices: **{len(src):,}**
- Our exported GLB body primitive vertices: **{len(dst):,}**
- Original max-firmness target vertices: **{len(ids_firm):,}**
- Original min-firmness target vertices: **{len(ids_soft):,}**
- Different mesh topology / vertex indices: **direct copy is not possible**.
- Fitted approximate uniform scale: **{scale:.6f}**
- Fitted Y/Z translation (m): **{ty:.5f}, {tz:.5f}**
- Nearest surface discrepancy in body region, p50/p90/p99 (m): **{q(dall)}**
- Nearest surface discrepancy for target vertices, p50/p90/p99 (m): **{q(breast_match)}**

## Original firmness displacement (soft minus firm)
- Changed source points: **{len(moved):,}**
- Mean signed source-space displacement (x, y, z): **{np.round(np.mean(shift[moved],axis=0),4).tolist()}**
- Mean magnitude source units: **{float(norms.mean()):.4f}**
- 90th percentile magnitude source units: **{float(np.quantile(norms,.9)):.4f}**
- These displacements encode breast shape, not a gravity simulation.
- Axes here are original OBJ coordinate axes: X horizontal, Y vertical, Z depth.
- Soft vs firm is one of several combinations of cup size, muscle, weight and age.

## What transfer would require
We can transfer an *approximate displacement field* by spatial interpolation after
aligning base meshes, but it would not reproduce MakeHuman's original morph exactly.
This neutral hm08 base and the modified GLB differ in both topology and anatomy.
Check fit errors and inspect the transferred shape before exposing a user slider.
At minimum, limit it to breast-weighted vertices, damp the displacement at the
chest wall, and validate face orientation/under-breast folds.

## Source files
- https://github.com/makehumancommunity/makehuman/tree/master/makehuman/data/targets/breast
- https://github.com/makehumancommunity/makehuman/blob/master/makehuman/data/3dobjs/base.obj
- https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/target.md

"""
(OUT/"TARGET_TRANSFER_REPORT.md").write_text(report)
print(report)

# Generate an EXPERIMENTAL spatial transfer for optional browser preview.
# This is not an original MakeHuman target: GLB geometry has different topology.
import json
import struct
from scipy.sparse import coo_matrix

glb_bytes=(HERE/"assets/female-base-mesh-base_female.glb").read_bytes()
json_length=struct.unpack_from("<I",glb_bytes,12)[0]
gltf=json.loads(glb_bytes[20:20+json_length].decode("utf-8"))
bin_start=20+json_length+8
def accessor(idx):
    a=gltf["accessors"][idx]
    view=gltf["bufferViews"][a["bufferView"]]
    dtype={5121:"u1",5123:"<u2",5125:"<u4",5126:"<f4"}[a["componentType"]]
    ncomp={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a["type"]]
    offset=bin_start+view["byteOffset"]+a.get("byteOffset",0)
    return np.frombuffer(glb_bytes,dtype=np.dtype(dtype),offset=offset,
                         count=a["count"]*ncomp).reshape(-1,ncomp).copy()
source_tree=cKDTree(mapped_src)
breast_joint_ids=set()
for skin in gltf["skins"]:
    for j,nid in enumerate(skin["joints"]):
        name=gltf["nodes"][nid].get("name","").lower().replace(".","")
        if name in ("breastl","breastr"): breast_joint_ids.add(j)
def sm(x):
    t=np.clip(x,0.0,1.0)
    return t*t*(3-2*t)
def weighted_mapped_displacement(pos):
    dist,nn=source_tree.query(pos,k=12,workers=1)
    ww=1.0/(dist+0.003)**2
    ww/=ww.sum(axis=1,keepdims=True)
    dv=(shift[nn]*ww[:,:,None]).sum(axis=1)*scale
    # Keep physically moderate displacement; this source is not the
    # exact body topology/shape from which our exported GLB was produced.
    dv=np.clip(dv,[-0.035,-0.055,-0.035],[0.035,0.025,0.035])
    return dv
entries={}
metrics=[]
for mid,m in enumerate(gltf["meshes"]):
  for pi,prim in enumerate(m["primitives"]):
    attrs=prim["attributes"]
    if "JOINTS_0" not in attrs or "WEIGHTS_0" not in attrs:continue
    pos=accessor(attrs["POSITION"]).astype(float)
    joints=accessor(attrs["JOINTS_0"])
    weights=accessor(attrs["WEIGHTS_0"]).astype(float)
    w=np.sum(np.where(np.isin(joints,list(breast_joint_ids)),weights,0.0),axis=1)
    tissue=sm((w-0.003)/0.30)
    # Exclude the back/upper chest and all arm/torso regions outside
    # the breast's actual bone-weighted surface.
    front=sm((pos[:,2]-0.025)/0.065)
    region=sm((pos[:,1]-1.02)/0.075)*(1-sm((pos[:,1]-1.38)/0.07))
    gate=tissue*front*region
    mapped=weighted_mapped_displacement(pos)*gate[:,None]
    if prim["indices"] is not None and len(pos)>30000:
        faces=accessor(prim["indices"]).reshape(-1,3)
        edge0=np.concatenate([faces[:,0],faces[:,1],faces[:,2]])
        edge1=np.concatenate([faces[:,1],faces[:,2],faces[:,0]])
        A=coo_matrix((np.ones(len(edge0)),(edge0,edge1)),
                     shape=(len(pos),len(pos))).tocsr()
        degree=np.asarray(A.sum(axis=1)).ravel().clip(min=1)
        for _ in range(4):
            mapped=.75*mapped+.25*(A@mapped)/degree[:,None]
        mapped*=gate[:,None]
        def inversion_count(field):
            old=np.cross(pos[faces[:,1]]-pos[faces[:,0]],pos[faces[:,2]]-pos[faces[:,0]])
            newpos=pos+field
            new=np.cross(newpos[faces[:,1]]-newpos[faces[:,0]],newpos[faces[:,2]]-newpos[faces[:,0]])
            area=np.linalg.norm(old,axis=1)
            cosine=np.einsum("ij,ij->i",old,new)
            return int(np.sum((cosine<0)&(area>1e-9)))
        inv=inversion_count(mapped)
        attenuate=1.0
        while inv>2 and attenuate>0.16:
            attenuate*=0.8
            inv=inversion_count(mapped*attenuate)
        mapped*=attenuate
    else:
        inv=0
        attenuate=1.0
    good=np.where(np.linalg.norm(mapped,axis=1)>0.00008)[0]
    key=str(len(pos))
    entries[key]=[[int(i)]+[round(float(n),6) for n in mapped[i]] for i in good]
    metrics.append((key,int(len(good)),round(float(np.linalg.norm(mapped,axis=1).max()),5),inv,attenuate))
output={
 "source":"MakeHuman hm08 CC0 target soft-minus-firm, spatially interpolated",
 "license":"CC0",
 "version":1,
 "warning":"Experimental approximate transfer. Not a native MakeHuman shape key.",
 "referenceMaxCup":"female-young-averagemuscle-averageweight-maxcup",
 "referenceAxis":"GLB XYZ, metres",
 "parts":entries
}
(HERE/"assets/makehuman_firmness_approx.json").write_text(json.dumps(output,separators=(",",":")))
with (OUT/"TARGET_TRANSFER_REPORT.md").open("a") as fp:
    fp.write("\n## Experimental approximate transfer preview\n")
    for key,count,maximum,flips,atten in metrics:
        fp.write("- GLB primitive with "+key+" vertices: "+str(count)+" moved; max displacement "+str(maximum)+" m; flipped faces "+str(flips)+"; safety scale "+str(round(atten,3))+"\n")
    fp.write("- Preview data: torso_mesh_lab/assets/makehuman_firmness_approx.json\n")
print("Generated experimental preview:", metrics)
