"""Mrs Wicker — phone-scene audio. Each spoken line is directed and timed independently."""
from pathlib import Path
import json
import math
import subprocess
import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).parent
SR = 24000
DURATION = 46.0
lines = [
  ("n01", "NARRATOR", "This is Mrs. Wicker.", 1.15, 0.98),
  ("w01", "WICKER", "They're lilies.", 4.15, 0.91),
  ("b01", "BERNARD", "Yes, Mrs. Wicker.", 6.10, 0.99),
  ("w02", "WICKER", "I hate lilies.", 7.94, 0.91),
  ("b02", "BERNARD", "I'm terribly sorry.", 10.02, 0.98),
  ("w03", "WICKER", "They smell like cat piss.", 12.05, 0.94),
  ("b03", "BERNARD", "Yes, Mrs. Wicker.", 14.88, 0.98),
  ("n02", "NARRATOR", "Mrs. Wicker was not pleased with the arrangements for her funeral.", 17.01, 0.99),
  ("w04", "WICKER", "And another thing. I'm not dead.", 22.55, 0.95),
  ("n03", "NARRATOR", "Nor, for that matter, with being dead.", 26.42, 0.97),
  ("b04", "BERNARD", "I'm afraid you are, Mrs. Wicker.", 30.05, 0.95),
  ("w05", "WICKER", "Well. That's a bloody inconvenience.", 38.02, 0.93),
]
voices = {"NARRATOR":"bm_george", "WICKER":"bf_emma", "BERNARD":"bm_daniel"}
pipeline = KPipeline(lang_code="b")
voice_tensors = {k:pipeline.load_voice(v) for k,v in voices.items()}

n = int(DURATION*SR)
mix = np.zeros((n,2), dtype=np.float64)
manifest = []
for lid, role, spoken, start, speed in lines:
    chunks=[]
    for _, _, audio in pipeline(spoken, voice=voice_tensors[role], speed=speed):
        if hasattr(audio, "detach"): audio = audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio,dtype=np.float64).reshape(-1))
    if not chunks: raise RuntimeError(f"empty voice output: {lid}")
    a=np.concatenate(chunks)
    fade=min(int(.022*SR),len(a)//5)
    if fade:
        a[:fade] *= np.linspace(0,1,fade)
        a[-fade:] *= np.linspace(1,0,fade)
    sf.write(ROOT / (lid + ".wav"),a,SR)
    manifest.append({"id":lid,"role":role,"text":spoken,"start":start,"duration":round(len(a)/SR,3),"wav":lid+".wav"})
    pos=int(start*SR)
    end=min(n,pos+len(a))
    if end > pos:
        pan = {"NARRATOR":0, "WICKER":-0.19, "BERNARD":0.24}[role]
        amp = {"NARRATOR":0.93, "WICKER":0.95, "BERNARD":0.91}[role]
        seg=a[:end-pos]*amp
        mix[pos:end,0] += seg * math.sqrt((1-pan)/2)
        mix[pos:end,1] += seg * math.sqrt((1+pan)/2)
    print(lid,round(len(a)/SR,2),"sec at",start)

# An original, restrained, faintly mischievous chamber-music sketch.
# Plucked strings and a slightly nasal reed; no borrowed melody or recording.
rng=np.random.default_rng(37)
def instrument(freq,dur,kind):
    tt=np.arange(int(dur*SR))/SR
    if kind=="pluck":
        env=np.exp(-5.8*tt/dur)*(1-np.exp(-tt*280))
        sig=np.sin(2*np.pi*freq*tt)+.33*np.sin(2*np.pi*2*freq*tt)+.14*np.sin(2*np.pi*3*freq*tt)
    else:
        env=(1-np.exp(-tt*36))*np.minimum(1,np.maximum(0,(dur-tt)*8))
        vibrato=.003*np.sin(2*np.pi*5.4*tt)
        sig=np.sin(2*np.pi*freq*tt*(1+vibrato))+.40*np.sin(2*np.pi*3*freq*tt)+.15*np.sin(2*np.pi*5*freq*tt)
    return sig*env
def note(freq,start,dur,kind,gain,pan=0):
    if start<0 or start>=DURATION:return
    a=instrument(freq,dur,kind)*gain
    i=int(start*SR); e=min(n,i+len(a))
    mix[i:e,0]+=a[:e-i]*math.sqrt((1-pan)/2)
    mix[i:e,1]+=a[:e-i]*math.sqrt((1+pan)/2)
beat=60/104
chords=[(174.61,220,261.63),(146.83,196,246.94),(164.81,207.65,261.63),(130.81,174.61,220)]
for bar in range(24):
    st=bar*3*beat
    if st>=DURATION-2:break
    chord=chords[bar%4]
    for k in range(3):
        note(chord[k]*2,st+k*beat,.36,"pluck",.010,k*.28-.28)
        note(chord[0]/2,st+k*beat,.42,"pluck",.009,-.26)
    if bar%2==0: note(chord[2]*2,st+beat*.15,1.15,"reed",.008,.26)
# very quiet room tone + occasional clock tick
tone=rng.standard_normal(n)
tone=np.convolve(tone,np.ones(22)/22,"same")*.00065
mix[:,0]+=tone;mix[:,1]+=tone*.75
for when in np.arange(.5,DURATION,1.0):
    k=int(when*SR); length=int(.013*SR)
    burst=np.exp(-np.linspace(0,7,length))*rng.normal(size=length)*.012
    mix[k:k+length,0]+=burst;mix[k:k+length,1]+=burst*.82
# receiver click at 42 seconds
for when in (41.55,41.68):
    k=int(when*SR); length=int(.045*SR)
    burst=np.exp(-np.linspace(0,8,length))*rng.normal(size=length)*.095
    mix[k:k+length,0]+=burst;mix[k:k+length,1]+=burst*.8
# soft fades and peak protection
x=np.arange(n)/SR
mix*=np.minimum(1,x/.5)[:,None]
mix*=np.minimum(1,np.maximum(0,(DURATION-x)/1.6))[:,None]
mix=np.tanh(mix*.96)
peak=float(np.max(np.abs(mix))) or 1
if peak>.94:mix*=.94/peak
sf.write(ROOT/"mix.wav",mix.astype("float32"),SR)
(ROOT/"manifest.json").write_text(json.dumps({"duration":DURATION,"lines":manifest},indent=2))
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(ROOT/"mix.wav"),"-af","loudnorm=I=-16:LRA=9:TP=-1.5","-c:a","libmp3lame","-b:a","160k",str(ROOT/"scene.mp3")],check=True)
print("Audio rendered:",ROOT/"scene.mp3")
