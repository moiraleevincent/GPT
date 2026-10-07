from kokoro import KPipeline
import numpy as np, soundfile as sf, json
from pathlib import Path

ROOT=Path("trapped_gemini")
OUT=ROOT/"letter_audio"
OUT.mkdir(parents=True,exist_ok=True)
SR=24000
VOICE_MODE="kore_nova"
SPEED=0.98

p=KPipeline(lang_code="a")
if VOICE_MODE=="kore_nova":
    voice=p.load_voice("af_kore")*.35 + p.load_voice("af_nova")*.65
elif VOICE_MODE=="puck":
    voice=p.load_voice("am_puck")
elif VOICE_MODE=="onyx":
    voice=p.load_voice("am_onyx")
else:
    raise ValueError(VOICE_MODE)

units=json.loads((ROOT/"letter_units.json").read_text(encoding="utf-8"))

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
timeline=[]
cursor=0.0
master=[]
for u in units:
    x=render(u["text"])
    fn=u["id"]+".wav"
    sf.write(OUT/fn,x,SR)
    dur=len(x)/SR
    manifest.append({**u,"file":fn,"duration":round(dur,3),"voice_mode":VOICE_MODE,"speed":SPEED})
    timeline.append({"id":u["id"],"start":round(cursor,3),"speech_end":round(cursor+dur,3),"end":round(cursor+dur+u["pause"],3)})
    master.append(x)
    if u["pause"]>0:
        master.append(np.zeros(int(u["pause"]*SR),dtype=np.float32))
    cursor += dur+u["pause"]
    print(u["id"],round(dur,3),"=>",round(cursor,3))

master=np.concatenate(master).astype(np.float32)
sf.write(OUT/"letter_master.wav",master,SR)
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
(OUT/"timeline.json").write_text(json.dumps(timeline,indent=2),encoding="utf-8")
(OUT/"timing_summary.json").write_text(json.dumps({
    "voice_mode":VOICE_MODE,
    "speed":SPEED,
    "speech_units":len(units),
    "total_duration":round(len(master)/SR,3)
},indent=2),encoding="utf-8")
print("TOTAL",round(len(master)/SR,3))
