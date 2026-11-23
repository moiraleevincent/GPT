"""Kokoro voice-only re-voice of Mara: The Key to Almost Everything.
Keeps the original 34-second picture edit and dramatic beat times.
"""
from pathlib import Path
import json
import subprocess
import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000
DURATION = 34.0
OUT = Path("mara_kokoro_revoice")
OUT.mkdir(parents=True, exist_ok=True)
p = KPipeline(lang_code="a")
voices = {
    "NARRATOR": p.load_voice("bm_george"),
    "MARA": p.load_voice("af_nova"),
}
lines = [
    ("01", 0.50, "NARRATOR", "In a city... where every second counts...", 1.06),
    ("02", 7.60, "NARRATOR", "Emergency!", 1.00),
    ("03", 11.30, "NARRATOR", "The last cookie... is trapped!", 1.08),
    ("04", 16.55, "MARA", "Stand back. I have a key.", 1.02),
    ("05", 19.96, "NARRATOR", "Behold! The master key!", 1.12),
    ("06", 25.35, "NARRATOR", "The city is saved!", 1.04),
    ("07", 27.88, "NARRATOR", "It was a twist-off lid.", 1.08),
    ("08", 30.03, "MARA", "I knew that.", 0.99),
]
master = np.zeros(int(SR * DURATION), dtype=np.float32)
manifest=[]
for id, start, speaker, text, speed in lines:
    chunks=[]
    for _, _, chunk in p(text, voice=voices[speaker], speed=speed):
        if hasattr(chunk, "detach"):
            chunk=chunk.detach().cpu().numpy()
        chunks.append(np.asarray(chunk, dtype=np.float32))
    if not chunks:
        raise RuntimeError("Kokoro returned no audio for "+id)
    a=np.concatenate(chunks)
    fade=min(int(.025*SR),len(a)//4)
    if fade:
        ramp=np.linspace(0,1,fade)
        a[:fade]*=ramp
        a[-fade:]*=ramp[::-1]
    # Each line separate for later animation adjustments.
    sf.write(OUT/f"line_{id}.wav",a,SR)
    st=round(start*SR)
    end=min(len(master),st+len(a))
    if end>st:
        master[st:end]+=a[:end-st] * (0.87 if speaker=="MARA" else 0.78)
    manifest.append(dict(id=id,start=start,duration=round(len(a)/SR,3),speaker=speaker,text=text,speed=speed,file=f"line_{id}.wav"))
    print(id, speaker, round(len(a)/SR,2), "s (space to next:", round((lines[int(id)][1]-start) if int(id)<len(lines) else 34-start,2),")",flush=True)
peak=float(np.max(np.abs(master)))
if peak>0.94:
    master*=0.94/peak
sf.write(OUT/"voices_only.wav",master,SR)
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(OUT/"voices_only.wav"),"-c:a","libmp3lame","-b:a","160k",str(OUT/"voices_only.mp3")],check=True)
print("KOKORO VOICES READY",len(manifest),flush=True)
