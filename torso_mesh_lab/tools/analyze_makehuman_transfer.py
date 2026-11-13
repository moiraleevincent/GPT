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
