"""Independent 3D tool audition: small articulated creature and cinematic camera."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=640; sc.render.resolution_y=640; sc.render.resolution_percentage=100
sc.render.fps=12; sc.frame_start=1; sc.frame_end=48
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
def mat(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF");bs.inputs["Base Color"].default_value=(*color,1)
 bs.inputs["Roughness"].default_value=rough;bs.inputs["Metallic"].default_value=metal
 return m
porcelain=mat("hand-painted porcelain",(.67,.83,.82),.38)
blue=mat("deep sea blue",(.07,.19,.31),.52)
pink=mat("rosy blush",(.9,.31,.37),.6)
gold=mat("brushed brass",(.86,.58,.24),.32,.65)
dark=mat("ink",(.015,.03,.07))
floor=mat("stage",(.06,.09,.14))
def ell(name,loc,scale,material,segments=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 return o
def parent(o,p):
 o.parent=p; o.matrix_parent_inverse=p.matrix_world.inverted()
def empty(name,location,parent_obj=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=location
 if parent_obj: parent(o,parent_obj)
 return o
root=empty("ROOT controls the creature",(0,0,0))
body=ell("pear-shaped body",(0,0,1.42),(.54,.40,.69),porcelain);parent(body,root)
belly=ell("painted chest oval",(0,-.382,1.38),(.29,.045,.4),blue);parent(belly,root)
head=empty("head pivot",(0,0,1.97),root)
skull=ell("rounded head",(0,-.01,2.37),(.47,.39,.45),porcelain);parent(skull,head)
for s in [-1,1]:
 eye=ell("eye white",(.18*s,-.36,2.39),(.11,.042,.11),gold);parent(eye,head)
 iris=ell("eye ink",(.18*s,-.399,2.39),(.052,.029,.065),dark);parent(iris,head)
 cheek=ell("painted cheek",(.29*s,-.338,2.20),(.11,.026,.055),pink);parent(cheek,head)
 shoulder=empty("shoulder pivot "+str(s),(.49*s,0,1.77),root)
 arm=ell("upper arm "+str(s),(.20*s,-.01,-.23),(.22,.21,.37),blue);parent(arm,shoulder)
 elbow=empty("elbow pivot "+str(s),(.37*s,0,-.48),shoulder)
 fore=ell("forearm "+str(s),(.055*s,-.01,-.19),(.16,.16,.29),porcelain);parent(fore,elbow)
 hand=ell("hand "+str(s),(.1*s,-.02,-.43),(.15,.13,.17),gold);parent(hand,elbow)
 leg=ell("leg "+str(s),(.25*s,-.01,.60),(.23,.26,.46),blue);parent(leg,root)
 foot=ell("foot "+str(s),(.25*s,-.21,.20),(.24,.39,.16),gold);parent(foot,root)
 if s==1:
  for frame,a,b in [(1,0,0),(13,-.85,-.4),(26,-1.35,-.72),(38,-.8,-.2),(48,0,0)]:
   shoulder.rotation_euler[1]=a;shoulder.keyframe_insert(data_path="rotation_euler",frame=frame)
   elbow.rotation_euler[1]=b;elbow.keyframe_insert(data_path="rotation_euler",frame=frame)
nose=ell("nose",(0,-.408,2.24),(.07,.06,.065),pink);parent(nose,head)
for frame,a in [(1,-.09),(20,.11),(34,-.16),(48,-.09)]:
 head.rotation_euler[2]=a;head.keyframe_insert(data_path="rotation_euler",frame=frame)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.02));bpy.context.object.data.materials.append(floor)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(4,-8.6,3.45));cam=bpy.context.object;aim(cam,(0,0,1.45))
sc.camera=cam;cam.data.type="PERSP";cam.data.lens=48;cam.data.dof.use_dof=True;cam.data.dof.focus_object=body;cam.data.dof.aperture_fstop=7
for name,pos,power,size,color in [
 ("warm key",(-3,-4,6),850,5,(1,.75,.64)),
 ("blue fill",(4,-3,3),650,4,(.45,.65,1)),
 ("rim",(0,3,5),1100,3,(.7,.93,1))]:
 bpy.ops.object.light_add(type="AREA",location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.size=size;o.data.color=color;aim(o,(0,0,1.5))
sc.world.color=(.10,.10,.10)
sc.frame_set(24);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"creature.blend"))
sc.render.filepath=str(OUT/"poster.png");bpy.ops.render.render(write_still=True)
sc.render.filepath=str(OUT/"frames"/"frame_");(OUT/"frames").mkdir(exist_ok=True)
bpy.ops.render.render(animation=True)
print("3D_AUDITION_DONE")
