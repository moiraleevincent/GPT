# The Complaints Department — Series Bible

## Premise
Municipal buildings can file complaints about their occupants. Most file about leaks, structural indignities, or nuisances. The unofficial Department XIII receives the ones that cannot be resolved by ordinary inspection.

Iris Vale, a municipal night investigator, discovers that the complaints are sometimes warnings. The city has a deep institutional history of treating warnings as administrative problems.

## Tone
Noir supernatural mystery with dry municipal humor, restrained dread, and a recurring question about who gets believed. A character-driven series, not just twist delivery. Every eerie event should have a clear immediate human stake. Narration, dialogue, and internal monologue are central to the storytelling.

## Episode architecture
Short episodes (1–3 minutes initially), one problem per episode, an evolving underlying case, a hook at the end. Balance procedural investigation with quietly unsettling emotional disclosures. Give secondary characters motives and places to push back against Iris.

## Main characters
**Iris Vale** — City investigator, observant and proud of her competence, dry wit. Distinguishes spoken and inner voice by rhythm and distance, not by using separate actors. Amber scarf, dark bob haircut, teal overcoat.
**Cal** — Colleague reachable by telephone. Fast, skeptical, sarcastic, but keeps answering her calls.
**House 14** — Old residence on Bell Street. Speaks through its letter slot with a dry, patient voice; uncanny because it knows Iris, not because it roars.

## Episode 1: House 14
Complaint: someone crying inside the walls of an apparently empty house. The house claims to have been waiting 47 years for Iris, says Iris herself is crying, and commands her not to look at the upstairs window. She looks. Upstairs, there is a silhouette in an illuminated window.

Established facts: buildings file forms; the department is unofficially numbered XIII; houses can communicate, or at least this one can; Iris and Cal work together; the building recognizes Iris before she understands why. Do not prematurely explain why it waited 47 years.

## Sound
Kokoro voice casting lives in `episode_01/generate.py`. Narrated and spoken Iris are the same Kore/Nova blend. Cal uses Liam; House 14 uses Onyx, restrained filtering/early reflections. Speech assets have stable IDs and manifests; new episodes should preserve these voices and identifiers.

## Visual grammar
960×540 animated vector scenes in the first browser episode, cool blue/teal shadows with aged brass/amber light. The camera lingers on the listener or on a meaningful prop. Rain accompanies the city; interior rooms should feel quieter than street scenes. The window is a recurring visual motif, not a generic horror flourish.

## Production
- `episode_01/index.html` browser-playable scene and subtitle player.
- `episode_01/generate.py` Kokoro dialogue rendering and audio mix.
- `.github/workflows/complaints-department-ep01.yml` renders and commits audio/manifest.
- The renderer must publish a playable result, not only source code.
- Keep character voice WAVs separate so timing can be adjusted independently of visuals.
