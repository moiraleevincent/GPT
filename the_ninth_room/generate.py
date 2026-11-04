#!/usr/bin/env python3
"""Render Kokoro performances and an original synthesized stereo score for The Ninth Room."""
from pathlib import Path
import json
import math
import subprocess

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)
SR = 24_000
SHOTS = json.loads((ROOT / "script.json").read_text(encoding="utf-8"))
pipe = KPipeline(lang_code="a")
voices = {}

def perform(item):
    name = item["voice"]
    if name not in voices:
        voices[name] = pipe.load_voice(name)
    pieces = []
    for _, _, samples in pipe(item["text"], voice=voices[name], speed=item.get("speed", 1)):
        if samples is None:
            continue
        if hasattr(samples, "detach"):
            samples = samples.detach().cpu().numpy()
        pieces.append(np.asarray(samples, dtype=np.float32))
    if not pieces:
        raise RuntimeError("Kokoro returned no audio for: " + item["text"])
    a = np.concatenate(pieces)
    ramp_n = min(int(SR * .030), len(a)//4)
    if ramp_n:
        ramp = np.linspace(0, 1, ramp_n, dtype=np.float32)
        a[:ramp_n] *= ramp
        a[-ramp_n:] *= ramp[::-1]
    return a

# Dialogue and timing are separate, editable artifacts.
timeline = []
lines = []
cursor = 0.0
for ix, s in enumerate(SHOTS):
    entry = {k:v for k,v in s.items() if k not in ("voice", "speed")}
    if "text" in s:
        wav = perform(s)
        line_id = f"line_{ix:02d}"
        sf.write(AUDIO / f"{line_id}.wav", wav, SR)
        speech_duration = len(wav) / SR
        entry["audio"] = f"audio/{line_id}.wav"
        entry["speech_at"] = round(cursor + 0.85, 3)
        entry["speech_duration"] = round(speech_duration, 3)
        duration = max(s["duration"], speech_duration + 2.10)
        lines.append({
            "id": line_id, "speaker": s["speaker"], "text": s["text"],
            "voice": s["voice"], "speed": s.get("speed", 1),
            "file": f"audio/{line_id}.wav", "duration": round(speech_duration, 3),
            "start": entry["speech_at"]
        })
        print(f"{line_id}: {s['speaker']} {speech_duration:.2f}s")
    else:
        duration = s["duration"]
    entry["start"] = round(cursor, 3)
    cursor += duration
    entry["end"] = round(cursor, 3)
    timeline.append(entry)

total = round(cursor, 3)
(ROOT/"timeline.json").write_text(json.dumps({"duration":total,"shots":timeline}, indent=2)+"\n")
(ROOT/"manifest.json").write_text(json.dumps(lines, indent=2)+"\n")
n = math.ceil((total + .5) * SR)
master = np.zeros((n, 2), dtype=np.float32)
rng = np.random.default_rng(2178)

def put(sound, at, pan=0.0, gain=1.0):
    k = int(at*SR)
    if k < 0:
        sound = sound[-k:]
        k = 0
    m = min(len(sound), n-k)
    if m <= 0:
        return
    z = np.asarray(sound[:m], dtype=np.float32)*gain
    # Slightly separated stereo without eliminating either channel.
    master[k:k+m,0] += z * (0.82 - .23*pan)
    master[k:k+m,1] += z * (0.82 + .23*pan)

def pluck(at, freq, amp=.033, sec=2.2, bright=1.0, pan=0):
    count = int(sec*SR)
    t = np.arange(count,dtype=np.float32)/SR
    attack = np.minimum(1, t/.007)
    env = attack*np.exp(-t*3.5)
    bell = (np.sin(2*np.pi*freq*t)
          + .23*np.sin(2*np.pi*freq*2.008*t)
          + .09*bright*np.sin(2*np.pi*freq*3.99*t))
    put(bell*env*amp, at, pan)

def knock(at, amp=.16, pan=0):
    sec=.29
    t=np.arange(int(sec*SR),dtype=np.float32)/SR
    env=np.exp(-t*27)
    noise=rng.standard_normal(len(t)).astype(np.float32)
    thud=np.sin(2*np.pi*(105-40*t)*t)*.65 + noise*.15
    put(env*thud*amp,at,pan)

def clock_tick(at, amp=.02):
    t=np.arange(int(.10*SR),dtype=np.float32)/SR
    z=np.sin(2*np.pi*1900*t)*np.exp(-t*65)*amp
    put(z,at,pan=.1)

# Very quiet ventilator, tape hiss, low detuned harmonic beating.
t = np.arange(n,dtype=np.float32)/SR
fade_in = np.minimum(1,t/3)
fade_out=np.minimum(1,np.maximum(0,(total-t)/2.5))
room = (.0020*rng.standard_normal(n).astype(np.float32)
      + .0034*np.sin(2*np.pi*54.7*t)
      + .0025*np.sin(2*np.pi*55.3*t))
intensity = 1 + 1.6*np.clip((t-total*.61)/(total*.33),0,1)
master[:,0] += room*fade_in*fade_out*intensity
master[:,1] += (room*.92 + .0012*np.sin(2*np.pi*56.1*t))*fade_in*fade_out*intensity

# Original sparse toy-piano figure: deliberately pleasant notes in an uncomfortable order.
notes=[392.0, 493.88, 466.16, 329.63]
for ix,s in enumerate(timeline):
    a=s["start"]
    if s["scene"] not in ("title","end"):
        pluck(a + .24, notes[ix%4],amp=.022 if ix<9 else .015,pan=(-1)**ix*.35)
        if ix in (1,5,8,10,14,16):
            pluck(a+2.00, notes[(ix+1)%4]/2, amp=.013,sec=3.0,bright=.3)
    if s["scene"] in ("keys","ledger","ledger_final"):
        pluck(a+3.4, 784 if ix<10 else 659.25, amp=.008,sec=1.3)
    if s["scene"]=="corridor":
        knock(a+4.6,.10,pan=-.8)
        knock(a+5.15,.09,pan=.75)
    if s["scene"]=="door":
        knock(a+4.4,.13,pan=0)
        knock(a+4.93,.15,pan=0)
        knock(a+5.86,.12,pan=0)
    if s["scene"]=="room":
        knock(a+1.4,.06,pan=.6)
    if s["scene"]=="mirror":
        pluck(a+2.0, 164.81,amp=.04,sec=5.0,bright=.15)
    if s["scene"]=="ledger_final":
        pluck(a+1.0, 880,amp=.025,sec=4.0)
        pluck(a+1.04, 830.61,amp=.016,sec=4.0)
    if s["scene"]=="facade_final":
        pluck(a+1.0,392,amp=.017,sec=4)
    if s["scene"]=="end":
        pluck(a+.2, 261.63,amp=.03,sec=5,bright=.1)

for seconds in np.arange(6,total-8,2.0):
    clock_tick(float(seconds),.012 if seconds<total*.6 else .02)

# Place original Kokoro lines according to the locked timeline.
for line in lines:
    samples,sr = sf.read(ROOT/line["file"],dtype="float32")
    if sr!=SR:
        raise RuntimeError("Unexpected sample rate")
    pos={"FELIX":-.45,"VALE":.45,"NARRATOR":0}.get(line["speaker"],0)
    put(samples,line["start"],pos,gain=.78)
    # Tiny early reflections, distinct from dry speech.
    put(samples,line["start"]+.075,-pos,gain=.052)
    put(samples,line["start"]+.138,pos,gain=.028)

# Deliberate tails and safe peak.
master=np.tanh(master*1.18)
peak=float(np.max(np.abs(master))) or 1.0
if peak>.94: master *= .94/peak
tmp=ROOT/"soundtrack.wav"
sf.write(tmp,master,SR,subtype="PCM_16")
subprocess.run([
    "ffmpeg","-y","-hide_banner","-loglevel","error",
    "-i",str(tmp),"-af","loudnorm=I=-17:LRA=10:TP=-1.5",
    "-codec:a","libmp3lame","-b:a","160k",
    str(ROOT/"soundtrack.mp3")],check=True)
tmp.unlink()
print(f"Finished The Ninth Room: {total:.1f}s, {len(lines)} Kokoro lines.")
