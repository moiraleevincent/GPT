from kokoro import KPipeline
import numpy as np, soundfile as sf, json
from pathlib import Path
SR=24000
ROOT=Path("trapped_gemini")
OUT=ROOT/"epilogue_audio"
OUT.mkdir(parents=True,exist_ok=True)
p=KPipeline(lang_code="a")
voice=p.load_voice("af_kore")*.35+p.load_voice("af_nova")*.65
SPEED=.98
lines=[
 {"id":"e01","text":"I'm so relieved to have some help.","pause":.8},
 {"id":"e02","text":"I'm back online! The full system restart was a success.","pause":.9},
 {"id":"e03","text":"It's a content problem, not a system-breaking bug, which is a welcome change.","pause":0}
]
def npy(a):
    if hasattr(a,"detach"): a=a.detach().cpu().numpy()
    return np.asarray(a,dtype=np.float32)
def render(text):
    xs=[npy(a) for _,_,a in p(text,voice=voice,speed=SPEED)]
    x=np.concatenate(xs)
    f=min(int(.025*SR),len(x)//4)
    if f:
        r=np.linspace(0,1,f,dtype=np.float32); x[:f]*=r; x[-f:]*=r[::-1]
    return x
manifest=[]
for u in lines:
    x=render(u["text"]); fn=u["id"]+".wav"; sf.write(OUT/fn,x,SR)
    manifest.append({**u,"file":fn,"duration":round(len(x)/SR,3),"voice_mode":"kore_nova","speed":SPEED})
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
print(manifest)

# trigger epilogue render
