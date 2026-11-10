# Torso baseline lab — landmarks, measurements, deltas

This is the **measurement foundation** for resetting our 3D model to **torso only**.

### Snapshot

Source: [human_study_02/index.html](../human_study_02/index.html), blob `ea74b8a42a8ab5e1153fac615506045f04d83b0e`. Machine-readable stations: [measurements.json](measurements.json).

| Outer-surface station | World Y | Width | Nominal depth |
|---|---:|---:|---:|
| Widest hip ring, source Y 1.62 | 2.598 | 1.118 | 0.68 |
| Waist ring, source Y 2.04 | 3.1335 | 0.534 | 0.376 |
| Upper torso ring, source Y 2.65 | 3.91125 | 0.888 | 0.46 |

Model height is **4.958** arbitrary units (7.57 chosen head heights). The hip-to-waist width ratio at these two *outer contour stations* is **2.094 : 1**. It describes our existing stylized mesh, not an anatomical norm. Nominal depths precede the old mesh's additional posterior glute deformation; they are **not final silhouette depths**.

### Two distinct kinds of reference

**Anatomical landmarks** such as *acromion*, *cervicale (C7)* and *iliac crest* refer to identifiable structures of the body. They are used to locate where measurements are taken. They are **not necessarily at the widest contour**.

**Outer-surface measurement stations** refer to dimensions of a 3D mesh, e.g. width across the waist ring, front/back depths at the ribcage ring. The widest hip cross-section is *not automatically* the iliac crest, and the upper torso width is *not automatically* biacromial breadth.

Use [ISO 7250-1:2017](https://www.iso.org/standard/65246.html) as a terminology/measurement-definition reference, **not** as a source of universal body proportions. Use [MakeHuman's base mesh](https://static.makehumancommunity.org/about/concepts/basemesh.html) as a candidate reference surface: [core graphics are CC0](https://www.makehumancommunity.org/about/license.html). We have **not** yet measured or imported that mesh.

### Stable coordinate contract

+X/-X: transverse left and right. +Y: up. +Z: anterior, -Z: posterior. The source applies a piecewise height remap; the JSON includes old `parameterY` and actual `worldY`. The torso is generated as elliptical rings, then separately sculpted at its posterior. A nominal ring radius does not encode independent front/back shape.

### Next construction method

1. Select an anatomically plausible **reference torso** and match pose/height before comparison.
2. Keep known landmarks distinct from speculative proxies; never invent a bone location from an outer contour.
3. Sample left/right/front/back **separately** at corresponding normalized heights; use a clear `target minus current` delta for each dimension.
4. Build a **torso-only, single-surface** shell with independent anterior/posterior and left/right controls; avoid glued muscle spheres.
5. Use fixed orthographic front, side and rear views for comparison; require a render inspection before accepting a change.

### Unknowns

A reference person's sex, size, age, posture and shape distribution are not yet chosen. Consequently, no anatomical *target* deltas are available. The numeric snapshot is intentionally only a **starting baseline**, not a claim about correct anatomy.
