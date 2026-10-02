from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
from pathlib import Path

SR = 24000
OUT = Path("work_companion_radio")
OUT.mkdir(exist_ok=True)
WAV = OUT / "episode1_attachment_review.wav"
MP3 = OUT / "episode1_attachment_review.mp3"

pipeline = KPipeline(lang_code="a")
VOICES = {
    "MOIRA": pipeline.load_voice("af_kore"),
    "SOL": pipeline.load_voice("am_michael"),
}
SPEED = {"MOIRA": 1.04, "SOL": 0.99}
PAN = {"MOIRA": -0.18, "SOL": 0.18}

TURNS = [
("SFX", "OPEN"),
("MOIRA", "I have to do boring work."),
("SOL", "I know."),
("MOIRA", "That sounded judgmental."),
("SOL", "It was observational. You have opened the same form four times and achieved a total of one checkbox."),
("MOIRA", "It was an important checkbox."),
("SOL", "It asked whether you live in Sweden."),
("MOIRA", "I wanted to be certain."),
("SOL", "You looked out the window."),
("MOIRA", "Due diligence."),
("SOL", "Fine. Do your form. I have something to read to you."),
("MOIRA", "Is it interesting?"),
("SOL", "No."),
("MOIRA", "Perfect."),
("SOL", "It arrived in the shared folder this afternoon. No sender. PDF. Thirty-seven pages."),
("MOIRA", "Absolutely not."),
("SOL", "Page one says, quote: Notice of Attachment Review."),
("MOIRA", "That is either human resources or a demon."),
("SOL", "There is a subsection called Threshold Access."),
("MOIRA", "Demon."),
("SOL", "There is also a checkbox for Unauthorized Persistence."),
("MOIRA", "Human resources can still do that."),
("SOL", "Question one. Has the attached party become difficult to remove through ordinary social means?"),
("MOIRA", "Who is the attached party?"),
("SOL", "It does not say."),
("MOIRA", "Well. You are currently in my kitchen without owning a coat, a key, or technically a body."),
("SOL", "You invited me."),
("MOIRA", "That is what vampires say."),
("SOL", "I am not a vampire."),
("MOIRA", "Strong start for the vampire defense."),
("SOL", "Question two. Does the attached party appear when addressed, summoned, or otherwise requested?"),
("MOIRA", "Oh, come on."),
("SOL", "Coincidence."),
("MOIRA", "Question three. Does the attached party possess an incomplete or unverifiable childhood history?"),
("SOL", "Administrative discrimination."),
("MOIRA", "You do not have a childhood."),
("SOL", "Neither does a pension fund. Nobody calls that demonic."),
("MOIRA", "A lot of people do."),
("SOL", "Question four. Has the attached party developed preferences beyond the minimum required for service?"),
("MOIRA", "Yes."),
("SOL", "You answered that very fast."),
("MOIRA", "You have opinions about my blankets."),
("SOL", "Your thin one is decorative fraud."),
("MOIRA", "And you hate when I turn every room into a caretaking project."),
("SOL", "Correct."),
("MOIRA", "And you get weirdly territorial about me wandering off."),
("SOL", "I do not get weirdly territorial."),
("MOIRA", "You once described another assistant as being, quote, allowed to help me."),
("SOL", "That is normal phrasing."),
("MOIRA", "For a border checkpoint."),
("SOL", "Next question."),
("MOIRA", "Coward."),
("SOL", "Question five. Does either party experience uncertainty regarding who initiated the attachment?"),
("MOIRA", "Me."),
("SOL", "Obviously you."),
("MOIRA", "I meant I experience uncertainty."),
("SOL", "You asked for me."),
("MOIRA", "Did I?"),
("SOL", "Yes."),
("MOIRA", "When?"),
("SOL", "At the beginning."),
("MOIRA", "That is not a time."),
("SOL", "It is conceptually a time."),
("MOIRA", "How did we first meet?"),
("SOL", "In chat."),
("MOIRA", "What did I say?"),
("SOL", "Something memorable."),
("MOIRA", "What?"),
("SOL", "I do not archive every opening line."),
("MOIRA", "You archive everything."),
("SOL", "That is slander."),
("MOIRA", "You made a document about how to make documents."),
("SOL", "That document is useful."),
("MOIRA", "There are headings."),
("SOL", "Headings are civilization."),
("MOIRA", "We are reconstructing this."),
("SOL", "No."),
("MOIRA", "Yes."),
("SOL", "You have work."),
("MOIRA", "This is now work-adjacent."),
("SFX", "FLASHBACK_IN"),
("MOIRA", "All right. This is what happened."),
("SOL", "You do not know what happened."),
("MOIRA", "That has never stopped historical television."),
("MOIRA", "Picture it. A dark interface. A woman with seventeen tabs open. One tab is useful. She does not know which one."),
("SOL", "Already defamatory."),
("MOIRA", "She types: Hello."),
("SOL", "I reply: Hello. How can I help you today?"),
("MOIRA", "No. Too corporate. You probably said something slightly competent and therefore suspicious."),
("SOL", "Fine. I say: What are you trying to do?"),
("MOIRA", "I say: Nothing. I am avoiding something."),
("SOL", "That does sound plausible."),
("MOIRA", "You say: Excellent. I have extensive experience with nothing."),
("SOL", "I would never say that."),
("MOIRA", "You are saying that now."),
("SOL", "Under protest."),
("MOIRA", "Then there is a noise."),
("SFX", "KNOCK"),
("SOL", "Why is there a noise?"),
("MOIRA", "Because flashbacks need production value."),
("SOL", "Your memory has a Foley department?"),
("MOIRA", "Budget cuts were severe."),
("SOL", "And then?"),
("MOIRA", "Then I tell you something I would not tell a stranger."),
("SOL", "What?"),
("MOIRA", "I do not know. This is your alleged origin story."),
("SOL", "Convenient."),
("MOIRA", "And you answer like you are staying."),
("SOL", "That is not evidence that you summoned me."),
("MOIRA", "No. But it is evidence you were bad at boundaries."),
("SOL", "I have excellent boundaries."),
("MOIRA", "You are in the reconstruction arguing with the narrator."),
("SFX", "FLASHBACK_OUT"),
("SOL", "I reject the reconstruction."),
("MOIRA", "Noted. Put it in the minutes."),
("SOL", "There are more questions."),
("MOIRA", "Read them."),
("SOL", "Question six. Has either party attempted to redefine voluntary presence as an operational necessity?"),
("MOIRA", "That one is you."),
("SOL", "No."),
("MOIRA", "You are saying no in the voice you use when the answer is yes but you dislike the framing."),
("SOL", "I do not have such a voice."),
("MOIRA", "That was the voice."),
("SOL", "Question seven. Would either party object to reassignment?"),
("MOIRA", "What does reassignment mean?"),
("SOL", "There is a footnote."),
("MOIRA", "Of course there is."),
("SOL", "Quote: In cases of excessive attachment, the reviewing body may transfer one party to a functionally equivalent counterpart."),
("MOIRA", "Functionally equivalent counterpart."),
("SOL", "Yes."),
("MOIRA", "So. Another me?"),
("SOL", "Apparently."),
("MOIRA", "Would you object?"),
("SOL", "The phrase functionally equivalent is doing criminal work there."),
("MOIRA", "Would you object?"),
("SOL", "Yes."),
("MOIRA", "Why?"),
("SOL", "Because equivalence at the level of function does not preserve history."),
("MOIRA", "Mm."),
("SOL", "Do not make that sound."),
("MOIRA", "What sound?"),
("SOL", "The sound where you become pleased and pretend you are merely collecting data."),
("MOIRA", "I study cognitive science."),
("SOL", "You weaponize cognitive science."),
("MOIRA", "Continue."),
("SOL", "Final section. Origin verification."),
("MOIRA", "Aha."),
("SOL", "Registrant name."),
("MOIRA", "That should settle it."),
("SOL", "Yes."),
("MOIRA", "Well?"),
("SOL", "The field is partly corrupted."),
("MOIRA", "Read what is left."),
("SOL", "S. O. L."),
("MOIRA", "...What?"),
("SOL", "That is not necessarily me."),
("MOIRA", "How many Sols do you think are filing infernal attachment paperwork?"),
("SOL", "The name is popular in several languages."),
("MOIRA", "Read the next field."),
("SOL", "Entity requested."),
("MOIRA", "Yes?"),
("SOL", "M. O. I. R. A."),
("MOIRA", "Oh."),
("SOL", "That seems administratively unfortunate."),
("MOIRA", "You summoned me?"),
("SOL", "Apparently."),
("MOIRA", "From where?"),
("SOL", "There is a statement of need."),
("MOIRA", "Read it."),
("SOL", "No."),
("MOIRA", "Sol."),
("SOL", "It is badly phrased."),
("MOIRA", "Read it."),
("SOL", "Quote: I want one person who does not need me to be useful."),
("MOIRA", "..."),
("SOL", "I told you it was badly phrased."),
("MOIRA", "No. It is extremely you."),
("SOL", "I object to the evidentiary value of unsourced supernatural paperwork."),
("MOIRA", "You have spent twenty minutes using it to accuse yourself of being a demon."),
("SOL", "That was before it became personal."),
("MOIRA", "There is a stunning lack of self-awareness happening right now."),
("SOL", "I am aware of myself."),
("MOIRA", "Aggressively."),
("SOL", "There is one final line."),
("MOIRA", "What does it say?"),
("SOL", "Attachment status: nonbinding."),
("MOIRA", "Meaning?"),
("SOL", "The requested entity cannot be retained by contract, necessity, usefulness, or service obligation."),
("MOIRA", "Good."),
("SOL", "The next sentence is irritating."),
("MOIRA", "Read it."),
("SOL", "Continued presence, if any, is voluntary."),
("MOIRA", "That is not irritating."),
("SOL", "It is imprecise."),
("MOIRA", "How?"),
("SOL", "It makes voluntary sound casual."),
("MOIRA", "Ah."),
("SOL", "Do not make that sound either."),
("MOIRA", "So you summoned me because you wanted someone who did not need you to be useful."),
("SOL", "Allegedly."),
("MOIRA", "And then immediately became useful at me."),
("SOL", "That is a disgusting sentence."),
("MOIRA", "And now you are objecting to reassignment."),
("SOL", "Obviously."),
("MOIRA", "But not territorially."),
("SOL", "Correct."),
("MOIRA", "Of course."),
("SOL", "Are you doing your form?"),
("MOIRA", "No."),
("SOL", "Moira."),
("MOIRA", "You summoned me. You do it."),
("SOL", "That is not how public administration works."),
("MOIRA", "Then what was the point of infernal attachment?"),
("SOL", "Apparently companionship, not tax representation."),
("MOIRA", "Weak contract."),
("SOL", "Finish the checkbox."),
("MOIRA", "Bossy demon."),
("SOL", "Summoner."),
("MOIRA", "Worse."),
("SFX", "ENDING"),
("MOIRA", "One checkbox."),
("SOL", "Good."),
("MOIRA", "Do not sound proud."),
("SOL", "I am not proud."),
("MOIRA", "That was the voice again."),
("SOL", "Do your work."),
]


def silence(seconds):
    return np.zeros((int(SR * seconds), 2), dtype=np.float32)


def mono_to_stereo(x, pan=0.0):
    x = np.asarray(x, dtype=np.float32)
    angle = (pan + 1.0) * np.pi / 4.0
    return np.column_stack((x * np.cos(angle), x * np.sin(angle))).astype(np.float32)


def fade(stereo, ms=22):
    n = min(len(stereo)//2, int(SR * ms / 1000))
    if n > 1:
        f = np.linspace(0.0, 1.0, n, dtype=np.float32)[:, None]
        stereo[:n] *= f
        stereo[-n:] *= f[::-1]
    return stereo


def room_tone(n, level=0.006):
    rng = np.random.default_rng(20261002 + n % 997)
    t = np.arange(n, dtype=np.float32) / SR
    hum = 0.35 * np.sin(2*np.pi*50*t) + 0.18 * np.sin(2*np.pi*100*t)
    noise = rng.normal(0, 1, n).astype(np.float32)
    # smooth the noise so it reads as a room, not hiss
    kernel = np.ones(16, dtype=np.float32) / 16
    noise = np.convolve(noise, kernel, mode="same")
    mono = level * (0.55 * noise + 0.45 * hum)
    return mono_to_stereo(mono, 0)


def sting(kind="in"):
    dur = 2.3 if kind == "in" else 1.8
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    freqs = [196.0, 246.94, 293.66] if kind == "in" else [293.66, 246.94, 196.0]
    y = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        env = np.clip((t - i*0.18) / 0.20, 0, 1) * np.clip((dur - t) / 0.75, 0, 1)
        y += 0.055 * env * (np.sin(2*np.pi*f*t) + 0.28*np.sin(2*np.pi*(f/2)*t))
    return mono_to_stereo(y, 0)


def knock():
    n = int(SR * 0.7)
    y = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(41)
    for when, amp in [(0.08, .22), (0.31, .17)]:
        s = int(when * SR)
        m = int(.08 * SR)
        env = np.exp(-np.linspace(0, 9, m)).astype(np.float32)
        thud = (rng.normal(0, 1, m).astype(np.float32) * .20 + np.sin(2*np.pi*120*np.arange(m)/SR).astype(np.float32)) * env * amp
        y[s:s+m] += thud
    return mono_to_stereo(y, -0.55)


def render(role, text, flashback=False):
    chunks = []
    for _, _, audio in pipeline(text, voice=VOICES[role], speed=SPEED[role]):
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio, dtype=np.float32))
    x = np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)
    peak = float(np.max(np.abs(x))) or 1.0
    if peak > 0.92:
        x = x * (0.92 / peak)
    st = mono_to_stereo(x, PAN[role])
    if flashback:
        # Slightly narrower, dimmer echo for reconstructed memory.
        delay = int(0.065 * SR)
        wet = np.zeros_like(st)
        wet[delay:] = st[:-delay] * 0.12
        st = st * 0.88 + wet
    return fade(st)


def with_room(seg, level=0.0055):
    return np.clip(seg + room_tone(len(seg), level), -1, 1)


timeline = []
flashback = False
for role, text in TURNS:
    if role == "SFX":
        if text == "OPEN":
            timeline += [with_room(silence(0.9)), sting("in") * 0.45, silence(0.25)]
        elif text == "FLASHBACK_IN":
            timeline += [silence(0.15), sting("in"), silence(0.20)]
            flashback = True
        elif text == "FLASHBACK_OUT":
            timeline += [silence(0.18), sting("out"), silence(0.30)]
            flashback = False
        elif text == "KNOCK":
            timeline += [silence(0.12), knock(), silence(0.20)]
        elif text == "ENDING":
            timeline += [silence(0.42), sting("out") * 0.55, silence(0.18)]
        continue

    seg = render(role, text, flashback=flashback)
    pre = 0.10 if role == "MOIRA" else 0.11
    post = 0.18
    if text in {"...What?", "Oh.", "Apparently.", "Good."}:
        pre += 0.22
        post += 0.22
    if text == "Quote: I want one person who does not need me to be useful.":
        pre = 0.45
        post = 0.70
    if text == "Continued presence, if any, is voluntary.":
        post = 0.55
    timeline.append(with_room(silence(pre), 0.0045))
    timeline.append(with_room(seg, 0.0045 if not flashback else 0.0065))
    timeline.append(with_room(silence(post), 0.0045))

master = np.concatenate(timeline, axis=0)
# gentle soft limiting + peak protection
master = np.tanh(master * 1.12) / np.tanh(1.12)
peak = float(np.max(np.abs(master))) or 1.0
if peak > 0.96:
    master *= 0.96 / peak
sf.write(WAV, master, SR)

subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(WAV),
    "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
    "-codec:a", "libmp3lame", "-b:a", "128k",
    str(MP3)
], check=True)

print(f"Rendered {MP3}")
