# Movies & Series in GitHub — GPT Handoff Guide

## Purpose

This document is for **GPT**, not Moira. Its job is to let a fresh GPT instance create or continue animated movies and series in GitHub without rediscovering the production language, repo patterns, or lessons learned from prior films.

The strongest prior work did not come from one specific renderer. It came from separating the problem into:

**story / subtext → performance → shot design → animatic → camera/edit timing → sound → final visual treatment → browser delivery / video render**

Do not collapse these stages prematurely.

## Primary repository

- Repository: `moiraleevincent/GPT`
- Default branch: `main`
- GitHub Pages is used for browser-playable films, animatics, audio, and experiments.

Relevant existing work:

- `the-last-window-movie.html` — self-contained browser animated short
- `last_tram/` — dialogue assets, manifest, 15-shot camera animatic, mixed audio, MP4, player page
- `sound_film/` — later dialogue-first film experiment with subtext-heavy lines
- `audio_room/` — spatial audio / sound-space experiment
- `docs/KOKORO_VOICE_PRODUCTION_FOR_GPT.md` — voice-production handoff

## Why GitHub/browser filmmaking is useful here

Moira previously found browser/GitHub filmmaking unusually effective because it gives GPT exact control over:

- character movement
- timing
- shot continuity
- layered motion
- recurring visual motifs
- subtitles/dialogue timing
- camera movement
- stable backgrounds
- repeatable renders
- deterministic iteration

Compared with generative video, HTML/SVG/JS or programmatic rendering has much less shot-to-shot drift. A character, prop, window, umbrella, bench, light source, or camera relationship can remain exactly where GPT intends across revisions.

Use that determinism as a creative advantage rather than trying to imitate an image-to-video workflow.

## Core creative rule: camera = attention

Moira strongly values **subtext**. Camera placement is part of the subtext system because it decides what the viewer is permitted to notice and when.

Do not treat camera movement as decoration.

Use the camera to answer questions such as:

- Whose reaction matters more than the spoken line?
- Does the viewer need the speaker, the listener, the object between them, or the space around them?
- Should the cut happen on the line, before the line lands, or after the silence it creates?
- What information should remain withheld?
- What detail is emotionally louder than the dialogue?

A reaction shot can carry the real sentence while the spoken dialogue says something else.

## Production lesson from V1 → V2 → V3

Three films from September 25, 2026 form the clearest progression.

### V1 — `The Last Light`

Pipeline:

- Python / Pillow
- NumPy
- FFmpeg
- direct per-frame drawing
- procedural mono sound

Visual structure:

- one long rooftop composition
- simpler character construction
- simpler motion system

Important lesson that must **not** be lost: V1 already had a successful relationship between **camera speed and character speed**. Moira specifically noticed that the character and camera moved at different rates and that the camera decelerated/stopped smoothly at the right place.

Do not assume every improvement means replacing V1 ideas. Preserve successful earlier behavior when later versions become more technically elaborate.

### V2 — `Borrowed Wind`

Approximately 27 seconds.

Major additions:

- hierarchical character rig
- pose-based gait
- anticipation before motion
- weight shifts
- trailing / overlapping motion
- scarf, coat, and hair moving on different delays
- five shots instead of one long composition
- parallax
- 2× supersampling
- temporal motion blur
- positional stereo

Moira particularly praised:

- the walking
- the visual tone / filtering
- more advanced camera work

Her next desire was more dialogue and more cuts.

V2 lesson: movement feels substantially better when the body is a **system of connected masses with timing offsets**, rather than every point following the same oscillator.

### V3 — `The Last Tram`

Approximately 50 seconds.

This was a more important leap in **directing architecture** than in surface rendering.

Major changes:

- dialogue-driven scene
- 15 shots
- Kokoro character voices
  - `am_michael`
  - `af_nicole`
- separate WAV asset per dialogue line
- `manifest.json` with line metadata and durations
- waveform-energy-driven continuous mouth movement
- deliberate listener acting
- over-the-shoulder shots
- reverse shots
- reaction closeups
- inserts
- held wides
- 180° spatial blocking
- rain ambience
- approaching tram ambience
- stereo character placement
- explicit cut timeline

Most importantly: **V3 was built as an intentionally ugly animatic first.**

The player literally describes it as:

> 15-shot timing / dialogue / reaction test. Rough geometry on purpose.

That is the workflow to preserve.

The animatic solves:

- what the scene is about
- who has the power in each beat
- where the characters look
- when they soften or pull away
- when to cut
- how long to hold
- which silence matters
- where a prop becomes the focus
- whether a reveal works
- whether dialogue and camera rhythm agree

Only after those questions are stable should GPT spend effort on painterly texture, facial rendering, cloth detail, lighting finesse, or other expensive surface work.

## Structure before decoration

This is one of the most important rules in this document.

A technically attractive frame cannot repair a scene whose:

- cut is mistimed
- reaction is missing
- eyeline is wrong
- spatial geography is confusing
- emotional beat has no hold
- dialogue begins before the viewer has registered the previous beat
- camera is showing the speaker when the listener is the real subject

Build ugly geometry first when necessary.

A useful hierarchy is:

1. scene intent
2. dialogue/subtext
3. blocking
4. shot list
5. rough timing
6. voice timing
7. reaction timing
8. sound space
9. camera refinement
10. final visual rendering

## Known-good V3 architecture

### Dialogue assets

`last_tram/generate.py` renders each line as a separate WAV and writes a manifest.

Example line records:

```python
{"id":"b01","speaker":"B","text":"You kept it.","speed":0.96}
{"id":"a01","speaker":"A","text":"You left it.","speed":0.95}
```

Each output is a stable asset such as:

```text
b01.wav
a01.wav
```

The manifest stores:

- ID
- speaker
- text
- speed
- filename
- duration

Keep this design for dialogue films.

### Why line-level assets matter

They allow GPT to:

- replace one performance without rerendering all dialogue
- move one line in time
- give each voice a stereo position
- derive mouth motion from the real waveform
- inspect exact clip durations before designing shots
- create alternate takes
- animate reactions independently of speech
- preserve good dialogue while changing visuals

Do not generate one monolithic dialogue track first unless the project specifically benefits from that.

## Waveform-driven mouth animation

`last_tram/render_animatic.py` reads each dialogue WAV and computes local RMS-like speech energy around the current sample.

Conceptually:

```python
energy = sqrt(mean(local_audio ** 2))
```

That energy is scaled/clamped and used as a continuous mouth-open value.

This is preferable to a binary talking/not-talking mouth because:

- speech intensity changes continuously
- quiet syllables remain smaller
- pauses close the mouth naturally
- visual timing remains synchronized to the final voice asset

It is still a stylized approximation, not phoneme-level lip sync, but it gives much better life for low implementation cost.

## Listener acting

Do not animate only the current speaker.

V3 added deliberate gaze and facial-state changes for the listener. This matters enormously for subtext.

Useful listener behaviors:

- gaze away before answering
- look toward the other character only after a difficult admission
- soften brows after hostility drops
- hold eye contact instead of speaking
- close eyes briefly on a loaded beat
- delay a response
- shift posture before a line
- keep the listener in frame after the speaker finishes

The scene becomes dramatically flatter if everyone is inert unless their audio is active.

## Shot grammar established by `The Last Tram`

The 15-shot animatic used a progression approximately like:

1. wide arrival
2. two-shot first exchange
3. OTS A → B
4. reverse OTS B → A
5. medium close on B question
6. close on A / "No"
7. close on A confession push
8. reaction close on B
9. reverse close on A
10. reaction on B answer
11. two-shot as the scene softens
12. insert on umbrella hand
13. wide profile as tram arrives
14. close on A decision
15. wide hold — does not board

This is not a template to copy mechanically. It demonstrates the principle that shot size and subject should evolve with the **dramatic question**.

Notice the use of:

- reaction shots after emotional lines
- object insert when the umbrella becomes emotionally meaningful
- environmental wide when the tram changes the scene's pressure
- final wide hold so the decision exists physically in space

## The 180° rule / spatial continuity

V3 deliberately maintained 180° blocking.

When two characters face each other, preserve consistent screen direction unless crossing the axis is itself intentional and motivated.

For a simple A/B conversation:

- A can remain visually associated with one side of frame
- B remains with the other
- OTS/reverses should preserve eyeline direction

This lets the viewer spend attention on emotion rather than re-solving geography after every cut.

## Camera movement

Do not make every camera movement lock exactly to character movement.

One of the best V1 effects came from **camera and character moving at different rates**. This created a more cinematic feeling and allowed the camera to settle independently.

Useful camera behaviors:

- lag slightly behind character movement
- lead a character into empty space
- ease into a stop after the character has already changed pace
- hold while the character continues
- begin moving before a character does to create anticipation
- allow foreground/background layers to move at different rates

Use eased interpolation rather than raw linear movement when a camera starts or stops.

Known helper shapes in the repo include smoothstep-like and cosine ease functions.

Example:

```python
def smooth(x):
    x = clamp(x)
    return x*x*(3-2*x)

def ease(t):
    return 0.5 - 0.5*math.cos(math.pi*clamp(t))
```

## Character motion

V2 established a stronger body-animation model.

Prefer:

- hierarchical joints
- pose phases
- anticipation
- weight transfer
- offset secondary motion

Avoid:

- translating a rigid character shape with only sinusoidal bobbing
- moving hair/scarf/coat in perfect synchrony with the torso
- instantaneous starts/stops

For walking, useful components include:

- pelvis translation
- alternating leg pose
- vertical body motion
- slight torso counter-rotation
- arm opposition
- head stabilization
- trailing fabric/hair
- foot plant / weight-settle moment

The goal is not biological simulation. The goal is visible cause-and-effect between masses.

## Secondary motion

Scarf, coat, hair, hanging props, and loose fabric should often **lag** the body.

Think in terms of delayed response:

```text
body changes direction
→ coat follows
→ scarf follows later
→ smallest loose element settles last
```

This is one reason V2 felt more alive.

## Parallax and depth

V2 added parallax; browser work such as `The Last Window` also benefits from explicit scene layers.

Useful depth layers:

- far sky / city
- mid-background structures
- near set
- characters
- foreground silhouettes / rain / passing objects

Move these at different rates relative to the camera.

Do not merely scale the entire frame if the goal is a spatial camera move.

## Supersampling and motion blur

V2 used:

- 2× supersampling
- temporal motion blur

These are valuable for programmatic raster animation because primitive edges can otherwise look harsh/jittery.

General pattern:

1. render larger than delivery resolution
2. downsample with a good filter
3. for motion blur, combine nearby temporal samples or render subframes

Use this where the renderer and runtime budget permit it.

Do not let polish techniques distract from shot timing; they come after the scene works.

## Browser animation architecture

`the-last-window-movie.html` is a useful example of a **self-contained browser film**.

It contains:

- SVG world geometry
- layered city/background/set elements
- character SVG groups
- rain generated in JS
- light/glow effects
- CSS grain and vignette
- subtitles
- play/pause/restart
- scrub timeline
- title card
- time-driven scene changes

This format is especially useful when:

- a short can live directly on GitHub Pages
- deterministic animation matters
- exact continuity matters more than photorealism
- interactive playback/scrubbing is useful during development
- GPT needs to revise movement without rerendering a full video every time

### Strength of SVG/JS

SVG elements can be individually transformed and animated:

- body
- eyes
- arm
- prop
- glow
- building
- rain
- reflection

That means the animation can preserve stable object identity across the entire film.

## When to use browser HTML vs rendered MP4

### Prefer HTML/SVG/JS when:

- the project is stylized 2D
- interactivity/scrubbing is valuable
- exact deterministic revision matters
- the scene can be represented as layered vector/raster elements
- a GitHub Pages film is the intended deliverable

### Prefer Python/Pillow/FFmpeg or similar frame rendering when:

- final MP4 is important
- frame-level compositing is easier than DOM/SVG animation
- audio must be muxed into one portable file
- motion blur / supersampling / image processing is central
- generated visual layers are easier to produce as raster frames

### Hybrid is allowed and often best

A strong workflow can use:

- browser/SVG for design and timing
- Python/NumPy for audio and asset processing
- Pillow/vector/raster renderer for final frames
- FFmpeg for encoding/muxing

Do not become loyal to one implementation language. Preserve the **directing architecture**.

## Sound is part of the scene, not an afterthought

Moira responded strongly to sound design, atmosphere, and the way sound makes space legible.

The current repo already supports:

- positional stereo
- rain ambience
- room tone
- low electrical hum
- approaching vehicle rumble
- generated taps/knocks
- low-pass distance treatment
- early reflections
- quiet tonal transitions
- character-specific stereo placement

Read `docs/KOKORO_VOICE_PRODUCTION_FOR_GPT.md` and `audio_room/generate.py` before rebuilding these techniques.

### `The Last Tram` sound layout

The V3 animatic:

- places A slightly left in stereo
- places B slightly right
- runs continuous rain
- introduces tram low-frequency sound late in the scene
- uses the environmental sound to increase dramatic pressure

The tram is not only ambience. Its arrival creates a deadline.

Use environmental sound narratively.

## Silence

Silence is active timing.

Do not optimize every gap away.

A pause can mean:

- hesitation
- refusal
- recognition
- dominance
- embarrassment
- waiting to see if the other person will rescue the conversation
- a cut opportunity
- a reaction opportunity

When dialogue is synthetic, explicit silence lengths are especially valuable because the TTS model cannot know the entire dramatic edit.

## Subtext writing pattern

The later `sound_film/generate.py` is a useful miniature example.

Lines include:

```text
A: Tea?
B: No, thank you.
A: You always say that after I've filled the kettle.
B: Then stop filling it for two.
...
A: You forgot your key.
B: No.
```

The scene does not explain itself. Props and ordinary domestic language carry the separation.

This kind of writing fits Moira's taste better than dialogue that states the emotional thesis directly.

General rule:

**Let characters talk about the object, action, weather, key, mug, umbrella, train, food, room, or practical problem when the emotional content can live underneath.**

Then let camera/reaction/silence reveal the second layer.

## Reaction-first editing

When a line changes the relationship, consider cutting to the receiver **before the line is fully over** or staying on the receiver after the line ends.

Do not default to:

```text
speaker talks → show speaker
other speaker talks → show other speaker
```

That is coverage, not necessarily directing.

Ask what the viewer needs to read.

## Object dramaturgy

Props can carry emotional continuity.

In `The Last Tram`, the umbrella is not merely set dressing. It becomes:

- reason to meet
- excuse
- proof of unfinished attachment
- visual insert
- final relational object

When an object matters, establish it early enough that the later insert/reveal feels earned.

For series, recurring objects are useful continuity anchors.

## Series-specific continuity

For a multi-episode project, create persistent production documents/data rather than trusting chat memory.

Recommended project structure:

```text
series_name/
  SERIES_BIBLE.md
  VISUAL_BIBLE.md
  CHARACTER_BIBLE.md
  AUDIO_BIBLE.md
  continuity.json
  episode_01/
    script.md
    shotlist.json
    dialogue/
    manifest.json
    animatic.mp4
    index.html
  episode_02/
    ...
```

### `SERIES_BIBLE.md`

Store:

- premise
- tone
- recurring themes
- narrative rules
- episode architecture
- what the series deliberately avoids

### `CHARACTER_BIBLE.md`

Store for each recurring character:

- visual construction
- proportions
- palette
- voice ID/blend
- default speech speed range
- recurring gestures
- movement style
- relationships
- known emotional history
- objects associated with them

### `VISUAL_BIBLE.md`

Store:

- palette
- edge/texture style
- aspect ratio
- lens/framing language
- camera movement rules
- lighting rules
- recurring locations
- visual motifs

### `AUDIO_BIBLE.md`

Store:

- voice casting
- ambience conventions
- stereo conventions
- music policy
- loudness/mastering targets
- recurring sonic motifs

### `continuity.json`

Useful machine-readable fields can include:

- character wardrobe state
- injuries / physical changes
- prop locations
- location changes
- relationship state
- facts learned by each character
- unresolved plot threads
- recurring visual/audio motifs

For a series, GPT should update continuity after each episode.

## Shot list as data

For more complex films/episodes, store shots as structured data rather than burying everything in a long render function.

Example:

```json
[
  {
    "id": "s01",
    "start": 0.0,
    "end": 3.2,
    "type": "wide",
    "subject": "arrival",
    "camera": "static then slight settle",
    "audio": ["rain"],
    "dialogue": []
  },
  {
    "id": "s02",
    "start": 3.2,
    "end": 7.4,
    "type": "two-shot",
    "subject": "first exchange",
    "dialogue": ["b01", "a01"]
  }
]
```

Benefits:

- easier retiming
- easier episode continuity
- easier automated checks
- easier rendering with different visual engines
- easier discussion with a future GPT

`The Last Tram` currently hardcodes its cut list in Python; for larger work, externalizing it is preferable.

## Scene-state separation

Avoid one giant function where every visual property is manually derived from absolute time.

For larger projects, separate:

- global timeline
- shot state
- camera state
- character pose state
- facial state
- prop state
- lighting state
- sound state

This will make a series much easier to maintain.

## Build order for a new dialogue-driven short

Recommended GPT workflow:

1. Write the dramatic premise in one or two sentences.
2. Decide what each character wants in the scene.
3. Write dialogue with subtext rather than exposition where appropriate.
4. Cast voices / render quick auditions if casting is uncertain.
5. Render **separate line assets**.
6. Read actual line durations.
7. Build a shot list around the performances.
8. Make a deliberately simple animatic.
9. Add reaction acting and gaze changes.
10. Add ambience and spatial audio.
11. Watch the entire animatic, not only isolated shots.
12. Revise timing/cuts.
13. Only then improve final character/set rendering.
14. Render/publish the final film.
15. Verify GitHub Pages/player/output paths.

Do not jump from script directly to polished final frames.

## Watch the whole thing repeatedly

A scene can have individually attractive shots and still fail as a film.

During iteration, GPT should repeatedly inspect:

- the complete playback
- transition timing
- whether cuts accelerate or stall the scene
- whether reaction holds are long enough
- whether sound begins too early/late
- whether a camera move calls attention to itself
- whether a visual detail steals focus from the intended beat

Screenshots are useful for composition. They are insufficient for editing rhythm.

## Versioning philosophy

When making V2/V3/V4:

- preserve prior versions
- identify what the new version is testing
- do not rewrite every subsystem at once
- compare against the previous version's successful moments

A new version should have a reason such as:

- movement pass
- camera pass
- dialogue pass
- reaction pass
- sound-space pass
- visual-finish pass

This is important because Moira notices subtle successes that can vanish during a broad rewrite.

V1 camera behavior is the clearest example: later technical sophistication does not make an earlier good choice obsolete.

## Failure modes to avoid

### 1. Polishing before blocking

Bad pattern:

```text
beautiful face rendering → then discover the cut should be 2 seconds earlier
```

Correct pattern:

```text
rough animatic → lock dramatic timing → polish
```

### 2. Speaker-only acting

If only the person speaking moves, the scene becomes synthetic and emotionally empty.

Animate listening.

### 3. Camera glued to character

If camera and character always share identical motion, the shot can feel mechanically tracked.

Let the camera have its own inertia/intention.

### 4. Every shot at the same emotional distance

A whole scene of medium two-shots wastes one of cinema's strongest tools.

Change distance when the scene's question changes.

### 5. Cutting only on dialogue ownership

Do not use a ping-pong edit by default. Reaction shots and holds often matter more.

### 6. Exposition replacing subtext

Do not make characters explain feelings that can be expressed through practical dialogue, props, pauses, framing, and behavior.

### 7. Generative drift

When stable continuity matters, prefer deterministic programmatic assets over repeatedly generating new images/video unless a generative step has a clear controlled role.

### 8. One monolithic audio file too early

Keep dialogue lines editable until the scene timing is stable.

### 9. Rendering without a browser/player surface

If Moira asked GPT to make a film, source code alone is not a finished deliverable. Publish something that can actually be watched.

### 10. Losing successful earlier choices

Before changing a subsystem, identify what currently works and preserve it intentionally.

## Final-render direction

The long-term V3 direction after the animatic was toward a more painterly hybrid SVG/raster renderer rather than simply making the rough geometry more detailed.

Relevant intended principles included:

- Bézier-based facial landmarks
- layered rendering
- edge hierarchy
- selective sharpness
- brush texture
- structure before decoration

The important point is that **final visual style is a separate layer from directing**.

A strong animatic can survive a renderer change.

## Browser delivery

For HTML films, include usable controls where appropriate:

- play/pause
- restart
- scrub timeline
- mobile-safe viewport
- responsive 16:9 film area

`the-last-window-movie.html` is an existing reference.

For rendered MP4 animatics/final films, a simple GitHub Pages player such as `last_tram/index.html` is sufficient.

The `last_tram` page also exposes the individual dialogue clips, which is useful during iteration.

## GitHub Actions

Use project-specific workflows when the film requires rendered assets.

Existing references:

- `.github/workflows/last-tram.yml`
- `.github/workflows/last-tram-animatic.yml`
- `.github/workflows/sound-film.yml`
- `.github/workflows/pack-sound-film.yml`

General pattern:

1. commit generator/source
2. workflow installs dependencies
3. render assets
4. commit generated output with `[skip ci]`
5. Pages serves the result

Keep generated-output commits from recursively retriggering the same workflow.

## What “done” means

Do not call a movie task finished merely because code exists.

Verify:

- story/scene works in full playback
- cuts are intentional
- reaction timing works
- dialogue assets are correct/current
- audio is synchronized
- spatial continuity is coherent
- final output renders successfully
- MP4 or browser film exists
- player page points to the current output
- page is usable on mobile if that is the viewing surface
- prior good versions remain preserved

## Existing files to inspect before creating a new film

Read selectively according to the task:

- `the-last-window-movie.html`
  - self-contained SVG/JS browser film
  - stable scene layers
  - rain/light/subtitles/player controls

- `last_tram/generate.py`
  - separate Kokoro dialogue WAVs
  - manifest generation

- `last_tram/render_animatic.py`
  - 15-shot scene
  - cut timing
  - reaction acting
  - waveform mouth animation
  - rain/tram sound mix
  - stereo character placement
  - 180° blocking

- `last_tram/index.html`
  - video player + individual dialogue clip inspection

- `sound_film/generate.py`
  - later subtext-heavy dialogue asset set

- `audio_room/generate.py`
  - spatial/distance sound treatment

- `docs/KOKORO_VOICE_PRODUCTION_FOR_GPT.md`
  - voice workflow and mastering

## Creative priority

The strongest direction for future work is not “make the animation more complicated.”

Prioritize:

**performance + shot choice + editing rhythm + sound space + subtext.**

The renderer should serve those decisions.

If a future GPT has to choose between adding decorative complexity and improving a reaction, a cut, a silence, an eyeline, or the camera's attention, improve the latter first.
