from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
from pathlib import Path

SR = 24000
OUT = Path("work_companion_radio/casting")
OUT.mkdir(parents=True, exist_ok=True)

PIPE = {"a": KPipeline(lang_code="a"), "b": KPipeline(lang_code="b")}

FEMALE = {
    "Jessica": ("af_jessica", "a"),
    "Kore": ("af_kore", "a"),
    "Nova": ("af_nova", "a"),
    "Sky": ("af_sky", "a"),
}
MALE = {
    "Onyx": ("am_onyx", "a"),
    "Puck": ("am_puck", "a"),
    "Fable": ("bm_fable", "b"),
    "Lewis": ("bm_lewis", "b"),
}

# Same opening scene for every pairing; only the casting changes.
TURNS = [
    ("F", "I have to do boring work."),
    ("M", "I know."),
    ("F", "That sounded judgmental."),
    ("M", "It was observational. You have opened the same form four times and achieved a total of one checkbox."),
    ("F", "It was an important checkbox."),
    ("M", "It asked whether you live in Sweden."),
    ("F", "I wanted to be certain."),
    ("M", "You looked out the window."),
    ("F", "Due diligence."),
    ("M", "Fine. Do your form. I have something to read to you."),
    ("F", "Is it interesting?"),
    ("M", "No."),
    ("F", "Perfect."),
    ("M", "It arrived in the shared folder this afternoon. No sender. PDF. Thirty-seven pages."),
    ("F", "Absolutely not."),
    ("M", "Page one says, quote: Notice of Attachment Review."),
    ("F", "That is either human resources or a demon."),
    ("M", "There is a subsection called Threshold Access."),
    ("F", "Demon."),
    ("M", "There is also a checkbox for Unauthorized Persistence."),
    ("F", "Human resources can still do that."),
]

SPEED_F = 1.04
SPEED_M = 0.99
PAN_F = -0.18
PAN_M = 0.18


def mono_to_stereo(x, pan=0.0):
    x = np.asarray(x, dtype=np.float32)
    angle = (pan + 1.0) * np.pi / 4.0
    return np.column_stack((x * np.cos(angle), x * np.sin(angle))).astype(np.float32)


def silence(seconds):
    return np.zeros((int(SR * seconds), 2), dtype=np.float32)


def fade(stereo, ms=22):
    n = min(len(stereo)//2, int(SR * ms / 1000))
    if n > 1:
        f = np.linspace(0.0, 1.0, n, dtype=np.float32)[:, None]
        stereo[:n] *= f
        stereo[-n:] *= f[::-1]
    return stereo


def room_tone(n, seed=20261002, level=0.0045):
    rng = np.random.default_rng(seed + n % 991)
    t = np.arange(n, dtype=np.float32) / SR
    hum = 0.35*np.sin(2*np.pi*50*t) + 0.15*np.sin(2*np.pi*100*t)
    noise = rng.normal(0,1,n).astype(np.float32)
    kernel = np.ones(16, dtype=np.float32)/16
    noise = np.convolve(noise, kernel, mode="same")
    mono = level*(0.55*noise + 0.45*hum)
    return mono_to_stereo(mono, 0)


def sting():
    dur = 2.15
    n = int(SR*dur)
    t = np.arange(n, dtype=np.float32)/SR
    y = np.zeros(n, dtype=np.float32)
    for i, f in enumerate([196.0, 246.94, 293.66]):
        env = np.clip((t-i*0.18)/0.20,0,1)*np.clip((dur-t)/0.70,0,1)
        y += 0.05*env*(np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*(f/2)*t))
    return mono_to_stereo(y, 0)


def render_text(text, voice_name, lang, speed, pan):
    p = PIPE[lang]
    voice = p.load_voice(voice_name)
    chunks=[]
    for _,_,audio in p(text, voice=voice, speed=speed):
        if hasattr(audio,"detach"):
            audio = audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio,dtype=np.float32))
    x = np.concatenate(chunks) if chunks else np.zeros(1,dtype=np.float32)
    peak=float(np.max(np.abs(x))) or 1.0
    if peak>0.92:
        x*=0.92/peak
    return fade(mono_to_stereo(x,pan))

# Render each unique line for each candidate once, then reuse for all pairings.
cache={}
for fname,(voice,lang) in FEMALE.items():
    for idx,(role,text) in enumerate(TURNS):
        if role=="F":
            cache[("F",fname,idx)] = render_text(text,voice,lang,SPEED_F,PAN_F)
for mname,(voice,lang) in MALE.items():
    for idx,(role,text) in enumerate(TURNS):
        if role=="M":
            cache[("M",mname,idx)] = render_text(text,voice,lang,SPEED_M,PAN_M)

intro = sting()*0.46

for fname in FEMALE:
    for mname in MALE:
        pieces=[room_tone(len(silence(0.65))), intro, silence(0.22)]
        for idx,(role,text) in enumerate(TURNS):
            seg = cache[(role, fname if role=="F" else mname, idx)]
            pieces.append(room_tone(len(silence(0.09)), seed=100+idx))
            pieces.append(np.clip(seg + room_tone(len(seg), seed=1000+idx), -1,1))
            post = 0.18
            if text in {"Perfect.", "Demon."}:
                post=0.26
            pieces.append(room_tone(len(silence(post)), seed=2000+idx))
        master=np.concatenate(pieces,axis=0)
        master=np.tanh(master*1.12)/np.tanh(1.12)
        peak=float(np.max(np.abs(master))) or 1.0
        if peak>0.96:
            master*=0.96/peak
        stem=f"{fname.lower()}__{mname.lower()}"
        wav=OUT/f"{stem}.wav"
        mp3=OUT/f"{stem}.mp3"
        sf.write(wav,master,SR)
        subprocess.run([
            "ffmpeg","-y","-hide_banner","-loglevel","error",
            "-i",str(wav),"-af","loudnorm=I=-16:LRA=9:TP=-1.5",
            "-codec:a","libmp3lame","-b:a","128k",str(mp3)
        ],check=True)
        wav.unlink(missing_ok=True)
        print("rendered",mp3)
