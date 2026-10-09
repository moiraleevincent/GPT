"""FERN'S PERFORMANCE REVIEW
Original 2D workplace mockumentary film (not footage from any television show).
Script, animation, character rigs, synthetic voices and sound designed for this project.
Run: python office_fern_performance_review/render.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import numpy as np
import soundfile as sf
import math, os, bisect, subprocess

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(parents=True, exist_ok=True)
W, H, FPS, SR = 960, 540, 20, 24000
FINAL = ROOT / "fern_performance_review.mp4"

SCENES = [
    dict(shot="wide", secs=2.25, note="establish"),
    dict(shot="mae", who="MAE", line="We need to talk about Fern.", pause=0.55),
    dict(shot="jonah", who="JONAH", line="Fern is a plant.", pause=0.62),
    dict(shot="mae", who="MAE", line="Fern has failed to meet a single growth target this quarter.", pause=0.55),
    dict(shot="plant", secs=1.48, note="Fern"),
    dict(shot="interview_jonah", who="JONAH", line="I handle accounts. Mae handles operations. Fern photosynthesizes. Somehow Fern is the only one of us with a performance improvement plan.", pause=0.7),
    dict(shot="wide", who="MAE", line="You can't manage what you don't measure.", pause=0.42),
    dict(shot="jonah", who="JONAH", line="Her job is to sit next to the window.", pause=0.44),
    dict(shot="mae", who="MAE", line="And yet she has demonstrated more resilience than the entire analytics team.", pause=0.54),
    dict(shot="reaction", secs=1.36, note="camera glance"),
    dict(shot="interview_mae", who="MAE", line="Good managers identify potential. Even when that potential is... leafy.", pause=0.56),
    dict(shot="document", secs=1.9, note="improvement plan"),
    dict(shot="wide", who="MAE", line="After careful consideration, I've decided to promote Fern.", pause=0.45),
    dict(shot="jonah", who="JONAH", line="To what?", pause=0.47),
    dict(shot="mae", who="MAE", line="Interim head of culture.", pause=0.50),
    dict(shot="jonah", who="JONAH", line="Does that make her my manager?", pause=0.56),
    dict(shot="mae", who="MAE", line="Temporarily.", pause=0.55),
    dict(shot="wide", secs=2.0, note="silence"),
    dict(shot="wide", who="JONAH", line="Fern, can I take Friday off?", pause=0.45),
    dict(shot="plant_punch", secs=2.4, note="plant interview"),
    dict(shot="mae", who="MAE", line="She's not taking questions.", pause=0.60),
    dict(shot="reaction", secs=2.65, note="hard stare"),
    dict(shot="end", secs=2.1, note="end card"),
]

def fonts(size, bold=False):
    name = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(name, size) if os.path.isfile(name) else ImageFont.load_default()

F10, F14, F16, F20, F22, F28, F34, F48 = [fonts(x, x>=20) for x in (10,14,16,20,22,28,34,48)]
def clamp(v,a=0.0,b=1.0): return max(a, min(b, v))
def ease(x): x=clamp(x); return x*x*(3-2*x)
def lerp(a,b,t): return a+(b-a)*t

# Generate one isolated synthetic performance per line and preserve the timing.
from kokoro import KPipeline
pipe=KPipeline(lang_code="a")
mae_voice = .55*pipe.load_voice("af_nova") + .45*pipe.load_voice("af_kore")
jonah_voice = pipe.load_voice("am_michael")
voices={"MAE":mae_voice, "JONAH":jonah_voice}
speech=[]
for i,s in enumerate(SCENES):
    if "line" not in s:
        s["secs"] = float(s["secs"])
        continue
    voice = voices[s["who"]]
    speed = 1.02 if s["who"]=="MAE" else .99
    chunks=[]
    for _,_,part in pipe(s["line"], voice=voice, speed=speed):
        a=part.detach().cpu().numpy() if hasattr(part,"detach") else np.asarray(part)
        chunks.append(np.asarray(a, dtype=np.float32))
    if not chunks:
        raise RuntimeError("Kokoro produced no speech for "+s["line"])
    a=np.concatenate(chunks)
    fa=min(240,len(a)//2)
    a[:fa] *= np.linspace(0,1,fa,dtype=np.float32)
    a[-fa:] *= np.linspace(1,0,fa,dtype=np.float32)
    s["audio"]=a
    s["speech_offset"]=0.22
    s["secs"]=len(a)/SR+float(s.get("pause",0.50))+.24

starts=[]; elapsed=0.
for s in SCENES:
    s["start"]=elapsed
    starts.append(elapsed)
    elapsed+=s["secs"]
DURATION=elapsed
print(f"Generating {len(SCENES)} scenes / {DURATION:.1f} seconds",flush=True)

# Studio audio. Avoid copying an existing program's music cues.
n=int(DURATION*SR)+SR
rng=np.random.default_rng(20261009)
noise=rng.normal(0,1,n).astype(np.float32)
# low office ventilation; no atmosphere loudly competing with dialogue
noise=np.convolve(noise,np.ones(41,dtype=np.float32)/41,mode="same")
mix=np.column_stack((noise*.007, noise*.007)).astype(np.float32)
t0=np.arange(n,dtype=np.float32)/SR
hum=(.0012*np.sin(2*np.pi*57*t0)).astype(np.float32)
mix[:,0]+=hum;mix[:,1]+=hum

def add_mono(y,start,pan=0,gain=1.):
    pos=max(0,int(start*SR)); m=min(len(y),n-pos)
    if m<=0: return
    l=math.sqrt((1-clamp(pan,-1,1))/2); r=math.sqrt((1+clamp(pan,-1,1))/2)
    mix[pos:pos+m,0]+=y[:m]*gain*l
    mix[pos:pos+m,1]+=y[:m]*gain*r

def beep(start,f=780,length=.09,vol=.018):
    k=int(SR*length); tt=np.arange(k,dtype=np.float32)/SR
    x=(np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/length)**2*vol).astype(np.float32)
    add_mono(x,start,pan=.65)

for s in SCENES:
    if "audio" in s:
        add_mono(s["audio"],s["start"]+s["speech_offset"],pan=-.15 if s["who"]=="MAE" else .16,gain=.92)
    if s.get("note")=="improvement plan": beep(s["start"]+.45,870,.08,.019)
    if s.get("note")=="silence": beep(s["start"]+1.0,520,.055,.009)
# One very short, original two-note plucked tag at the end.
at=SCENES[-1]["start"]+.18
for i,hz in enumerate([349.23,523.25]):
    k=int(.55*SR); tt=np.arange(k,dtype=np.float32)/SR
    wave=(np.sin(2*np.pi*hz*tt)+.22*np.sin(4*np.pi*hz*tt))*np.exp(-7*tt)*.018
    add_mono(wave.astype(np.float32),at+i*.20,.0)
mix=np.tanh(mix*1.05)*.92
WAV=ROOT/"_scratch_mix.wav"
sf.write(WAV,mix,SR)

# --- Cinematography and character art ---
BG="#b9b8ad"
INK="#273137"
def txt(draw, xy, message, font=F16, color=INK, anchor=None):
    draw.text(xy,message,font=font,fill=color,anchor=anchor,stroke_width=0)

def shadow(draw, bbox, radius, opacity=40):
    x0,y0,x1,y1=bbox
    draw.ellipse((x0,y0+radius*.3,x1,y1+radius*.3),fill=(28,33,37,opacity))

def office_bg(im,t):
    d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((0,0,W,H),fill="#b9b9b0")
    d.rectangle((0,0,W,142),fill="#c5c7be")
    d.polygon([(0,145),(960,145),(960,166),(0,159)],fill="#989f99")
    d.rectangle((0,444,W,H),fill="#6a746f")
    for x in range(0,960,96):
        d.line((x,458,x-68,540),fill=(215,219,213,21),width=2)
    # fluorescents with flat light and hard office geometry
    for x in [92,550]:
        d.rounded_rectangle((x,30,x+282,47),radius=3,fill="#f3ede0",outline="#969f9c",width=2)
    # window / blinds
    d.rectangle((53,82,274,339),fill="#556c72",outline="#e0ddd4",width=11)
    d.rectangle((64,93,263,328),fill="#8cabb0")
    for x,hh in [(73,100),(125,138),(172,124),(215,151)]:
        d.rectangle((x,hh+111,x+23,329),fill="#6d8990")
        for yy in range(hh+129,325,25): d.rectangle((x+5,yy,x+18,yy+7),fill=(238,224,188,62))
    for yy in range(106,321,18):
        d.line((65,yy,261,yy+5),fill=(241,240,229,102),width=4)
    # wall elements
    d.rectangle((690,102,933,312),fill="#e9e8df",outline="#788585",width=7)
    txt(d,(712,123),"TEAM CULTURE",F22)
    d.line((713,156,908,156),fill="#8e9d9a",width=2)
    for i,label in enumerate(["Listening", "Growth", "Alignment"]):
        d.ellipse((710,174+i*35,719,183+i*35),fill="#547b73")
        txt(d,(732,171+i*35),label,F16)
    d.rectangle((738,321,883,345),fill="#d4c7b0")
    txt(d,(746,325),"MEETING ROOM  B",F14)
    # paper-filled printer at far right
    d.rounded_rectangle((782,368,947,452),radius=8,fill="#5a6466",outline="#2d383d",width=3)
    d.rectangle((798,347,926,395),fill="#d4d4cb",outline="#4d5756",width=2)
    d.rectangle((812,404,897,428),fill="#c4d0c9")
    d.ellipse((903,412,915,423),fill="#91d3b3")
    # table / flat foreground desk
    d.rounded_rectangle((90,440,750,530),radius=7,fill="#9c8e79",outline="#5a5b50",width=4)
    d.rectangle((99,448,739,461),fill="#b6a58b")
    d.rounded_rectangle((126,419,196,460),radius=4,fill="#627171",outline="#39474b",width=3)
    d.ellipse((165,418,196,437),outline="#39474b",width=4)
    d.rounded_rectangle((300,427,410,458),radius=3,fill="#f5f0dc",outline="#8f8c80")
    d.line((316,436,391,436),fill="#9a9990",width=2)
    d.line((316,443,380,443),fill="#9a9990",width=2)
    d.rounded_rectangle((591,425,618,448),radius=3,fill="#252d2d")
    # continuing micro movement (air conditioning line shadow)
    d.rectangle((0,0,W,H),outline=(12,20,23,10),width=6)

def interview_bg(im,t):
    d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((0,0,W,H),fill="#87948e")
    d.rectangle((0,0,310,H),fill="#758985")
    d.rectangle((55,75,258,394),fill="#536e74",outline="#d0d3c7",width=11)
    for yy in range(102,380,21): d.line((66,yy,246,yy+4),fill=(218,220,204,114),width=5)
    d.rectangle((312,0,328,H),fill="#647770")
    d.rectangle((635,115,905,391),fill="#d0d0c4",outline="#67746e",width=7)
    txt(d,(666,146),"VALUES",F28)
    for j,a in enumerate(["OWNERSHIP","MOMENTUM","GROWTH"]):
        d.ellipse((666,210+j*49,677,221+j*49),fill="#4c8274")
        txt(d,(696,207+j*49),a,F16)
    d.rectangle((0,437,W,H),fill="#475953")
    d.rounded_rectangle((310,420,655,560),radius=20,fill="#525d5b")

def person(d,x,y,who,t,scale=1.,speaking=0.,camera=False,emotion="neutral"):
    # x and y mark upper torso starting point
    s=scale
    if who=="MAE":
        skin="#945d49"; skin_sh="#754838"; hair="#222a2d"; garment="#b86945"; under="#273944"
        hairline="#232a2d"; eye="#2e2524"; ear="#d2a35b"
    else:
        skin="#cfa486"; skin_sh="#b88a6d"; hair="#343131"; garment="#6f8273"; under="#e1d9c6"
        hairline="#342b2b"; eye="#312d2d"; ear="#cfa486"
    bob=math.sin(t*1.4+(0 if who=="MAE" else 1.4))*(1.6 if speaking>.18 else .55)*s
    x=float(x);y=float(y)+bob
    # body silhouette
    d.ellipse((x-97*s,y-2*s,x+96*s,y+285*s),fill="#32413e")
    d.rounded_rectangle((x-86*s,y-11*s,x+87*s,y+245*s),radius=int(31*s),fill=garment)
    d.polygon([(x-37*s,y+5*s),(x,y+60*s),(x+37*s,y+5*s)],fill=under)
    if who=="MAE":
        d.polygon([(x-62*s,y+1*s),(x-14*s,y+57*s),(x-31*s,y+95*s),(x-76*s,y+24*s)],fill="#d58b62")
        d.polygon([(x+63*s,y+1*s),(x+14*s,y+57*s),(x+31*s,y+95*s),(x+76*s,y+24*s)],fill="#d58b62")
        d.line((x,y+63*s,x,y+245*s),fill="#824a37",width=max(1,int(3*s)))
        d.ellipse((x-4*s,y+118*s,x+4*s,y+126*s),fill="#e4bd78")
        d.ellipse((x-4*s,y+159*s,x+4*s,y+167*s),fill="#e4bd78")
    else:
        d.polygon([(x-43*s,y),(x,y+48*s),(x+43*s,y)],fill="#e5dec9")
        d.line((x,y+57*s,x,y+195*s),fill="#485a50",width=max(1,int(4*s)))
        d.rectangle((x+20*s,y+93*s,x+36*s,y+101*s),fill="#b9bfa9")
    # neck, shoulders
    d.rectangle((x-17*s,y-36*s,x+17*s,y+10*s),fill=skin_sh)
    # head and ears
    cy=y-84*s;xx=x+1.5*math.sin(t*.7)*s
    d.ellipse((xx-52*s,cy-60*s,xx+52*s,cy+55*s),fill=skin,outline=skin_sh,width=max(1,int(2*s)))
    d.ellipse((xx-57*s,cy-5*s,xx-46*s,cy+17*s),fill=skin_sh)
    d.ellipse((xx+46*s,cy-5*s,xx+57*s,cy+17*s),fill=skin_sh)
    # hair volumetric silhouettes
    if who=="MAE":
        for dx,dy,rr in [(-48,-44,26),(-31,-70,31),(-3,-80,33),(29,-71,31),(50,-44,26),(-45,-22,20),(41,-30,23)]:
            d.ellipse((xx+(dx-rr)*s,cy+(dy-rr)*s,xx+(dx+rr)*s,cy+(dy+rr)*s),fill=hair)
        d.ellipse((xx-17*s,cy-61*s,xx+25*s,cy-32*s),fill=hair)
        # small hoop earrings
        for a in [-1,1]:
            ex=xx+a*55*s
            d.arc((ex-5*s,cy+9*s,ex+5*s,cy+26*s),0,320,fill="#e0b46e",width=max(1,int(3*s)))
    else:
        d.polygon([(xx-52*s,cy-17*s),(xx-54*s,cy-51*s),(xx-32*s,cy-74*s),(xx+2*s,cy-73*s),(xx+37*s,cy-65*s),(xx+54*s,cy-38*s),(xx+47*s,cy-10*s),(xx+26*s,cy-32*s),(xx-5*s,cy-34*s),(xx-28*s,cy-18*s)],fill=hair)
        d.ellipse((xx-51*s,cy-59*s,xx-1*s,cy-26*s),fill=hair)
    # eyes and brows; comedic camera glances
    gy=cy+0*s
    gaze=0 if not camera else (4 if who=="JONAH" else 0)
    blink=((t+(1.0 if who=="MAE" else 2.2))%5.4)<.13
    brow= -6 if emotion=="question" else 0
    for side in [-1,1]:
        ex=xx+side*20*s
        d.line((ex-10*s,gy-17*s+brow*s,ex+10*s,gy-18*s+brow*s),fill=hairline,width=max(1,int(4*s)))
        if blink:
            d.line((ex-9*s,gy,ex+9*s,gy+1*s),fill=hairline,width=max(1,int(2*s)))
        else:
            d.ellipse((ex-9*s,gy-7*s,ex+9*s,gy+8*s),fill="#f5eee5")
            px=gaze*s
            d.ellipse((ex-3*s+px,gy-3*s,ex+4*s+px,gy+5*s),fill=eye)
            d.ellipse((ex-1*s+px,gy-3*s,ex+1*s+px,gy-1*s),fill="#f9f4ea")
    d.line((xx+2*s,gy+3*s,xx-2*s,gy+19*s,xx+6*s,gy+20*s),fill=skin_sh,width=max(1,int(2*s)))
    # speech energy controls jaw; no binary snapping
    mm=clamp(speaking*1.65)
    my=cy+31*s
    if mm>.17:
        ht=lerp(2,13,mm)*s
        d.ellipse((xx-10*s,my-3*s,xx+10*s,my+ht),fill="#5b3430",outline=skin_sh,width=max(1,int(s)))
        if mm>.55:
            d.line((xx-6*s,my+2*s,xx+5*s,my+2*s),fill="#ead3c2",width=max(1,int(2*s)))
    else:
        d.arc((xx-13*s,my-5*s,xx+13*s,my+7*s),8,171,fill="#583831",width=max(1,int(2*s)))
    # subtle creases
    d.arc((xx-35*s,cy+26*s,xx-14*s,cy+45*s),210,270,fill=skin_sh,width=max(1,int(s)))
    # arm gestures driven by scene but consistent rig 
    gest= math.sin(t*1.8)*5*s if speaking>.12 else 0.
    if who=="MAE":
        d.rounded_rectangle((x+70*s,y+48*s,x+94*s,y+154*s+gest),radius=int(11*s),fill=garment)
        d.ellipse((x+70*s,y+142*s+gest,x+96*s,y+170*s+gest),fill=skin)
        d.rounded_rectangle((x+45*s,y+116*s,x+108*s,y+175*s),radius=int(3*s),fill="#b9a786",outline="#62584b",width=max(1,int(2*s)))
        for iy in (128,139,150):d.line((x+54*s,y+iy*s,x+96*s,y+iy*s),fill="#716d60",width=max(1,int(s)))
    else:
        d.rounded_rectangle((x-91*s,y+61*s,x-65*s,y+177*s),radius=int(9*s),fill=garment)
        d.ellipse((x-94*s,y+160*s,x-65*s,y+187*s),fill=skin)

def plant(d,t,x=517,y=432,scale=1.):
    s=scale
    x=float(x); y=float(y)
    drift=math.sin(t*2.3)*2.4
    # plant leaves, drawn as folded lanceolate shapes
    leaves=[(-85,-105,-55,-145),(-64,-151,-81,-186),(-38,-164,-25,-214),(-8,-177,7,-234),(27,-168,41,-207),(64,-135,92,-172),(82,-94,121,-107),(-92,-63,-119,-78),(43,-97,62,-125)]
    for i,(dx,dy,ex,ey) in enumerate(leaves):
        a=x+dx*.37*s; ay=y-39*s+dy*.43*s
        tipx=x+(ex+drift*(1+i%3)*.35)*s
        tipy=y+(ey+math.sin(t*1.6+i)*2)*s
        base=(x, y-35*s)
        midpoint=((a+tipx)*.5, (ay+tipy)*.5)
        width=(16+i%3*4)*s
        # leaf geometry
        vx=tipx-base[0];vy=tipy-base[1];length=max(1.,math.hypot(vx,vy));nx=-vy/length;ny=vx/length
        pts=[base,(midpoint[0]+nx*width,midpoint[1]+ny*width), (tipx,tipy),
            (midpoint[0]-nx*width*.75,midpoint[1]-ny*width*.75)]
        greens=["#3d7153","#477d57","#537f52","#296b53","#588c68"]
        d.polygon(pts,fill=greens[i%len(greens)])
        d.line([base,(tipx,tipy)],fill="#a1af73",width=max(1,int(2*s)))
    # soil and pot
    d.ellipse((x-51*s,y-33*s,x+51*s,y-11*s),fill="#685d4d")
    d.polygon([(x-51*s,y-21*s),(x+51*s,y-21*s),(x+38*s,y+54*s),(x-39*s,y+54*s)],fill="#b97862")
    d.rounded_rectangle((x-55*s,y-29*s,x+55*s,y-7*s),radius=int(6*s),fill="#d48e72",outline="#7d594d",width=max(1,int(2*s)))
    d.rectangle((x-24*s,y+6*s,x+26*s,y+38*s),fill="#efe6cd")
    txt(d,(x-18*s,y+10*s),"FERN",F16,"#465b4d")

def document_bg(im,t):
    office_bg(im,t)
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle((252,79,719,515),radius=9,fill=(0,0,0,65))
    d.rounded_rectangle((244,65,710,502),radius=5,fill="#f6f1e7",outline="#c9bba3",width=4)
    txt(d,(284,100),"PEOPLE OPERATIONS",F20,"#41544f")
    d.line((283,136,668,136),fill="#999b90",width=3)
    txt(d,(284,160),"PERFORMANCE SUPPORT PLAN",F22)
    txt(d,(284,203),"SUBJECT: FERN   /   DEPARTMENT: OFFICE",F14)
    txt(d,(284,249),"GOALS",F20)
    for i,a in enumerate(["Demonstrate measurable growth","Improve participation in meetings","Practice proactive alignment"]):
        yy=294+i*48
        d.rectangle((291,yy,312,yy+20),outline="#5f746d",width=2)
        txt(d,(331,yy),a,F16)
    txt(d,(284,450),"MANAGER SIGNATURE:  MAE",F14)
    d.line((283,474,673,474),fill="#8c8b81",width=2)

def draw_scene(s,local,t):
    im=Image.new("RGBA",(W,H))
    kind=s["shot"]
    if kind.startswith("interview"):
        interview_bg(im,t)
        who="JONAH" if kind.endswith("jonah") else "MAE"
        rms=energy(s,t)
        person(ImageDraw.Draw(im,"RGBA"),465,405,who,t,scale=1.40,speaking=rms,camera=False,emotion="neutral")
    elif kind=="document":
        document_bg(im,t)
    elif kind=="end":
        d=ImageDraw.Draw(im,"RGBA")
        d.rectangle((0,0,W,H),fill="#344942")
        for yy in range(0,H,28): d.line((0,yy,W,yy),fill="#3d534a",width=1)
        plant(d,t,x=480,y=318,scale=.73)
        txt(d,(480,417),"FERN'S PERFORMANCE REVIEW",F28,"#f3eddd",anchor="mm")
        txt(d,(480,456),"A SMALL WORKPLACE DOCUMENTARY",F14,"#d0dbcd",anchor="mm")
    else:
        office_bg(im,t)
        d=ImageDraw.Draw(im,"RGBA")
        who=s.get("who")
        mae_e=energy(s,t) if who=="MAE" else 0.
        jonah_e=energy(s,t) if who=="JONAH" else 0.
        look=(kind=="reaction")
        person(d,327,365,"MAE",t,scale=1.0,speaking=mae_e,emotion="neutral")
        person(d,730,366,"JONAH",t,scale=1.0,speaking=jonah_e,camera=look,emotion="question" if look else "neutral")
        plant(d,t,514,441,1.)
        if kind=="wide" and s.get("note")=="establish":
            d.rounded_rectangle((24,26,381,99),radius=8,fill=(20,31,32,196))
            txt(d,(40,40),"HART & VALE",F28,"#efece3")
            txt(d,(42,75),"ONE COMPANY. MANY PRIORITIES.",F10,"#e0c8a1")
    return im

def energy(s,t):
    if "audio" not in s:return 0.
    a=s["audio"];st=s["start"]+s["speech_offset"]
    i=int((t-st)*SR)
    if i<0 or i>=len(a):return 0.
    window=a[max(0,i-360):min(len(a),i+360)]
    return clamp(float(np.sqrt(np.mean(window*window)+1e-10))*9)

def crop_shot(im,s,u,t):
    shot=s["shot"]
    mapping={
      "wide":(480,280,1.01),
      "mae":(330,305,1.67),
      "jonah":(721,309,1.67),
      "plant":(516,337,1.81),
      "plant_punch":(515,331,2.55),
      "reaction":(721,309,1.67),
      "document":(485,283,1.00),
      "interview_jonah":(470,283,1.32),
      "interview_mae":(470,283,1.32),
      "end":(480,270,1.00),
    }
    cx,cy,z=mapping[shot]
    if shot=="plant_punch":
        z=lerp(1.7,2.68,ease(u/.21))
        cy-=5*ease(u/.21)
    if shot=="reaction":
        z=lerp(1.60,1.81,ease(u/.65))
    if shot=="mae":
        cx-=4*ease(u)
    if shot=="jonah":
        cx+=3*ease(u)
    # Minimal hand-held drift. Camera is imperfect but not nauseating.
    cx+=2.2*math.sin(t*1.81)+.8*math.sin(t*6.0)
    cy+=1.6*math.sin(t*1.23)
    cw=W/z; ch=H/z
    box=(int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))
    im=im.crop(box).resize((W,H),Image.Resampling.BICUBIC)
    return im

def wrap(draw,text,font,max_w):
    words=text.split();lines=[];current=""
    for w in words:
        test=(current+" "+w).strip()
        if draw.textbbox((0,0),test,font=font)[2]>max_w and current:
            lines.append(current);current=w
        else:current=test
    if current:lines.append(current)
    return lines

def overlay(im,s,u,t):
    d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((0,0,W,H),outline=(20,25,25,65),width=10)
    # Subtle documentary grade and witness stamp
    if s["shot"].startswith("interview"):
        name="MAE  /  OPERATIONS" if s["shot"]=="interview_mae" else "JONAH  /  ACCOUNTS"
        d.rounded_rectangle((35,403,383,450),radius=5,fill=(27,36,36,205))
        txt(d,(47,415),name,F20,"#f0eee3")
    if "line" in s:
        spoken_start=s["start"]+s.get("speech_offset",0.)
        if spoken_start<=t<spoken_start+len(s["audio"])/SR+.19:
            captions=wrap(d,s["line"],F20,800)
            captions=captions[:3]
            bh=29*len(captions)+16
            top=H-19-bh
            d.rounded_rectangle((W//2-426,top,W//2+426,H-13),radius=9,fill=(13,21,24,217))
            for ii,c in enumerate(captions):
                txt(d,(W/2,top+9+ii*29),c,F20,"#fff8e8",anchor="mt")
    if s["shot"]=="end":return
    # world as observed, not a TV show imitation
    d.text((W-38,21),"●",font=F14,fill=(151,55,47,140))
    d.text((23,18),"OFFICE DOCUMENTARY  •  CAM 02",font=F10,fill=(233,233,221,170))

def frame(t):
    ix=max(0,min(len(starts)-1,bisect.bisect_right(starts,t)-1))
    s=SCENES[ix]
    local=t-s["start"]
    u=clamp(local/s["secs"])
    im=draw_scene(s,local,t)
    im=crop_shot(im,s,u,t)
    overlay(im,s,u,t)
    return im.convert("RGB")

# Full video render piped to ffmpeg without storing thousands of PNG files.
TMP=ROOT/"_scratch_video.mp4"
cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
     "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
     "-r",str(FPS),"-i","-",
     "-an","-c:v","libx264","-preset","veryfast","-crf","21",
     "-pix_fmt","yuv420p",str(TMP)]
process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
frames=math.ceil(DURATION*FPS)
try:
    for i in range(frames):
        process.stdin.write(np.asarray(frame(i/FPS),dtype=np.uint8).tobytes())
        if i%300==0:print("Frames:",i,"/",frames,flush=True)
finally:
    process.stdin.close()
if process.wait()!=0: raise RuntimeError("FFmpeg video render failed")
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
                "-i",str(TMP),"-i",str(WAV),"-c:v","copy","-c:a","aac",
                "-b:a","160k","-movflags","+faststart","-shortest",str(FINAL)],check=True)
TMP.unlink(missing_ok=True); WAV.unlink(missing_ok=True)
print("SUCCESS",FINAL,FINAL.stat().st_size,"bytes",f"{DURATION:.1f}s",flush=True)
