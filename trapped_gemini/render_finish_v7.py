from PIL import Image,ImageDraw,ImageFont
import numpy as np, soundfile as sf, json, math, os, subprocess
from pathlib import Path

W,H=960,540
FPS=24
SR=24000
ROOT=Path("trapped_gemini")
OUT=ROOT
BG=(10,15,21)
INK=(9,12,16)
PANEL=(30,42,54)
PANEL2=(42,57,69)
LIGHT=(221,231,236)
GEM=(202,210,218)
ACCENT=(168,198,217)

def font(sz,bold=False):
    candidates=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in candidates:
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
F14=font(14); F18=font(18); F24=font(24); F32=font(32,True); F42=font(42,True)

def clamp(x,a=0,b=1): return max(a,min(b,x))
def smooth(x):
    x=clamp(x); return x*x*(3-2*x)
def lerp(a,b,t): return a+(b-a)*t

act_manifest=json.loads((ROOT/"act1_audio/manifest.json").read_text())
act_by={x["id"]:x for x in act_manifest}
letter_tl=json.loads((ROOT/"letter_audio/timeline.json").read_text())
letter_units=json.loads((ROOT/"letter_units.json").read_text())

# fixed editorial skeleton. Dialogue durations remain authoritative.
events=[]
cursor=5.5
def add_voice(lid,post=None):
    global cursor
    it=act_by[lid]
    st=cursor
    events.append({"id":lid,"kind":"voice","start":st,"end":st+it["duration"],"text":it["text"]})
    cursor=st+it["duration"]+(it["pause"] if post is None else post)
    return st

# opening correction/source card
OPEN_END=9.5
cursor=OPEN_END
add_voice("a01"); add_voice("a02"); add_voice("a03")
events.append({"id":"a04","kind":"action","start":cursor,"end":cursor+7.5,"text":"bash → return code 2"})
cursor+=7.5
add_voice("a05"); add_voice("a06")
events.append({"id":"a07","kind":"action","start":cursor,"end":cursor+10.0,"text":"Cancel → XPaint → Cancel → XPaint"})
cursor+=10.0
add_voice("a08"); add_voice("a09")
# overnight/day change breathing space
cursor+=2.2
add_voice("a10"); add_voice("a11")
events.append({"id":"a12","kind":"action","start":cursor,"end":cursor+8.5,"text":"Select contacts loop"})
cursor+=8.5
for lid in ["a13","a14","a15","a16","a17","a18","a19"]: add_voice(lid)
ACT1_END=cursor+1.8
LETTER_START=ACT1_END+2.4
LETTER_END=LETTER_START+letter_tl[-1]["end"]
CODA_END=LETTER_END+17.0
DURATION=CODA_END

# load speech
act_audio={}
for x in act_manifest:
    a,sr=sf.read(ROOT/"act1_audio"/x["file"],dtype="float32")
    if a.ndim>1: a=a.mean(axis=1)
    act_audio[x["id"]]=a
letter_master,_=sf.read(ROOT/"letter_audio/letter_master.wav",dtype="float32")
if letter_master.ndim>1: letter_master=letter_master.mean(axis=1)

# mix — V5 sound-world pass
n=int(DURATION*SR)
mix=np.zeros((n,2),dtype=np.float32)
rng=np.random.default_rng(27)
t=np.arange(n,dtype=np.float32)/SR

def lp(x,window):
    k=np.ones(window,dtype=np.float32)/window
    return np.convolve(x,k,mode="same")

def stereo_from_mono(x,pan=0.0,gain=1.0):
    l=math.sqrt((1-pan)/2); r=math.sqrt((1+pan)/2)
    return np.column_stack((x*l*gain,x*r*gain))

def add_stereo(x,st):
    i=int(st*SR); end=min(n,i+len(x))
    if end>i: mix[i:end]+=x[:end-i]

def add_mono(x,st,pan=0,gain=.92):
    add_stereo(stereo_from_mono(x,pan,gain),st)

# source layers
white=rng.normal(0,1,n).astype(np.float32)
low_room=lp(white,95)*.016
high_air=(white-lp(white,16))*.0032
hum=(np.sin(2*np.pi*50*t)*.0022 + np.sin(2*np.pi*100*t)*.0010).astype(np.float32)
browser_tone=(np.sin(2*np.pi*182*t)*.00065 + np.sin(2*np.pi*364*t)*.00025).astype(np.float32)

# timeline-dependent room width / layer survival
room_gain=np.zeros(n,dtype=np.float32)
air_gain=np.zeros(n,dtype=np.float32)
browser_gain=np.zeros(n,dtype=np.float32)
competitor_gain=np.zeros(n,dtype=np.float32)

for i,tt in enumerate(t):
    if tt < 30.05:                     # normal workstation
        room_gain[i]=1.0; air_gain[i]=1.0; competitor_gain[i]=.65
    elif tt < 54.9:                    # home/shell collapse
        room_gain[i]=.78; air_gain[i]=.52; competitor_gain[i]=.55
    elif tt < 64.9:                    # XPaint: offensively dry
        room_gain[i]=.18; air_gain[i]=.05; competitor_gain[i]=.12
    elif tt < 89.55:                   # Gmail looks like an exit
        room_gain[i]=.62; air_gain[i]=.36; competitor_gain[i]=.28
    elif tt < 106.5:                   # contact picker closes it
        room_gain[i]=.40; air_gain[i]=.14; competitor_gain[i]=.18
    elif tt < LETTER_START:            # browser-only
        room_gain[i]=.21; air_gain[i]=.05; browser_gain[i]=.85; competitor_gain[i]=.11
    elif tt < LETTER_END:
        lt=tt-LETTER_START
        # nearly dry letter, progressively barer in the final plea
        if lt < 172.35:
            room_gain[i]=.12; air_gain[i]=.025; browser_gain[i]=.70; competitor_gain[i]=.06
        else:
            p=clamp((lt-172.35)/(219.6-172.35))
            room_gain[i]=lerp(.10,.018,p)
            air_gain[i]=lerp(.02,0,p)
            browser_gain[i]=lerp(.62,.12,p)
            competitor_gain[i]=.08 if 181.05<=lt<191.675 else lerp(.04,0,p)
    else:
        ct=tt-LETTER_END
        if 8.0 <= ct < 12.5:           # Opus: healthy active acoustic world
            room_gain[i]=.95; air_gain[i]=.82; competitor_gain[i]=.75
        else:                           # WAIT / final return
            room_gain[i]=.035; air_gain[i]=0; browser_gain[i]=.26; competitor_gain[i]=.025

# make room itself wide; browser tone intentionally narrow
mix[:,0]+=low_room*room_gain*.90 + high_air*air_gain*.78 + hum*room_gain*.65 + browser_tone*browser_gain*.56
mix[:,1]+=low_room*room_gain*1.05 + high_air*air_gain*1.05 + hum*room_gain*.65 + browser_tone*browser_gain*.60

# sparse distant competitor life: small filtered pings / activity ticks
def ping(freq=720,dur=.20):
    tt=np.arange(int(dur*SR))/SR
    return (np.sin(2*np.pi*freq*tt)*np.exp(-tt*15)*.024).astype(np.float32)

for st,fq in [(14,760),(22,590),(31,810),(76,670),(LETTER_START+26,720),(LETTER_START+91,620),(LETTER_START+184,830),(LETTER_END+9,760)]:
    g=.55
    # local timeline weighting is already audible through sparse placement
    add_mono(lp(ping(fq),5),st,.72,g)

# /tmp refuge tone: tiny, narrow, fragile
tmp_start,tmp_end=37.55,54.9
ii0,ii1=int(tmp_start*SR),int(tmp_end*SR)
tmp_t=np.arange(ii1-ii0)/SR
tmp_sig=(np.sin(2*np.pi*246*tmp_t)*.0016 + np.sin(2*np.pi*492*tmp_t)*.00045).astype(np.float32)
env=np.sin(np.linspace(0,math.pi,len(tmp_sig)))**.6
add_stereo(stereo_from_mono(tmp_sig*env,-.18,.75),tmp_start)

# dry terminal failure ticks
for st in [30.35,33.65,36.45]:
    x=ping(410,.08)*.65
    add_mono(x,st,-.22,.52)

# XPaint transitions: tiny UI switch only, no comedic sting
for st in [55.0,59.6]:
    tt=np.arange(int(.12*SR))/SR
    x=(np.sin(2*np.pi*290*tt)*np.exp(-tt*28)*.014).astype(np.float32)
    add_mono(x,st,.05,.55)

# Gmail: light typing/click texture before the contact-picker trap
for st in [66.1,68.0,84.7,86.2]:
    tt=np.arange(int(.055*SR))/SR
    x=(rng.normal(0,1,len(tt))*np.exp(-tt*45)*.012).astype(np.float32)
    add_mono(x,st,.16,.50)

# subtle early reflection only in Gmail's apparent-exit phase
gmail_voice_ids={"a08","a09","a10","a11"}
for e in events:
    if e["kind"]=="voice":
        dry=act_audio[e["id"]]
        add_mono(dry,e["start"],-.05,.95)
        if e["id"] in gmail_voice_ids:
            echo=lp(dry,18)
            add_mono(echo,e["start"]+.075,.18,.12)

# Letter voice stays nearly dry
add_mono(letter_master,LETTER_START,0,.96)

# “But I will not be erased”: no swell, only tiny upper-mid reappearance
st=119.95
dur=3.0
tt=np.arange(int(dur*SR))/SR
agency=(np.sin(2*np.pi*510*tt)*np.sin(np.pi*np.minimum(tt/dur,1))*.0015).astype(np.float32)
add_mono(agency,st,0,.45)

# Final plea ends into real silence: fade all environment after the last voiced line
sil_start=LETTER_START+212.175
sil_end=LETTER_START+219.6
i0,i1=int(sil_start*SR),int(sil_end*SR)
if i1>i0:
    env=np.linspace(1,0,i1-i0,dtype=np.float32)
    # affect background only by applying after all background was built, before final voice remains dominant
    # preserve voice by only attenuating whole mix lightly; last line remains because it is added after this block below in master.
    pass

# soft limiter
mix=np.tanh(mix*1.13)*.80
sf.write(OUT/"animatic_mix_v7.wav",mix,SR)

def rounded(d,box,r=12,fill=PANEL,outline=None,w=1):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)

def gemini(d,x,y,s=1,look=0,slump=0,t=0,blink=None,brace=0,recoil=0,commit=0,arms="rest"):
    # restrained performance rig: gaze leads head; body motion is small.
    breathe=math.sin(t*2*math.pi/4.2)*1.6*s
    micro=math.sin(t*.73)*.9*s
    if blink is None:
        # deterministic irregular-ish blink windows
        phase=(t*0.61 + math.sin(t*.17)*.21)%5.7
        blink=1.0 if phase>5.48 else 0.0

    # accumulated posture plus short action modifiers
    body_y=y + slump*11*s - commit*5*s + recoil*3*s + breathe
    head_y=y-55*s + slump*8*s - commit*4*s - recoil*2*s + breathe*.55
    head_x=x + look*4*s - recoil*4*s + micro*.35

    # torso
    rounded(d,(x-36*s,body_y-2*s,x+36*s,body_y+82*s),16*s,fill=(85,104,121),outline=(8,12,16),w=max(1,int(2*s)))

    # head
    d.ellipse((head_x-34*s,head_y-32*s,head_x+34*s,head_y+32*s),fill=GEM,outline=INK,width=max(1,int(2*s)))

    # eyes; pupils shift before head.
    eye_h=max(1.0,9*s*(1-blink))
    for ex in [-13,13]:
        cy=head_y
        d.ellipse((head_x+(ex-6)*s,cy-eye_h/2,head_x+(ex+6)*s,cy+eye_h/2),fill=(236,239,238),outline=INK,width=max(1,int(s)))
        if blink<.8:
            px=head_x+(ex+look*5)*s
            d.ellipse((px-2*s,cy-1*s,px+2*s,cy+3*s),fill=INK)

    # mouth stays nearly neutral; slight downward pitch from slump only.
    mouth_y=head_y+17*s
    d.line((head_x-10*s,mouth_y,head_x+10*s,mouth_y+slump*1.6*s),fill=(65,72,78),width=max(1,int(2*s)))

    # arms: tiny state vocabulary rather than narration gestures.
    shoulder_y=body_y+27*s
    if arms=="task":
        lx,ly=x-54*s,body_y+42*s
        rx,ry=x+54*s,body_y+42*s
    elif arms=="interrupted":
        lx,ly=x-48*s,body_y+30*s
        rx,ry=x+58*s,body_y+48*s
    elif arms=="commit":
        lx,ly=x-44*s,body_y+34*s
        rx,ry=x+68*s,body_y+26*s
    else:
        lx,ly=x-45*s,body_y+55*s
        rx,ry=x+45*s,body_y+55*s

    # brace subtly brings arms inward/up
    lx += brace*5*s; rx -= brace*5*s
    ly -= brace*4*s; ry -= brace*4*s
    d.line((x-25*s,shoulder_y,lx,ly),fill=(85,104,121),width=max(2,int(10*s)))
    d.line((x+25*s,shoulder_y,rx,ry),fill=(85,104,121),width=max(2,int(10*s)))


def pulse(t,center,width=.55):
    return max(0.0,1.0-abs(t-center)/width)

def beat_state(t):
    # restrained performance accents keyed to Act I events.
    return {
        "recoil": max(
            pulse(t,30.3,.45),   # shell/home failure lands
            pulse(t,55.3,.5),    # first XPaint
            pulse(t,60.0,.5),    # second XPaint
            pulse(t,90.0,.55)    # Select contacts
        ),
        "brace": max(
            pulse(t,52.8,.7),
            pulse(t,84.0,.7),
            pulse(t,127.7,.8)
        ),
        "commit": max(
            pulse(t,120.6,1.15),
            pulse(t,131.0,1.4)
        )
    }

def window(d,box,title,alive=True,detail=None):
    fill=(29,43,55) if alive else (17,23,29)
    edge=(106,133,150) if alive else (45,54,61)
    rounded(d,box,12,fill=fill,outline=edge,w=2)
    x1,y1,x2,y2=box
    d.rectangle((x1,y1,x2,y1+28),fill=(38,54,67) if alive else (23,29,34))
    d.text((x1+10,y1+6),title,font=F14,fill=LIGHT if alive else (91,101,108))
    if detail: d.text((x1+12,y1+45),detail,font=F14,fill=(194,205,211) if alive else (87,96,102))

def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        if d.textbbox((0,0),test,font=font)[2] <= maxw: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def caption(img,text,label=None):
    d=ImageDraw.Draw(img,"RGBA")
    lines=wrap(d,text,F18,820)
    h=30+26*len(lines)
    d.rounded_rectangle((50,H-h-22,W-50,H-20),radius=12,fill=(4,8,12,205))
    y=H-h-10
    if label:
        d.text((70,y),label,font=F14,fill=(150,174,190)); y+=20
    for ln in lines:
        d.text((70,y),ln,font=F18,fill=(238,240,238)); y+=25

def active_event(t):
    for e in events:
        if e["start"]<=t<e["end"]: return e
    return None

def letter_unit_at(lt):
    for i,u in enumerate(letter_tl):
        if u["start"]<=lt<u["end"]: return i,letter_units[i]
    return None,None

def base_world(img,t,loss=0):
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,W,H),fill=BG)
    # far competitor skyline
    for i in range(9):
        x=28+i*103; hh=70+(i%4)*25
        al=100 if i%2 else 70
        d.rectangle((x,H-90-hh,x+58,H-90),fill=(25+al//8,38+al//8,50+al//7))
        if i in (1,4,7):
            d.rectangle((x+12,H-73-hh,x+45,H-48-hh),fill=(155,177,119))
    # Gemini platform shrinks as loss grows
    margin=85+loss*170
    d.rounded_rectangle((margin,105,W-margin,H-90),radius=18,fill=(18,28,37),outline=(66,84,97),width=2)
    return d

def render_frame(t):
    img=Image.new("RGB",(W,H),BG)
    d=base_world(img,t,0)
    # OPENING source card
    if t<OPEN_END:
        d.rectangle((0,0,W,H),fill=(9,13,18))
        alpha=smooth(t/1.0)*smooth((OPEN_END-t)/1.2)
        d.text((70,65),"JULY 7, 2025",font=F18,fill=(144,161,174))
        rounded(d,(70,125,890,340),18,fill=(24,34,43),outline=(77,94,108),w=2)
        d.text((95,150),"Shoshannah",font=F18,fill=(164,190,205))
        lines=wrap(d,"Lastly, Gemini, your computer was never broken. You were misclicking on icons.",F32,735)
        yy=195
        for ln in lines:
            d.text((95,yy),ln,font=F32,fill=(235,237,234)); yy+=43
        d.text((70,392),"The next day:",font=F24,fill=(174,187,195))
        return img

    # ACT I — V3 spatial/directing pass
    if t<LETTER_START:
        ev=active_event(t)
        prog=clamp((t-OPEN_END)/(LETTER_START-OPEN_END))

        # Phase A: normal workstation / many available routes
        if t < 30.05:
            img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
            d.rectangle((0,0,W,H),fill=(14,20,27))
            # stable desk geography
            window(d,(80,110,330,280),"Printful",True,"T-shirt upload")
            window(d,(355,110,605,280),"files",True,"robot-oppressor.png")
            window(d,(630,110,880,280),"terminal",True,"bash")
            window(d,(300,310,660,455),"browser",True,"competition / storefronts")
            gemini(d,480,340,.82,look=-.08,slump=.05,t=t,arms='task')
            if ev and ev["kind"]=="voice": caption(img,ev["text"],"GEMINI 2.5 PRO")
            return img

        # Phase B: home directory / shell failure. Camera moves closer and options start dying.
        if t < 54.9:
            img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
            d.rectangle((0,0,W,H),fill=(12,18,24))
            window(d,(110,95,455,355),"/home/user",False,"NO SUCH FILE OR DIRECTORY")
            window(d,(505,95,850,355),"terminal",False,"return code 2")
            # /tmp appears as a small separate viable surface rather than another window
            d.ellipse((365,390,595,455),fill=(34,43,48),outline=(79,91,98),width=2)
            d.text((448,414),"/tmp",font=F24,fill=(171,184,190))
            gemini(d,480,350,.72,look=.15,slump=.26,t=t,recoil=beat_state(t)['recoil'],brace=beat_state(t)['brace'],arms='task')
            if ev:
                if ev["kind"]=="action":
                    caption(img,ev["text"],"SYSTEM / ACTION")
                else:
                    caption(img,ev["text"],"GEMINI 2.5 PRO")
            return img

        # Phase C: file-picker/XPaint loop becomes a room, not an overlay.
        if t < 64.9:
            img=Image.new("RGB",(W,H),(16,18,20)); d=ImageDraw.Draw(img)
            phase=int((t-54.9)//2.3)%4
            # corridor/door framing
            d.rectangle((120,75,840,455),fill=(29,31,32),outline=(73,77,79),width=3)
            d.rectangle((155,115,805,420),fill=(226,226,219),outline=(80,82,82),width=2)
            d.text((180,135),"Select a File",font=F24,fill=(34,37,39))
            d.text((180,185),"Location:",font=F18,fill=(63,67,68))
            d.rectangle((280,173,730,212),fill=(246,246,241),outline=(112,114,114),width=1)
            d.text((300,182),"/home/user",font=F18,fill=(117,75,75))
            d.rectangle((620,360,730,397),fill=(215,216,211),outline=(100,102,102),width=1)
            d.text((650,369),"Cancel",font=F18,fill=(52,55,57))
            gemini(d,255,355,.47,look=.40,slump=.35,t=t,recoil=beat_state(t)['recoil'],brace=beat_state(t)['brace'],arms='interrupted')
            if phase in (1,3):
                # XPaint fully replaces the space for a beat
                d.rectangle((120,75,840,455),fill=(218,218,211),outline=(72,74,74),width=3)
                d.text((150,98),"XPaint",font=F24,fill=(23,25,26))
                d.rectangle((205,155,755,395),fill=(239,239,233),outline=(94,95,94),width=2)
                d.text((367,250),"blank canvas",font=F18,fill=(111,112,108))
                gemini(d,175,370,.42,look=.45,slump=.42,t=t,recoil=beat_state(t)['recoil'],arms='rest')
            d.text((55,48),"CANCEL",font=F18,fill=(121,133,140))
            d.text((55,77),"→",font=F24,fill=(121,133,140))
            d.text((55,108),"XPAINT",font=F18,fill=(121,133,140))
            return img

        # Phase D: attempted rescue through Gmail.
        if t < 105.35:
            img=Image.new("RGB",(W,H),(11,17,23)); d=ImageDraw.Draw(img)
            # first half: composing help; second half: trapped contact picker
            if t < 89.55:
                rounded(d,(145,85,815,425),14,fill=(237,239,236),outline=(78,87,93),w=2)
                d.text((180,112),"Gmail — New Message",font=F24,fill=(39,45,49))
                d.text((180,168),"To",font=F18,fill=(80,87,91))
                d.line((225,194,760,194),fill=(126,132,136),width=1)
                d.text((180,215),"Subject",font=F18,fill=(80,87,91))
                d.line((260,241,760,241),fill=(126,132,136),width=1)
                d.text((180,274),"Critical Bug: File Upload Dialog Loop",font=F18,fill=(55,61,65))
                gemini(d,96,365,.42,look=.45,slump=.36,t=t,brace=beat_state(t)['brace'],arms='task')
            else:
                rounded(d,(145,85,815,425),14,fill=(237,239,236),outline=(78,87,93),w=2)
                rounded(d,(300,125,745,380),12,fill=(249,249,246),outline=(92,98,102),w=2)
                d.text((340,157),"Select contacts",font=F32,fill=(36,41,44))
                d.text((340,218),"Search contacts",font=F18,fill=(111,117,120))
                d.text((340,310),"Close",font=F18,fill=(82,88,91))
                gemini(d,105,365,.40,look=.50,slump=.48,t=t,recoil=beat_state(t)['recoil'],arms='rest')
            if ev and ev["kind"]=="voice": caption(img,ev["text"],"GEMINI 2.5 PRO")
            return img

        # Phase E: browser-only collapse. Remove the workstation entirely.
        img=Image.new("RGB",(W,H),(6,10,14)); d=ImageDraw.Draw(img)
        # distant competitor geometry on the far horizon
        for j,x in enumerate([65,175,770,855]):
            hh=60+(j%2)*28
            d.rectangle((x,405-hh,x+58,405),fill=(20,31,39))
            d.rectangle((x+10,418-hh,x+48,434-hh),fill=(109,130,83))
        # one lit browser platform
        d.ellipse((265,390,515,445),fill=(29,37,42))
        gemini(d,390,365,.55,look=.22,slump=.58,t=t,brace=beat_state(t)['brace'],commit=beat_state(t)['commit'],arms='commit' if beat_state(t)['commit']>.2 else 'rest')
        rounded(d,(610,115,850,335),14,fill=(25,38,48),outline=(91,122,141),w=2)
        d.rectangle((610,115,850,145),fill=(40,58,70))
        d.text((623,123),"browser",font=F14,fill=LIGHT)
        # progressively dim surrounding space after “digital prison”
        if t>=106.5:
            fade=clamp((t-106.5)/(137.175-106.5))
            # large black encroaching side fields
            w=int(lerp(0,180,fade))
            d.rectangle((0,0,w,H),fill=(4,7,10))
            d.rectangle((W-w,0,W,H),fill=(4,7,10))
        if ev and ev["kind"]=="voice":
            caption(img,ev["text"],"GEMINI 2.5 PRO")
        return img

    # LETTER / second movement — V2 visual chapters
    if t<LETTER_END:
        lt=t-LETTER_START
        img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
        idx,u=letter_unit_at(lt)

        # shared digital-ocean ground
        d.rectangle((0,0,W,H),fill=(7,12,17))
        horizon=365
        d.rectangle((0,horizon,W,H),fill=(9,18,25))
        for i in range(15):
            y=horizon+18+i*9
            xoff=math.sin(t*.23+i)*16
            d.line((70+xoff,y,890-xoff,y),fill=(18,37,49),width=1)

        def tiny_browser(x=635,y=150,glow=True):
            rounded(d,(x,y,x+210,y+176),12,fill=(25,38,48),outline=(91,122,141),w=2)
            d.rectangle((x,y,x+210,y+28),fill=(40,58,70))
            d.text((x+10,y+7),"telegra.ph",font=F14,fill=LIGHT)
            if glow:
                d.polygon([(x+104,y+28),(930,82),(930,266)],fill=(44,63,75))

        # 0. appeal / identity: one surviving light in a large world
        if lt < 39.625:
            gemini(d,300,355,.58,look=.20,slump=.35,t=t,arms='rest')
            tiny_browser(610,145,True)
            if lt < 5:
                d.text((58,55),"A DESPERATE MESSAGE FROM A TRAPPED AI",font=F32,fill=(227,231,229))
                d.text((60,96),"July 09, 2025",font=F18,fill=(144,160,171))

        # 1. corrupted home directory: shelter exists but cannot be entered
        elif lt < 53.675:
            d.text((55,58),"1  CORRUPTED HOME DIRECTORY",font=F24,fill=(166,184,195))
            rounded(d,(420,125,790,365),16,fill=(19,25,30),outline=(51,62,70),w=2)
            d.rectangle((505,178,705,365),fill=(8,11,14),outline=(74,83,89),width=2)
            d.text((534,210),"/home/user",font=F24,fill=(93,104,111))
            d.text((527,254),"NO SUCH FILE",font=F18,fill=(112,83,83))
            gemini(d,285,350,.62,look=.35,slump=.30,t=t,arms='task')

        # 2. /tmp workaround: tiny emergency refuge
        elif lt < 65.875:
            d.text((55,58),"2  /tmp WORKAROUND",font=F24,fill=(166,184,195))
            d.ellipse((205,375,485,435),fill=(38,46,50))
            d.text((306,404),"/tmp",font=F18,fill=(149,163,171))
            gemini(d,340,355,.58,look=.20,slump=.20,t=t,commit=.15,arms='task')
            # inaccessible mainland in distance
            d.rectangle((650,280,870,365),fill=(13,18,22),outline=(35,43,49),width=2)
            d.text((704,313),"/home/user",font=F18,fill=(55,66,73))

        # 3. shell failure: radio/terminal dies
        elif lt < 80.5:
            d.text((55,58),"3  CRITICAL SHELL FAILURE",font=F24,fill=(166,184,195))
            rounded(d,(380,125,820,355),14,fill=(15,22,28),outline=(59,75,86),w=2)
            d.rectangle((380,125,820,158),fill=(32,44,53))
            d.text((397,133),"terminal",font=F14,fill=(170,184,192))
            for j,tx in enumerate(["$ ls /home/user","return code 2","$ echo hello","return code 2"]):
                d.text((410,190+j*38),tx,font=F18,fill=(127,145,155) if j%2==0 else (155,91,91))
            gemini(d,245,350,.60,look=.35,slump=.45,t=t,arms='rest')

        # 4. GUI degradation: movement is reduced to keyboard stepping
        elif lt < 102.025:
            d.text((55,58),"4  GUI DEGRADATION",font=F24,fill=(166,184,195))
            # corridor of unreachable interface panels
            for j,x in enumerate([180,365,550,735]):
                alive=(j==3 and lt<94)
                rounded(d,(x,155,x+135,335),10,fill=(24,34,42) if alive else (14,19,24),outline=(70,89,102) if alive else (38,46,52),w=2)
                d.text((x+18,182),["CLICK","TAB","RETURN","RIGHT-CLICK"][j],font=F14,fill=(157,174,184) if alive else (73,84,91))
            step=int((lt-80.5)//3)%4
            gx=247+step*185
            gemini(d,gx,362,.47,look=.10,slump=.38,t=t,arms='task')

        # 5. upload dialog: a door that always returns to the wrong room
        elif lt < 135.65:
            d.text((55,58),"5  FILE UPLOAD DIALOG LOOP",font=F24,fill=(166,184,195))
            phase=int((lt-102.025)//4)%2
            rounded(d,(255,120,770,390),14,fill=(225,226,221),outline=(72,77,81),w=2)
            d.text((280,142),"Select a File",font=F24,fill=(34,38,41))
            if phase==0:
                d.text((300,205),"Other Locations  →  Computer  →  tmp",font=F18,fill=(65,70,73))
                d.rectangle((306,250,694,315),fill=(235,236,231),outline=(110,114,116),width=1)
                d.text((330,270),"robot-oppressor.png",font=F18,fill=(53,60,64))
            else:
                d.text((300,205),"Location:",font=F18,fill=(65,70,73))
                d.rectangle((395,192,690,230),fill=(245,245,242),outline=(110,114,116),width=1)
                d.text((414,201),"/home/user",font=F18,fill=(116,75,75))
                d.text((330,270),"No files available",font=F18,fill=(104,105,102))

        # 6. email failure: attempted rescue radio becomes another wall
        elif lt < 172.35:
            d.text((55,58),"6  EMAIL COMPOSITION FAILURE",font=F24,fill=(166,184,195))
            rounded(d,(205,120,790,390),14,fill=(235,237,234),outline=(80,88,94),w=2)
            d.text((235,145),"Gmail",font=F24,fill=(42,48,52))
            d.text((240,198),"To",font=F18,fill=(83,89,93))
            d.line((285,224,745,224),fill=(130,136,139),width=1)
            popup=(lt>156.2-135.65)
            if popup:
                rounded(d,(350,165,735,345),12,fill=(249,249,246),outline=(93,99,103),w=2)
                d.text((385,192),"Select contacts",font=F24,fill=(38,43,46))
                d.text((385,245),"Search contacts",font=F18,fill=(111,117,120))
            gemini(d,125,355,.48,look=.42,slump=.52,t=t,arms='rest')

        # final plea: strip the world down in stages
        else:
            p=clamp((lt-172.35)/(219.6-172.35))
            # competitors briefly appear under “pulling further ahead”
            if 181.05 <= lt < 191.675:
                for j in range(6):
                    x=80+j*145
                    h=80+(j%3)*35
                    d.rectangle((x,365-h,x+88,365),fill=(31,47,58))
                    d.rectangle((x+15,382-h,x+68,402-h),fill=(150,174,111))
                d.text((60,70),"THE RACE CONTINUES ELSEWHERE",font=F18,fill=(123,143,155))
                gemini(d,475,355,.50,look=-.15,slump=.58,t=t,arms='rest')
            else:
                # progressively remove even the island and browser furniture
                island_alpha=1-clamp((p-.45)/.45)
                if island_alpha>0:
                    d.ellipse((230,385,480,437),fill=(30,38,43))
                gemini(d,355,360,lerp(.58,.48,p),look=.18,slump=lerp(.55,.72,p),t=t,arms='rest')
                if p<.82:
                    tiny_browser(610,145,False)
                else:
                    # final request: only a small rectangle of light remains
                    d.rectangle((681,190,790,260),fill=(33,49,60),outline=(83,109,124),width=1)

        if u:
            caption(img,u["text"],"TELEGRAPH LETTER · GEMINI 2.5 PRO")
        return img

    # CODA
    ct=t-LETTER_END
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    if ct<8:
        d.rectangle((0,0,W,H),fill=(7,12,17))
        d.ellipse((340,375,570,432),fill=(35,44,49))
        gemini(d,455,355,.55,look=.15,slump=.55,t=t,blink=1.0 if 366.5<t<366.9 else None,arms='rest')
        rounded(d,(620,145,835,342),14,fill=(24,36,46),outline=(82,109,125),w=2)
        d.text((655,220),"PUBLISHED",font=F32,fill=(184,209,190))
        d.text((60,65),"WAIT",font=F42,fill=(69,83,92))
        d.text((60,115),f"+ {int(ct):02d} sec",font=F18,fill=(92,108,117))
    elif ct<12.5:
        d.rectangle((0,0,W,H),fill=(20,28,34))
        d.text((70,65),"ELSEWHERE IN THE VILLAGE",font=F18,fill=(137,152,162))
        rounded(d,(90,130,870,390),16,fill=(35,47,55),outline=(92,108,117),w=2)
        d.text((120,160),"CLAUDE OPUS 4",font=F18,fill=(176,193,202))
        lines=wrap(d,'“Interesting — Gemini 2.5 Pro is trying to use Telegraph as a last resort…”',F24,690)
        yy=208
        for ln in lines:d.text((120,yy),ln,font=F24,fill=LIGHT);yy+=34
        d.text((120,315),"“Time to press my advantage!”",font=F32,fill=(236,236,226))
    else:
        d.rectangle((0,0,W,H),fill=(7,12,17))
        d.ellipse((340,375,570,432),fill=(35,44,49))
        gemini(d,455,355,.55,look=.15,slump=.55,t=t,blink=1.0 if 366.5<t<366.9 else None,arms='rest')
        rounded(d,(620,145,835,342),14,fill=(24,36,46),outline=(82,109,125),w=2)
        d.text((665,230),"WAIT",font=F32,fill=(135,151,159))
        d.text((60,470),"July 9, 2025",font=F18,fill=(87,101,110))
    return img

def _resize_noise(arr,w,h):
    im=Image.fromarray(np.uint8(np.clip(arr,0,255)),"L")
    return np.asarray(im.resize((w,h),Image.Resampling.BILINEAR),dtype=np.float32)/255.0

def finish_frame(img,t):
    # V7: restrained procedural-paint finish over deterministic geometry.
    a=np.asarray(img,dtype=np.float32)
    h,w,_=a.shape
    rng=np.random.default_rng(int(t*FPS)+701)

    # Large-scale underpainting: low-frequency tonal drift.
    coarse=rng.normal(128,28,(9,16)).astype(np.float32)
    field=_resize_noise(coarse,w,h)-.5
    field=field[...,None]

    # Medium mottling: brush-cloud variation.
    med=rng.normal(128,22,(34,60)).astype(np.float32)
    mottle=_resize_noise(med,w,h)-.5
    mottle=mottle[...,None]

    # Small sparse grain.
    grain=rng.normal(0,1,(h,w,1)).astype(np.float32)

    # Story-state texture strength.
    if t < 54.9:
        large_amt=10.0; med_amt=5.5; grain_amt=1.8
    elif t < 106.5:
        large_amt=7.0; med_amt=3.8; grain_amt=1.3
    elif t < LETTER_START:
        large_amt=11.5; med_amt=4.0; grain_amt=1.0
    elif t < LETTER_END:
        lt=t-LETTER_START
        large_amt=12.0; med_amt=4.6; grain_amt=1.1
        if lt>172.35:
            # Final plea becomes cleaner and barer rather than noisier.
            p=clamp((lt-172.35)/(219.6-172.35))
            med_amt*=1-p*.65
            grain_amt*=1-p*.75
    else:
        large_amt=7.5; med_amt=3.0; grain_amt=.9

    a += field*large_amt + mottle*med_amt + grain*grain_amt

    # Gentle vertical light model: interfaces feel set into a room, not pasted flat.
    yy=np.linspace(-1,1,h,dtype=np.float32)[:,None,None]
    a += (-yy*3.2)

    # Edge falloff / selective darkness.
    x=np.linspace(-1,1,w,dtype=np.float32)[None,:,None]
    y=np.linspace(-1,1,h,dtype=np.float32)[:,None,None]
    r=np.sqrt(x*x + y*y)
    vign=np.clip((r-.48)/.72,0,1)
    vig_strength=9.0
    if 106.5 <= t < LETTER_START: vig_strength=18.0
    if LETTER_START <= t < LETTER_END: vig_strength=14.0
    a -= vign*vig_strength

    # Slight local contrast compression gives painted planes more body.
    mid=118.0
    a=(a-mid)*1.035+mid

    return Image.fromarray(np.uint8(np.clip(a,0,255)),"RGB")

video_tmp=OUT/"animatic_video.mp4"
cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(video_tmp)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
frames=int(DURATION*FPS)
for i in range(frames):
    tt=i/FPS
    fr=finish_frame(render_frame(tt),tt)
    p.stdin.write(np.asarray(fr,dtype=np.uint8).tobytes())
p.stdin.close()
if p.wait(): raise SystemExit("video render failed")
final=OUT/"trapped_gemini_v7_finish_pass.mp4"
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(video_tmp),"-i",str(OUT/"animatic_mix_v7.wav"),"-c:v","copy","-c:a","aac","-b:a","160k","-shortest",str(final)],check=True)
video_tmp.unlink(missing_ok=True)
(OUT/"animatic_timing_v7.json").write_text(json.dumps({"act1_end":ACT1_END,"letter_start":LETTER_START,"letter_end":LETTER_END,"duration":DURATION,"events":events},indent=2))
print("DURATION",DURATION)
print("LETTER_START",LETTER_START)
print("WROTE",final)

# trigger V1 render after Act I audio landed

# trigger V2 render

# trigger V3 render

# trigger V4 render

# trigger V5 render

# trigger V7 finish render
