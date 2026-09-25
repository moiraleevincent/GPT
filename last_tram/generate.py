from kokoro import KPipeline
import numpy as np
import soundfile as sf
from pathlib import Path
import json

OUT = Path("last_tram")
OUT.mkdir(exist_ok=True)
SR = 24000

p = KPipeline(lang_code="a")
voices = {
    "A": p.load_voice("am_michael"),
    "B": p.load_voice("af_nicole"),
}

lines = [
    {"id":"b01","speaker":"B","text":"You kept it.","speed":0.96},
    {"id":"a01","speaker":"A","text":"You left it.","speed":0.95},
    {"id":"b02","speaker":"B","text":"Six months ago.","speed":0.93},
    {"id":"a02","speaker":"A","text":"I know.","speed":0.92},
    {"id":"b03","speaker":"B","text":"You asked me here to return an umbrella?","speed":0.98},
    {"id":"a03","speaker":"A","text":"No.","speed":0.88},
    {"id":"a04","speaker":"A","text":"I asked you here because I couldn't think of anything else you'd answer.","speed":0.93},
    {"id":"b04","speaker":"B","text":"You could've said you missed me.","speed":0.92},
    {"id":"a05","speaker":"A","text":"Would you have come?","speed":0.91},
    {"id":"b05","speaker":"B","text":"Probably not.","speed":0.90},
    {"id":"b06","speaker":"B","text":"But I came for the umbrella.","speed":0.94},
    {"id":"a06","speaker":"A","text":"Coward.","speed":0.90},
    {"id":"b07","speaker":"B","text":"That's yours.","speed":0.94},
    {"id":"a07","speaker":"A","text":"I know.","speed":0.88},
]

def render(text, voice, speed):
    chunks=[]
    for _,_,audio in p(text, voice=voice, speed=speed):
        chunks.append(audio)
    if not chunks:
        return np.zeros(1,dtype=np.float32)
    return np.concatenate(chunks).astype(np.float32)

manifest=[]
for item in lines:
    audio=render(item["text"], voices[item["speaker"]], item["speed"])
    # gentle fade to avoid hard waveform edges
    fade=min(int(.025*SR), len(audio)//4)
    if fade>0:
        ramp=np.linspace(0,1,fade,dtype=np.float32)
        audio[:fade]*=ramp
        audio[-fade:]*=ramp[::-1]
    path=OUT/f'{item["id"]}.wav'
    sf.write(path,audio,SR)
    manifest.append({**item,"file":path.name,"duration":round(len(audio)/SR,3)})
    print(path, manifest[-1]["duration"])

(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
