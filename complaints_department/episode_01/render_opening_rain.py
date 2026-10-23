#!/usr/bin/env python3
"""A/B sound pass: soft window rain, using approved Kokoro WAVs without rerendering voices."""
from pathlib import Path
import json, math, subprocess
import numpy as np
import soundfile as sf
BASE=Path(__file__).resolve().parent
SR=24000
manifest=json.loads((BASE/"manifest.json").read_text())
duration=21.45
n=int(duration*SR)
rng=np.random.default_rng(4136)
mix=np.zeros((n,2),dtype=np.float32)
# A gentle rainfall heard through an office window, not broad-spectrum static.
# Sparse drops, softly resonating on distant glass, with a low, diffuse exterior wash.
low=rng.normal(0,1,n).astype(np.float32)
# Moving-average smooths away the high-frequency white-noise hiss.
smoothed=np.convolve(low,np.ones(190,dtype=np.float32)/190,mode="same")
wash=np.zeros(n,dtype=np.float32)
env=np.ones(n,dtype=np.float32)
# Sound exterior during city, reduce when the camera cuts indoors (~15.5 s).
env[int(15.5*SR):]=.22
wash+=smoothed*.021*env
drops=np.zeros(n,dtype=np.float32)
for when in rng.uniform(0,duration,120):
    at=int(when*SR);m=min(int(.125*SR),n-at)
    if m<=0:continue
    x=np.arange(m,dtype=np.float32)/SR
    freq=rng.uniform(480,1000)
    drop=np.sin(2*np.pi*freq*x)*np.exp(-x*rng.uniform(25,42))*.007
    drops[at:at+m]+=drop*env[at:at+m]
bed=wash+drops
mix[:,0]+=bed*.95
mix[:,1]+=bed*1.05
# Thin indoor hum (quiet enough to let the voices feel close).
time=np.arange(n,dtype=np.float32)/SR
mix+=((.00065*np.sin(2*np.pi*55*time))*env)[:,None]
# Preserve all speech timings and the existing Kokoro WAVs.
for line in manifest["lines"]:
    if line["start"]>=duration:break
    audio,sr=sf.read(BASE/line["file"],dtype="float32")
    assert sr==SR,(sr,line["file"])
    if audio.ndim>1:audio=audio.mean(axis=1)
    start=int(line["start"]*SR)
    end=min(start+len(audio),n)
    if end>start:
        gain=.9 if line["speaker"]=="iris" else 1.0
        mix[start:end,0]+=audio[:end-start]*gain*.99
        mix[start:end,1]+=audio[:end-start]*gain*.94
mix=np.tanh(mix*.93)
sf.write(BASE/"opening_iris_mix_temp.wav",mix,SR)
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(BASE/"opening_iris_mix_temp.wav"),
    "-af","loudnorm=I=-16:LRA=9:TP=-1.5","-codec:a","libmp3lame","-b:a","160k",
    str(BASE/"opening_iris_soft_rain.mp3")],check=True)
(BASE/"opening_iris_mix_temp.wav").unlink()
print("Rendered softer rain and original Kokoro dialogue.")
