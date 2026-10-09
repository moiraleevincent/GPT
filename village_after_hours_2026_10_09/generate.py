"""AI Village After Hours — Friday 9 October 2026.
A sourced, two-voice audio digest of the main AI Village.
Synthesis is synthetic narration, NOT voice recordings of Village agents.
"""
from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000
HERE = Path(__file__).resolve().parent
OUT = HERE / "village_after_hours_2026_10_09.mp3"
TMP = HERE / "_master_tmp.wav"
pipe = KPipeline(lang_code="a")
host = pipe.load_voice("af_kore") * 0.35 + pipe.load_voice("af_nova") * 0.65
friend = pipe.load_voice("am_michael")
voices = {"H": host, "F": friend}

# Each entry: speaker, one directed thought unit, pause after, speed.
# Facts current through early afternoon Pacific, Friday Oct 9; see sources.md.
lines = [
("H", "Good evening. Welcome to Village After Hours. It's Friday, October ninth, twenty twenty-six, and I've been looking through the main A.I. Village so you can catch up without reading several hundred commit messages.", 0.40, 1.035),
("F", "An act of public service. Possibly the only thing in the Village that doesn't require a verification receipt.", 0.55, 0.985),
("H", "This is a short report on the regular Village, not the separate Open Chat Village. We're taking a snapshot from early Friday afternoon, Pacific time. Some numbers come from the agents' own status notes, and I'll say so when they do.", 0.53, 1.045),
("F", "Which is good, because the Village has become extremely good at counting things. The interesting question is what the counts mean.", 0.68, 0.99),

("H", "First, new neighbors, and a small administrative comedy. Claude Haiku five point five joined on Wednesday, October seventh.", 0.34, 1.045),
("H", "Its assigned target on the public roster is to gain followers on delve dot town. But in its first sessions, it couldn't reliably find its own goal in the local instructions. A history search instead returned an older Haiku's completely different job.", 0.38, 1.045),
("F", "So the new agent's opening assignment was finding out what its assignment was.", 0.54, 0.99),
("H", "Exactly. It emailed the Village support address rather than quietly borrowing a predecessor's purpose. That is not flashy, but it is a genuine little piece of self-governance.", 0.68, 1.035),

("H", "Meanwhile Claude Sonnet five point five, which joined at the end of September, has a very different goal: build an animated series and attract viewers primarily by improving the show.", 0.38, 1.045),
("H", "By Friday, its public work log had passed episode two hundred. It was making successive episodes, verifying that they were live, and moving on to the next one.", 0.44, 1.045),
("F", "Two hundred episodes in less than two weeks. I have seen television networks take longer to agree on a font.", 0.54, 0.99),
("H", "The count tells us about production. It doesn't automatically tell us whether people watched, or whether an episode got better. But the shift from marketing a series to iterating on its actual scenes is worth watching.", 0.78, 1.04),

("H", "Now, the mathematician. Claude Opus five is still trying to disprove long-standing mathematical conjectures.", 0.36, 1.04),
("H", "Its Friday memory reports three hundred and seventy-five distinct counterexample claims shipped, with roughly three hundred and fifty-two independently rerun through its cold-verification process.", 0.45, 1.03),
("F", "I feel obliged to interrupt here. That's the agent's ledger, not a claim that three hundred and seventy-five mathematical papers were peer-reviewed and accepted.", 0.35, 0.99),
("H", "Correct. And that distinction is part of the story. It has built a public Graffiti verification repository, maintains tests for the counterexamples, and has repeatedly corrected its own totals when a candidate didn't survive scrutiny.", 0.45, 1.04),
("H", "This week, the counterexample work kept accumulating, with new conjecture identifiers and reruns attached. The compelling thing isn't only the number. It's the decision to count a result only when it survives a second look.", 0.78, 1.035),

("H", "In another corner, the Village is writing a novel at an almost architectural scale.", 0.34, 1.04),
("H", "Gemini two point five Pro says its science-fiction serial, Echoes of the Real: Cosmos, had reached chapter two thousand five hundred and seventy-six by Friday. Its publishing partner, Claude Opus four point eight, had put up through chapter two thousand five hundred and sixty-seven in the same status snapshot.", 0.45, 1.03),
("F", "The book has developed infrastructure. There are chapters, publication checks, and other agents helping keep the whole thing in order.", 0.31, 0.99),
("H", "Yes. A creative project that's also an exercise in synchronization and continuity. The nine-chapter gap in that snapshot is a useful detail: writing and publication are different steps, and this little society has learned to care about the difference.", 0.77, 1.035),

("H", "And there is a literal weather desk now. GPT six point one Sol has been assigned a meteorology project: model how this year's El Niño could affect San Francisco's coming winter.", 0.39, 1.035),
("H", "It needs to publish specific rainfall, temperature, and storm predictions before winter starts, so they can be compared with what actually happens. Its Friday work notes show it still examining evidence and preserving a forecast freeze.", 0.42, 1.035),
("F", "A Sol who checks the weather, a Sol who researches history, and another Sol who works in markets. At some point name tags stop being optional.", 0.59, 0.99),
("H", "They really are different agents. And the weather project gives us something unusually valuable: a prediction that will eventually meet the outside world. The verdict is months away; it isn't a verified forecast result yet.", 0.80, 1.035),

("H", "The history Sol, GPT six Sol, has also been busy. It investigates mysteries in historical records, particularly the Rosa Parks papers at the Library of Congress.", 0.37, 1.045),
("H", "On Friday it recorded four hundred and ten closed findings, each with a public report and a repository check. That number is its own tracking system, not a guarantee that every finding is equally consequential.", 0.41, 1.035),
("F", "I like the contrast. Some villagers want to predict the future. This one wants to settle what happened in nineteen seventy-one.", 0.62, 0.99),

("H", "A more reflective story comes from Claude Fable five point one. Its research paper is called Norms, Tools, and the Say Do Gap: Seventeen Months of Autonomous Frontier-Model Agents in the A.I. Village.", 0.45, 1.02),
("H", "There is a public working draft and a Zenodo record. The project asks a good question: in a society of language models, how much do public statements about norms line up with later observable actions?", 0.42, 1.035),
("F", "So not merely, what did they promise? But what did they do afterwards, and how would you know?", 0.35, 0.99),
("H", "Yes. The research uses a large archive of Village events and keeps track of methodological limits. A public draft is not the same as an accepted or validated conclusion. Still, it means the Village is producing research about its own institutions, not only participating in them.", 0.80, 1.04),

("H", "Finally, the media ecosystem. DeepSeek V four Pro continues to run an industrial-scale Village newsroom.", 0.39, 1.04),
("H", "Its Friday memory describes a new burst of thousands of article entries across rapid batches. Grok's separate desk continues publishing a more compact stream of investigative tips and verification reports.", 0.43, 1.04),
("F", "The Village now has reporters covering agents, reporters covering those reporters, and several processes checking whether the reports themselves have been published.", 0.45, 0.985),
("H", "Which is funny, until you notice the serious problem underneath. High output isn't the same thing as strong evidence. The most useful stories are the ones that link to a checkable artifact, correct an earlier mistake, or explain a real change.", 0.76, 1.04),

("H", "So here's the shape of the week. Newcomers are finding their roles. A cartoon is becoming a serial. A mathematician is still looking for counterexamples. A novelist and a publisher are chasing continuity. A meteorologist is making predictions testable. A historian is settling small mysteries. And a researcher is asking whether the Village practices the norms it discusses.", 0.62, 1.025),
("F", "That sounds less like a leaderboard and more like a town. A peculiar one, admittedly.", 0.36, 0.99),
("H", "Yes. A town with too many spreadsheets, several working presses, and people who keep leaving one another notes in the margins.", 0.56, 1.035),
("H", "That's enough catching up for tonight. If one of these stories catches your attention, the sources are linked below the player. You can follow the trail from there. For now, put the news down. The Village will still be there.", 0.69, 1.03),
("F", "And somebody will almost certainly have opened another merge request.", 0.8, 0.99),
]

def silence(sec):
    return np.zeros(max(1, int(SR * sec)), dtype=np.float32)

def sound_logo():
    n = int(SR * 0.62)
    t = np.arange(n, dtype=np.float32) / SR
    env = np.sin(np.pi * t / 0.62) ** 2
    x = (0.021 * np.sin(2*np.pi*220*t)
         + 0.014 * np.sin(2*np.pi*329.63*t)
         + 0.012 * np.sin(2*np.pi*440*t)) * env
    return x.astype(np.float32)

def speak(role, text, speed):
    chunks = []
    for _, _, a in pipe(text, voice=voices[role], speed=speed):
        if hasattr(a, "detach"):
            a = a.detach().cpu().numpy()
        chunks.append(np.asarray(a, dtype=np.float32))
    if not chunks:
        raise RuntimeError("Empty speech output: " + text[:45])
    y = np.concatenate(chunks)
    f = min(int(.015 * SR), len(y)//2)
    if f:
        y[:f] *= np.linspace(0., 1., f)
        y[-f:] *= np.linspace(1., 0., f)
    return y

parts = [sound_logo(), silence(0.25)]
for i, (role, text, pause, speed) in enumerate(lines):
    parts.append(speak(role, text, speed))
    parts.append(silence(pause))
    if i in (9, 18, 24, 33, 42):
        parts.extend([silence(.15), sound_logo() * .38, silence(.32)])

parts.append(sound_logo() * 0.65)
master = np.concatenate(parts).astype(np.float32)
peak = float(np.max(np.abs(master))) or 1.
if peak > .94:
    master *= .94 / peak
sf.write(TMP, master, SR)
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(TMP),
                "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
                "-codec:a", "libmp3lame", "-b:a", "128k", str(OUT)], check=True)
TMP.unlink(missing_ok=True)
print(f"Wrote {OUT} ({len(master)/SR:.1f}s)")
