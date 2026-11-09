#!/usr/bin/env python3
"""Four Kokoro voice auditions based on ideas in Chapter 2 of Don Norman's book.

The narration is original, not a verbatim reproduction of the book.
Render: two listening passages x two contrasting voices -> mastered MP3s.
"""
from pathlib import Path
import json
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "audio"
OUT.mkdir(parents=True, exist_ok=True)
SR = 24000

PASSAGES = {
    "two_gulfs": {
        "title": "The two gulfs",
        "parts": [
            ("When you approach an unfamiliar device, there are two questions.", 0.31),
            ("First: what can I do, and how do I do it? That is the gulf of execution.", 0.49),
            ("Second: what happened after I acted, and did it accomplish what I wanted? That is the gulf of evaluation.", 0.56),
            ("Good design narrows both distances. It makes the possible actions clear, and the results easy to understand.", 0.45),
        ],
    },
    "wrong_blame": {
        "title": "Blaming the wrong things",
        "parts": [
            ("You turn a control, wait, and nothing seems to happen.", 0.38),
            ("You try again. This time, perhaps, you wonder whether you misunderstood something obvious.", 0.48),
            ("But when people repeatedly struggle with an ordinary object, the important question is not whether they are clever enough to use it.", 0.48),
            ("It is whether the design has given them enough information to succeed.", 0.51),
        ],
    },
}


def to_numpy(sound):
    if hasattr(sound, "detach"):
        sound = sound.detach().cpu().numpy()
    return np.asarray(sound, dtype=np.float32).reshape(-1)


def render_line(pipe, text, voice, speed):
    chunks = [to_numpy(sound) for _, _, sound in pipe(text, voice=voice, speed=speed)]
    if not chunks or not any(len(x) for x in chunks):
        raise RuntimeError(f"Empty Kokoro rendering: {text}")
    result = np.concatenate([x for x in chunks if len(x)])
    fade = min(360, len(result)//4)  # 15ms fade at 24kHz
    if fade:
        result[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        result[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return result


def render_passage(pipe, parts, voice, speed):
    frames = [np.zeros(int(SR * 0.20), dtype=np.float32)]
    for text, pause in parts:
        frames.append(render_line(pipe, text, voice, speed))
        frames.append(np.zeros(int(SR * pause), dtype=np.float32))
    audio = np.concatenate(frames)
    peak = float(np.max(np.abs(audio)))
    if peak > 0.94:
        audio = audio * (0.94 / peak)
    return audio


def export_mp3(audio, path):
    with tempfile.TemporaryDirectory() as temp:
        wav = Path(temp) / "unmastered.wav"
        sf.write(wav, audio, SR, subtype="PCM_16")
        subprocess.run([
            "ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(wav),
            "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
            "-codec:a", "libmp3lame", "-b:a", "128k", str(path)
        ], check=True)
    if not path.exists() or path.stat().st_size < 5000:
        raise RuntimeError("MP3 generation failed: " + str(path))


def main():
    pipeline = KPipeline(lang_code="a")
    kore = pipeline.load_voice("af_kore")
    nova = pipeline.load_voice("af_nova")
    voices = [
        ("host", "Kore / Nova blend", kore * 0.35 + nova * 0.65, 1.04),
        ("george", "George", pipeline.load_voice("bm_george"), 0.98),
    ]

    manifest = {
        "title": "The Psychology of Everyday Actions — Kokoro Voice Study",
        "source": "Original adaptations of concepts from chapter 2 of Don Norman's The Design of Everyday Things; not book quotations.",
        "sample_rate": SR,
        "samples": [],
    }
    for key, passage in PASSAGES.items():
        for slug, voice_name, tensor, speed in voices:
            name = f"{key}_{slug}.mp3"
            print("RENDER", name, flush=True)
            clip = render_passage(pipeline, passage["parts"], tensor, speed)
            dest = OUT / name
            export_mp3(clip, dest)
            manifest["samples"].append({
                "passage": key,
                "title": passage["title"],
                "voice": slug,
                "voice_name": voice_name,
                "speed": speed,
                "file": "audio/" + name,
                "seconds": round(len(clip)/SR, 2),
                "bytes": dest.stat().st_size,
                "text": " ".join(text for text, _ in passage["parts"]),
            })
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("COMPLETE", len(manifest["samples"]), "MP3s", flush=True)


if __name__ == "__main__":
    main()
