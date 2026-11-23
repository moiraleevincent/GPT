"""Re-render the original Mara SVG film as an MP4 with real Kokoro dialogue.
The picture edit, narration cues, music notes and sound effects preserve v1.
"""
from pathlib import Path
import subprocess, time, random
import numpy as np
from scipy import signal as sig
import soundfile as sf
from playwright.sync_api import sync_playwright

ROOT=Path("mara_kokoro_revoice")
SR=24000
DURATION=34.0
FPS=16
N=int(DURATION*SR)
rng=np.random.default_rng(17)
mix=np.zeros(N, dtype=np.float32)
def add(t,signal,gain=1.):
    st=int(t*SR)
    if st>=N:return
    signal=np.asarray(signal,dtype=np.float32)*gain
    a=max(st,0); count=min(N-a,len(signal)-max(0,-st))
    if count>0:mix[a:a+count]+=signal[max(0,-st):max(0,-st)+count]
def tone(freq,seconds,amp=.1,kind='brass',decay=.9):
    n=int(seconds*SR);x=np.arange(n)/SR
    if kind=='brass':
        y=np.sin(2*np.pi*freq*x)+.33*np.sin(4*np.pi*freq*x)+.18*np.sin(6*np.pi*freq*x)+.09*np.sin(8*np.pi*freq*x)
        env=np.minimum(1,x/.022)*np.minimum(1,(seconds-x)/.09)*np.exp(-x/decay)
    elif kind=='plucky':
        y=np.sin(2*np.pi*freq*x)+.3*np.sin(4*np.pi*freq*x)
        env=np.minimum(1,x/.009)*np.exp(-x/(seconds*.37))
    elif kind=='bass':
        y=np.sin(2*np.pi*freq*x)+.3*np.sin(4*np.pi*freq*x)
        env=np.minimum(1,x/.015)*np.exp(-x/(seconds*.85))
    else:
        y=np.sin(2*np.pi*freq*x)
        env=np.minimum(1,x/.01)*np.minimum(1,(seconds-x)/.08)*np.exp(-x/decay)
    return (amp*y*env).astype(np.float32)
def midi(m):return 440*2**((m-69)/12)
beat=.53
chords=[(48,55,60,63),(44,51,56,60),(51,58,63,67),(43,50,55,59)]
for bar in range(16):
    root,ch2,ch3,ch4=chords[bar%4]
    base=bar*beat*4
    for j in range(4):
        add(base+j*beat,tone(midi(root-12 if j%2==0 else root-5),.34,.11,'bass'))
        add(base+j*beat+.265,tone(midi(ch2),.17,.045,'plucky'))
    seq=[ch3,ch4,ch3,ch2] if bar%2==0 else [ch2,ch3,ch4,ch3]
    for j,m in enumerate(seq):
        add(base+j*beat+.05,tone(midi(m+12),beat*.6,.048 if bar<7 else .071,'brass',.4))
    for j in range(4):
        t=base+j*beat
        n=int(.07*SR);x=np.arange(n)/SR
        add(t,rng.standard_normal(n)*np.exp(-x*70),.045)
        if j in (1,3):add(t,tone(155,.09,.05,'plucky'))
for ts,pitch in [(31.3,67),(31.55,72),(31.8,76),(32.2,79),(32.85,72)]:
    add(ts,tone(midi(pitch),.72,.14,'brass',.6))
def chirp(t,f0,f1,length,amp=.16):
    x=np.arange(int(length*SR))/SR
    ff=f0+(f1-f0)*(x/length)
    ph=np.cumsum(ff)*2*np.pi/SR
    env=np.sin(np.pi*np.minimum(1,x/length))**2
    add(t,amp*np.sin(ph)*env)
for t in (7.55,8.3,9.05,9.75):
    chirp(t,390,690,.36,.12)
    chirp(t+.38,690,420,.34,.12)
for t in np.arange(3.2,7.1,.53):
    x=np.arange(int(.04*SR))/SR
    add(t,.10*np.sin(2*np.pi*1450*x)*np.exp(-x*135))
for t in (12.1,24.5):
    chirp(t,480,620,.22,.12)
    chirp(t+.18,620,260,.38,.15)
x=np.arange(int(.85*SR))/SR
ww=sig.lfilter([1],[1,-.95],rng.standard_normal(len(x)))
ww=ww/(np.max(np.abs(ww))+1e-10)
add(18.6,ww*np.sin(np.pi*x/.85)**2,.26)
for t in np.arange(19.8,22.45,.12):
    pitch=rng.uniform(900,2100)
    chirp(float(t),pitch,pitch*1.4,.16,.055)
chirp(21.48,110,1600,.48,.23)
x=np.arange(int(.25*SR))/SR
pop=(rng.standard_normal(len(x))*.19+np.sin(2*np.pi*(200-140*x/.25)*x)*.65)*np.exp(-x*24)
add(21.55,pop,.39)
for p in (659,880,1318):add(25.3,tone(p,1.18,.09,'pure',1))
x=np.arange(int(.48*SR))/SR
scratch=rng.standard_normal(len(x))*.7+np.sin(2*np.pi*(2000-1600*x/.48)*x)
add(27.75,scratch*np.sin(np.pi*x/.48)**2,.13)
for k,p in enumerate((392,370,349,330)):
    add(28.3+k*.28,tone(p,.32,.075,'plucky'))
# Narration always dominates the score; duck music and effects beneath each line.
import json
lines=json.loads((ROOT/"manifest.json").read_text())
duck=np.ones(N,dtype=np.float32)*.58
for item in lines:
    start=float(item["start"]);end=start+float(item["duration"])
    a=max(0,int((start-.12)*SR));b=min(N,int((end+.10)*SR))
    lo=max(0,int((start-.28)*SR))
    hi=min(N,int((end+.30)*SR))
    if lo<a:duck[lo:a]=np.minimum(duck[lo:a],np.linspace(.58,.27,a-lo,dtype=np.float32))
    duck[a:b]=np.minimum(duck[a:b],.27)
    if b<hi:duck[b:hi]=np.minimum(duck[b:hi],np.linspace(.27,.58,hi-b,dtype=np.float32))
mix*=duck
voice,rate=sf.read(ROOT/"voices_only.wav",dtype="float32")
if voice.ndim==2:voice=voice.mean(axis=1)
assert rate==SR and len(voice)==N,(rate,len(voice),N)
mix+=voice
env=np.ones(N,dtype=np.float32)
env[:int(.38*SR)]=np.linspace(0,1,int(.38*SR))
env[-int(.5*SR):]=np.linspace(1,0,int(.5*SR))
mix*=env
peak=float(np.max(np.abs(mix)))
if peak>.97:mix*=.97/peak
sf.write(ROOT/"master_mix.wav",mix,SR)
print("Audio master ready:",len(mix)/SR,"sec, peak",peak,flush=True)
# Reuse exactly the original SVG/JS picture animation, without image generation.
visual=ROOT/"movie_silent.mp4"
command=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","image2pipe",
         "-framerate",str(FPS),"-vcodec","mjpeg","-i","-","-an","-c:v","libx264",
         "-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",
         "-threads","4",str(visual)]
proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
started=time.monotonic()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
    page=browser.new_page(viewport={"width":960,"height":540},device_scale_factor=1)
    page.set_content((ROOT/"movie.html").read_text(),wait_until="load")
    for f in range(round(DURATION*FPS)):
        page.evaluate("(t)=>window.setFrame(t)", f/FPS)
        jpg=page.screenshot(type="jpeg",quality=88,animations="disabled")
        proc.stdin.write(jpg)
        if f%100==0:print(f"Rendered {f} frames in {round(time.monotonic()-started,1)}s",flush=True)
    browser.close()
proc.stdin.close()
err=proc.stderr.read().decode()
code=proc.wait()
if code:raise RuntimeError(err)
out=ROOT/"mara_the_key_to_almost_everything_kokoro.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(visual),
                "-i",str(ROOT/"master_mix.wav"),"-c:v","copy","-c:a","aac","-b:a","160k",
                "-shortest","-movflags","+faststart",str(out)],check=True)
print("VIDEO SUCCESS:",out,out.stat().st_size,flush=True)
