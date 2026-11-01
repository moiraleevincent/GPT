"""The Star Keeper — procedural low-poly Blender character and real skeletal animation.
This scene is generated from code, with continuous quad-ring joints and gradient
bone weights (instead of separate cylinders). Blender runs headlessly on GitHub.
"""
import bpy
import math
import random
from mathutils import Vector, Quaternion
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/"output"
FRAMES=OUT/"frames"
FRAMES.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=12
scene.render.resolution_x=480
scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.render.fps=12
scene.frame_start=1
scene.frame_end=30
scene.view_settings.view_transform="Standard"
if hasattr(scene.cycles,"use_denoising"):
    scene.cycles.use_denoising=False
if hasattr(bpy.context.view_layer.cycles,"use_denoising"):
    bpy.context.view_layer.cycles.use_denoising=False
scene.world.color=(.14,.14,.14)

def material(name,rgb,rough=.72,metal=0,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgb,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    if emission:
        e=m.node_tree.nodes.new("ShaderNodeEmission")
        e.inputs["Color"].default_value=(*rgb,1)
        e.inputs["Strength"].default_value=emission
        mix=m.node_tree.nodes.new("ShaderNodeAddShader")
        m.node_tree.links.new(p.outputs["BSDF"],mix.inputs[0])
        m.node_tree.links.new(e.outputs[0],mix.inputs[1])
        m.node_tree.links.new(mix.outputs[0],m.node_tree.nodes.get("Material Output").inputs["Surface"])
    return m

skin=material("warm porcelain skin",(.78,.57,.43))
blush=material("auburn rose",(.53,.20,.19))
hair=material("dark auburn hair",(.125,.053,.050))
hair_light=material("copper hair highlights",(.41,.16,.10))
ink=material("midnight blue velvet",(.038,.064,.103))
blue=material("indigo coat panels",(.065,.115,.19))
wine=material("wine red vest",(.28,.065,.115))
leather=material("black leather boots",(.039,.034,.045))
gold=material("brushed antique gold",(.77,.49,.19),.4,.65)
cream=material("bone white linen",(.87,.73,.53))
eyes=material("eyes and pupils",(.032,.065,.074))
moon=material("luminous moth light",(.42,.95,.77),emission=2.8)
stone=material("charcoal carved stone",(.094,.104,.136))
floor=material("midnight stage",(.083,.115,.15))
back=material("dusky violet backdrop",(.13,.115,.18))

# Actual Blender armature: moving a bone deforms weighted mesh vertices.
data=bpy.data.armatures.new("Star Keeper skeleton")
rig=bpy.data.objects.new("RIG • animate the character here",data)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
def bone(n,head,tail,parent=None):
    b=data.edit_bones.new(n)
    b.head=head
    b.tail=tail
    if parent:
        b.parent=data.edit_bones[parent]
bone("Hips",(0,0,1.53),(0,0,1.87))
bone("Spine",(0,0,1.87),(0,0,2.81),"Hips")
bone("Head",(0,0,2.82),(0,0,3.62),"Spine")
for side,sgn in [("R",1),("L",-1)]:
    bone("UpperArm."+side,(sgn*.43,0,2.72),(sgn*.72,0,2.31),"Spine")
    bone("Forearm."+side,(sgn*.72,0,2.31),(sgn*.83,0,1.91),"UpperArm."+side)
    bone("Hand."+side,(sgn*.83,0,1.91),(sgn*.87,0,1.72),"Forearm."+side)
    bone("Thigh."+side,(sgn*.20,0,1.60),(sgn*.25,0,.99),"Hips")
    bone("Shin."+side,(sgn*.25,0,.99),(sgn*.24,0,.24),"Thigh."+side)
bpy.ops.object.mode_set(mode="OBJECT")
rig.show_in_front=True

def skin_mesh(obj,weights):
    for n,arr in weights.items():
        group=obj.vertex_groups.new(name=n)
        for i,w in arr:
            if w>0.0001:
                group.add([i],min(1,max(0,w)),"REPLACE")
    mod=obj.modifiers.new("Skinning • follows bones","ARMATURE")
    mod.object=rig
    return obj

def all_to_bone(obj,bone_name):
    # Apply transforms so every vertex rests in armature's world coordinates.
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return skin_mesh(obj,{bone_name:[(i,1) for i in range(len(obj.data.vertices))]})

def mesh_obj(name,verts,faces,mat,weights=None):
    md=bpy.data.meshes.new(name+" geometry")
    md.from_pydata(verts,[],faces)
    md.update()
    obj=bpy.data.objects.new(name,md)
    bpy.context.collection.objects.link(obj)
    md.materials.append(mat)
    if weights:skin_mesh(obj,weights)
    return obj

def ellipse(name,pos,radii,mat,bone_name=None,segments=16,rings=10):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=pos)
    o=bpy.context.object;o.name=name;o.scale=radii;o.data.materials.append(mat)
    if bone_name:all_to_bone(o,bone_name)
    return o

def cyl(name,a,b,radius,mat,bone_name=None,vertices=12):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=(b-a).length,location=(a+b)*.5)
    o=bpy.context.object;o.name=name
    o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(mat)
    if bone_name:all_to_bone(o,bone_name)
    return o

# A tapered tube with connected quad rings and properly blended skinning.
# The knee and elbow get extra loops, per the topology references.
def joint_tube(name,points,radii,upper,lower,mat,axis="Y",n=12):
    verts=[];faces=[]
    weights={upper:[],lower:[]}
    for ri,p in enumerate(points):
        p=Vector(p)
        direction=Vector(points[min(ri+1,len(points)-1)])-Vector(points[max(0,ri-1)])
        direction.normalize()
        reference=Vector((0,1,0)) if axis=="Y" else Vector((1,0,0))
        u=direction.cross(reference).normalized()
        v=direction.cross(u).normalized()
        blend=(0,0,.14,.46,.82,1,1)[ri] if len(points)==7 else ri/(len(points)-1)
        for j in range(n):
            theta=2*math.pi*j/n
            q=p+radii[ri]*(math.cos(theta)*u+math.sin(theta)*v)
            index=len(verts)
            verts.append(q[:])
            weights[upper].append((index,1-blend))
            weights[lower].append((index,blend))
    for k in range(len(points)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n
            faces.append((a,b,b+n,a+n))
    faces.append(tuple(reversed(tuple(range(n)))))
    faces.append(tuple((len(points)-1)*n+j for j in range(n)))
    return mesh_obj(name,verts,faces,mat,weights)

def torso_loft():
    # Closed, intentional waist/hip silhouette instead of a cylinder.
    rings=[
        (1.52,.30,.23),(1.72,.34,.235),
        (1.91,.255,.20),(2.10,.245,.19),
        (2.36,.34,.225),(2.61,.39,.24),(2.79,.31,.205)]
    n=14;v=[];f=[]
    for z,rx,ry in rings:
        for i in range(n):
            angle=2*math.pi*i/n
            v.append((rx*math.cos(angle),ry*math.sin(angle),z))
    for k in range(len(rings)-1):
        for i in range(n):
            a=k*n+i;b=k*n+(i+1)%n
            f.append((a,b,b+n,a+n))
    f+=[tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
    weights={"Hips":[],"Spine":[]}
    for k in range(len(rings)):
        w=max(0,min(1,(k-1)/2.5))
        for i in range(n):
            ix=k*n+i
            weights["Hips"].append((ix,1-w))
            weights["Spine"].append((ix,w))
    mesh_obj("Tailored torso • 7 cross-section loops",v,f,blue,weights)
torso_loft()

# Shape the two legs individually; they are not fused at the crotch.
for side,sgn in [("R",1),("L",-1)]:
    x=sgn*.205
    points=[(x,0,1.57),(x+sgn*.023,0,1.37),
            (x+sgn*.05,0,1.10),(x+sgn*.055,0,1.015),
            (x+sgn*.057,0,.965),(x+sgn*.04,0,.70),
            (x+sgn*.015,0,.22)]
    joint_tube("continuous knee mesh "+side,points,[.19,.18,.145,.133,.13,.11,.095],
               "Thigh."+side,"Shin."+side,ink)
    ellipse("boot cap "+side,(x+sgn*.015,-.095,.155),(.165,.28,.13),leather,"Shin."+side,12)
    cyl("tall boot trim "+side,(x+sgn*.02,0,.55),(x+sgn*.04,0,.66),.13,gold,"Shin."+side,12)
    a=(sgn*.43,0,2.72);b=(sgn*.72,0,2.31);c=(sgn*.83,0,1.91)
    line=[
       a,(sgn*.51,0,2.61),(sgn*.67,0,2.385),
       b,(sgn*.745,0,2.245),
       (sgn*.79,0,2.07),c]
    joint_tube("continuous elbow mesh "+side,line,
               [.17,.165,.135,.124,.12,.108,.095],
               "UpperArm."+side,"Forearm."+side,wine if side=="R" else blue)
    ellipse("small articulated hand "+side,(sgn*.87,0,1.80),(.105,.075,.15),skin,"Hand."+side,12)
    ellipse("shoulder cloth "+side,a,(.22,.22,.19),ink,"UpperArm."+side,12)
    cyl("gold cuff "+side,(sgn*.81,0,2.0),(sgn*.83,0,1.955),.12,gold,"Forearm."+side,12)

# Short, flared, low-poly asymmetric coat panels
def coat_panel(name,x_offset,shift,mt,bn):
    verts=[(-.30+x_offset,-.18,1.87),(.30+x_offset,-.18,1.87),
          (.37+x_offset,-.23,1.43),(-.42+x_offset,-.23,1.43),
          (-.31+x_offset,.08,1.86),(.30+x_offset,.08,1.86),
          (.42+x_offset,.07,1.43),(-.45+x_offset,.07,1.43)]
    verts=[(x+shift if z<1.7 else x,y,z) for x,y,z in verts]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)]
    mesh_obj(name,verts,faces,mt,{bn:[(i,1) for i in range(8)]})
coat_panel("swinging cloak tails",0,.14,ink,"Hips")
ellipse("wine scarf collar",(0,-.17,2.71),(.25,.12,.105),wine,"Spine",12)
ellipse("embroidered front vest",(0,-.224,2.28),(.238,.049,.42),wine,"Spine",14)
cyl("gold diagonal sash",(-.17,-.286,2.57),(.21,-.30,1.99),.031,gold,"Spine",10)
ellipse("gold compass brooch",(.01,-.305,2.52),(.115,.046,.115),gold,"Spine",12)
ellipse("brooch inset",(.01,-.352,2.52),(.057,.023,.057),moon,"Spine",12)

# Stylized expressive face with volume, eyes, nose, brows, cheek planes.
ellipse("head • low poly face",(0,-.012,3.20),(.315,.245,.413),skin,"Head",20,12)
for side,sgn in [("R",1),("L",-1)]:
    ellipse("ear "+side,(sgn*.30,.015,3.13),(.073,.07,.12),skin,"Head",10)
    ellipse("eye white "+side,(sgn*.126,-.23,3.225),(.085,.041,.054),cream,"Head",12)
    ellipse("dark iris "+side,(sgn*.133,-.265,3.228),(.038,.020,.046),eyes,"Head",12)
    ellipse("eye sparkle "+side,(sgn*.119,-.282,3.251),(.011,.006,.014),moon,"Head",10)
    cyl("dramatic brow "+side,(sgn*.055,-.252,3.35),(sgn*.21,-.225,3.375),.017,hair,"Head",8)
    ellipse("rosy cheek "+side,(sgn*.18,-.218,3.085),(.075,.014,.034),blush,"Head",10)
ellipse("small nose",(0,-.278,3.122),(.042,.067,.093),skin,"Head",12)
cyl("smile",(-.07,-.242,2.993),(.07,-.242,2.993),.012,blush,"Head",10)
ellipse("hair crown",(0,.027,3.56),(.326,.247,.19),hair,"Head",16,10)
ellipse("high braided bun",(-.17,.14,3.81),(.21,.21,.21),hair,"Head",12)
ellipse("bun gold clasp",(-.23,-.018,3.83),(.06,.04,.06),gold,"Head",10)
for i in range(7):
    x=-.255+i*.085
    ellipse("layered swept fringe %d"%i,(x,-.177,3.48+.018*math.sin(i)),(.077,.11,.15),hair_light if i%3==1 else hair,"Head",9,6)
for side,sgn in [("R",1),("L",-1)]:
    ellipse("loose hair lock "+side,(sgn*.285,-.055,3.33),(.07,.09,.27),hair,"Head",10)

# The star moth: a decorative articulated prop attached to the raised hand.
def star(name,center,r1,r2,mat,bn):
    x,y,z=center
    v=[]
    for i in range(10):
        a=2*math.pi*i/10+math.pi/2
        r=r1 if i%2==0 else r2
        v.append((x+r*math.cos(a),y,z+r*math.sin(a)))
    v.append((x,y-.06,z))
    faces=[(10,i,(i+1)%10) for i in range(10)]
    o=mesh_obj(name,v,faces,mat,{bn:[(j,1) for j in range(len(v))]})
    return o
star("magical star (wrist driven)",(.91,-.02,1.64),.19,.084,moon,"Hand.R")
ellipse("star central jewel",(.91,-.068,1.64),(.045,.037,.045),gold,"Hand.R",12)

# A graphic, architecturally interesting stage to show the 3D lighting.
cyl("black stage plinth",(0,0,.02),(0,0,.105),1.5,stone,vertices=32)
cyl("brass plinth edge",(0,0,.115),(0,0,.143),1.48,gold,vertices=32)
# Pillars deliberately behind the character, never crossing the face.
for i,(x,y) in enumerate([(-1.56,1.16),(-1.34,1.32),(1.34,1.32),(1.56,1.16)]):
    cyl("background pillar %d"%i, (x,y,.28),(x,y,3.68),.019,gold,vertices=12)
# A luminous ring behind the character, made from many small 3D tubes.
for i in range(32):
    a=2*math.pi*i/32
    b=2*math.pi*(i+1)/32
    p=(1.28*math.cos(a),.83,2.09+1.39*math.sin(a))
    q=(1.28*math.cos(b),.83,2.09+1.39*math.sin(b))
    cyl("celestial halo segment",p,q,.014,gold,vertices=8)
random.seed(11)
for i in range(28):
    a=random.uniform(0,2*math.pi)
    rad=random.uniform(1.35,2.65)
    x=rad*math.cos(a)
    z=2.06+rad*math.sin(a)
    if z<.3 or z>4.5:continue
    ellipse("distant floating dust %02d"%i,(x,1.5,z),(.022,.021,.022),moon,segments=8,rings=5)

# Background/ground material geometry
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.0))
bpy.context.object.name="floor"
bpy.context.object.data.materials.append(floor)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,2.3,2))
wall=bpy.context.object;wall.name="violet gallery backdrop"
wall.rotation_euler=(math.pi/2,0,0)
wall.data.materials.append(back)

bpy.ops.object.camera_add(location=(5.7,-9.5,4.05))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,2.06))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=4.84
scene.camera=cam

for name,position,power,size,rgb in [
    ("warm portrait key",(-3.5,-4.3,7),760,4.5,(1.0,.77,.54)),
    ("lavender fill",(4.2,-3.4,4.5),480,4.2,(.64,.72,1.0)),
    ("turquoise rim",(1.7,2,4.4),620,3.1,(.44,1.0,.88))]:
    bpy.ops.object.light_add(type="AREA",location=position)
    l=bpy.context.object;l.name=name;l.data.energy=power;l.data.size=size;l.data.color=rgb
    l.rotation_euler=(Vector((0,0,2))-l.location).to_track_quat("-Z","Y").to_euler()

# Keyframed motion, not independent rendered images.
def rotate(n,deg,frame):
    p=rig.pose.bones[n]
    rest=rig.data.bones[n].matrix_local.to_3x3()
    axis=rest.inverted() @ Vector((0,1,0))
    p.rotation_mode="QUATERNION"
    p.rotation_quaternion=Quaternion(axis,math.radians(deg))
    p.keyframe_insert(data_path="rotation_quaternion",frame=frame)
for frame,arm,elbow,spine,head in [
    (1,0,0,-1,-3),(7,-27,-7,1,0),
    (14,-79,-24,0,-7),(20,-67,-29,-1,-2),
    (25,-83,-14,1,-6),(30,0,0,-1,-3)]:
    rotate("UpperArm.R",arm,frame)
    rotate("Forearm.R",elbow,frame)
    rotate("Spine",spine,frame)
    rotate("Head",head,frame)

scene.frame_set(18)
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"star_keeper.blend"))
scene.cycles.samples=36
scene.render.filepath=str(OUT/"poster.png")
bpy.ops.render.render(write_still=True)
scene.cycles.samples=12
scene.render.filepath=str(FRAMES/"frame_")
bpy.ops.render.render(animation=True)
print("STAR_KEEPER_SUCCESS",OUT)
