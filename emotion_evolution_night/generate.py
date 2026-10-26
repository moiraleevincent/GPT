#!/usr/bin/env python3
"""Render an original single-narrator Kokoro science sleepcast.

Inputs: part_01.txt, part_02.txt. Output: the_social_lives_of_emotions.mp3
Research/source ledger: sources.md
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
SR = 24000
SPEED = 1.10
VOICE_KORE = 0.35
VOICE_NOVA = 0.65
OUTPUT = ROOT / "the_social_lives_of_emotions.mp3"
TEMP_WAV = ROOT / "_master_temp.wav"


def blank(seconds: float) -> np.ndarray:
    return np.zeros(round(SR * seconds), dtype=np.float32)


def split_long_sentence(sentence: str, limit: int) -> list[str]:
    """Defensive length guard, preferring comma/semicolon/space boundaries."""
    parts = []
    while len(sentence) > limit:
        cut = max(sentence.rfind(c, 0, limit) for c in [", ", "; ", ": ", " — ", " "])
        if cut < limit // 3:
            cut = limit
        piece = sentence[:cut].strip()
        if piece:
            parts.append(piece)
        sentence = sentence[cut:].strip()
    if sentence:
        parts.append(sentence)
    return parts


def units_of(paragraph: str, limit: int = 385) -> list[str]:
    """Split on sentence boundaries, avoiding excessive text in one Kokoro call."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    sentences = [sub for s in sentences for sub in split_long_sentence(s, limit)]
    units = []
    unit = ""
    for sentence in sentences:
        candidate = (unit + " " + sentence).strip()
        if len(candidate) <= limit:
            unit = candidate
        else:
            if unit:
                units.append(unit)
            unit = sentence
    if unit:
        units.append(unit)
    return units


def load_paragraphs() -> list[str]:
    parts = []
    for part_index, filename in enumerate(("part_01.txt", "part_02.txt")):
        text = (ROOT / filename).read_text(encoding="utf-8").strip()
        chunks = re.split(r"\n\s*\n", text)
        for chunk_index, chunk in enumerate(chunks):
            paragraph = " ".join(chunk.split())
            if not paragraph:
                continue
            # The show title is spoken just once; part two's label remains audible.
            if part_index == 1 and chunk_index == 0 and paragraph == "THE SOCIAL LIVES OF EMOTIONS":
                continue
            parts.append(paragraph)
    return parts


def render_unit(pipeline: KPipeline, voice, sentence: str, count: int) -> np.ndarray:
    chunks = []
    for _, _, audio in pipeline(sentence, voice=voice, speed=SPEED):
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        arr = np.asarray(audio, dtype=np.float32).reshape(-1)
        if arr.size:
            chunks.append(arr)
    if not chunks:
        raise RuntimeError(f"Kokoro returned no audio for unit {count}: {sentence[:120]!r}")
    result = np.concatenate(chunks)
    if not np.isfinite(result).all():
        raise RuntimeError(f"Kokoro returned NaN/Inf at unit {count}")

    # Gently ramp the boundaries before adding silence, avoiding sharp clicks.
    fade = min(int(SR * 0.012), result.size // 4)
    if fade:
        ramp = np.linspace(0, 1, fade, endpoint=True, dtype=np.float32)
        result[:fade] *= ramp
        result[-fade:] *= ramp[::-1]
    return result


def main() -> None:
    paragraphs = load_paragraphs()
    word_count = sum(len(p.split()) for p in paragraphs)
    print(f"Preparing {word_count} words in {len(paragraphs)} paragraphs.", flush=True)
    pipeline = KPipeline(lang_code="a")
    kore = pipeline.load_voice("af_kore")
    nova = pipeline.load_voice("af_nova")
    # A single, stable blended *narrator*, never alternating speakers.
    narrator = kore * VOICE_KORE + nova * VOICE_NOVA

    pieces = [blank(0.55)]
    unit_index = 0
    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        heading = paragraph.isupper() and len(paragraph) < 100
        units = units_of(paragraph)
        for i, unit in enumerate(units):
            unit_index += 1
            clip = render_unit(pipeline, narrator, unit, unit_index)
            pieces.append(clip)
            if i != len(units) - 1:
                pieces.append(blank(0.13))
        # Gentle transitions; chapter headings get extra air without SFX.
        pieces.append(blank(0.85 if heading else 0.43))
        if paragraph_index % 20 == 0:
            print(f"Rendered {paragraph_index}/{len(paragraphs)} paragraphs, {unit_index} units.", flush=True)

    pieces.append(blank(2.2))
    master = np.concatenate(pieces)
    peak = float(np.max(np.abs(master))) or 1.0
    if peak > 0.95:
        master *= 0.95 / peak
    sf.write(TEMP_WAV, master, SR, subtype="PCM_16")
    del master, pieces

    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(TEMP_WAV),
            "-af", "loudnorm=I=-18:LRA=7:TP=-1.5",
            "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "112k",
            str(OUTPUT),
        ],
        check=True,
    )
    TEMP_WAV.unlink(missing_ok=True)
    print(f"Published {OUTPUT.name}, {OUTPUT.stat().st_size:,} bytes.", flush=True)


if __name__ == "__main__":
    main()
