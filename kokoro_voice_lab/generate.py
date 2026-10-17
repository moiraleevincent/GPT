#!/usr/bin/env python3
"""Kokoro voice laboratory: controlled A/B tests for audio direction.

Output: individually playable MP3 files + results.json.
The original Evolutionary Court and its existing generator are untouched.
Compare the same sentence across variants before judging differences.
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
LINE = "I said it could evolve, not that it had to."

def gap(seconds):
    return np.zeros(round(max(0, seconds) * SR), dtype=np.float32)

def fade(x, n=190):
    x = np.asarray(x, dtype=np.float32).reshape(-1).copy()
    width = min(n, len(x) // 4)
    if width:
        x[:width] *= np.linspace(0, 1, width, dtype=np.float32)
        x[-width:] *= np.linspace(1, 0, width, dtype=np.float32)
    return x

def speech(pipe, words, voice, speed=1.04):
    clips = []
    for _, _, sound in pipe(words, voice=voice, speed=speed):
        if hasattr(sound, "detach"):
            sound = sound.detach().cpu().numpy()
        clips.append(np.asarray(sound, dtype=np.float32))
    if not clips:
        raise RuntimeError("Kokoro returned no speech for: " + words)
    return fade(np.concatenate(clips))

def ffmpeg_audio(source, af):
    with tempfile.TemporaryDirectory() as td:
        a = Path(td) / "source.wav"
        b = Path(td) / "out.wav"
        sf.write(a, source, SR)
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",str(a),"-af",af,"-ar",str(SR),"-ac","1",str(b)],check=True)
        data, rate = sf.read(b, dtype="float32")
    if rate != SR or not len(data):
        raise RuntimeError("Unexpected FFmpeg result")
    return fade(data)

def pitch_shift(source, factor):
    # Rubber Band changes pitch while retaining tempo/formants. Falls back
    # to a standard FFmpeg resample + tempo-correction path if unavailable.
    try:
        return ffmpeg_audio(source, f"rubberband=pitch={factor:.4f}:formant=preserved")
    except subprocess.CalledProcessError:
        return ffmpeg_audio(source, f"asetrate={round(SR*factor)},aresample={SR},atempo={1/factor:.5f}")

def export(name, data, label, group, method, note):
    data = np.asarray(data, dtype=np.float32)
    if not len(data):
        raise RuntimeError("Empty audio: " + name)
    peak = float(np.max(np.abs(data)))
    if peak > .95:
        data *= .95 / peak
    dest = OUT / (name + ".mp3")
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        sf.write(wav, data, SR)
        subprocess.run([
          "ffmpeg", "-nostdin", "-hide_banner","-loglevel","error","-y",
          "-i",str(wav),"-af","loudnorm=I=-16:LRA=9:TP=-1.5",
          "-codec:a","libmp3lame","-b:a","128k",str(dest)
        ],check=True)
    info={"id":name,"file":"audio/"+dest.name,"label":label,"group":group,
          "method":method,"note":note,"duration":round(len(data)/SR,2),
          "bytes":dest.stat().st_size}
    print("EXPORTED",json.dumps(info),flush=True)
    return info

def knock():
    # Synthetic wooden tap, no third-party audio.
    dur=.25
    t=np.arange(round(dur*SR),dtype=np.float32)/SR
    return fade((.075*np.sin(2*np.pi*137*t)+.023*np.sin(2*np.pi*301*t))*np.exp(-26*t))

def stage_scene(pipe, examiner, counsel):
    turns=[
      ("E","Court is in session. Today we ask: can an animal be selfish and cooperative at the same time?",.30,1.07),
      ("C","Of course. You're confusing motivation with what natural selection favors.",.30,1.03),
      ("E","That's a dangerous thing to say in a courtroom.",.30,1.06),
      ("C","Only if the judge is a mongoose.",.50,1.02),
      ("E","The [judge](+1) is a mongoose.",.66,1.02),
      ("C","Then I'd like to revise my testimony.",.68,1.03)
    ]
    track=[gap(.16),knock(),gap(.27)]
    for role,words,wait,speed in turns:
        voice=examiner if role=="E" else counsel
        track += [speech(pipe,words,voice,speed), gap(wait)]
    return np.concatenate(track)

def main():
    p=KPipeline(lang_code="a")
    kore=p.load_voice("af_kore")
    nova=p.load_voice("af_nova")
    examiner = kore*.35 + nova*.65  # exact pilot voice
    counsel = p.load_voice("bm_george") # exact pilot co-host
    results=[]
    print("RENDER baseline",flush=True)
    base = speech(p,LINE,examiner,1.04)
    results.append(export("01_original",base,"01 · Original take","Voice direction",
      "Original words, punctuation, voice blend, and 1.04 speed",
      "The untouched comparison reference."))
    print("RENDER stress",flush=True)
    emphasis=speech(p,"I said it [could](+2) evolve, not that it [had](-1) to.",examiner,1.04)
    results.append(export("02_stress",emphasis,"02 · Stress marks","Voice direction",
      "Kokoro: [could](+2), [had](-1)",
      "Tests native phonological stress; it may be very subtle."))
    print("RENDER punctuation",flush=True)
    punct=speech(p,"I said it could evolve — not that it had to.",examiner,1.04)
    results.append(export("03_punctuation",punct,"03 · The em dash","Voice direction",
      "Replace the comma with an em dash, otherwise unchanged",
      "Tests whether a punctuation cue reshapes the sentence."))
    print("RENDER split",flush=True)
    beat=np.concatenate([
      speech(p,"I said it could evolve.",examiner,1.04),
      gap(.43),
      speech(p,"Not that it had to.",examiner,1.04)
    ])
    results.append(export("04_cut_and_pause",beat,"04 · Directed pause","Voice direction",
      "Two separately synthesised clauses + exactly 430 ms of silence",
      "Pacing and sentence segmentation, with a deliberate beat."))
    print("RENDER speed",flush=True)
    quick=speech(p,LINE,examiner,1.08)
    results.append(export("05_speed",quick,"05 · Slightly faster","Voice direction",
      "Native Kokoro speed 1.08 versus 1.04",
      "A small proposed adjustment for future episodes."))
    print("PROCESS lower pitch",flush=True)
    low=pitch_shift(base,.955)
    results.append(export("06_pitch_lower",low,"06 · Lower pitch","Audio processing",
      "The original take, post-processed at 0.955× pitch",
      "Should sound modestly deeper while preserving approximately the same duration."))
    print("PROCESS higher pitch",flush=True)
    high=pitch_shift(base,1.055)
    results.append(export("07_pitch_higher",high,"07 · Higher pitch","Audio processing",
      "The original take, post-processed at 1.055× pitch",
      "Should sound modestly brighter; this is not pitch-contour editing."))
    print("PROCESS room sound",flush=True)
    distant=ffmpeg_audio(base,"lowpass=f=2400,aecho=0.8:0.7:55|125:0.12|0.07,volume=0.88")
    results.append(export("08_distance",distant,"08 · Across the room","Audio processing",
      "Low-pass filter, short echoes, reduced gain",
      "Changes acoustic location, not the speaker's acting or emotion."))
    print("RENDER dialogue",flush=True)
    scene=stage_scene(p,examiner,counsel)
    results.append(export("09_two_hosts",scene,"09 · Two-host scene","Performance",
      "Kore/Nova host + George counsel; timing, stress, synthetic gavel",
      "A miniature scene combining the controls, rather than an A/B comparison."))
    manifest={
      "title":"Kokoro Voice Laboratory · Session 01",
      "source_sentence":LINE,
      "voices":{"examiner":"35% Kore + 65% Nova","counsel":"George"},
      "samples":results,
      "warning":"A/B judgments are subjective; tests vary only the specified production dimension where feasible. The directed pause also changes segmentation and punctuation."
    }
    (ROOT/"results.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("COMPLETE",len(results),"samples",flush=True)

if __name__=="__main__":
    main()
