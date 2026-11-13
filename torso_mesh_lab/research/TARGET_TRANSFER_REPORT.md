# MakeHuman firmness target transfer — diagnostic

Input source: MakeHuman community hm08 CC0 base.obj and CC0 breast targets.
Destination: Innerscene adapted female GLB, \`torso_mesh_lab/assets/\`.

## Vertex correspondence
- Original MakeHuman source vertices: **19,158**
- Our exported GLB body primitive vertices: **63,750**
- Original max-firmness target vertices: **704**
- Original min-firmness target vertices: **864**
- Different mesh topology / vertex indices: **direct copy is not possible**.
- Fitted approximate uniform scale: **0.094131**
- Fitted Y/Z translation (m): **0.78514, -0.00074**
- Nearest surface discrepancy in body region, p50/p90/p99 (m): **[0.00648, 0.01682, 0.03673]**
- Nearest surface discrepancy for target vertices, p50/p90/p99 (m): **[0.00718, 0.01647, 0.03734]**

## Original firmness displacement (soft minus firm)
- Changed source points: **876**
- Mean signed source-space displacement (x, y, z): **[0.0, -0.318, 0.0036]**
- Mean magnitude source units: **0.3423**
- 90th percentile magnitude source units: **0.8118**
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


## Experimental approximate transfer preview
- GLB primitive with 63750 vertices: 1229 moved; max displacement 0.01502 m; flipped faces 0; safety scale 0.262
- GLB primitive with 457 vertices: 457 moved; max displacement 0.0151 m; flipped faces 0; safety scale 0.262
- GLB primitive with 2210 vertices: 0 moved; max displacement 0.0 m; flipped faces 0; safety scale 0.262
- GLB primitive with 639 vertices: 0 moved; max displacement 0.0 m; flipped faces 0; safety scale 0.262
- GLB primitive with 1195 vertices: 0 moved; max displacement 0.0 m; flipped faces 0; safety scale 0.262
- GLB primitive with 3444 vertices: 0 moved; max displacement 0.0 m; flipped faces 0; safety scale 0.262
- GLB primitive with 1076 vertices: 0 moved; max displacement 0.0 m; flipped faces 0; safety scale 0.262
- Preview data: torso_mesh_lab/assets/makehuman_firmness_approx.json
