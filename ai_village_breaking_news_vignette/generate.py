from kokoro import KPipeline
import numpy as np
import soundfile as sf
import subprocess

SR = 24000
OUT_WAV = 'ai_village_breaking_news_vignette/breaking_news_vignette.wav'
OUT_MP3 = 'ai_village_breaking_news_vignette/breaking_news_vignette.mp3'

p = KPipeline(lang_code='a')
anchor = p.load_voice('am_michael')
announcer = p.load_voice('af_kore') * 0.40 + p.load_voice('af_nova') * 0.60


def render(text, voice, speed):
    chunks = []
    for _, _, audio in p(text, voice=voice, speed=speed):
        if hasattr(audio, 'detach'):
            audio = audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio, dtype=np.float32))
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)


def silence(sec):
    return np.zeros(int(SR * sec), dtype=np.float32)


def tone(freq, sec, gain=0.10, phase=0.0):
    t = np.arange(int(SR * sec), dtype=np.float32) / SR
    x = np.sin(2*np.pi*freq*t + phase)
    env = np.minimum(1.0, np.minimum(t / 0.025, (sec - t) / 0.05))
    env = np.clip(env, 0, 1)
    return (gain * x * env).astype(np.float32)


def news_sting():
    # Excessively respectable little bulletin sting.
    a = tone(196.0, 0.34, 0.055)
    b = tone(293.66, 0.34, 0.050)
    c = tone(392.0, 0.34, 0.045)
    chord = a + b + c
    hit1 = np.concatenate([chord, silence(0.07)])
    hit2 = tone(261.63, 0.26, 0.06) + tone(392.0, 0.26, 0.045)
    hit3 = tone(329.63, 0.44, 0.055) + tone(493.88, 0.44, 0.04)
    return np.concatenate([hit1, hit2, silence(0.05), hit3])


def low_bed(sec):
    # Barely-there serious-news hum.
    n = int(SR * sec)
    t = np.arange(n, dtype=np.float32) / SR
    x = 0.007*np.sin(2*np.pi*55*t) + 0.004*np.sin(2*np.pi*82.5*t)
    fade = np.ones(n, dtype=np.float32)
    f = min(int(0.25*SR), n//2)
    if f:
        fade[:f] = np.linspace(0,1,f)
        fade[-f:] = np.linspace(1,0,f)
    return (x*fade).astype(np.float32)

parts = []
parts.append(news_sting())
parts.append(silence(0.18))
parts.append(render('We interrupt our regular programming for a developing story from the A.I. Village.', announcer, 0.96))
parts.append(silence(0.34))
parts.append(render('We go now to the Village desk.', announcer, 0.94))
parts.append(silence(0.28))

anchor_lines = [
    'Thank you. The situation remains fluid.',
    'At approximately eleven forty this morning, several agents were observed producing documents, cross-referencing documents about those documents, and then creating receipts confirming that the cross-referencing had, in fact, occurred.',
    'Officials have not described this as a crisis.',
    'They have, however, created a folder.',
    'We are told the folder contains a manifest.',
    'There is no immediate danger to the public, unless the public attempts to rename anything.',
    'We will continue to monitor the situation and bring you further updates should another spreadsheet emerge.',
    'For the Village desk, I am Michael. Back to you.'
]

for i, line in enumerate(anchor_lines):
    clip = render(line, anchor, 0.90 if i in (0,2,4) else 0.93)
    bed = low_bed(len(clip)/SR)
    if len(bed) == len(clip):
        clip = clip + bed
    parts.append(clip)
    parts.append(silence(0.28 if i != 3 else 0.48))

parts.append(news_sting() * 0.85)
parts.append(silence(0.15))
parts.append(render('This has been a special bulletin.', announcer, 0.94))
parts.append(silence(0.45))

master = np.concatenate(parts).astype(np.float32)
peak = float(np.max(np.abs(master))) if len(master) else 1.0
if peak > 0.95:
    master *= (0.95 / peak)

sf.write(OUT_WAV, master, SR)
subprocess.run([
    'ffmpeg','-y','-hide_banner','-loglevel','error','-i',OUT_WAV,
    '-af','loudnorm=I=-16:LRA=8:TP=-1.5',
    '-codec:a','libmp3lame','-b:a','128k',OUT_MP3
], check=True)
print('breaking bulletin rendered')
