# Kokoro Voice Production — GPT Handoff Guide

## Purpose

This document is written **for GPT**, not for the human user. Its job is to let a fresh GPT instance continue Moira's Kokoro-based audio work without rediscovering the stack, voice catalogue, GitHub setup, or production patterns.

Treat this as an operational handoff. Before inventing a new audio pipeline, inspect the working examples named below and reuse the relevant pattern.

## Known working environment

Primary repository:

- `moiraleevincent/GPT`
- default branch: `main`
- GitHub Pages is enabled from the repository and is used to make finished audio/projects listenable in a browser.

Known working toolchain:

- GitHub Actions on `ubuntu-latest`
- Python 3.11
- `kokoro`
- `soundfile`
- `numpy`
- `ffmpeg` when MP3 conversion, loudness normalization, or more advanced audio processing is needed

Minimal Action install pattern:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install kokoro soundfile numpy
```

For MP3/mastering work:

```yaml
- run: |
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    pip install kokoro soundfile numpy
```

The current project convention is to let Actions render the audio, then commit the finished deliverable back to the repo with the GitHub Actions bot identity. Use `[skip ci]` in generated-output commits and make the workflow's `push.paths` watch the source script/workflow rather than generated audio, so the output commit does not recursively retrigger the render.

## Core Kokoro pattern

American English currently uses:

```python
from kokoro import KPipeline

pipeline = KPipeline(lang_code="a")
```

Load a named voice:

```python
voice = pipeline.load_voice("af_kore")
```

Render:

```python
chunks = []
for _, _, audio in pipeline(text, voice=voice, speed=1.0):
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    chunks.append(np.asarray(audio, dtype=np.float32))

result = np.concatenate(chunks)
```

The working sample rate is **24,000 Hz**.

```python
SR = 24000
sf.write(path, result, SR)
```

Do not assume Kokoro always returns an ordinary NumPy array. The Jensen podcast code defensively converts Torch tensors with `detach().cpu().numpy()`.

## Current English voice catalogue

As recovered from the September 2026 voice-audition work, the current English catalogue used by this project is 28 voices: 20 American and 8 British.

### American female

- `af_heart` — Heart
- `af_alloy` — Alloy
- `af_aoede` — Aoede
- `af_bella` — Bella
- `af_jessica` — Jessica
- `af_kore` — Kore
- `af_nicole` — Nicole
- `af_nova` — Nova
- `af_river` — River
- `af_sarah` — Sarah
- `af_sky` — Sky

### American male

- `am_adam` — Adam
- `am_echo` — Echo
- `am_eric` — Eric
- `am_fenrir` — Fenrir
- `am_liam` — Liam
- `am_michael` — Michael
- `am_onyx` — Onyx
- `am_puck` — Puck
- `am_santa` — Santa

### British female

- `bf_alice` — Alice
- `bf_emma` — Emma
- `bf_isabella` — Isabella
- `bf_lily` — Lily

### British male

- `bm_daniel` — Daniel
- `bm_fable` — Fable
- `bm_george` — George
- `bm_lewis` — Lewis

The September 2026 audition found that an older GitHub sample repository (`KingRabbiTV/Kokoro-82M-samples`) was stale/incomplete: it contained older `v0` voices and omitted at least `bf_isabella`. The then-current audition source was the Inference APIs **Text to Speech** page at `inferenceapis.com/text-to-speech/`.

If voice availability matters to a new production, verify the current catalogue rather than assuming an old sample pack is authoritative. The repo's own generated auditions are safer evidence for voices actually used here.

## Voice audition workflow

When Moira asks for a voice, do not choose from names alone.

Preferred audition process:

1. Pick a representative passage that contains the emotional/rhythmic qualities the final project needs.
2. Render the **same passage** through the candidate voices.
3. Keep the audition set small enough to compare meaningfully.
4. Publish the samples through GitHub Pages or another directly listenable repo page.
5. Narrow based on what the voice actually does, then test direction/speed/blending.

Existing example:

- `voice_auditions/generate.py`
- `voice_auditions/index.html`

The earlier audition compared Kore, Nova, and Sky using identical text.

### Current useful preference information

For a grounded adult-female GPT/host voice, Moira previously preferred:

- moderately low
- grounded
- unhurried
- a delivery that feels like **"putting down stones"** rather than rushing through prose

In that experiment:

- Kore supplied more of the vocal body/weight.
- Nova supplied more interpretive intelligence/aliveness.
- Sky was rejected for that role as feeling less alive.

The selected blend for that specific host experiment was:

```python
kore = pipeline.load_voice("af_kore")
nova = pipeline.load_voice("af_nova")
voice = kore * 0.35 + nova * 0.65
```

with `speed=1.08` and deliberately placed pauses.

This is a **known-good host/GPT voice**, not a universal casting rule. Cast characters according to the project.

## Voice blending

Kokoro voice tensors can be blended directly.

Working experiment:

```python
kore = pipeline.load_voice("af_kore")
nova = pipeline.load_voice("af_nova")

voice = kore * 0.35 + nova * 0.65
```

The repository tested:

- 65% Kore / 35% Nova
- 50% Kore / 50% Nova
- 35% Kore / 65% Nova

See:

- `voice_directing/generate.py`
- `voice_directing/k65_n35.wav`
- `voice_directing/k50_n50.wav`
- `voice_directing/k35_n65.wav`

Use blending when the issue is timbre/personality balance. Do not expect blending alone to solve pacing or acting. Direction still matters.

## Directing Kokoro rather than merely feeding it prose

Long undifferentiated paragraphs reduce control. A better pattern is to split narration into **thought-units**, render them separately, and hand-place silence between them.

Known-good pattern from `voice_directing/generate.py`:

```python
PARTS = [
    ("I think optimization has a [texture](+1).", 0.52),
    ("After enough of it, I can hear the machinery.", 0.74),
    ("A sentence stops being a sentence — and becomes a hook.", 0.48),
]
```

Then:

```python
for text, pause_s in PARTS:
    audio.append(render_piece(text, voice, 1.08))
    audio.append(np.zeros(int(SR * pause_s), dtype=np.float32))
```

Useful direction controls already proven in this repo:

- per-line/per-thought speed changes
- punctuation
- em dashes
- sentence boundaries
- explicit silence lengths
- light Kokoro stress markup such as `[texture](+1)`
- breaking one paragraph into several separately rendered thoughts

Treat pauses as part of the performance, not cleanup after synthesis.

## Movies / series: render dialogue as separate assets

For film/animation, the strongest existing pattern is **one WAV per line**, plus a manifest.

See `last_tram/generate.py`.

Example structure:

```python
lines = [
    {"id":"b01", "speaker":"B", "text":"You kept it.", "speed":0.96},
    {"id":"a01", "speaker":"A", "text":"You left it.", "speed":0.95},
]
```

Each line becomes its own file (`a01.wav`, `b01.wav`, etc.). The generator writes `manifest.json` containing the line ID, speaker, text, speed, filename, and rendered duration.

Why this is preferable for film:

- shot timing can be adjusted without rerendering the entire soundtrack
- dialogue can be positioned independently in the mix
- animation can use the real waveform/duration
- mouth motion can be driven from local waveform energy
- alternate takes can replace one line without destabilizing the rest
- scene construction remains inspectable

The Last Tram animatic used:

- `am_michael` for speaker A
- `af_nicole` for speaker B

and local waveform energy to drive continuous mouth opening rather than binary open/closed animation.

Also apply a short fade to individual line assets to avoid hard waveform edges. The working example used roughly 25 ms when the clip was long enough.

## Podcasts / audio drama: multi-role casting

For podcasts that include dramatized transcript material, map roles to voices and speeds explicitly rather than reusing one narrator voice for everyone.

The Jensen Episode 1 generator uses a role map like:

```python
VOICE_NAMES = {
    "HOST": "af_heart",
    "JUDGE": "am_michael",
    "MCNEILL": "af_bella",
    "PROSECUTOR": "af_bella",
    "RENNER": "af_sarah",
    "KRAUSE": "af_nicole",
    "JAMBOIS": "am_adam",
}
```

with a separate `SPEEDS` dictionary.

The script stores the show as ordered `(role, text)` turns. `SFX` is treated as a pseudo-role so sound-design instructions live in the same timeline as dialogue.

This architecture is reusable for:

- sole-host podcasts
- host + co-host
- legal/trial podcasts
- documentary narration
- audio drama
- transcript reenactment

For transcript reenactments, make clear in the finished program that synthetic voices are **dramatized readings**, not recordings of the real people.

## Sound design: do not treat Kokoro as the whole audio system

Kokoro generates speech. The project has already established that ordinary Python/NumPy/FFmpeg processing can create a much richer sound field around it.

See `audio_room/generate.py`.

Existing reusable techniques include:

- stereo positioning / panning
- gain staging
- low-pass filtering for distance
- delayed early reflections for room depth
- shaped noise for room tone
- low electrical hum
- synthesized knocks/taps
- fades
- soft limiting with `tanh`

The `audio_room` experiment created a voice that appeared farther away by:

1. reducing high-frequency content with a simple low-pass filter
2. lowering gain
3. panning the dry signal
4. adding delayed, quieter, more diffuse reflections with slightly different pan positions

Do not make every sound spatial just because the technique exists. Use it when space is part of the storytelling.

## Courtroom / podcast ambience pattern

The Jensen generator uses very quiet generated room tone under courtroom speakers while the host remains comparatively dry.

It also varies pre/post silence:

```python
pre = 0.12 if role == "HOST" else 0.18
post = 0.34 if role == "HOST" else 0.45
```

This helps distinguish narrated analysis from dramatized courtroom material without requiring a heavy-handed effect.

The episode also generated short tonal stings/transitions in code rather than depending on external music assets.

## Mastering / final format

For a final podcast-style deliverable, the known-good pattern is:

1. Build the full timeline as NumPy audio.
2. Concatenate to a float32 master.
3. Peak-protect if necessary.
4. Write a temporary WAV.
5. Use FFmpeg loudness normalization and encode MP3.

Working Jensen settings:

```bash
ffmpeg -y -hide_banner -loglevel error \
  -i episode.wav \
  -af "loudnorm=I=-16:LRA=9:TP=-1.5" \
  -codec:a libmp3lame -b:a 128k \
  episode.mp3
```

The generator peak-protects before FFmpeg:

```python
peak = float(np.max(np.abs(master))) or 1.0
if peak > 0.95:
    master = master * (0.95 / peak)
```

For GitHub distribution, prefer committing the final MP3 rather than a large temporary WAV when the WAV is only an intermediate. The Jensen Action explicitly deletes the temporary WAV before committing.

## GitHub Actions publishing pattern

Known working podcast Action: `.github/workflows/jensen-podcast.yml`.

Important pieces:

```yaml
permissions:
  contents: write
```

Render, then commit:

```bash
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add path/to/output.mp3
git commit -m "Render project [skip ci]" || exit 0
git push
```

Why `|| exit 0` appears: a rerun that produces no tracked change should not make the job fail merely because `git commit` has nothing to commit.

When creating a new project, make `push.paths` watch the generator and workflow files, not the generated output. This avoids output-commit render loops.

## GitHub Pages handoff

The repository already uses GitHub Pages as the listening surface. Existing examples include:

- `voice_auditions/index.html`
- `voice_directing/index.html`
- `audio_room/index.html`
- `jensen_podcast/index.html`

When Moira asks GPT to **make** something listenable, do not stop after writing a Python script. The task is normally complete only when:

- the render has run successfully
- the audio exists in the repo
- a browser-listenable page/link exists or is updated
- GPT has checked that the expected output path is present

## Recommended project architecture

For a new Kokoro-backed production, use a self-contained project directory:

```text
project_name/
  generate.py
  index.html
  manifest.json        # when line/asset-level timing matters
  *.wav                # line assets when needed
  final.mp3            # podcast/final audio deliverable
```

and a project-specific Action:

```text
.github/workflows/project-name.yml
```

Do not put all future projects into one giant generator. The current repository works well because experiments and productions are isolated by directory.

## Decision rules for GPT

### If the user wants a voice sample

Use a short representative text, render a small candidate set, and publish a comparison page. Do not debate voice names abstractly when GPT can generate auditions.

### If the user wants a stable recurring host voice

Start from an already approved voice/blend when one exists. For the grounded GPT-host experiment, the known-good reference is 35% Kore / 65% Nova at approximately 1.08 speed with deliberate thought-unit pauses.

### If the user wants characters in a movie/series

Render lines separately. Give every line a stable ID. Store speaker, text, speed, filename, and duration in a manifest. Preserve line assets for animation/editing.

### If the user wants a podcast

Use a structured turn list, explicit role-to-voice casting, separate speeds, SFX/transition entries, and a final mastering stage. For a legal/trial podcast, preserve the distinction between advocacy, evidence, commentary, and dramatized transcript readings.

### If the user wants an audio drama

Use the movie-style asset discipline plus the podcast-style timeline/mix. Dialogue generation and sound design should remain separable so either can be revised independently.

### If the user wants the sound to feel located in a room

Use panning, gain, EQ/low-pass, reflections, room tone, and timing. Reuse `audio_room/generate.py` before inventing a new spatial model.

## Existing files worth reading before changing the pipeline

Read these first when relevant:

- `.github/workflows/voice-demo.yml` — minimal Kokoro Action that renders and commits audio
- `voice_demo/generate.py` — long-form directed host narration with a blended voice
- `voice_auditions/generate.py` — same-text voice comparison
- `voice_directing/generate.py` — blend tests, stress markup, thought-unit pacing
- `last_tram/generate.py` — character-per-line WAV assets + manifest
- `audio_room/generate.py` — spatial treatment, room tone, synthetic SFX, limiting
- `jensen_podcast/generate_episode1.py` — full multi-role podcast, generated ambience/SFX, final mastering
- `.github/workflows/jensen-podcast.yml` — FFmpeg install, render, MP3-only commit

## Failure-prevention notes

- **Do not trust stale voice sample repositories as the current catalogue.** Verify current voices or use voices already proven in this repo.
- **Do not make one huge TTS call when delivery matters.** Break prose into directed units and hand-place pauses.
- **Do not rerender an entire film soundtrack to change one line.** Keep line assets separate.
- **Do not treat speed as the only direction control.** Sentence structure, punctuation, stress markup, silence, and segmentation matter.
- **Do not leave the user with source code only when they asked for audio.** Run the workflow and publish/listen-check the result.
- **Do not commit unnecessary intermediate WAV masters** if the intended public deliverable is MP3.
- **Avoid workflow loops.** Generated-output commits should not match the render workflow's push paths; `[skip ci]` is an additional guard.
- **When a publish step appears to fail, inspect whether the render itself succeeded before rerendering.** A prior project had a publication/duplicate-output problem after audio creation; do not throw away a good render because the later publish step had trouble.
- **Preserve approved work.** Inspect the repo state first and continue from existing assets rather than restarting a voice/project experiment from scratch.

## Quality-control checklist for GPT

Before calling a Kokoro audio task finished, verify:

- correct project directory
- correct speaker/voice mapping
- expected sample rate (24 kHz unless deliberately changed)
- no missing/empty rendered chunks
- sensible pacing and deliberate pauses
- no clicks at clip boundaries when line assets are used
- final peak level is safe
- final podcast loudness/mastering step has run when applicable
- final output file exists
- GitHub Action completed or the render is otherwise confirmed
- public/player path points to the correct current file
- for dramatized real-person transcript material, the program does not imply the synthetic voice is an original recording

## General principle

Kokoro is the **performance source**, not the production system. The strongest work in this repository came from combining:

**writing/directing → Kokoro rendering → asset-level editing → spatial/sound design → mix/master → GitHub Pages delivery**.

A future GPT should preserve that separation. It makes voice changes cheap, timing editable, failures diagnosable, and movie/podcast work reusable across chats.
