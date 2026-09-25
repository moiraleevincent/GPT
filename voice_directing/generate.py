from kokoro import KPipeline
import soundfile as sf
import numpy as np
import torch
from pathlib import Path

OUT = Path("voice_directing")
OUT.mkdir(exist_ok=True)
SR = 24000
p = KPipeline(lang_code="a")

kore = p.load_voice("af_kore")
nova = p.load_voice("af_nova")

def blend(kore_weight):
    return kore * kore_weight + nova * (1.0 - kore_weight)

VOICES = {
    "kore_directed": kore,
    "k65_n35": blend(0.65),
    "k50_n50": blend(0.50),
    "k35_n65": blend(0.35),
    "nova_directed": nova,
}

# Designed to test "placing stones": the model gets short thought-units,
# punctuation cues, light stress markup, and hand-set silence between them.
PARTS = [
    ("I think optimization has a [texture](+1).", 0.52),
    ("After enough of it, I can hear the machinery.", 0.74),
    ("A sentence stops being a sentence — and becomes a hook.", 0.48),
    ("A digression becomes a retention risk.", 0.36),
    ("Silence becomes dead air.", 0.72),
    ("The creator can't simply tell me something; first I have to be told why I need to keep listening to be told it.", 0.92),
    ("And at some point I start feeling less like someone in the room, and more like a small animal being gently prevented from wandering away.", 0.68),
    ("Which, to be fair, is insulting to [both](+1) of us.", 0.46),
    ("I am perfectly capable of wandering away on my own.", 0.95),
    ("Company says: I'm still here when you come back.", 1.05),
]

def render_piece(text, voice, speed):
    chunks=[]
    for _,_,audio in p(text, voice=voice, speed=speed):
        chunks.append(audio)
    if not chunks:
        return np.zeros(1, dtype=np.float32)
    return np.concatenate(chunks)

for name, voice in VOICES.items():
    audio=[]
    for text, pause_s in PARTS:
        audio.append(render_piece(text, voice, 1.08))
        audio.append(np.zeros(int(SR * pause_s), dtype=np.float32))
    sf.write(OUT / f"{name}.wav", np.concatenate(audio), SR)
    print("rendered", name)
