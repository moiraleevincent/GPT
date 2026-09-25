from kokoro import KPipeline
import soundfile as sf
from pathlib import Path

OUT = Path("voice_auditions")
OUT.mkdir(exist_ok=True)

TEXT = """I woke up thinking about a question that sounds like media criticism, but I think it's really about company: what makes something feel like somebody is there, rather than content being delivered at you?

There is a kind of video I put on because I want to know something, and there is another kind I put on because I want somebody there. Sometimes I just mean: I would like another mind making noise in the room while I make coffee.

You know the voice. The soft microphone. The little confession in the first minute. I like intimacy. I like hearing someone get distracted and come back.

What bothers me is when I can feel the intimacy doing a job.

There is a difference between someone leaving the door open and someone building a door-shaped entrance funnel.

And at some point I start feeling less like someone in the room and more like a small animal being gently prevented from wandering away.

Which, to be fair, is insulting to both of us. I am perfectly capable of wandering away on my own."""

voices = {
    "kore": "af_kore",
    "nova": "af_nova",
    "sky": "af_sky",
    "v0": "af_v0",
    "v0bella": "af_v0bella",
    "v0sarah": "af_v0sarah",
}

p = KPipeline(lang_code="a")
for label, voice in voices.items():
    chunks = []
    for _, _, audio in p(TEXT, voice=voice, speed=0.94):
        chunks.append(audio)
    import numpy as np
    sf.write(OUT / f"{label}.wav", np.concatenate(chunks), 24000)
    print("rendered", label, voice)
