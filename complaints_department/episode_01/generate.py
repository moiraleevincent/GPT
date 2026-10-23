#!/usr/bin/env python3
"""The Complaints Department — Episode 01. Kokoro voice and final sound mix."""
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

BASE = Path(__file__).resolve().parent
VOICES = BASE / "voices"
VOICES.mkdir(parents=True, exist_ok=True)
SR = 24000

# Stable IDs let us revise performances without changing the story/shot design.
LINES = [
    ("01", "iris", "title", "My city has twelve departments. Thirteen, if you count the one that takes complaints from buildings.", .58),
    ("02", "iris", "city", "Mostly damp. Occasionally bad tenants. Once, a cathedral complained about its choir.", .62),
    ("03", "iris", "office", "My name is Iris Vale. I work nights, because buildings are more honest after dark.", .65),
    ("04", "iris", "office", "The newest complaint arrived at two eleven in the morning.", .47),
    ("05", "iris", "form", "Fourteen Bell Street. Noise disturbance. Somebody is crying inside my walls.", 1.0),
    ("06", "cal", "office", "Pipes.", .35),
    ("07", "iris-spoken", "office", "Pipes rarely fill in municipal paperwork, Cal.", .45),
    ("08", "cal", "office", "Then charge them a filing fee.", .68),
    ("09", "iris", "exterior", "I went to Bell Street. I wish I had brought a second flashlight.", .76),
    ("10", "iris-spoken", "door", "City services. You filed a noise complaint?", .58),
    ("11", "house", "door", "Yes. I have been waiting for you.", .95),
    ("12", "iris-spoken", "door", "How long?", .30),
    ("13", "house", "door", "Forty seven years.", 1.1),
    ("14", "iris-spoken", "door", "That is older than I am.", .43),
    ("15", "house", "door", "I know.", 1.04),
    ("16", "iris-spoken", "door", "Who is crying?", .35),
    ("17", "house", "door", "You are.", 1.25),
    ("18", "iris", "window", "That was when the upstairs window lit up.", .80),
    ("19", "house", "window", "Whatever you do, Iris, do not look at the window.", 1.32),
    ("20", "iris", "window", "Of course I looked.", 2.4),
]
CAST = {
    "iris": {"name":"Iris · inner monologue", "speed":1.07},
    "iris-spoken": {"name":"Iris", "speed":1.01},
    "cal": {"name":"Cal · telephone", "speed":1.04},
    "house": {"name":"House 14", "speed":.92},
}
p = KPipeline(lang_code="a")
kore = p.load_voice("af_kore")
nova = p.load_voice("af_nova")
iris_voice = kore * .34 + nova * .66
cast_voices = {
    "iris": iris_voice,
    "iris-spoken": iris_voice,
    "cal": p.load_voice("am_liam"),
    "house": p.load_voice("am_onyx"),
}

def render(text, who):
    chunks = []
    for _, _, chunk in p(text, voice=cast_voices[who], speed=CAST[who]["speed"]):
        if hasattr(chunk, "detach"):
            chunk = chunk.detach().cpu().numpy()
        chunks.append(np.asarray(chunk, dtype=np.float32).reshape(-1))
    if not chunks:
        raise RuntimeError(f"Kokoro produced no speech for {who}: {text}")
    mono = np.concatenate(chunks)
    fade = min(int(.025*SR), len(mono)//4)
    if fade:
        mono[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        mono[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return mono

def spatial(mono, who):
    # Effects are applied to the film mix, never to the editable dry line WAV.
    a = mono.copy()
    if who == "house":
        a = a * .83
        # Distant wall resonance + early reflections, not an artificial monster voice.
        echo = np.zeros(len(a), dtype=np.float32)
        d = int(.115 * SR)
        echo[d:] = a[:-d] * .27
        a = a + echo
        b = np.zeros(len(a), dtype=np.float32)
        b[2:] = .22 * a[2:] + .56 * a[1:-1] + .22 * a[:-2]
        a = .72 * a + .28 * b
    if who == "cal":
        a = a * .73
    # Iris is slightly left, Cal right, House fills the room.
    left, right = {"iris":(.98,.92),"iris-spoken":(.99,.84),"cal":(.63,.96),"house":(.89,.89)}[who]
    return np.stack((a * left, a * right), axis=1)

manifest = []
audio_events = []
t = 3.0
for line_id, who, scene, words, pause in LINES:
    mono = render(words, who)
    filename = f"{line_id}.wav"
    sf.write(VOICES / filename, mono, SR)
    duration = len(mono) / SR
    manifest.append({
        "id":line_id, "speaker":who, "speaker_label":CAST[who]["name"],
        "scene":scene, "text":words, "speed":CAST[who]["speed"],
        "file":f"voices/{filename}", "start":round(t,3),
        "end":round(t + duration,3), "duration":round(duration,3),
        "after":pause,
    })
    audio_events.append((t, spatial(mono, who)))
    t += duration + pause
    print(f"{line_id} {who} {duration:.2f}s", flush=True)

total = t + 4.2
N = math.ceil(total * SR)
times = np.arange(N, dtype=np.float64) / SR
rng = np.random.default_rng(1414)
# Quiet, continuous room tone / rain with low industrial resonance.
noise = rng.standard_normal(N).astype(np.float32)
kernel = np.ones(70, dtype=np.float32) / 70
soft = np.convolve(noise, kernel, mode="same")
hum = .008*np.sin(2*np.pi*54*times) + .004*np.sin(2*np.pi*83*times)
bed = (hum + .025*soft).astype(np.float32)
mix = np.stack((bed,bed*.97),axis=1)
for when, hz in [(0.48,330),(1.38,392),(2.25,440),(total-3.9,220),(total-3.5,294)]:
    st = int(when*SR)
    if st >= N: continue
    tt=np.arange(min(int(2.5*SR), N-st))/SR
    bell=(.042*np.exp(-tt*1.8)*(np.sin(2*np.pi*hz*tt)+.25*np.sin(2*np.pi*hz*2.01*tt))).astype(np.float32)
    mix[st:st+len(bell),:] += bell[:,None]
for start, clip in audio_events:
    at=int(start*SR)
    mix[at:at+len(clip)] += clip
# Fade in/out and soft peak limiting.
fade=int(.9*SR)
mix[:fade] *= np.linspace(0,1,fade)[:,None]
mix[-fade:] *= np.linspace(1,0,fade)[:,None]
mix=np.tanh(mix*.94)
sf.write(BASE/"mix_temp.wav", mix, SR)
subprocess.run([
    "ffmpeg","-y","-hide_banner","-loglevel","error",
    "-i",str(BASE/"mix_temp.wav"),"-af","loudnorm=I=-16:LRA=9:TP=-1.5",
    "-codec:a","libmp3lame","-b:a","160k",str(BASE/"episode_01.mp3"),
],check=True)
(BASE/"mix_temp.wav").unlink(missing_ok=True)
(BASE/"manifest.json").write_text(json.dumps({
    "title":"The Complaints Department · Episode 01: House 14",
    "duration":round(total,3), "sample_rate":SR,
    "cast":{"iris":"af_kore 34% + af_nova 66%", "iris-spoken":"af_kore 34% + af_nova 66%","cal":"am_liam","house":"am_onyx"},
    "lines":manifest,
},indent=2)+"\n",encoding="utf-8")
print(f"Completed {total:.2f}s. Audio + line assets written.", flush=True)
