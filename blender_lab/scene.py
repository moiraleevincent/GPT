"""First Motion: a small, genuinely rigged Blender puppet.
Run: blender --background --factory-startup --python-exit-code 1 --python blender_lab/scene.py
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
FRAMES=OUT/"frames"
FRAMES.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine="CYCLES"
s.cycles.samples=8
# Ubuntu package can lack OpenImageDenoiser; render without denoising.
if hasattr(s.cycles, "use_denoising"):
    s.cycles.use_denoising=False
if hasattr(bpy.context.view_layer.cycles, "use_denoising"):
    bpy.context.view_layer.cycles.use_denoising=False
s.render.resolution_x=480
s.render.resolution_y=560
s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGBA"
s.render.fps=12
s.frame_start=1
s.frame_end=24
s.view_settings.view_transform="Standard"
s.world.color=(.15,.15,.15)

def mat(name,rgb,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    shader=m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value=(*rgb,1)
    shader.inputs["Metallic"].default_value=metal
    shader.inputs["Roughness"].default_value=.58
    return m
ink=mat("Midnight ink",(.025,.07,.13))
ivory=mat("Porcelain",(.8,.66,.49))
gold=mat("Old gold",(.78,.47,.13),.58)
rose=mat("Rose",(.53,.15,.21))
teal=mat("Teal",(.11,.35,.39))
cream=mat("Warm paper",(.94,.88,.78))
floor_mat=mat("Blue stage",(.12,.17,.22))

def ellipsoid(name,xyz,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=xyz)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o
def tube(name,start,end,radius,material):
    a,b=Vector(start),Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

arm_data=bpy.data.armatures.new("Joint structure")
rig=bpy.data.objects.new("RIG — edit these bones",arm_data)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
def bone(name,head,tail,parent=None):
    b=arm_data.edit_bones.new(name)
    b.head=head;b.tail=tail
    if parent:b.parent=arm_data.edit_bones[parent]
bone("Spine",(0,0,1.25),(0,0,2.36))
bone("Head",(0,0,2.36),(0,0,2.95),"Spine")
bone("Upper arm",(.37,0,2.28),(.73,0,1.96),"Spine")
bone("Forearm",(.73,0,1.96),(.85,0,1.52),"Upper arm")
bone("Hand",(.85,0,1.52),(.91,0,1.32),"Forearm")
bone("Other upper arm",(-.37,0,2.28),(-.7,0,1.96),"Spine")
bone("Other forearm",(-.7,0,1.96),(-.78,0,1.52),"Other upper arm")
bone("Right thigh",(.17,0,1.22),(.25,0,.62),"Spine")
bone("Right shin",(.25,0,.62),(.25,0,.20),"Right thigh")
bone("Left thigh",(-.17,0,1.22),(-.25,0,.62),"Spine")
bone("Left shin",(-.25,0,.62),(-.25,0,.20),"Left thigh")
bpy.ops.object.mode_set(mode="OBJECT")
rig.show_in_front=True

def attach(o,bn):
    # Real vertex groups and an armature modifier, not pre-rendered frame swapping.
    g=o.vertex_groups.new(name=bn)
    g.add(list(range(len(o.data.vertices))),1,"REPLACE")
    mod=o.modifiers.new("Skeleton drives artwork","ARMATURE")
    mod.object=rig

for name,loc,size,mt,bn in [
    ("Torso",(0,0,1.93),(.37,.19,.56),ink,"Spine"),
    ("Golden sash",(0,0,1.38),(.34,.20,.12),gold,"Spine"),
    ("Face",(0,-.02,2.72),(.29,.18,.37),ivory,"Head"),
    ("Hair",(0,.02,2.97),(.31,.18,.17),ink,"Head"),
    ("Hair bun",(-.23,.09,3.08),(.19,.2,.19),ink,"Head"),
    ("Collar",(0,0,2.32),(.16,.18,.09),rose,"Spine"),
    ("Left eye",(-.10,-.183,2.78),(.035,.025,.06),gold,"Head"),
    ("Right eye",(.10,-.183,2.78),(.035,.025,.06),gold,"Head"),
    ("Nose",(0,-.205,2.67),(.03,.018,.05),ivory,"Head"),
    ("Mouth",(0,-.177,2.56),(.07,.021,.017),rose,"Head"),
    ("Right shoe",(.29,-.02,.15),(.18,.28,.10),ink,"Right shin"),
    ("Left shoe",(-.22,-.02,.15),(.18,.28,.10),ink,"Left shin"),
    ("Right shoulder pin",(.37,-.15,2.28),(.09,.045,.09),gold,"Spine"),
    ("Right elbow pin",(.73,-.15,1.96),(.09,.045,.09),gold,"Upper arm")]:
    attach(ellipsoid(name,loc,size,mt),bn)
for name,p,q,r,mt,bn in [
    ("Right upper arm",(.37,0,2.28),(.73,0,1.96),.115,rose,"Upper arm"),
    ("Right forearm",(.73,0,1.96),(.85,0,1.52),.085,ivory,"Forearm"),
    ("Right hand",(.85,0,1.52),(.91,0,1.32),.09,ivory,"Hand"),
    ("Other upper arm",(-.37,0,2.28),(-.70,0,1.96),.115,ink,"Other upper arm"),
    ("Other forearm",(-.70,0,1.96),(-.78,0,1.52),.085,ivory,"Other forearm"),
    ("Right leg",(.17,0,1.22),(.25,0,.62),.14,teal,"Right thigh"),
    ("Right calf",(.25,0,.62),(.25,0,.20),.12,ink,"Right shin"),
    ("Left leg",(-.17,0,1.22),(-.25,0,.62),.14,teal,"Left thigh"),
    ("Left calf",(-.25,0,.62),(-.25,0,.20),.12,ink,"Left shin")]:
    attach(tube(name,p,q,r,mt),bn)

ellipsoid("Graphic background disc",(0,.36,2.43),(.84,.065,.84),teal)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.035))
bpy.context.object.data.materials.append(floor_mat)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,.9,2))
bg=bpy.context.object
bg.rotation_euler=(math.pi/2,0,0)
bg.data.materials.append(cream)

bpy.ops.object.camera_add(location=(0,-9,2.03))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.73))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=4.5
s.camera=cam
for name,pos,power,size in [
    ("Warm softbox",(-3,-4,6),650,5),
    ("Cool rim",(3,1,4),450,4)]:
    bpy.ops.object.light_add(type="AREA",location=pos)
    l=bpy.context.object
    l.name=name
    l.data.energy=power
    l.data.size=size
    l.rotation_euler=(Vector((0,0,1.8))-l.location).to_track_quat("-Z","Y").to_euler()

def turn(name,degrees,frame):
    p=rig.pose.bones[name]
    rest=rig.data.bones[name].matrix_local.to_3x3()
    axis=rest.inverted() @ Vector((0,1,0))
    p.rotation_mode="QUATERNION"
    p.rotation_quaternion=Quaternion(axis,math.radians(degrees))
    p.keyframe_insert("rotation_quaternion",frame=frame)
for frame,shoulder,elbow,tilt in [
    (1,0,0,0),(5,65,-40,-3),(9,110,-25,2),
    (13,90,25,-2),(17,110,-22,3),(21,75,-20,0),(24,0,0,0)]:
    turn("Upper arm",shoulder,frame)
    turn("Forearm",elbow,frame)
    turn("Spine",tilt,frame)
s.frame_set(1)
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
s.render.filepath=str(FRAMES/"frame_")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"first_motion.blend"))
s.render.filepath=str(OUT/"poster.png")
bpy.ops.render.render(write_still=True)
s.render.filepath=str(FRAMES/"frame_")
bpy.ops.render.render(animation=True)
print("BLENDER_SMOKE_TEST_SUCCESS",OUT)
