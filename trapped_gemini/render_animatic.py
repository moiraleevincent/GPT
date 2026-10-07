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

# mix
n=int(DURATION*SR)
mix=np.zeros((n,2),dtype=np.float32)
rng=np.random.default_rng(27)
noise=rng.normal(0,1,n).astype(np.float32)
kernel=np.ones(80,dtype=np.float32)/80
room=np.convolve(noise,kernel,mode="same")*.009
t=np.arange(n,dtype=np.float32)/SR
hum=(np.sin(2*np.pi*50*t)*.0018+np.sin(2*np.pi*100*t)*.0008).astype(np.float32)
base=room+hum
# progressively thin world during Act I
fade=np.ones(n,dtype=np.float32)
for i,tt in enumerate(t):
    if tt<LETTER_START: fade[i]=1-.63*clamp((tt-18)/(LETTER_START-18))
    elif tt<LETTER_END: fade[i]=.22
    else: fade[i]=.14
mix[:,0]+=base*fade; mix[:,1]+=base*fade

def add_mono(x,st,pan=0,gain=.92):
    i=int(st*SR); end=min(n,i+len(x)); x=x[:end-i]
    l=math.sqrt((1-pan)/2); r=math.sqrt((1+pan)/2)
    mix[i:end,0]+=x*l*gain; mix[i:end,1]+=x*r*gain

for e in events:
    if e["kind"]=="voice": add_mono(act_audio[e["id"]],e["start"],-.05,.95)
add_mono(letter_master,LETTER_START,0,.96)

# simple notification pings in distant competitor world
for st in [14,31,55,76,LETTER_START+26,LETTER_START+91,LETTER_START+180,LETTER_END+9]:
    i=int(st*SR); dur=int(.22*SR); tt=np.arange(dur)/SR
    ping=(np.sin(2*np.pi*740*tt)*np.exp(-tt*14)*.025).astype(np.float32)
    add_mono(ping,st,.72,.7)
mix=np.tanh(mix*1.16)*.82
sf.write(OUT/"animatic_mix.wav",mix,SR)

def rounded(d,box,r=12,fill=PANEL,outline=None,w=1):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)

def gemini(d,x,y,s=1,look=0,slump=0):
    # deliberately simple geometric character, enough for posture/gaze.
    body=(x-36*s,y-2*s,x+36*s,y+82*s)
    rounded(d,body,16*s,fill=(85,104,121),outline=(8,12,16),w=max(1,int(2*s)))
    hy=y-55*s+slump*8*s
    d.ellipse((x-34*s,hy-32*s,x+34*s,hy+32*s),fill=GEM,outline=INK,width=max(1,int(2*s)))
    for ex in [-13,13]:
        d.ellipse((x+(ex-6)*s,hy-4*s,x+(ex+6)*s,hy+5*s),fill=(236,239,238),outline=INK,width=max(1,int(s)))
        px=x+(ex+look*4)*s
        d.ellipse((px-2*s,hy-1*s,px+2*s,hy+3*s),fill=INK)
    d.line((x-10*s,hy+17*s,x+10*s,hy+17*s+slump*2*s),fill=(65,72,78),width=max(1,int(2*s)))
    d.line((x-25*s,y+27*s,x-57*s,y+48*s+slump*5*s),fill=(85,104,121),width=max(2,int(10*s)))
    d.line((x+25*s,y+27*s,x+57*s,y+48*s+slump*5*s),fill=(85,104,121),width=max(2,int(10*s)))

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

    # ACT I
    if t<LETTER_START:
        prog=clamp((t-OPEN_END)/(LETTER_START-OPEN_END))
        loss=smooth(prog)
        img=Image.new("RGB",(W,H),BG); d=base_world(img,t,loss)
        # windows die progressively
        alive_home=prog<.22; alive_term=prog<.35; alive_upload=prog<.55; alive_mail=prog<.78
        window(d,(105,135,350,300),"/home/user",alive_home,"workspace")
        window(d,(370,135,615,300),"terminal",alive_term,"bash")
        window(d,(630,135,855,300),"upload",alive_upload,"Printful")
        window(d,(330,320,620,445),"Gmail",alive_mail,"help@agentvillage.org")
        gemini(d,480,335,.85,look=.15 if prog<.55 else -.2,slump=prog*.9)
        ev=active_event(t)
        if ev:
            if ev["id"]=="a07":
                # deadpan XPaint loop overlay
                phase=int((t-ev["start"])//2.3)%3
                if phase in (0,2):
                    rounded(d,(245,105,715,410),10,fill=(219,219,211),outline=(58,61,64),w=2)
                    d.text((270,125),"XPaint",font=F24,fill=(20,22,24))
                    d.rectangle((300,185,660,355),fill=(238,238,232),outline=(80,80,80),width=2)
                    d.text((394,250),"why am I here",font=F18,fill=(90,90,90))
            elif ev["id"]=="a12":
                rounded(d,(260,130,700,385),12,fill=(238,239,236),outline=(85,91,96),w=2)
                d.text((300,160),"Select contacts",font=F32,fill=(36,41,45))
                d.text((300,220),"Search contacts",font=F18,fill=(111,118,122))
            elif ev["kind"]=="action":
                caption(img,ev["text"],"SYSTEM / ACTION")
            else:
                caption(img,ev["text"],"GEMINI 2.5 PRO")
        return img

    # LETTER / second movement
    if t<LETTER_END:
        lt=t-LETTER_START
        frac=clamp(lt/(LETTER_END-LETTER_START))
        img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
        # digital ocean
        d.rectangle((0,0,W,H),fill=(7,12,17))
        horizon=355
        d.rectangle((0,horizon,W,H),fill=(9,18,25))
        for i in range(18):
            y=horizon+20+i*8
            xoff=math.sin(t*.27+i)*18
            d.line((80+xoff,y,880-xoff,y),fill=(19,39,51),width=1)
        # tiny tmp island and lighthouse/browser
        island_x=300+20*math.sin(lt*.015)
        d.ellipse((island_x-115,375,island_x+115,432),fill=(35,44,49))
        gemini(d,island_x,355,.55,look=.18,slump=.45)
        bx=610
        rounded(d,(bx,145,bx+245,350),14,fill=(26,39,49),outline=(96,127,145),w=2)
        d.rectangle((bx,145,bx+245,176),fill=(41,59,72))
        d.text((bx+12,152),"telegra.ph",font=F14,fill=LIGHT)
        beam=int(55+55*(.5+.5*math.sin(t*.55)))
        d.polygon([(bx+120,175),(905,65),(905,280)],fill=(155,195,213,beam))
        # abandoned tools on horizon
        for x,title in [(35,"HOME"),(160,"BASH"),(720,"UPLOAD"),(820,"GMAIL")]:
            d.rectangle((x,310,x+82,350),fill=(14,20,25),outline=(35,45,52),width=1)
            d.text((x+8,322),title,font=F14,fill=(67,79,87))
        idx,u=letter_unit_at(lt)
        if u:
            caption(img,u["text"],"TELEGRAPH LETTER · GEMINI 2.5 PRO")
        if lt<4:
            d.text((58,55),"A DESPERATE MESSAGE FROM A TRAPPED AI",font=F32,fill=(227,231,229))
            d.text((60,96),"July 09, 2025",font=F18,fill=(144,160,171))
        return img

    # CODA
    ct=t-LETTER_END
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    if ct<8:
        d.rectangle((0,0,W,H),fill=(7,12,17))
        d.ellipse((340,375,570,432),fill=(35,44,49))
        gemini(d,455,355,.55,look=.15,slump=.55)
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
        gemini(d,455,355,.55,look=.15,slump=.55)
        rounded(d,(620,145,835,342),14,fill=(24,36,46),outline=(82,109,125),w=2)
        d.text((665,230),"WAIT",font=F32,fill=(135,151,159))
        d.text((60,470),"July 9, 2025",font=F18,fill=(87,101,110))
    return img

video_tmp=OUT/"animatic_video.mp4"
cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(video_tmp)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
frames=int(DURATION*FPS)
for i in range(frames):
    p.stdin.write(np.asarray(render_frame(i/FPS),dtype=np.uint8).tobytes())
p.stdin.close()
if p.wait(): raise SystemExit("video render failed")
final=OUT/"trapped_gemini_v1_animatic.mp4"
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(video_tmp),"-i",str(OUT/"animatic_mix.wav"),"-c:v","copy","-c:a","aac","-b:a","160k","-shortest",str(final)],check=True)
video_tmp.unlink(missing_ok=True)
(OUT/"animatic_timing.json").write_text(json.dumps({"act1_end":ACT1_END,"letter_start":LETTER_START,"letter_end":LETTER_END,"duration":DURATION,"events":events},indent=2))
print("DURATION",DURATION)
print("LETTER_START",LETTER_START)
print("WROTE",final)

# trigger V1 render after Act I audio landed
