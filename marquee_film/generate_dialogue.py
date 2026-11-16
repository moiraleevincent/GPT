#!/usr/bin/env python3
"""Render timed Kokoro dialogue for The Last Name on the Marquee, opening sequence.

The timeline is the JSON-compatible cues array embedded in index.html.
Generating a single voice track keeps the browser film editable while preserving
exact cut and caption timing. Ambient sound/music remain procedural in the browser.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
match = re.search(r"const cues=(\[[\s\S]*?\]);", HTML)
if not match:
    raise RuntimeError("Could not locate const cues array in index.html")
CUES = json.loads(match.group(1))
SR = 24000
DURATION = 192
CAST = {
    "ESTHER": ("bf_emma", 1.06, -0.15),
    "ROWAN": ("bf_isabella", 1.06, +0.15),
    "BOY": ("bm_george", 1.09, -0.04),
    "WORKER": ("bm_daniel", 1.08, +0.08),
}
pipeline = KPipeline(lang_code="b")
voice_cache = {}
mix = np.zeros((DURATION * SR + SR, 2), dtype=np.float32)
events = []

def as_numpy(y):
    if hasattr(y, "detach"):
        y = y.detach().cpu().numpy()
    return np.asarray(y, dtype=np.float32).reshape(-1)

for i, (start, end, speaker, text) in enumerate(CUES):
    name, speed, pan = CAST[speaker]
    if name not in voice_cache:
        voice_cache[name] = pipeline.load_voice(name)
    voice = voice_cache[name]
    parts = [as_numpy(audio) for _, _, audio in pipeline(text, voice=voice, speed=speed)]
    if not parts:
        raise RuntimeError("Empty Kokoro dialogue: " + text)
    a = np.concatenate(parts)
    available = min(end - start - 0.15, len(a) / SR)
    if available <= 0.05:
        continue
    samples = min(len(a), int(available * SR))
    a = a[:samples].copy()
    fade = min(int(SR * 0.028), samples // 5)
    if fade:
        a[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        a[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    rms = float(np.sqrt(np.mean(a * a) + 1e-9))
    gain = min(2.2, 0.105 / max(rms, 1e-5))
    a *= gain
    idx = int(start * SR)
    angle = (pan + 1.0) * np.pi / 4
    mix[idx:idx+samples, 0] += a * np.cos(angle)
    mix[idx:idx+samples, 1] += a * np.sin(angle)
    events.append({"id": i + 1, "at": start, "end": end, "speaker": speaker, "text": text, "voice": name, "actual_seconds": round(samples/SR, 2)})
    print(f"{i+1:02d} {speaker:7} {start:6.1f}s   {samples/SR:4.1f}s   {text[:70]}", flush=True)

peak = max(float(np.max(np.abs(mix))), 0.01)
mix *= min(1., .82 / peak)
out = ROOT / "audio"
out.mkdir(exist_ok=True)
wav = out / "dialogue.wav"
mp3 = out / "dialogue.mp3"
sf.write(str(wav), mix, SR)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-qscale:a", "3", str(mp3)], check=True)
wav.unlink()
(out / "manifest.json").write_text(json.dumps({"sample_rate":SR,"duration":DURATION,"casting":CAST,"events":events}, indent=2), encoding="utf-8")
print(f"Saved {mp3} ({mp3.stat().st_size/1024/1024:.2f} MB)")
