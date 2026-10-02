import math
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline
from kokoro_lab.engine import KokoroLab

SR = 24000
OUT = Path("work_companion_radio/internal_prosody")
OUT.mkdir(parents=True, exist_ok=True)

# We deliberately keep this experiment dry: no room tone, no reverb, no
# post-hoc pitch shifting, no time-stretching. Every performance change below
# happens before Kokoro's decoder renders the waveform.
lab = KokoroLab.load(device="cpu")
g2p = lab.make_g2p("a")
voice_pipe = KPipeline(lang_code="a", model=False)

PACKS = {
    "nova": voice_pipe.load_voice("af_nova").cpu(),
    "kore": voice_pipe.load_voice("af_kore").cpu(),
    "onyx": voice_pipe.load_voice("am_onyx").cpu(),
    "puck": voice_pipe.load_voice("am_puck").cpu(),
}

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

# Hand direction. The values are intentionally small. pitch is in semitones;
# range changes the contour around its own geometric mean; dur stretches the
# model's per-phoneme durations internally; fall adds a local phrase-final drop.
DIRECT = {
    0:  dict(pitch=+0.05, range=1.02, energy=1.00, dur=1.00, fall=-0.10),
    1:  dict(pitch=-0.18, range=0.82, energy=0.96, dur=1.04, fall=-0.30),
    2:  dict(pitch=-0.05, range=0.96, energy=0.98, dur=1.00, fall=-0.20),
    3:  dict(pitch=-0.10, range=0.88, energy=0.97, dur=1.01, fall=-0.22),
    4:  dict(pitch=-0.05, range=0.93, energy=0.98, dur=1.01, fall=-0.15),
    5:  dict(pitch=-0.16, range=0.84, energy=0.96, dur=1.02, fall=-0.28),
    6:  dict(pitch=+0.02, range=0.98, energy=0.99, dur=1.00, fall=-0.10),
    7:  dict(pitch=-0.22, range=0.82, energy=0.95, dur=1.03, fall=-0.35),
    8:  dict(pitch=-0.10, range=0.86, energy=0.96, dur=1.03, fall=-0.22),
    9:  dict(pitch=-0.08, range=0.90, energy=0.98, dur=1.00, fall=-0.18),
    10: dict(pitch=+0.10, range=1.08, energy=1.00, dur=0.99, fall=+0.05),
    11: dict(pitch=-0.28, range=0.72, energy=0.91, dur=1.08, fall=-0.32),
    12: dict(pitch=-0.08, range=0.90, energy=0.96, dur=1.04, fall=-0.16),
    13: dict(pitch=-0.16, range=0.84, energy=0.97, dur=0.99, fall=-0.24),
    14: dict(pitch=-0.10, range=0.92, energy=0.97, dur=1.01, fall=-0.18),
    15: dict(pitch=-0.14, range=0.86, energy=0.97, dur=1.01, fall=-0.25),
    16: dict(pitch=+0.02, range=1.02, energy=0.99, dur=1.00, fall=-0.10),
    17: dict(pitch=-0.14, range=0.88, energy=0.97, dur=1.01, fall=-0.22),
    18: dict(pitch=-0.24, range=0.76, energy=0.92, dur=1.07, fall=-0.30),
    19: dict(pitch=-0.12, range=0.88, energy=0.97, dur=1.01, fall=-0.22),
    20: dict(pitch=-0.10, range=0.90, energy=0.97, dur=1.02, fall=-0.18),
}

# Lines where I want just a trace of the more alert Puck or grounded Kore
# texture. This is style-vector blending, not audio mixing.
M_BLEND = {9: 0.08, 13: 0.06}
F_BLEND = {8: 0.06, 12: 0.06, 18: 0.05}


def phonemes(text):
    return lab.phonemize(g2p, text)


def pack_for(ps, role, idx, blend=False):
    if role == "M":
        pack = PACKS["onyx"]
        if blend and idx in M_BLEND:
            a = M_BLEND[idx]
            pack = pack * (1 - a) + PACKS["puck"] * a
    else:
        pack = PACKS["nova"]
        if blend and idx in F_BLEND:
            a = F_BLEND[idx]
            pack = pack * (1 - a) + PACKS["kore"] * a
    return pack[len(ps) - 1].detach().cpu().numpy()


def reshape_pitch(f0, semis=0.0, range_scale=1.0, final_fall=0.0):
    f0 = np.asarray(f0, np.float32).copy().ravel()
    voiced = f0 > 1e-3
    if voiced.any():
        mean_log = float(np.log(f0[voiced]).mean())
        f0[voiced] = np.exp(mean_log + (np.log(f0[voiced]) - mean_log) * range_scale)
        f0[voiced] *= 2.0 ** (semis / 12.0)

        if abs(final_fall) > 1e-6:
            start = int(len(f0) * 0.70)
            ramp = np.linspace(0.0, final_fall, len(f0) - start, dtype=np.float32)
            factor = 2.0 ** (ramp / 12.0)
            tail_voiced = f0[start:] > 1e-3
            tail = f0[start:]
            tail[tail_voiced] *= factor[tail_voiced]
            f0[start:] = tail
    return np.clip(f0, 0, 1000).astype(np.float32)


def internally_direct(ctx, spec):
    base_dur = ctx.pred_dur.detach().cpu().numpy().astype(np.int32).ravel()
    base_f0 = ctx.f0.detach().cpu().numpy().squeeze().astype(np.float32)
    base_n = ctx.n.detach().cpu().numpy().squeeze().astype(np.float32)

    new_dur = np.maximum(1, np.rint(base_dur * spec["dur"]).astype(np.int32))
    if not np.array_equal(new_dur, base_dur):
        f0 = lab.resample_by_dur(base_f0, base_dur, new_dur)
        n = lab.resample_by_dur(base_n, base_dur, new_dur)
    else:
        f0 = base_f0.copy()
        n = base_n.copy()

    f0 = reshape_pitch(f0, spec["pitch"], spec["range"], spec["fall"])
    n = np.maximum(0.0, n * spec["energy"]).astype(np.float32)
    return lab.decode_full(ctx, new_dur, f0, n).astype(np.float32)


def render_line(role, text, idx, directed=False, blend=False):
    ps = phonemes(text)
    ref = pack_for(ps, role, idx, blend=blend)
    audio, _, ctx = lab.synthesize(ps, ref, speed=1.0, trace=True)
    if directed:
        audio = internally_direct(ctx, DIRECT[idx])
    return np.asarray(audio, np.float32)


def mono_to_stereo(x, pan):
    x = np.asarray(x, np.float32)
    angle = (pan + 1.0) * math.pi / 4.0
    return np.column_stack((x * math.cos(angle), x * math.sin(angle))).astype(np.float32)


def silence(sec):
    return np.zeros((int(SR * sec), 2), np.float32)


def fade(x, ms=14):
    x = np.asarray(x, np.float32).copy()
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n > 1:
        f = np.linspace(0, 1, n, dtype=np.float32)[:, None]
        x[:n] *= f
        x[-n:] *= f[::-1]
    return x


def intro_sting():
    # Same simple musical identity as the earlier tests, but completely dry.
    dur = 1.55
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    y = np.zeros(n, dtype=np.float32)
    for i, f in enumerate((196.0, 246.94, 293.66)):
        env = np.clip((t - i * 0.14) / 0.16, 0, 1) * np.clip((dur - t) / 0.55, 0, 1)
        y += 0.040 * env * np.sin(2 * np.pi * f * t)
    return mono_to_stereo(y, 0)


def write_mp3(name, stereo):
    stereo = np.asarray(stereo, np.float32)
    peak = float(np.max(np.abs(stereo))) or 1.0
    if peak > 0.94:
        stereo *= 0.94 / peak
    wav = OUT / f"{name}.wav"
    mp3 = OUT / f"{name}.mp3"
    sf.write(wav, stereo, SR)
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)
    ], check=True)
    wav.unlink(missing_ok=True)
    print("rendered", mp3)


def scene(name, directed=False, blend=False):
    parts = [silence(0.35), intro_sting(), silence(0.20)]
    for idx, (role, text) in enumerate(TURNS):
        audio = render_line(role, text, idx, directed=directed, blend=blend)
        seg = fade(mono_to_stereo(audio, -0.16 if role == "F" else 0.16))
        parts += [silence(0.08), seg, silence(0.16)]
    write_mp3(name, np.concatenate(parts, axis=0))


def isolated(name, idx, directed=False, blend=False):
    role, text = TURNS[idx]
    audio = render_line(role, text, idx, directed=directed, blend=blend)
    stereo = fade(mono_to_stereo(audio, 0.0))
    write_mp3(name, np.concatenate([silence(0.18), stereo, silence(0.22)], axis=0))


scene("01_scene_baseline", directed=False, blend=False)
scene("02_scene_internal_prosody", directed=True, blend=False)
scene("03_scene_clean_style_blend", directed=False, blend=True)
scene("04_scene_prosody_plus_blend", directed=True, blend=True)

# Isolated actor tests. Hearing the same tiny line twice makes subtle changes
# easier to judge than asking the listener to remember a full minute.
for idx, label in [(1, "onyx_i_know"), (11, "onyx_no"), (13, "onyx_document"), (12, "nova_perfect"), (18, "nova_demon")]:
    isolated(f"line_{label}_baseline", idx, directed=False, blend=False)
    isolated(f"line_{label}_directed", idx, directed=True, blend=False)

print("internal prosody experiment complete")
