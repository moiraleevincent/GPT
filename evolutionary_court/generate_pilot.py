#!/usr/bin/env python3
"""Evolutionary Court, pilot. Original teaching dialogue inspired by Chapter 7,
The Evolutionary Psychology of Social Behaviour: Kin Relationships and Conflict,
provided by the listener (photographed pp. 170-173).
Synthetic voices portray fictional presenters, not source quotations.
"""
from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
from kokoro import KPipeline

HERE = Path(__file__).resolve().parent
SR = 24000

# Each turn is a separately directed performance, not one TTS monologue.
TURNS = [
    ("EXAMINER", "Court is now in session. The accused: natural selection. The charge: producing animals that sacrifice their own reproduction to help somebody else.", .55),
    ("COUNSEL", "That seems like the opposite of natural selection.", .35),
    ("EXAMINER", "Exactly. And today, the jury wants an explanation.", .70),
    ("MUSIC", "", .10),
    ("EXAMINER", "Welcome to The Evolutionary Court. This case comes from chapter seven: The Evolutionary Psychology of Social Behaviour, Kin Relationships and Conflict. Our question: why would an animal help a relative at a cost to itself?", .35),
    ("COUNSEL", "First, we have to fix a word. Altruism. In everyday psychology, it often implies somebody means to be selfless. In evolutionary biology, the definition is about an action's effects: the recipient benefits, while the actor pays a fitness cost.", .35),
    ("EXAMINER", "So we're not putting a mongoose on the witness stand and asking whether it had pure intentions?", .25),
    ("COUNSEL", "We could. But I doubt it would answer.", .55),
    ("EXAMINER", "Fine. Exhibit A: African wild dogs regurgitate food for other members of their pack. Exhibit B: dwarf mongooses sometimes nurse one another's offspring. Exhibit C: some worker ants don't reproduce, yet defend the colony with their lives.", .50),
    ("COUNSEL", "The chapter uses examples like these to introduce kin altruism. They're striking behaviours. But observing one doesn't prove a particular evolutionary explanation. We need a mechanism.", .42),
    ("EXAMINER", "Bring in William Hamilton.", .35),
    ("COUNSEL", "Hamilton's insight is that fitness has more than one route. Direct fitness comes from producing your own offspring. Indirect fitness comes from helping relatives reproduce, when they carry copies of genes you also carry by common descent.", .40),
    ("EXAMINER", "So an animal can lose something in its own reproductive prospects, and still increase the expected representation of shared genes in the next generation?", .25),
    ("COUNSEL", "Yes. That's the logic of inclusive fitness: direct plus indirect effects. Not a conscious calculation. It's a way of analyzing how selection can favor a behaviour.", .55),
    ("EXAMINER", "Now I want the equation. Briefly. This is a courtroom, not a three-hour statistics seminar.", .30),
    ("COUNSEL", "Hamilton's rule. R times B must exceed C. R is genetic relatedness. B is the reproductive benefit to the recipient. C is the reproductive cost to the helper. If the weighted benefit exceeds the cost, helping can be favored by selection.", .42),
    ("EXAMINER", "Make it concrete.", .25),
    ("COUNSEL", "A simplified thought experiment. Imagine helping a full sibling costs you one expected offspring, but allows your sibling four additional offspring. Relatedness between ordinary full siblings averages one half. One half times four equals two. Two exceeds one. Hamilton's inequality is satisfied.", .55),
    ("EXAMINER", "And if the help gave the sibling only one extra offspring?", .24),
    ("COUNSEL", "Half of one is less than one. Not enough, in this simplified comparison. Relatedness doesn't make every sacrifice evolutionarily advantageous.", .60),
    ("EXAMINER", "Wait. You said full siblings average one half. The book also mentions an odd twist with ants.", .30),
    ("COUNSEL", "Right. In certain haplodiploid species, including many ants, full sisters can have an average relatedness of three quarters, under particular reproductive conditions. That can change the incentives for helping sisters rather than reproducing independently. But it's not a universal explanation of eusocial insects.", .55),
    ("EXAMINER", "I have an objection. You're describing gene-level consequences. That doesn't tell us what a real individual feels, believes, or has learned.", .24),
    ("COUNSEL", "Objection sustained. Hamilton's rule is about evolutionary conditions. It does not establish the immediate psychological cause of an individual act. That's the distinction between ultimate and proximate explanation.", .48),
    ("EXAMINER", "And a family is not a harmonious gene-sharing commune, either.", .22),
    ("COUNSEL", "No. Parent and offspring share genes, but they can still have different fitness interests. The chapter turns to that conflict, too. A relative can be worth helping without everyone wanting the same outcome.", .60),
    ("EXAMINER", "The verdict, then. Helping relatives is not a contradiction of natural selection. Under the right costs, benefits, and relatedness, it can be one of the things selection favors.", .31),
    ("COUNSEL", "And none of this means every kind act is a hidden genetic bargain.", .35),
    ("EXAMINER", "Agreed. The court dismisses the charge of contradiction. The deeper question stays open: how do you tell a compelling evolutionary story from a tested explanation?", .52),
    ("COUNSEL", "That's a case worth hearing.", .60),
    ("MUSIC", "", .25),
    ("EXAMINER", "End of the pilot. Next time, we're calling the parents and their children to the witness stand. That one could get unpleasant.", .85),
]

def silence(seconds):
    return np.zeros(max(0, int(seconds * SR)), dtype=np.float32)

def smooth_audio(data):
    data = np.asarray(data, dtype=np.float32).flatten()
    # Ten millisecond fade protects each dialogue edit.
    n = min(240, len(data) // 3)
    if n:
        data[:n] *= np.linspace(0, 1, n, dtype=np.float32)
        data[-n:] *= np.linspace(1, 0, n, dtype=np.float32)
    return data

def title_sting():
    duration = 1.5
    t = np.arange(round(duration * SR), dtype=np.float32) / SR
    # Original, softly chiming courtroom theme with no external copyrighted assets.
    notes = [196.0, 247.0, 294.0]
    signal = sum(np.sin(2 * np.pi * n * t + i * .6) for i, n in enumerate(notes))
    env = np.minimum(1, t * 24) * np.exp(-2.8 * t)
    return smooth_audio((.11 * signal * env).astype(np.float32))

def render():
    pipe = KPipeline(lang_code="a")
    kore = pipe.load_voice("af_kore")
    nova = pipe.load_voice("af_nova")
    voices = {
        "EXAMINER": kore * .35 + nova * .65,
        "COUNSEL": pipe.load_voice("bm_george"),
    }
    speeds = {"EXAMINER": 1.04, "COUNSEL": 1.00}
    parts = [silence(.18)]
    for idx, (role, line, pause) in enumerate(TURNS, 1):
        print(f"{idx:02d}/{len(TURNS)} {role}: {line[:75]}", flush=True)
        if role == "MUSIC":
            parts.extend([title_sting(), silence(pause)])
            continue
        chunks = []
        for _, _, audio in pipe(line, voice=voices[role], speed=speeds[role]):
            if hasattr(audio, "detach"):
                audio = audio.detach().cpu().numpy()
            chunks.append(np.asarray(audio, dtype=np.float32))
        if not chunks:
            raise RuntimeError(f"Empty synthesis for turn {idx}: {line!r}")
        parts.extend([smooth_audio(np.concatenate(chunks)), silence(pause)])
    master = np.concatenate(parts)
    peak = float(np.max(np.abs(master)))
    if peak > .96:
        master *= .96 / peak
    wav = HERE / "pilot_kin_altruism.wav"
    mp3 = HERE / "pilot_kin_altruism.mp3"
    sf.write(wav, master, SR)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(wav), "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
        "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3)
    ], check=True)
    print("Created", mp3, "duration_s", round(len(master)/SR, 1), "bytes", mp3.stat().st_size, flush=True)
    wav.unlink()

if __name__ == "__main__":
    render()
