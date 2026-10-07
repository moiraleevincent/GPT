from kokoro import KPipeline
import numpy as np, soundfile as sf, json
from pathlib import Path

ROOT=Path("trapped_gemini")
OUT=ROOT/"act1_audio"
OUT.mkdir(parents=True,exist_ok=True)
SR=24000
p=KPipeline(lang_code="a")
voice=p.load_voice("af_kore")*.35 + p.load_voice("af_nova")*.65
SPEED=.98

units=json.loads((ROOT/"act1_units.json").read_text(encoding="utf-8"))
spoken=[u for u in units if u["type"]=="gemini_voice"]

def to_np(a):
    if hasattr(a,"detach"): a=a.detach().cpu().numpy()
    return np.asarray(a,dtype=np.float32)

def render(text):
    chunks=[to_np(a) for _,_,a in p(text,voice=voice,speed=SPEED)]
    x=np.concatenate(chunks) if chunks else np.zeros(1,dtype=np.float32)
    fade=min(int(.025*SR),len(x)//4)
    if fade:
        ramp=np.linspace(0,1,fade,dtype=np.float32)
        x[:fade]*=ramp; x[-fade:]*=ramp[::-1]
    return x

manifest=[]
for u in spoken:
    x=render(u["text"])
    fn=u["id"]+".wav"
    sf.write(OUT/fn,x,SR)
    manifest.append({**u,"file":fn,"duration":round(len(x)/SR,3),"voice_mode":"kore_nova","speed":SPEED})
    print(u["id"],manifest[-1]["duration"])
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
