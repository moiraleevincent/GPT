# Blender Lab — First Motion

A genuine Blender Python experiment: an articulated character with a real armature, keyframed joints, studio lighting, material colors and a camera. This is a technical test of our animation pipeline, not yet the character from the SVG sketch.

## Automatic rendering
The GitHub Actions workflow installs Blender and FFmpeg, builds the editable .blend scene, renders a 24-frame waving animation, creates an MP4 and saves a still poster. You can download all three from the workflow's artifact or see the two previews committed to this folder if the workflow succeeds.

## Run locally
From the repository root:

```bash
blender --background --factory-startup --python-exit-code 1 --python blender_lab/scene.py
ffmpeg -y -framerate 12 -i blender_lab/output/frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 22 -movflags +faststart blender_lab/output/first_motion.mp4
```

The puppet is not driven by individual hand-drawn frames: Blender interpolates its arm and spine bones and repositions the attached meshes.

Next, if the pipeline works, we can move from this toy puppet to a version using our existing editable SVG silhouette.
