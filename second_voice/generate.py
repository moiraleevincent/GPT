from pathlib import Path
import json, math, os, subprocess

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from kokoro import KPipeline

ROOT = Path(__file__).parent
SR = 24000
FPS = 24
W, H = 960, 540
DURATION = 56.5

LINES = [
    {"id":"m01","speaker":"MARA","voice":"af_nicole","speed":0.96,"text":"Floor eight. West corridor. Six doors. All clear.","start":3.0},
    {"id":"b01","speaker":"BUILDING","voice":"am_michael","speed":0.90,"text":"Seven.","start":8.1},
    {"id":"m02","speaker":"MARA","voice":"af_nicole","speed":0.94,"text":"There are six.","start":10.3},
    {"id":"b02","speaker":"BUILDING","voice":"am_michael","speed":0.90,"text":"There were.","start":12.9},
    {"id":"f01","speaker":"RECORDER","voice":"af_nicole","speed":0.92,"text":"Don't open it.","start":18.7},
    {"id":"m03","speaker":"MARA","voice":"af_nicole","speed":0.96,"text":"I didn't say that.","start":21.9},
    {"id":"b03","speaker":"BUILDING","voice":"am_michael","speed":0.88,"text":"Not yet.","start":24.3},
    {"id":"m04","speaker":"MARA","voice":"af_nicole","speed":0.96,"text":"What is this?","start":27.2},
    {"id":"b04","speaker":"BUILDING","voice":"am_michael","speed":0.88,"text":"A rehearsal.","start":29.6},
    {"id":"m05","speaker":"MARA","voice":"af_nicole","speed":0.96,"text":"For what?","start":32.2},
    {"id":"f02","speaker":"RECORDER","voice":"af_nicole","speed":0.90,"text":"For leaving.","start":34.2},
    {"id":"m06","speaker":"MARA","voice":"af_nicole","speed":0.92,"text":"No.","start":39.4},
    {"id":"b05","speaker":"BUILDING","voice":"am_michael","speed":0.88,"text":"Good.","start":41.5},
    {"id":"b06","speaker":"BUILDING","voice":"am_michael","speed":0.90,"text":"Again tomorrow?","start":46.3},
    {"id":"m07","speaker":"MARA","voice":"af_nicole","speed":0.90,"text":"No.","start":49.5},
    {"id":"b07","speaker":"BUILDING","voice":"am_michael","speed":0.86,"text":"Good.","start":51.3},
]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * clamp(x))


def lerp(a, b, t):
    return a + (b - a) * t


def font(size, bold=False):
    options = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in options:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_SMALL = font(17)
F_SUB = font(27, True)
F_TITLE = font(52, True)
F_MONO = font(22, True)


def render_tts():
    pipeline = KPipeline(lang_code="a")
    voices = {}
    manifest = []
    audio = {}
    fade = int(SR * 0.025)

    for item in LINES:
        voice_name = item["voice"]
        if voice_name not in voices:
            voices[voice_name] = pipeline.load_voice(voice_name)
        chunks = []
        for _, _, chunk in pipeline(item["text"], voice=voices[voice_name], speed=item["speed"]):
            if hasattr(chunk, "detach"):
                chunk = chunk.detach().cpu().numpy()
            chunks.append(np.asarray(chunk, dtype=np.float32))
        x = np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)
        if len(x) > fade * 2:
            ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
            x[:fade] *= ramp
            x[-fade:] *= ramp[::-1]
        path = ROOT / f"{item['id']}.wav"
        sf.write(path, x, SR)
        audio[item["id"]] = x
        rec = dict(item)
        rec["file"] = path.name
        rec["duration"] = round(len(x) / SR, 4)
        manifest.append(rec)

    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest, audio


def stereo(mono, pan=0.0, gain=1.0):
    p = clamp(pan, -1.0, 1.0)
    left = math.sqrt((1.0 - p) / 2.0)
    right = math.sqrt((1.0 + p) / 2.0)
    return np.column_stack([mono * left * gain, mono * right * gain]).astype(np.float32)


def lowpass(x, taps=11):
    if taps <= 1:
        return x.copy()
    kernel = np.ones(taps, dtype=np.float32) / taps
    return np.convolve(x, kernel, mode="same").astype(np.float32)


def wall_voice(x):
    y = lowpass(x, 13) * 0.83
    delay = int(SR * 0.070)
    out = y.copy()
    if len(y) > delay:
        out[delay:] += y[:-delay] * 0.20
    return np.tanh(out * 1.15).astype(np.float32)


def recorder_voice(x):
    y = lowpass(x, 7)
    body = lowpass(y, 95)
    y = (y - body * 0.55) * 0.95
    return np.tanh(y * 1.4).astype(np.float32)


def add_tone(mix, start, duration, freq, amp, pan=0.0):
    i0 = int(start * SR)
    n = min(int(duration * SR), len(mix) - i0)
    if n <= 0:
        return
    tt = np.arange(n, dtype=np.float32) / SR
    env = np.exp(-tt * 4.0).astype(np.float32)
    tone = (np.sin(2 * np.pi * freq * tt) * env * amp).astype(np.float32)
    mix[i0:i0+n] += stereo(tone, pan, 1.0)


def build_mix(manifest, audio):
    n = int(DURATION * SR)
    tt = np.arange(n, dtype=np.float32) / SR
    rng = np.random.default_rng(22)
    raw = rng.normal(0.0, 1.0, n).astype(np.float32)
    air = lowpass(raw, 31) * 0.018
    hum = (np.sin(2*np.pi*60*tt) * 0.0032 + np.sin(2*np.pi*120*tt) * 0.0011).astype(np.float32)
    mix = stereo(air + hum, 0.0, 1.0)

    # A barely audible elevator motor that wakes up before the impossible door becomes obvious.
    motor_env = np.clip((tt - 11.5) / 4.0, 0, 1) * np.clip((19.0 - tt) / 3.0, 0, 1)
    motor = (np.sin(2*np.pi*34*tt) + 0.32*np.sin(2*np.pi*68*tt)) * motor_env * 0.006
    mix += stereo(motor.astype(np.float32), 0.25, 1.0)

    byid = {m["id"]: m for m in manifest}
    for item in manifest:
        x = audio[item["id"]]
        if item["speaker"] == "BUILDING":
            x = wall_voice(x)
            pan, gain = 0.38, 0.90
        elif item["speaker"] == "RECORDER":
            x = recorder_voice(x)
            pan, gain = -0.28, 0.82
        else:
            pan, gain = -0.10, 0.92
        a = stereo(x, pan, gain)
        i = int(item["start"] * SR)
        j = min(n, i + len(a))
        mix[i:j] += a[:j-i]

    # Elevator bell, recorder chirps, door latch, fluorescent relays.
    add_tone(mix, 15.65, 0.55, 932, 0.022, 0.25)
    add_tone(mix, 18.35, 0.18, 1680, 0.030, -0.30)
    add_tone(mix, 34.0, 0.16, 1680, 0.024, -0.30)
    add_tone(mix, 38.15, 0.34, 176, 0.025, 0.35)
    for s in [52.2, 52.8, 53.4, 54.0, 54.6, 55.2]:
        add_tone(mix, s, 0.09, 88, 0.018, 0.0)

    mix = np.tanh(mix * 1.18) * 0.84
    sf.write(ROOT / "second_voice_mix.wav", mix, SR)
    return byid


# ---- visual system ---------------------------------------------------------
BG = (12, 16, 21)
WALL = (31, 38, 44)
WALL2 = (23, 29, 35)
FLOOR = (18, 22, 27)
LINE = (79, 91, 98)
LIGHT = (219, 227, 220)
SKIN = (176, 148, 132)
COAT = (40, 46, 53)
HAIR = (24, 21, 22)
RED = (191, 55, 48)
INK = (7, 9, 12)


def door7_amount(t):
    return smooth((t - 12.9) / 3.3)


def lights_remaining(t):
    if t < 52.0:
        return 1.0
    return clamp(1.0 - (t - 52.0) / 3.8)


def draw_corridor(img, t, mara_depth=0.20, close=False):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, H), fill=BG)
    vx, vy = (598, 224)
    d.polygon([(0,0),(W,0),(vx,vy),(0,176)], fill=(20,25,30,255))
    d.polygon([(0,H),(W,H),(vx,vy),(0,374)], fill=FLOOR + (255,))
    d.polygon([(0,176),(vx,vy),(vx,410),(0,374)], fill=WALL + (255,))
    d.polygon([(W,0),(vx,vy),(vx,410),(W,H)], fill=WALL2 + (255,))
    d.rectangle((vx-96, vy-68, vx+96, 410), fill=(29,35,40,255), outline=LINE+(190,), width=3)

    # fluorescent strips recede toward the vanishing point
    remaining = lights_remaining(t)
    for i in range(7):
        z = i / 7
        x = int(lerp(168, vx-22, z))
        y = int(lerp(54, vy-22, z))
        ww = int(lerp(180, 32, z))
        hh = max(4, int(lerp(16, 4, z)))
        on = remaining > (i / 7.0) or t < 52.0
        fill = (235,240,228,205 if on else 18)
        d.rounded_rectangle((x-ww//2, y-hh//2, x+ww//2, y+hh//2), radius=3, fill=fill)

    # six ordinary doors, three each side.
    left_doors = [(92,214,186,391),(250,224,322,386),(386,231,440,379)]
    right_doors = [(828,174,955,462),(746,196,821,438),(681,211,729,421)]
    for box in left_doors + right_doors:
        d.rectangle(box, fill=(28,34,39,255), outline=LINE+(180,), width=2)
        x0,y0,x1,y1 = box
        d.ellipse((x1-18, (y0+y1)//2-3, x1-12, (y0+y1)//2+3), fill=(139,126,96,220))

    # The seventh door is on the dead end. It starts as only a seam.
    a = door7_amount(t)
    if a > 0:
        x0,y0,x1,y1 = vx-48, vy+2, vx+48, 410
        d.rectangle((x0,y0,x1,y1), fill=(20,25,30,int(210*a)), outline=(112,123,127,int(230*a)), width=2)
        d.line((x0,y0,x0,y1), fill=(145,151,151,int(130*a)), width=1)
        d.ellipse((x1-18,318,x1-9,327), fill=(158,139,99,int(235*a)))
        if a > 0.55:
            d.text((vx-10,242), "7", font=F_SMALL, fill=(142,150,151,int(180*a)))

    # floor reflections / perspective guides
    for x in [140,330,515,705,885]:
        d.line((x,H,vx,410), fill=(98,110,116,35), width=1)
    d.line((0,374,vx,410,W,H), fill=(110,122,126,55), width=2)

    draw_mara(d, t, mara_depth, close=close)


def draw_mara(d, t, depth, close=False):
    # depth 0 = foreground, 1 = vanishing point
    s = lerp(1.0, 0.36, clamp(depth))
    x = lerp(345, 555, depth)
    y = lerp(304, 350, depth)
    if close:
        s *= 1.55
        x, y = 440, 350
    walk = math.sin(t * 7.4) * (1.0 if 14.2 < t < 18.1 else 0.0)
    bob = abs(math.sin(t * 7.4)) * 3.0 * s if 14.2 < t < 18.1 else 0.0
    y += bob
    d.ellipse((x-35*s,y+118*s,x+36*s,y+132*s), fill=(4,6,8,80))
    d.rounded_rectangle((x-48*s,y,x+48*s,y+113*s), radius=19*s, fill=COAT, outline=INK, width=max(1,int(2*s)))
    d.line((x-27*s,y+104*s,x-35*s+walk*4*s,y+160*s), fill=COAT, width=max(4,int(14*s)))
    d.line((x+27*s,y+104*s,x+35*s-walk*4*s,y+160*s), fill=COAT, width=max(4,int(14*s)))
    d.rectangle((x-11*s,y-19*s,x+11*s,y+8*s), fill=SKIN)
    d.ellipse((x-32*s,y-82*s,x+32*s,y-18*s), fill=SKIN, outline=INK, width=max(1,int(2*s)))
    d.pieslice((x-35*s,y-87*s,x+36*s,y-16*s), 176, 360, fill=HAIR)
    d.polygon([(x-34*s,y-53*s),(x-30*s,y-88*s),(x+10*s,y-91*s),(x+34*s,y-62*s),(x+22*s,y-77*s),(x-5*s,y-67*s)], fill=HAIR)
    # eyes are tiny until the close shot
    if close:
        look = 5 if t < 39 else -4
        for ex in [x-12*s, x+12*s]:
            d.ellipse((ex-5*s,y-51*s,ex+5*s,y-45*s), fill=(225,220,208))
            d.ellipse((ex-1.8*s+look,y-50*s,ex+1.8*s+look,y-46*s), fill=INK)
        d.line((x-9*s,y-28*s,x+8*s,y-29*s), fill=(92,58,55), width=max(1,int(2*s)))
    # recorder in left hand
    handx, handy = x-62*s, y+52*s
    d.line((x-36*s,y+40*s,handx,handy), fill=COAT, width=max(4,int(13*s)))
    d.rounded_rectangle((handx-9*s,handy-15*s,handx+11*s,handy+25*s), radius=3*s, fill=(19,23,27), outline=(105,113,116), width=max(1,int(s)))
    d.ellipse((handx-3*s,handy-9*s,handx+3*s,handy-3*s), fill=RED)


def draw_speaker(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0,0,W,H), fill=(22,27,32,255))
    # oblique wall seams
    for x in range(-80, W+140, 180):
        d.line((x,0,x+170,H), fill=(68,77,82,65), width=2)
    cx, cy = 565, 248
    d.ellipse((cx-104,cy-104,cx+104,cy+104), fill=(30,35,39), outline=(96,105,109), width=4)
    for r in [24,43,62,82]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(102,110,112,110), width=2)
    for yy in range(cy-70,cy+71,18):
        for xx in range(cx-70,cx+71,18):
            if (xx-cx)**2+(yy-cy)**2 < 72**2:
                d.ellipse((xx-2,yy-2,xx+2,yy+2), fill=(9,11,13,170))
    pulse = 0.45 + 0.55 * math.sin(t*10)**2
    d.ellipse((cx-6,cy+126,cx+6,cy+138), fill=(RED[0],RED[1],RED[2],int(110+100*pulse)))


def draw_recorder(img, t, phrase=None):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0,0,W,H), fill=(11,14,18,255))
    # hand and recorder close-up
    d.polygon([(90,430),(250,225),(415,255),(380,540),(0,540)], fill=(57,48,45,255))
    d.rounded_rectangle((300,72,708,486), radius=32, fill=(25,30,34), outline=(118,126,128), width=4)
    d.rectangle((344,122,664,312), fill=(7,13,14), outline=(68,84,84), width=3)
    d.ellipse((625,92,646,113), fill=RED)
    # waveform: future voice appears as a solid white line before it should exist
    base = 224
    for x in range(360,648,6):
        q = (x-360)/288
        amp = (math.sin(q*48 + t*2.2) * 0.5 + math.sin(q*19)*0.5) * 34
        d.line((x,base-amp,x,base+amp), fill=(155,200,184,170), width=2)
    if phrase:
        box = d.textbbox((0,0),phrase,font=F_MONO)
        tw = box[2]-box[0]
        d.text((504-tw/2,336), phrase, font=F_MONO, fill=(223,230,221))
    d.text((366,146), "00:00:18", font=F_SMALL, fill=(128,153,143))
    d.text((530,146), "REC", font=F_SMALL, fill=(199,72,64))


def draw_door_close(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0,0,W,H), fill=(13,17,21,255))
    d.rectangle((155,-20,845,570), fill=(29,35,40), outline=(100,111,116), width=5)
    d.line((184,0,184,H), fill=(77,87,92), width=2)
    d.text((472,58), "7", font=F_TITLE, fill=(130,140,143))
    turn = smooth((t-37.4)/1.4) * (1.0-smooth((t-39.2)/1.2))
    hx, hy = 723, 298
    d.ellipse((hx-24,hy-24,hx+24,hy+24), fill=(133,117,79), outline=(38,33,25), width=3)
    angle = -12 + 52*turn
    dx = math.cos(math.radians(angle))*92
    dy = math.sin(math.radians(angle))*92
    d.line((hx,hy,hx-dx,hy-dy), fill=(171,151,103), width=13)
    d.ellipse((hx-dx-8,hy-dy-8,hx-dx+8,hy-dy+8), fill=(104,91,63))
    # Mara's shadow enters frame but she never touches the handle.
    d.ellipse((-120,104,275,650), fill=(2,4,6,145))


def subtitle(img, t, manifest):
    active = None
    for item in manifest:
        if item["start"] <= t < item["start"] + item["duration"]:
            active = item
            break
    if not active:
        return
    d = ImageDraw.Draw(img, "RGBA")
    label = active["speaker"]
    text = active["text"]
    box = d.textbbox((0,0),text,font=F_SUB)
    tw, th = box[2]-box[0], box[3]-box[1]
    x, y = (W-tw)//2, H-62
    d.rounded_rectangle((x-18,y-10,x+tw+18,y+th+11), radius=8, fill=(4,6,8,188))
    d.text((x,y), text, font=F_SUB, fill=(238,239,233))
    d.text((x,y-24), label, font=F_SMALL, fill=(186,194,193,220))


def title_card(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    if 0.45 < t < 2.65:
        a = int(255 * min(smooth((t-.45)/.7), smooth((2.65-t)/.55)))
        txt = "SECOND VOICE"
        box = d.textbbox((0,0),txt,font=F_TITLE)
        tw = box[2]-box[0]
        d.text(((W-tw)//2,92), txt, font=F_TITLE, fill=(229,232,226,a))
        sub = "a short film"
        box2 = d.textbbox((0,0),sub,font=F_SMALL)
        d.text(((W-(box2[2]-box2[0]))//2,151), sub, font=F_SMALL, fill=(170,179,178,a))


def render_frame(t, manifest):
    img = Image.new("RGB", (W,H), BG)
    if t < 7.55:
        draw_corridor(img,t,mara_depth=0.12)
        title_card(img,t)
    elif t < 9.85:
        draw_speaker(img,t)
    elif t < 14.45:
        draw_corridor(img,t,mara_depth=0.16,close=(t>9.8))
    elif t < 18.25:
        dep = lerp(0.17,0.69,ease((t-14.45)/3.8))
        draw_corridor(img,t,mara_depth=dep)
    elif t < 21.55:
        draw_recorder(img,t,"DON'T OPEN IT")
    elif t < 25.75:
        draw_corridor(img,t,mara_depth=0.36,close=True)
    elif t < 32.0:
        # split attention between the impossible door and Mara.
        draw_corridor(img,t,mara_depth=0.56)
        d=ImageDraw.Draw(img,"RGBA")
        d.rectangle((760,0,W,H), fill=(5,7,10,70))
    elif t < 37.15:
        phrase = "FOR LEAVING" if t > 33.8 else None
        draw_recorder(img,t,phrase)
    elif t < 43.95:
        draw_door_close(img,t)
    elif t < 52.45:
        # Mara retreats. The camera does not follow her quite fast enough.
        dep = lerp(0.63,0.13,ease((t-43.95)/8.5))
        draw_corridor(img,t,mara_depth=dep)
    else:
        draw_corridor(img,t,mara_depth=-0.02)
        d=ImageDraw.Draw(img,"RGBA")
        darkness = smooth((t-55.0)/1.2)
        d.rectangle((0,0,W,H), fill=(0,0,0,int(245*darkness)))
        if t > 55.4:
            a=int(235*smooth((t-55.4)/.55))
            txt="END OF SWEEP"
            b=d.textbbox((0,0),txt,font=F_SMALL)
            d.text(((W-(b[2]-b[0]))//2,H//2),txt,font=F_SMALL,fill=(210,215,210,a))
    subtitle(img,t,manifest)
    return img


def encode_video(manifest):
    out = ROOT / "second_voice.mp4"
    cmd = [
        "ffmpeg","-y","-hide_banner","-loglevel","error",
        "-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24",
        "-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-i",str(ROOT/"second_voice_mix.wav"),
        "-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(out)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames = int(DURATION * FPS)
    try:
        for i in range(frames):
            frame = render_frame(i/FPS, manifest)
            proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
    finally:
        if proc.stdin:
            proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {rc}")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest, audio = render_tts()
    build_mix(manifest, audio)
    encode_video(manifest)
    print("Rendered", ROOT / "second_voice.mp4")


if __name__ == "__main__":
    main()
