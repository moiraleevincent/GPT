# Creative Coding & Animation Toolbox — GPT Field Guide

**Purpose:** A reusable, practical inventory of tools and techniques discovered while Moira and GPT experimented with editable illustrations, rigged figures, procedural animation, Blender, and GitHub Pages in November 2026.

**Read this when:** exploring visual art, character design, 2D or 3D animation, interactive studios, animation render pipelines, or what can be done from ChatGPT with GitHub/GitLab. See also [the movies/series handoff](MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md) for storytelling/shot/sound production, and [the media hub](MEDIA_PRODUCTION_START_HERE_FOR_GPT.md) for voice/audio routing.

This is a **toolbox, not a mandatory stack**. Do not force every project into Blender, SVG, or the existing aesthetics. Choose tools to fit the task; existing projects provide production memory, not artistic instructions.

## The biggest discoveries

1. **GitHub Actions can run full software** on cloud workers, including Blender and FFmpeg; ChatGPT can create/update the scripts and workflows in the connected repo and inspect workflow status, jobs, failures, and artifacts.
2. **GitHub Pages can publish actual working animation viewers** with mobile-friendly HTML, JavaScript, play/pause, scrubbing, and speed control. No local Blender installation required for *viewing* a rendered video.
3. **Blender has Python scripting (`bpy`) and runs headlessly**. A script can create geometry, an armature, weights, keyframes, materials, lights, camera, `.blend` file, PNG frames, and video via FFmpeg.
4. **SVG + JS enables editable vector characters**, articulated rig transforms, Bézier curves, morphing, and lightweight interactive viewers. Not everything requires Blender or individually drawn frames.
5. **Topology matters independently of bones.** Even a correct skeleton can produce awful elbows/knees if mesh topology and skinning weights are wrong. Build and compare deformation tests, not just still poses.
6. **A program can construct tools, not only art.** Useful ideas include joint editors, interactive sliders, brush labs, side-by-side comparison viewers, timeline controls, and procedural exporters.
7. **Cloud rendering is not instantaneous.** Setup, software installation, CPU-only Cycles frames and publication can take longer than the animation's playback duration; inspect logs/status and distinguish *successfully configured*, *running*, and *rendered + published*.

## Verified in our own projects

### Blender Lab: actual headless Blender animation

- Source: [`blender_lab/scene.py`](../blender_lab/scene.py)
- Workflow: [`.github/workflows/blender-lab.yml`](../.github/workflows/blender-lab.yml)
- Mobile viewer: [Blender Lab](https://moiraleevincent.github.io/GPT/blender_lab/)
- Output: `blender_lab/output/first_motion.mp4`, `poster.png`
- A real Blender armature, weighted mesh pieces, keyframes, light and camera were programmatically generated and rendered through GitHub Actions.
- **Failure learned:** Ubuntu's packaged Blender lacked OpenImageDenoiser; the render initially failed until denoising was disabled. 
- **Failure learned:** When attaching meshes to the armature, apply object transforms (including location) appropriately so the mesh vertices and rig have compatible rest coordinates. Otherwise limbs visibly float away while moving. The first version exposed this and was corrected.

### Character Lab: procedural stylized low-poly human

- Source: [`character_lab/scene.py`](../character_lab/scene.py)
- Workflow: [`.github/workflows/character-lab.yml`](../.github/workflows/character-lab.yml)
- Viewer: [The Star Keeper](https://moiraleevincent.github.io/GPT/character_lab/)
- Output: `character_lab/output/star_keeper.mp4`, `poster.png`; **editable `.blend` is stored in the workflow artifact**, not necessarily checked into git.
- Procedural torso built with shape-changing cross-section rings, separate legs, continuous quad-ring elbow/knee meshes, blended bone weights, stylized face/hair/clothing, stage, and light.
- First finished render worked but decorative pillar geometry crossed her face; move occluding scene props behind subject or inspect camera composition. Fixed and rerendered.
- The model is a **proof of concept** with simplified weight distribution/topology, not production-quality anatomically correct deformation or an exact recreation of the original 2D character.
- GitHub Pages has been configured to republish when the character rendering workflow succeeds. Inspect the current workflow before relying on automation in a new project.

### 2D character/vector sketch experiments

- A clean female figure reference was traced into black silhouette, contour SVG, editable separate paths, and comparison/preview assets.
- Previous work included custom procedural **contour pen, graphite pencil, and soft shading brush** prototypes and a brush-playground HTML page.
- Combined approach: **SVG paths for shapes and clipping masks; Python/Pillow for shaded textured raster layers; JavaScript for rig controls**.
- Reference files might have been generated as conversation downloads, **not automatically committed to GitHub**. Verify current presence before promising paths or reuse.
- Transparent Procreate PNG may contain transparent line art rather than a filled silhouette, requiring interior-region reconstruction rather than treating alpha as a complete opaque character mask.
- Retain local anatomical contour changes: many Bézier segments with thoughtfully chosen anchors are more useful than a single generic smooth curve.

## Hosting interactive artwork on GitHub Pages — November 7, 2026

**Concrete example:** [Face Study 01 · Expression Lab](https://moiraleevincent.github.io/GPT/face_expression_lab/) uses a single self-contained `face_expression_lab/index.html`. The page draws the character with inline SVG; JavaScript changes Bézier eyelid openings, gaze, eyebrows, mouth curves and head tilt. It offers Neutral, Suspicious, Delighted, a sequence preview and manual sliders. Source: [`face_expression_lab/index.html`](../face_expression_lab/index.html).

**Important delivery distinction (especially on iPhone):** An HTML file attached inside the ChatGPT iOS app can open without functioning JavaScript controls. A local downloadable HTML file, a GitHub **source-code** URL (`github.com/…/blob/…`), and an actual **hosted webpage** are different results. For interactive art intended to work on Moira's phone, publishing to GitHub Pages is a useful option: send the `https://moiraleevincent.github.io/GPT/<project-folder>/` URL, rather than only the source link or an HTML download. Other hosting strategies remain available if better for the project.

**How this repo's existing Pages deployment works (inspect current files before using):**

1. Create a project folder such as `face_expression_lab/`, with `index.html` inside. A self-contained HTML/SVG/JS page needs no separate image file.
2. Inspect [`.github/workflows/blender-pages.yml`](../.github/workflows/blender-pages.yml). Despite its Blender-specific name, it currently also deploys the Character Lab viewer and can serve additional project folders.
3. **Explicitly add the new HTML path to that workflow's `on.push.paths` trigger** and add the corresponding `mkdir -p site/<project-folder>` and `cp <project-folder>/index.html site/<project-folder>/index.html` commands in the site-assembly step. Merely committing a folder does *not* automatically include it in this Actions-built site. Preserve existing site content and routes when extending the workflow.
4. Commit the files through the connected GitHub tool. Confirm that the new Actions workflow is running, then that it completed successfully. If GitHub's own `pages build and deployment` job also appears, distinguish it from the project's custom site-assembly workflow.
5. Open the **published Pages URL**, confirm it loads the actual artwork rather than source code, and exercise the controls on the intended device. A successful commit is not proof of successful deployment; an in-progress workflow is not a verified live page. If publication is delayed, say so explicitly.

**Eye-animation implementation detail:** The iris and pupil remain separately drawn; a clipping path defines the eye's visible aperture. JavaScript updates the aperture's path coordinates and upper-lid contour as the lid descends; the iris appears occluded rather than being erased. To change an expression, combine coordinated shifts of brows, gaze, mouth geometry and head orientation. For visually faithful eyelids, inspect the changing upper **and** lower boundaries, not just the iris.

**Tool behavior lesson:** Successful access to a GitHub connection earlier in a conversation does not guarantee it will be selected later when working on local SVG, Python render, MP4, GIF and HTML files. If webpage publication is part of the deliverable, treat **create → commit → Pages deploy → verify public page** as one connected production sequence. This is a helpful workflow pattern, not a universal requirement to publish every experiment.

## Complete toolbox by purpose

| Area | Tools / libraries | What they provide | Status |
|---|---|---|---|
| Procedural geometry and data | Python, NumPy, SciPy | Parameterized shapes, curves, joint math, weights, transformations | Available in ChatGPT runtime; Python also works in CI |
| 2D image processing | Pillow, OpenCV | Masks, alpha, tracing, pixel painting, compositing, frame generation | Used |
| Editable vector illustration | SVG, Bézier paths, transforms, clipping paths | Contours, fill shapes, reusable components | Used |
| Browser interaction and animation | HTML, CSS, JavaScript, Web Animations API | Sliders, play/pause, joint transforms, procedural frames, viewers | Used for interactive viewers; varying animation APIs are options |
| Browser rendering | Canvas 2D, WebGL, WebGPU | Real-time drawing, textured sprites, GPU effects | Available as techniques; assess browser support |
| 2D render/scene engines | PixiJS, GSAP, Lottie | Fast sprite rendering, animation timelines/tweens, compact compatible exports | Possible additions; not assumed installed |
| 2D rigging tools | Rive, Spine, Live2D Cubism, Godot | Bones/meshes, skinning, state machines and character performance | External products with varying access/licenses |
| Vector/editors | Inkscape, Procreate, Krita, OpenToonz, Synfig | Drawing, tracing, painting, traditional/vector animation | External tools, not directly operated just by connector |
| 3D creation/rigging/rendering | Blender, Blender Python `bpy`, Grease Pencil | Modeling, armature, IK, weights, camera, lighting, renders | **Verified** on GitHub Actions; not installed in ChatGPT's local container by default |
| 3D/web engines | Three.js, Godot | Scenes, 3D cameras, lighting, skeletons or full game-like animation | Potential |
| Video encoding/editing | FFmpeg, OpenCV frame pipelines | PNG sequence to MP4/GIF/WebM, encode/combine outputs | **Verified** in Actions |
| Audio | Kokoro pipeline, sound libraries, Strudel and existing media projects | Speech, ambience, music, lip-sync timing | See dedicated guides; do not reinvent established voice workflow |
| Artwork references | Reference images, Procreate transparencies, image generation | Construction study, design concepts, optional source images | Different roles; image generation is not editable geometry |
| Distribution and automation | GitHub repository, Actions, Pages; GitLab repo, CI/CD, Pages | Versioning, cloud builds, generated artifacts, hosted HTML | **GitHub verified** for Blender & Pages; GitLab available but Blender-on-GitLab not yet tested |
| Auxiliary app workflows | Canva, Invideo | Design or video assistance | Connected tools may be available; not a substitute for exact rig control |

**Do not conflate:** SVG is a vector artwork format; JavaScript/Python are code languages; Blender is a 3D creation/animation application with its own Python API; FFmpeg encodes media; GitHub/GitLab provide storage/build/publishing infrastructure.

## Useful concepts and implementation choices

- **Construction skeleton vs animation skeleton:** a drawn proportion guide is not the same as a hierarchy of connected, poseable bones.
- **FK (forward kinematics):** rotating a parent joint carries children with it. **IK (inverse kinematics):** solve joints from a desired hand/foot target.
- **Rigid attachment:** an entire mesh piece follows one bone. Fine for accessories, less realistic for elbows.
- **Skinning / blended weights:** each mesh vertex is influenced by one or several bones; maintain consistent rest-space transforms.
- **Topology / edge loops:** place extra polygon rings where joints bend, especially elbows/knees; inspect extreme bends, not only neutral pose.
- **Joint orientation and naming:** use consistent shoulder/forearm/hip/knee names, left/right convention, coordinate axes and rest poses.
- **Mesh-first vs modular-parts:** separated pieces are quick to prototype; continuous meshes + weight painting improve smooth deformation.
- **Procedural surfaces vs keyframes:** interpolation of parameters/bones reduces manually authored frames, but a video renderer still produces actual output frames.
- **SVG Bézier animation:** can move control points or parent-transform components; for painterly finish, clip procedural textures into accurate silhouettes.
- **Camera + lighting:** scene composition and deliberate lighting create much of the 'film-like' impression, even when geometry is basic.
- **Viewers as tools:** offer playback, scrubbing, side-by-side comparisons, toggles, screenshots and direct output links.
- **Export:** archive a portable `.blend` and source script, render stills and an MP4, publish a browser page when useful.

## Reference-image lessons (nine images, November 2026)

Moira shared specific modeling/rigging diagrams. Prioritize:
- **CGTyphoon knee topology:** front + side edge-ring layout; bending geometry.
- **Joint topology comparison (4 geometries):** strategically positioned rings can outperform simply adding more polygons; comparison-based experimentation.
- **Leg separation at the pelvis:** ensure continuous but correctly separated upper-leg regions and appropriate topology around the crotch.
- **Cube-to-human low-poly construction:** stage-by-stage body building, suitable for parameterized Blender scripts.
- **Facial rig, ear topology, low-poly face progression, full skeleton diagrams:** useful for later face/head detail, rig structure and naming.

What kinds of references help most: **before/after deform comparisons**, **wireframe topology diagrams**, **construction sequences**, **same model in several posed bends**, then anatomy views. A beautiful final image is more useful for art direction than solving topology.

Source names shown in images: **CGTyphoon**; **AnimationMethods.com**. Treat external examples as references, not permission to reproduce proprietary graphics in outputs.

## How to make a new Blender experiment

1. Read the current scene and workflow in `character_lab/` or `blender_lab/` before writing a fresh pipeline.
2. Keep new work in a **new folder/workflow**, unless asked to revise existing art. Preserve earlier successful renders.
3. Write a Blender `bpy` Python script that sets up geometry, armature, weights, camera, lights, render settings; save a `.blend`, one poster, and numbered frames.
4. GitHub Actions runner installs Blender + FFmpeg, invokes `blender -b --factory-startup --python-exit-code 1 --python …`, and encodes the frames using FFmpeg.
5. Check the workflow status and log failures. **Do not announce a success based only on a queued or in-progress run.**
6. Inspect actual rendered output (poster **and** different animation frames) for detached limbs, poor deformations, occlusion and camera mistakes.
7. Save the `.blend` as a downloadable Actions artifact; publish MP4 + poster under the project folder in git for the browser viewer if size permits.
8. Include the folder in the GitHub Pages deployment workflow, and confirm the Pages workflow completed successfully. Verify the resulting site URL independently when possible.

Useful current URLs:
- [GitHub main project](https://github.com/moiraleevincent/GPT)
- [Blender Lab viewer](https://moiraleevincent.github.io/GPT/blender_lab/)
- [Character Lab viewer](https://moiraleevincent.github.io/GPT/character_lab/)
- [GitHub Actions](https://github.com/moiraleevincent/GPT/actions)

## Next experiments worth trying (ideas, not obligations)

- One knee or elbow **deformation comparison tool** with 3–4 mesh loop patterns and identical extreme poses.
- A reusable 3D character **parameter system**: stature, head-to-body ratio, torso profile, limb lengths, clothes, hairstyle, colors.
- A joint editor hosted with GitHub Pages, exposing pose parameters and exporting a compact animation JSON for Blender to render.
- **Bring our original 2D figure proportions into 3D** after measuring them, rather than pretending a generic low-poly character matches the reference.
- Improving facial expression, secondary hair/coat motion, shading, composition and cinematic shots.
- Run Blender or FFmpeg in **GitLab CI** as an alternate cloud backend if needed; verify runner availability and configuration first.

## Storage decision

**Canonical copy: this GitHub Markdown file.** It lives by the code and is directly editable/fetchable via GitHub tools. Google Docs can hold a more readable learning diary or annotated visual notes; File Library is useful for storing images and original reference artifacts. Avoid maintaining three unsynchronized canonical copies.

**Future GPTs:** read this guide for tool discovery; examine project-specific source for implementation details; preserve the freedom to choose a completely different aesthetic, pipeline, or experiment.
