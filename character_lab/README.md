# Character Lab — The Star Keeper

**Experiment 001: an original stylized low-poly 3D character built entirely in Blender Python.**

- Procedural torso with seven shaping rings, deliberately separate left/right legs, and a real Blender armature.
- Seven-ring quad-mesh limbs with extra control loops at knees and elbows, weighted across neighboring bones. The topology references inspired these choices, but this is not a hand-retopologized production character.
- Painted-by-material geometric details: face, swept hair, costume, brooch, stage, halo and a star that follows her hand.
- 30-frame (2.5 sec at 12 fps) keyed motion of upper arm, forearm, spine and head.
- Cycles CPU rendering to `output/poster.png`, `output/star_keeper.mp4` and editable `output/star_keeper.blend` (the .blend stays in the GitHub Actions artifact to keep git lean).

## Run
```bash
blender -b -t 4 --factory-startup --python-exit-code 1 --python character_lab/scene.py
ffmpeg -y -framerate 12 -i character_lab/output/frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 character_lab/output/star_keeper.mp4
```

## View
[Character Lab website](https://moiraleevincent.github.io/GPT/character_lab/)

[Rendering workflow](https://github.com/moiraleevincent/GPT/actions/workflows/character-lab.yml)

**Next stage:** improve joint weights, revise the silhouette and move toward a more complex character. The current model is intentionally a proof of concept.
