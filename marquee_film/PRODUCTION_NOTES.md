# The Last Name on the Marquee — Direction & Continuity

First animated cut: `marquee_film/index.html` (192 seconds, 17 camera setups). Created 16 November 2026.

## What this film is

A short adaptation of the beginning of the original story written in the ChatGPT conversation. This is **not** a remake of Rook and not an episode of The House of Almost.

Theatre magician Esther Vale, 58, discovers that the closing week's marquee now displays her estranged daughter Rowan's name instead of her own. She enters her failing theatre to confront Rowan. We see that the younger woman is not a visitor awaiting her mother's approval: she is already doing exacting practical work, directing technicians on stage. Their sharp, partly funny reunion turns painful at the very end, when Rowan answers why she left: “Because you nearly killed me.”

We deliberately stop on the accusation. Its explanation belongs to the next sequence, not a voiceover or explanatory title.

## Dramatic intentions

- **Esther**: brilliant, vain, caustically funny, frightened of becoming irrelevant, and genuinely capable of love. Her cigarette, posture, and ability to convert injury into performance are acting tools; avoid making her simply a villain.
- **Rowan**: talented, precise, controlled, and independently successful. She is not waiting for Esther to notice her. The way she directs the rope and refuses unsafe equipment establishes skill before their confrontation.
- **Delivery boy**: ordinary humanity and straight-man humor. He recognizes Esther without treating the celebrity signage as a grand tragedy.
- **The theatre**: a *real*, decaying workplace with a closing deadline, not a supernatural sentient character. Worn fabric, faulty electrics, and old machinery should have ordinary physical consequences.

## Cinematography decisions

1. **Distance first**: establish the elegant but shabby theatre. The street looks large, Esther small.
2. **Sign reveal**: creep closer to the enormous ROWAN VALE letters. Hold long enough to read, then cut to Esther's reaction.
3. **A face before a word**: cigarette, narrowed eyes, a deliberate pause before “Well.”
4. **Conversational comedy**: steady two-shots and slightly abrupt reverse cuts let Esther and the delivery boy play against one another; do not over-cut every line.
5. **Walking is a decision**: Esther discards the cigarette and crosses the street. The camera travels, but does not slavishly lock to her movement.
6. **Cold to warm**: transition from bluish exterior to amber-brown theatrical dust, fabric, backstage labor, and old machines. Sound should change with the location.
7. **Rowan's entrance**: introduce her already giving a technician precise instructions. Do not present her as a passive reveal waiting for Esther.
8. **The gap**: their first stage conversation should show space between them and the work Rowan has set up.
9. **The final cut**: after Rowan begins to answer, cut to Esther's close-up **while Rowan is still speaking**. The listener's reaction is the shot that ends the sequence. Fade only after the line has begun to land.

## Current assets

- `index.html` — self-contained Canvas 2D animation, 17-shot scripted camera timeline, facial changes, 2D backgrounds, letterbox, accessible controls, soundscape and dialogue captions.
- `generate_dialogue.py` — extracts the same timecoded caption list from `index.html` and renders Kokoro dialogue into one synchronized stereo MP3, preserving time for shot timing and effects.
- `audio/dialogue.mp3` — generated voice track (when available).
- `audio/manifest.json` — cue durations and speaker voice assignments.
- `qa_frames.py` — Playwright browser frame captures and contact sheet generator.
- `.github/workflows/marquee-dialogue.yml` — voice render workflow.
- `.github/workflows/marquee-qa.yml` — visual QA workflow.
- `.github/workflows/blender-pages.yml` — existing multi-project GitHub Pages publishing workflow now includes the movie and any rendered audio.

## Where to go next

Review the complete playback, particularly readable faces on mobile, voice timing and continuity. Improve acting and camera beats before painterly detail. If the final line works, the next cinematic scene should follow the existing story: Rowan's memory of the Delacourt stage accident and Esther's difficult admissions.

This rough film is a first artistic iteration, not a claim of final rendered quality. Preserve this version before major rewrites.
