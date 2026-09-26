# Podcast Production — GPT Handoff Guide

## Purpose

This document is for **GPT**, not Moira. Its job is to let a fresh GPT instance produce podcasts in the existing GitHub/Kokoro workflow without rediscovering the creative format, legal/trial style, source discipline, serial structure, or publishing process.

Read this together with:

- `docs/KOKORO_VOICE_PRODUCTION_FOR_GPT.md`
- `docs/MOVIES_AND_SERIES_IN_GITHUB_FOR_GPT.md` when using audio-drama or scene-style techniques

The podcast workflow is not only TTS. The production problem is:

**research / source control → episode scope → narrative structure → host format → transcript/clip selection → legal/context explanation → performance → sound design → mix/master → publication → series continuity**

## Primary repository and known working example

Repository:

- `moiraleevincent/GPT`

Main current podcast example:

- `jensen_podcast/generate_episode1.py`
- `.github/workflows/jensen-podcast.yml`
- `jensen_podcast/episode1_openings_are_not_evidence.mp3`
- `jensen_podcast/index.html`

The Jensen player identifies the format as **one host plus dramatized courtroom transcript readings using Kokoro voices**. The page also explicitly tells listeners that the courtroom voices are synthetic dramatizations based on the transcript and are not original courtroom audio.

Earlier experiments include the two-host **After Midnight** format and the single-host long-form Kokoro essay/podcast.

## The most important style correction from the Jensen test

The first Jensen episode proved that the pipeline can produce a full listenable legal/trial podcast. However, Moira's later reaction identified a significant presentation problem:

**The episode became too lecture-like and too judgmental in the way the host framed the listener.**

Avoid a host voice that sounds like:

- "Here is the correct way to watch a trial."
- "Notice what has happened."
- "This is the question you should be asking."
- "If you watch trials for the law rather than just the story..."
- repeated meta-instructions about how sophisticated viewers understand evidence

Even if the legal analysis itself is correct, this posture can make the program feel like the host is grading the listener.

### Better LawTube / LegalEagle-style principle

Prefer:

**story → concrete event/testimony → legal question naturally appears → concise explanation → immediate return to the people/evidence/consequences**

The legal concept should feel like the tool the listener suddenly needs because something happened in the story.

Example shape:

```text
A witness starts repeating what somebody else said.
↓
The listener now has a reason to ask: can the jury hear that?
↓
Explain hearsay / exception / confrontation only as far as needed.
↓
Return to this witness, this statement, this judge, this trial.
```

Do not build the story merely as an excuse to deliver a law lecture.

## LawTube reference in Google Drive

Moira has Google Docs such as:

- `Eagle Lindsay`
- `Eagle Lindsay 2`

These are reference examples for a more legal-analysis-focused narrative style.

One useful structural feature in `Eagle Lindsay 2` is the repeated pattern:

- establish the concrete human/event timeline
- insert a trial clip/testimony excerpt
- explain why that testimony matters
- introduce the legal/medical question only when it becomes necessary
- return to testimony and competing interpretations

For example, the document first walks through Patrick Clancy's testimony and only later moves into postpartum-depression vs postpartum-psychosis concepts and the Massachusetts criminal-responsibility standard. The law grows out of the evidentiary conflict rather than arriving as an abstract preamble.

Use these documents as **style references**, not rigid templates.

## Episode scope: do not compress a trial into one giant summary

For trial podcasts, Moira explicitly prefers serial treatment when there is enough material.

The Jensen request was:

- make this **Episode 1** of a series
- start with **Day One**
- do not try to compress the whole case into one episode

This should be the default instinct for large trials.

A useful episode boundary can be:

- one trial day
- one witness cluster
- one major evidentiary fight
- one major phase of the case
- one unresolved question that produces a natural next-episode handoff

Do not cram later trial developments into an early episode merely because they are known.

## Trial chronology and spoiler discipline

When building a sequential trial series:

- preserve the chronology of the trial unless the episode clearly signals a brief background flashback
- keep witnesses and testimony associated with the correct day
- do not casually preview later testimony/results when the episode is meant to recreate the experience of Day One
- distinguish what the lawyers **promised in opening** from what later became evidence
- distinguish what the host knows retrospectively from what the jury/listener has reached at that point

This is especially important because Moira likes uncertainty and evidence accumulation rather than flattened hindsight summaries.

## Research workflow for a trial episode

Before scripting, identify the source set.

Preferred hierarchy:

1. **trial transcript / courtroom record**
2. court orders, jury instructions, rulings, exhibits, appellate opinions
3. contemporaneous reporting for inaccessible moments or context
4. reliable secondary legal explanation
5. general background sources for scientific/medical/legal context

Do not let a secondary summary silently replace the transcript when the transcript is available.

### Google Drive workflow

Moira often keeps trial transcripts/openings/reference scripts in Google Docs.

For a new episode:

1. search Drive for the named trial/day/witness/opening
2. ground the exact document/version
3. read enough contiguous material to understand context
4. identify the episode's source boundaries
5. extract only the clips/quotes needed for the planned narrative

If multiple transcript versions exist, do not silently merge them.

## Source ledger

For serious factual podcasts, maintain a lightweight source ledger during production.

Recommended structure:

```python
SOURCES = {
    "opening_state": "Google Doc / transcript reference",
    "opening_defense": "Google Doc / transcript reference",
    "jury_instruction": "transcript page / court instruction",
    "background_appeal": "case/opinion/source",
}
```

or a separate `sources.md` / `sources.json`.

The purpose is to let future GPT instances answer:

- where did this fact come from?
- is this direct testimony or host synthesis?
- is this advocacy from a lawyer?
- is this a judicial ruling?
- is this external background research?

For a series, source provenance is part of continuity.

## Separate categories of truth inside the script

Trial podcasts must keep these distinct:

### 1. Evidence / testimony

Something the jury actually heard or an admitted exhibit.

### 2. Opening/closing advocacy

A lawyer's promise, interpretation, or argument.

### 3. Judicial instruction/ruling

What the judge told the jury or decided on admissibility/procedure.

### 4. Host explanation

The podcast's legal/contextual explanation.

### 5. External background

Appeal history, scientific context, prior trial history, reporting, etc.

Do not narrate advocacy as established fact merely because it sounds concrete.

## Dramatized transcript clips

Moira likes the possibility of making transcript material feel more like an **audio drama** by assigning different Kokoro voices to speakers.

This is a strong format and is already proven in the Jensen episode.

### Required listener clarity

When synthetic voices perform real transcript material, tell the listener clearly that these are dramatized readings, not original recordings.

The existing Jensen copy is a good pattern:

> courtroom voices are synthetic dramatizations based on the transcript, not original courtroom audio

### Clip discipline

For transcript dramatization:

- preserve speaker identity
- preserve meaning
- do not invent exchanges that are presented as transcript
- if shortening an exchange, do not splice it so the meaning changes
- keep objections/rulings when they are the reason the exchange matters
- do not use a theatrical voice performance to imply certainty or motive not contained in the words

The drama should come from the actual exchange, timing, casting, and sound environment.

## Quote vs paraphrase

Use direct dramatized transcript excerpts when the exact wording matters:

- a judge's instruction
- a key admission
- a disputed phrasing
- an objection/ruling exchange
- a cross-examination contradiction
- a line whose wording becomes legally important

Paraphrase when exact wording adds little and would slow the episode.

Do not turn the episode into a transcript read-through. The host still needs to select and shape.

## Single host vs two hosts

Both formats have working precedent.

### Single host

Best when:

- the narrative needs control and coherence
- research is dense
- legal analysis needs careful phrasing
- the episode follows one trial day
- dramatized courtroom voices already provide variety

The Jensen episode used this format.

### Two hosts

Best when:

- the concept benefits from banter
- one host can challenge or clarify the other
- the topic is exploratory, funny, strange, or conversational
- the show benefits from differing reactions or roles

The earlier **After Midnight** experiment used:

- `af_nicole` as Mara
- `am_michael` as Julian

with alternating short turns and approximately 0.28 seconds of silence between turns.

The strength of that experiment was conversational rhythm and tiny interruptions/jokes, not factual depth.

### Do not add a co-host merely to create variety

If the second host has no distinct function, use one host and spend the complexity on stronger structure, clips, and sound.

## Host personality

A synthetic host becomes more believable when the writing has **selection and edges**.

The successful long-form Kokoro podcast experiment emphasized:

- point of view
- specificity
- small preferences
- digressions
- natural pauses
- not treating listener retention as the organizing principle

A host should sound like someone thinking about something, not a neutral explainer optimizing every sentence.

For serious legal content, this does **not** mean becoming partisan or overconfident. It means having a recognizable human-scale curiosity and sense of what is interesting.

## Avoid fake intimacy and fake spontaneity

Do not add filler such as:

- "Okay, wow."
- "This is crazy."
- fake stumbles every few lines
- performative asides that exist only to simulate podcast informality

Naturalism should come from actual structure:

- variation in sentence length
- a host following an interesting detail
- a brief correction when genuinely useful
- silence
- understated reactions
- specificity

## Legal explanation length

Explain only enough law to unlock the scene.

A useful test:

**If removing two paragraphs of doctrine would leave the listener able to understand the courtroom consequence, remove them.**

Deeper legal explanation is worthwhile when:

- the ruling changes what evidence can be heard
- the distinction is central to the case
- a lawyer's strategy cannot be understood without it
- the legal rule creates a genuine surprise
- the same rule will recur throughout the series

If a doctrine will recur, teach the minimum reusable concept once, then rely on the listener's memory later.

## Use clips to reset abstraction

After an explanatory passage, return to a voice, scene, exhibit, or concrete fact.

Good rhythm:

```text
story
clip
explanation
clip
story
```

Potentially tiring rhythm:

```text
story
5 minutes of abstract doctrine
more abstract doctrine
host meta-commentary
story finally resumes
```

Audio has fewer visual anchors than video, so concrete voices and scenes matter even more.

## Trial-host stance

The host can analyze strategy, inconsistency, evidentiary significance, or weakness, but should avoid adopting the posture of a judge of the people involved unless that is actually the show's purpose.

Prefer phrasing such as:

- "The prosecution is using this to argue..."
- "The defense's problem here is..."
- "This matters because the judge has to decide..."
- "If the jury credits this testimony..."

over omniscient moralizing or treating one contested interpretation as the narrator's fact.

## Episode architecture

A flexible legal/trial episode structure:

### Cold open

Use a short moment that contains the episode's central tension.

Possibilities:

- judge instruction
- disputed testimony
- objection
- surprising cross-examination line
- two incompatible descriptions of the same event

Do not make the cold open a generic true-crime teaser if the episode's real value is legal/evidentiary.

### Title / premise

Tell the listener what slice of the case they are entering.

For a serial trial podcast, episode naming should reflect the day's real problem rather than sensationalizing the crime.

The existing Jensen episode is:

`Episode 1: Openings Are Not Evidence`

### Minimal background

Give only the case history necessary to understand the day's proceedings.

If the trial is a retrial, explain why only if it changes what the jury can hear or why the current proceeding is unusual.

### Main chronology

Walk through the day's events in order unless a different structure has a clear payoff.

### Legal questions as they arise

Explain evidence law/procedure where the actual events create the need.

### End on a real hinge

Good endings include:

- judge reserves a ruling overnight
- next witness is about to create a new evidentiary problem
- one side has made a promise not yet fulfilled
- testimony ends on a contradiction that will matter tomorrow

Do not manufacture a cliffhanger unrelated to the record.

## Episode title strategy

Prefer titles that identify the legal/narrative tension:

- `Openings Are Not Evidence`
- a disputed rule/phrase
- an evidentiary object
- a witness problem
- a question the day actually raises

Avoid generic titles such as `The Shocking Truth About...` unless the show itself intentionally uses that style.

## Serial continuity

For a recurring podcast, create and maintain:

```text
podcast_name/
  PODCAST_BIBLE.md
  sources.md
  continuity.json
  episode_01/
  episode_02/
```

### `PODCAST_BIBLE.md`

Store:

- show premise
- host format
- host voice(s)
- tone
- recurring intro/outro rules
- legal-analysis depth
- music/SFX policy
- what the show deliberately avoids

### `continuity.json`

For trial series, useful fields include:

- current trial day reached
- witnesses already covered
- evidence introduced so far
- objections/rulings already explained
- promises made in openings that remain unresolved
- recurring legal doctrines already taught
- unresolved factual conflicts
- source documents used

This prevents Episode 4 from accidentally re-explaining a doctrine as though it is new or spoiling testimony the series has not reached.

## Working Jensen casting

Current Episode 1 mapping:

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

Speeds are separately controlled per role.

Do not treat this as permanent canonical casting for every future episode if better voice continuity or new speakers require adjustment. However, preserve established recurring voices for recurring people unless there is a reason to recast.

## Turn-list architecture

The existing Jensen generator stores the entire episode as ordered turns:

```python
TURNS = [
    ("SFX", "COLD OPEN — quiet courtroom room tone. No music yet."),
    ("JUDGE", "..."),
    ("HOST", "..."),
    ...
]
```

This is a strong architecture because script and production timeline stay aligned.

For longer series work, consider externalizing the script into JSON/YAML/Markdown so the generator is not also the editorial master copy.

Example:

```json
{
  "role": "HOST",
  "text": "...",
  "source": "day1_opening_state",
  "type": "narration"
}
```

or:

```json
{
  "role": "JUDGE",
  "text": "...",
  "source": "day1_transcript_p12",
  "type": "dramatized_transcript"
}
```

That source metadata becomes increasingly useful across episodes.

## Sound language

The Jensen episode established a restrained sound vocabulary:

- quiet courtroom room tone beneath dramatized courtroom speakers
- dry host voice
- short tonal title sting
- short transition sting
- subtle late-day room change
- restrained outro

This is effective because it creates scene identity without turning the podcast into melodrama.

### Courtroom vs host acoustics

The existing pattern gives courtroom speakers a tiny amount of room sound while the host is dry. That tells the ear when the show has entered the dramatized record.

Preserve that distinction.

### Music policy

Do not put music continuously under serious testimony merely because podcasts often use beds.

Use music/stings for structure where helpful:

- opening
- section transition
- end

Let testimony and important silence remain exposed.

## Sound effects and generated ambience

The current repo can synthesize useful sound design directly with NumPy:

- room tone
- hum
- tonal stings
- simple impacts
- filtered noise
- spatial treatment

See:

- `audio_room/generate.py`
- `jensen_podcast/generate_episode1.py`

Avoid unnecessary stock-audio dependencies when a restrained generated texture is enough.

## Pacing

Podcast pacing should not be uniform.

Use:

- shorter pauses in ordinary host exposition
- slightly longer pauses around transcript clips
- real breathing room after emotionally or legally consequential lines
- section transitions only where the listener benefits from a reset

The Jensen generator currently uses shorter pre/post gaps for the host and slightly larger ones for courtroom roles.

The successful long-form host experiment also used deliberately hand-set pauses rather than trusting TTS paragraph rhythm.

## Duration

Do not optimize to an arbitrary episode length.

A prior Kokoro podcast worked well as a **real lunch-length episode**; Moira listened through while making lunch and regarded the result as effectively successful.

The target is enough time to develop the material without flattening it.

For trial series, an episode can be shorter if the day's natural unit is short. Do not pad.

## Script before render, but render early enough to test the writing

Do not wait until the script is editorially "perfect" before hearing any of it.

Synthetic audio exposes problems that are invisible on the page:

- sentence too long
- too many nested clauses
- repeated sentence rhythm
- lecture-like stretches
- clip/narration imbalance
- unnatural transitions
- insufficient silence

Useful workflow:

1. research and outline
2. script one representative section
3. render a few minutes
4. listen for format/style problems
5. revise the show's grammar if needed
6. finish script
7. render full episode

This is especially important after the Jensen Episode 1 lesson.

## Listener orientation

A podcast must periodically re-anchor the listener, especially in trials with many names.

Use natural reorientation:

- "Back in the courtroom..."
- "The witness here is..."
- "This is still the State's opening..."
- "The jury has not heard evidence of that yet..."

Do not overuse names/titles in every sentence.

## Names and roles

When a person first appears, identify them clearly.

Later, use the shortest unambiguous name/role.

A spoken podcast becomes cumbersome if every mention is "Deputy District Attorney Carli McNeill" rather than "McNeill" after introduction.

## Scientific / medical background

When a case requires technical background such as toxicology or psychiatry:

- teach only what is needed for the testimony
- connect the concept to a specific disputed fact
- distinguish general science from what a particular expert said in this case
- avoid letting background research silently decide a contested trial issue

For Jensen, ethylene glycol physiology matters because the competing theories depend on timing, symptoms, toxicology, and causation. Explain those concepts when they become evidentiary tools.

## Appeals / retrial background

If a current trial exists because of prior appellate litigation, explain the history only to the depth necessary for the listener to understand the current evidentiary landscape.

The Jensen Episode 1 draft spent time on the Confrontation Clause because the retrial excluded important prior material. That background is relevant.

However, do not front-load appellate doctrine for its own sake. If the effect can first be shown concretely — "the new jury will not hear X" — start there, then explain why.

## Commentary tone for tragedy

Do not use jaunty true-crime language around deaths merely to create energy.

The host can be curious, sharp, funny about legal procedure, lawyers, odd evidentiary details, or absurdities where appropriate, while remaining aware when the underlying subject is severe.

The show does not need to become solemn at all times. It needs control over **what** it treats lightly.

## Publishing / final delivery

Known working chain:

1. Python builds master audio at 24 kHz.
2. Write temporary WAV.
3. FFmpeg normalizes and encodes MP3.
4. GitHub Action removes the temporary WAV.
5. Action commits final MP3 with `[skip ci]`.
6. `index.html` provides browser playback.

Existing FFmpeg target:

```bash
-af "loudnorm=I=-16:LRA=9:TP=-1.5"
-codec:a libmp3lame -b:a 128k
```

Read `docs/KOKORO_VOICE_PRODUCTION_FOR_GPT.md` for the full technical pattern.

## Publish a listening surface, not merely a file

When Moira asks GPT to make a podcast, finishing `generate.py` is not enough.

Verify:

- render completed
- MP3 exists
- browser player points to current MP3
- page loads from the intended GitHub Pages path
- labeling accurately describes synthetic/dramatized material

Moira prefers practical listenable output rather than download friction or technical instructions.

## Quality-control listen

Before calling an episode finished, review at minimum:

- opening 2–3 minutes
- first transition from host to dramatized clip
- longest uninterrupted host explanation
- at least one dense legal/scientific section
- ending / next-episode transition

If possible, listen/read through the full timeline.

Ask:

- Does the host sound like a lecturer grading the audience?
- Did the law arise from the story or interrupt it?
- Are clips doing work, or are they decorative?
- Does the listener know what is evidence vs advocacy?
- Are names easy to follow in audio?
- Did we explain the same doctrine twice?
- Is there enough silence after consequential moments?
- Does the episode end where the day's real tension ends?

## Failure modes

### 1. Lecture voice

The biggest known creative failure.

Legal sophistication should not become a hierarchy between host and listener.

### 2. Law before story

Do not open with several minutes of doctrine when one concrete courtroom moment could create the question naturally.

### 3. Flattening the trial into hindsight

Preserve the difference between what was alleged, what was admitted, what was disputed, and what had not yet happened.

### 4. Over-compressing a series

If Day One can sustain an episode, let Day One be an episode.

### 5. Transcript cosplay

Synthetic dramatization should not pretend to be authentic courtroom audio.

### 6. Clip overload

Do not dramatize every exchange. Select lines whose wording, conflict, or rhythm benefits from being heard.

### 7. Host monopoly

If the host speaks abstractly for too long, insert concrete testimony/story rather than merely adding music.

### 8. Fake banter

A co-host should have a real role. Do not alternate voices just to make the waveform look varied.

### 9. Sensational sound design

Restraint usually serves courtroom material better than ominous drones and constant stings.

### 10. Losing source provenance

A future GPT must be able to tell whether a line came from transcript, court ruling, reporting, or host synthesis.

## Recommended build order for a new trial episode

1. Ground the exact trial/day/source documents.
2. Identify the natural episode boundary.
3. Write a chronology of what actually happens that day.
4. Mark legal questions where they arise from the chronology.
5. Identify exact transcript moments worth dramatizing.
6. Decide single-host vs two-host based on function, not novelty.
7. Draft cold open and first 3–5 minutes.
8. Render that sample and listen for lecture-tone problems.
9. Finish script.
10. Cast new courtroom roles while preserving recurring voice continuity.
11. Render role audio.
12. Build restrained ambience/transitions.
13. Mix/master.
14. Publish MP3/player.
15. Update series continuity/source ledger.

## General principle

The strongest podcast format for Moira is not "law lecture with clips" and not "true crime recap with legal trivia."

Aim for:

**a compelling human story in which the law keeps becoming necessary.**

When a witness speaks, an objection lands, a judge hesitates, an expert reframes a fact, or a lawyer makes a promise, follow that pressure. Explain the rule because the listener now wants to know what happens next.

Then get back to the room.
