"""House Rules — Kokoro rap with generated 92 BPM hip-hop beat.
Standalone renderer. Emits house_rules/house_rules.mp3 for GitHub Pages.
"""
from pathlib import Path
import subprocess

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
SR, BPM, BARS = 24000, 92, 16
BEAT = 60.0 / BPM
BAR = BEAT * 4
TOTAL = int((BARS * BAR + 0.5) * SR)
RNG = np.random.default_rng(917)

LINES = [
    "Midnight, keys on the table, lights low.",
    "Rain on the window like a private show.",
    "You saw the lock and you gave me that stare.",
    "I said, don't touch. You said, is that a dare?",
    "Floorboards talk and the stairwell hums.",
    "Somebody upstairs keeps time on drums.",
    "You want the truth? Then get close, stay near.",
    "If the walls start talking, I wanna hear.",
    "Knock knock. Let the bassline in.",
    "Turn that key, let the night begin.",
    "No ghosts? Fine. Let the shadows spin.",
    "House rules break when the drums kick in.",
]

def midi(note):
    return 440 * (2 ** ((note - 69) / 12))

def add(track, mono, seconds, gain=1, pan=0):
    start = round(seconds * SR)
    if start < 0 or start >= len(track):
        return
    a = np.asarray(mono, dtype=np.float32)[:len(track) - start]
    theta = (pan + 1) * np.pi / 4
    track[start:start + len(a), 0] += a * (gain * np.cos(theta))
    track[start:start + len(a), 1] += a * (gain * np.sin(theta))

def tone(hz, seconds, decay=1.5):
    t = np.arange(int(SR * seconds)) / SR
    return np.sin(2*np.pi*hz*t) * np.exp(-decay*t)

def make_beat():
    track = np.zeros((TOTAL, 2), dtype=np.float32)
    chords = [(50,53,57,62), (46,50,53,57), (53,57,60,65), (48,52,55,60)]
    bassnotes = [38,34,41,36]
    for b in range(BARS):
        t0 = BAR * b
        ix = (b//2) % 4
        for j, note in enumerate(chords[ix]):
            t = np.arange(int(SR * 1.9)) / SR
            freq = midi(note)
            pad = (np.sin(2*np.pi*freq*t) + 0.20*np.sin(4*np.pi*freq*t))
            pad *= np.minimum(1.0,t*16) * np.exp(-1.8*t)
            add(track, pad, t0+0.01, 0.026, -0.4 if j%2 else 0.4)
        if b < 2 or b > 14:
            continue
        kicks = (0, 1.5, 2.75) if b%2==0 else (0, 1.75, 2.5, 3.5)
        for p in kicks:
            t = np.arange(int(SR*0.38)) / SR
            frequency = 47 + 115*np.exp(-37*t)
            kick = np.sin(2*np.pi*np.cumsum(frequency)/SR)*np.exp(-13*t)
            add(track, kick, t0 + p*BEAT, 0.31)
        for p in (1,3):
            t = np.arange(int(SR*0.17))/SR
            n = RNG.standard_normal(len(t))
            snare = (n*0.65 + np.sin(2*np.pi*190*t)*0.35)*np.exp(-27*t)
            add(track, snare, t0 + p*BEAT, 0.13, 0.12)
        for h in range(8):
            t = np.arange(int(SR*0.065))/SR
            hat = RNG.standard_normal(len(t)) * np.exp(-70*t)
            add(track, hat, t0 + (h*0.5+0.055*(h%2))*BEAT, 0.038, (-0.55 if h%2 else 0.55))
        for p, shift in [(0,0), (1.75,7), (2.5,0), (3.5,0)]:
            t = np.arange(int(SR*0.49))/SR
            bass = np.tanh(2*np.sin(2*np.pi*midi(bassnotes[ix]+shift)*t)) * np.exp(-3.8*t)
            add(track, bass, t0+p*BEAT, 0.12)
    return track

def kokoro_line(pipeline, words, voice, speed):
    chunks=[]
    for _,_,audio in pipeline(words, voice=voice, speed=speed):
        if audio is None:
            continue
        if hasattr(audio,'detach'):
            audio = audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio, dtype=np.float32).reshape(-1))
    if not chunks:
        raise RuntimeError("Kokoro returned no audio for: "+words)
    x = np.concatenate(chunks)
    peak = max(1e-8,float(np.max(np.abs(x))))
    active = np.flatnonzero(np.abs(x) > 0.009*peak)
    if len(active):
        x = x[max(0,active[0]-320):min(len(x),active[-1]+1500)]
    # A rapper's bar is fixed. Compress spoken lines into the musical slot.
    max_length = round(SR * (BAR - 0.25))
    if len(x)>max_length:
        # Resampling also lifts pitch slightly, giving a more insistent delivery.
        ix = np.linspace(0,len(x)-1,max_length)
        x = np.interp(ix,np.arange(len(x)),x).astype(np.float32)
    fade = min(240,len(x)//5)
    if fade:
        x[:fade] *= np.linspace(0,1,fade)
        x[-fade:] *= np.linspace(1,0,fade)
    return x

def main():
    print("Loading Kokoro (Kore verse, Kore/Nova blended hook)", flush=True)
    p = KPipeline(lang_code="a")
    kore = p.load_voice("af_kore")
    nova = p.load_voice("af_nova")
    hook = kore*0.35 + nova*0.65
    track = make_beat()
    for i, words in enumerate(LINES):
        voice = kore if i<8 else hook
        speed = 1.30 if i<8 else 1.20
        x = kokoro_line(p, words, voice, speed)
        when = (i+2)*BAR + 0.08
        add(track, np.tanh(x*1.10), when, 0.64, -0.03)
        add(track, np.tanh(x*1.10), when+0.19, 0.065, 0.55)
        print(f"Rendered {i+1}/{len(LINES)}: {words}", flush=True)
    peak = float(np.max(np.abs(track)))
    if peak > 0.89:
        track *= 0.89/peak
    tmp = ROOT/"house_rules_mix.wav"
    out = ROOT/"house_rules.mp3"
    sf.write(tmp, track, SR)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(tmp), "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
        "-codec:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    print("Saved:",out, "bytes:",out.stat().st_size,flush=True)

if __name__=="__main__":
    main()
