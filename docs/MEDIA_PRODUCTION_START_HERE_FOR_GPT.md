# Media Production — Start Here (for GPT)

## Purpose

This is the routing document for a fresh GPT instance working on Moira's media projects in `moiraleevincent/GPT`.

Before doing anything else, determine whether the current request is **new work** or **continuation**. That distinction controls how existing projects should be used.

- **New work:** Moira is asking the current GPT to create a new movie, episode, podcast, voice piece, or other production. Prior projects are references and production memory. Learn from them, reuse useful infrastructure, and preserve their files, but do **not** adopt an existing finished or unfinished project as the answer merely because it is available. Author a new work unless the request indicates otherwise.
- **Continuation:** Moira is asking to continue, finish, revise, render, repair, publish, or otherwise pick up an existing project. Inspect the current project state first, preserve completed/approved work, and continue from there rather than restarting casually.

If the wording is ambiguous, infer the mode from the current request and context. A request framed around what **you** want to make, what **you** choose, or creating something new generally points toward new authorship even when a highly relevant existing artifact is nearby. An existing project is not automatically the task.

Do **not** begin by inventing a new production stack. Identify the medium, open the relevant handoff guide below, and inspect prior work for useful tools, lessons, and known-working techniques. Continue an existing working state only when continuation is actually the task.

## How to interpret these handoff documents

These documents are accumulated production memory: lessons from previous experiments, known-working techniques, mistakes, references, and judgments that earlier GPTs thought would be useful later.

They are a **toolbox and guide, not policy or superior artistic authority**. The current request, the current project's needs, and the current GPT's judgment still matter. Use what helps, ignore what does not, and depart from prior methods when there is a good reason.

Preserve the distinction between **production memory** and **authorship**. Reusing a voice pipeline, render method, timing lesson, or debugging fix does not require inheriting the prior project's story, aesthetic, camera language, pacing, or other creative decisions.

When Moira deliberately leaves creative choices open, treat the stated requirements as the boundaries of a sandbox rather than filling the open space with choices imported from reference projects. Existing work can show what is possible without deciding what the new work should be.

The handoff system currently covers three production areas:

- Kokoro / voice and audio production
- podcasts
- movies and series in GitHub

There is **no separate speech-to-text/transcription media guide** in this system; that was a voice-to-text misunderstanding in the conversation that created these docs.

## Fast routing

| Moira asks for… | Read first | Also read when relevant |
|---|---|---|
| Voice audition, TTS, narration, dialogue voices, Kokoro | `KOKORO_VOICE_PRODUCTION_FOR_GPT.md` | Podcast or movie guide if the voice belongs inside a larger production |
| Podcast episode, audio documentary, trial podcast, audio-drama podcast | `PODCAST_PRODUCTION_FOR_GPT.md` | `KOKORO_VOICE_PRODUCTION_FOR_GPT.md` |
| Animated short, movie, episode, series, animatic, dialogue scene | `MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md` | `KOKORO_VOICE_PRODUCTION_FOR_GPT.md` for voices/audio |
| Dialogue-heavy film with audio-drama techniques | `MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md` | Kokoro guide; podcast guide can be useful for transcript/source dramatization |
| Trial material used inside a podcast | `PODCAST_PRODUCTION_FOR_GPT.md` | Kokoro guide; source documents in Google Drive |
| Trial material used as a dramatized visual scene | `MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md` | Podcast guide for source discipline; Kokoro guide for voices |
| Spatial audio / room sound / distance effects | `KOKORO_VOICE_PRODUCTION_FOR_GPT.md` | Inspect `audio_room/generate.py` |

## The three handoff guides

### 1. `KOKORO_VOICE_PRODUCTION_FOR_GPT.md`

Use for:

- voice catalogue and auditions
- voice blending
- pacing and emphasis
- line-level dialogue assets
- manifests
- Kokoro/GitHub Actions setup
- spatial audio
- generated ambience/SFX
- mastering and MP3 output
- known working voices and prior casting choices

Important reference projects include:

- `voice_auditions/`
- `voice_directing/`
- `voice_demo/`
- `audio_room/`
- `last_tram/`
- `jensen_podcast/`

### 2. `PODCAST_PRODUCTION_FOR_GPT.md`

Use for:

- research/source workflow
- episode boundaries
- single-host vs co-host decisions
- legal/LawTube-style structure
- dramatized transcript clips
- distinguishing evidence, advocacy, rulings, host synthesis, and outside background
- trial chronology/spoiler discipline
- sound language and mastering
- serial continuity

The strongest current production reference is:

- `jensen_podcast/`

Important creative correction preserved in the guide:

**Do not let legal sophistication turn the host into a lecturer grading the listener.** Let the story create the legal question, explain what the listener now needs, then return to the room/evidence/people.

### 3. `MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md`

Use for:

- browser/SVG/JS filmmaking
- programmatic frame rendering
- animatics
- camera and shot grammar
- reaction acting
- dialogue timing
- character motion
- parallax / depth
- sound as part of directing
- versioning
- series bibles and continuity

Important references include:

- `the-last-window-movie.html`
- `last_tram/`
- `sound_film/`
- `audio_room/`

Important creative lesson preserved in the guide:

**Camera = attention.** The camera, listener reaction, silence, props, and environmental sound can all carry subtext. Treat this as a learned possibility, not a mandatory house style for every new film.

## Dependency map

Think of the system like this:

```text
KOKORO / AUDIO
      ↓
  voices, dialogue, ambience, spatial sound
      ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
PODCAST       MOVIE/SERIES     AUDIO-ONLY PIECE
 ↓               ↓
source/story   shot/camera/acting
 ↓               ↓
final mix      final mix + visual render
 └───────────────┴────────────────┘
                 ↓
         browser/player delivery
```

Kokoro is a production dependency, not the editorial/directing system itself.

## First actions for a fresh GPT

First classify the request as new work or continuation.

### For continuation

1. Inspect the current repo/project state before creating anything.
2. Read the relevant handoff guide.
3. Inspect the specific working reference files named there.
4. Preserve completed work and approved versions.
5. Identify what the new pass is actually testing or adding.
6. Change the smallest useful layer rather than restarting the pipeline.
7. Render/publish a usable result when the request is to *make* media, not merely design it.

### For new work

1. Read the relevant handoff guide for capabilities, lessons, and known-working infrastructure.
2. Inspect only as much prior work as is useful for understanding the production environment.
3. Keep prior projects as references rather than silently converting one into the requested new work.
4. Reuse technical machinery when useful without assuming prior creative decisions should transfer.
5. Make the current work's creative and technical decisions from the current brief.
6. Keep the new project's files distinct enough that prior work remains intact and authorship stays legible.
7. Render/publish a usable result when the request is to *make* media, not merely design it.

## Working lesson: preserve successful behavior

Do not assume a newer version makes every earlier decision obsolete.

A recurring lesson from the movie work is that subtle good behavior can disappear during broad rewrites. For example, V1 already had effective independent camera/character timing even before later versions added more sophisticated character rigs and editing.

Before replacing a subsystem, identify what currently works.

## Working lesson: rough structure before expensive finish

For complex media, solve the structural problem cheaply first.

Examples:

- voice: audition a short representative passage before rendering a whole episode
- podcast: render the first few minutes before committing to the full host grammar
- film: make an intentionally rough animatic before polishing character rendering

The common goal is to discover bad structure while changes are still cheap.

## Working lesson: build only as much production system as the work needs

Do not turn every media request into a framework project.

Build enough reusable structure to keep the current work editable, testable, and finishable. Generalize further when reuse is itself useful, not merely because more abstraction is possible.

A complete first artistic version can be a legitimate stopping point. Verify the actual end-to-end result, fix problems that defeat the intended experience, and do not keep expanding the production merely because additional polish or features are possible.

## Working lesson: assets should remain editable

Prefer modular assets during production:

- one dialogue WAV per line when useful
- manifests with IDs/durations
- structured shot lists for larger films
- source ledgers for factual podcasts
- recurring voice mappings
- series/podcast continuity files

Avoid flattening everything into one master file too early.

## Working lesson: sound is not the final garnish

Sound has repeatedly been one of the strongest parts of this workflow.

Use it when useful to establish:

- space
- distance
- pressure
- transitions
- attention
- deadlines / approaching events
- off-screen action
- emotional changes that dialogue does not state

`audio_room/generate.py`, `last_tram/render_animatic.py`, and `jensen_podcast/generate_episode1.py` are useful examples.

Silence can also be an active production choice rather than an absence that must automatically be filled.

## Working lesson: a media task ends with a usable surface

If Moira asked GPT to **make** something, source files alone are generally not the finish line.

Depending on the project, verify the existence of:

- playable MP3/WAV
- MP4
- browser film
- GitHub Pages player
- audition/comparison page

Check that the player points to the current output and that generated-output workflows do not recursively trigger themselves.

## Working lesson: use chat history as creative history, repo as production memory

Conversation history contains useful reactions and preferences, but the durable production state should live in files whenever possible.

For recurring projects, write down:

- casting
- style rules
- continuity
- source provenance
- shot structure
- approved behaviors
- failure lessons

A fresh GPT should not need the original conversation to reconstruct the pipeline.

## What is *not* currently documented here

Do not invent a handoff guide merely because the medium exists.

As of this routing document, there is no dedicated GPT handoff in `docs/` for:

- music/Strudel production
- manual drawing/painting/vector-art production
- document/transcript repair

Those may have prior experiments elsewhere, but they are not part of this media handoff set yet.

If one of those becomes a recurring production workflow, first inspect the actual prior work and then create a grounded guide rather than writing a generic one from memory.

## Current handoff set

```text
docs/
  MEDIA_PRODUCTION_START_HERE_FOR_GPT.md
  KOKORO_VOICE_PRODUCTION_FOR_GPT.md
  PODCAST_PRODUCTION_FOR_GPT.md
  MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md
```

For most new media requests, begin here, classify new work versus continuation, route to the narrow guide, then inspect only the project state that is relevant to that mode.
