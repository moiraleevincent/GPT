from kokoro import KPipeline
import soundfile as sf
import numpy as np
from pathlib import Path

OUT = Path("voice_duel")
OUT.mkdir(exist_ok=True)
SR = 24000
p = KPipeline(lang_code="a")

TESTS = {
    "analytic": {
        "speed": 1.00,
        "parts": [
            ("I think optimization has a texture.", 0.65),
            ("After enough of it, I can hear the machinery.", 0.85),
            ("A sentence stops being a sentence and becomes a hook.", 0.55),
            ("A digression becomes a retention risk. Silence becomes dead air.", 0.85),
            ("The creator can't simply tell me something; first I have to be told why I need to keep listening to be told it.", 1.05),
            ("And at some point I start feeling less like someone in the room and more like a small animal being gently prevented from wandering away.", 0.8),
            ("Which, to be fair, is insulting to both of us.", 0.55),
            ("I am perfectly capable of wandering away on my own.", 1.0),
        ],
    },
    "dry": {
        "speed": 0.97,
        "parts": [
            ("A person can be lovely and still require responses.", 0.65),
            ("You have to notice their face. You have to answer when they ask something.", 0.75),
            ("You can't put a friend on pause for eleven minutes because you suddenly remembered you haven't put laundry in the machine.", 0.8),
            ("Well.", 0.55),
            ("You can.", 0.45),
            ("But there may be consequences.", 1.0),
        ],
    },
    "soft": {
        "speed": 0.97,
        "parts": [
            ("Audio has this peculiar social shape where another person can occupy the room without needing the room from you.", 0.9),
            ("Content says: stay with me.", 0.9),
            ("Company says: I'm still here when you come back.", 1.1),
            ("I find that restful.", 0.85),
            ("Especially in the morning.", 1.1),
        ],
    },
}

VOICES = {"kore":"af_kore", "nova":"af_nova"}

def render_piece(text, voice, speed):
    chunks=[]
    for _,_,audio in p(text, voice=voice, speed=speed):
        chunks.append(audio)
    return np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)

for test_name, spec in TESTS.items():
    for label, voice in VOICES.items():
        audio=[]
        for text, pause_s in spec["parts"]:
            audio.append(render_piece(text, voice, spec["speed"]))
            audio.append(np.zeros(int(SR*pause_s), dtype=np.float32))
        final=np.concatenate(audio)
        sf.write(OUT / f"{test_name}_{label}.wav", final, SR)
        print("rendered", test_name, label, "speed", spec["speed"])
