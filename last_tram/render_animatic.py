from PIL import Image, ImageDraw, ImageFont
import numpy as np
import soundfile as sf
from pathlib import Path
import subprocess, json, math, os

W,H=960,540
FPS=24
SR=24000
DURATION=50.0
ROOT=Path(__file__).parent
OUT=ROOT

def clamp(x,a=0,b=1): return max(a,min(b,x))
def smooth(x):
    x=clamp(x); return x*x*(3-2*x)
def lerp(a,b,t): return a+(b-a)*t
def ease(t): return 0.5-0.5*math.cos(math.pi*clamp(t))

def font(size,bold=False):
    paths=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
F_SMALL=font(18); F_SUB=font(28,True); F_TITLE=font(42,True)

manifest=json.loads((ROOT/'manifest.json').read_text())
byid={x['id']:x for x in manifest}
STARTS={'b01':3.30,'a01':5.40,'b02':7.60,'a02':10.20,'b03':12.60,'a03':17.30,'a04':19.20,'b04':25.50,'a05':28.70,'b05':31.90,'b06':34.50,'a06':37.90,'b07':41.00,'a07':44.00}
line_audio={}
for lid,item in byid.items():
    x,sr=sf.read(ROOT/item['file'],dtype='float32')
    if x.ndim>1: x=x.mean(axis=1)
    line_audio[lid]=x

def active_line(t):
    for lid,st in STARTS.items():
        if st <= t < st+byid[lid]['duration']: return lid,byid[lid]
    return None,None

def speech_energy(lid,t):
    if not lid: return 0.0
    x=line_audio[lid]; i=int((t-STARTS[lid])*SR)
    if i<0 or i>=len(x): return 0.0
    r=260; a=max(0,i-r); b=min(len(x),i+r)
    return clamp(float(np.sqrt(np.mean(x[a:b]**2)+1e-8))*9.5)

def stereo(mono,pan=0,gain=1):
    pan=clamp(pan,-1,1)
    l=math.sqrt((1-pan)/2); r=math.sqrt((1+pan)/2)
    return np.column_stack([mono*l*gain,mono*r*gain]).astype(np.float32)

n=int(DURATION*SR)
rng=np.random.default_rng(3)
noise=rng.normal(0,1,n).astype(np.float32)
k=np.ones(17,dtype=np.float32)/17
rain=np.convolve(noise,k,mode='same')*.026
mix=stereo(rain,0,.9)
tt=np.arange(n,dtype=np.float32)/SR
mix += stereo((np.sin(2*np.pi*50*tt)*.0015 + np.sin(2*np.pi*100*tt)*.0008).astype(np.float32),0,1)
ramp=np.clip((tt-37.5)/9.0,0,1)
tram=(np.sin(2*np.pi*38*tt)+.45*np.sin(2*np.pi*76*tt)+.2*np.sin(2*np.pi*113*tt))*ramp*.014
mix += stereo(tram.astype(np.float32),.15,1)
for lid,st in STARTS.items():
    x=line_audio[lid]; sp=byid[lid]['speaker']
    a=stereo(x,-.16 if sp=='A' else .16,.88)
    i=int(st*SR); end=min(n,i+len(a)); mix[i:end]+=a[:end-i]
mix=np.tanh(mix*1.2)*.82
sf.write(OUT/'animatic_mix.wav',mix,SR)

BG=(23,31,42); A_COL=(61,76,91); B_COL=(83,71,86); SKIN=(181,154,139); INK=(15,19,25)

def draw_rain(img,t,amount=90,close=False):
    d=ImageDraw.Draw(img,'RGBA')
    for i in range(amount):
        x=(i*83 + 79*17) % W
        speed=170+(i%7)*23
        y=((i*137+t*speed)%(H+100))-50
        ln=16+(i%5)*6
        d.line((x,y,x-5,y+ln),fill=(185,207,220,70 if close else 48),width=1+(i%3==0))

def station_bg(img,t,close=False):
    d=ImageDraw.Draw(img,'RGBA')
    d.rectangle((0,0,W,H),fill=BG); d.rectangle((0,365,W,H),fill=(28,35,42,255))
    for i in range(16):
        x=35+i*61; y=125+(i*47)%170; rr=4+(i%3)*2
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(226,177,98,70 if close else 100))
    d.rectangle((120,95,750,370),fill=(28,39,50,190),outline=(103,123,136,170),width=3)
    d.line((120,95,165,55,790,55,750,95),fill=(105,123,136,180),width=5)
    for x in [150,740]: d.line((x,95,x,410),fill=(99,117,130,180),width=5)
    for x in [310,500,675]: d.line((x,100,x,350),fill=(86,109,124,90),width=2)
    d.rounded_rectangle((190,310,680,345),radius=7,fill=(82,72,62,255))
    d.rectangle((220,345,235,398),fill=(61,55,50,255)); d.rectangle((630,345,645,398),fill=(61,55,50,255))
    d.rectangle((0,430,W,440),fill=(154,130,71,110))
    d.line((0,475,W,455),fill=(122,134,138,180),width=3); d.line((0,510,W,488),fill=(122,134,138,180),width=3)
    for i in range(12):
        x=30+i*81; d.line((x,390,x-22,520),fill=(226,177,98,20+(i%3)*10),width=2)
    draw_rain(img,t,120,close)

def person(draw,x,y,s,who='A',facing=1,gaze=0,head_tilt=0,mouth=0,soft=0,eyes_closed=False):
    coat=A_COL if who=='A' else B_COL; hair=(31,30,32) if who=='A' else (34,28,33)
    shoulder=72*s
    draw.rounded_rectangle((x-shoulder,y,x+shoulder,y+135*s),radius=28*s,fill=coat,outline=INK,width=max(1,int(2*s)))
    if who=='B': draw.arc((x-48*s,y-12*s,x+48*s,y+55*s),10,170,fill=(101,111,124),width=max(2,int(12*s)))
    draw.rectangle((x-15*s,y-28*s,x+15*s,y+12*s),fill=SKIN)
    hx=x+head_tilt*8*s; hy=y-82*s
    draw.ellipse((hx-43*s,hy-52*s,hx+43*s,hy+48*s),fill=SKIN,outline=INK,width=max(1,int(2*s)))
    if who=='A':
        pts=[(hx-45*s,hy-5*s),(hx-48*s,hy-42*s),(hx-24*s,hy-62*s),(hx+4*s,hy-58*s),(hx+36*s,hy-48*s),(hx+44*s,hy-12*s),(hx+24*s,hy-27*s),(hx+5*s,hy-22*s),(hx-16*s,hy-31*s)]
    else:
        pts=[(hx-45*s,hy-2*s),(hx-48*s,hy-44*s),(hx-25*s,hy-60*s),(hx+5*s,hy-63*s),(hx+38*s,hy-45*s),(hx+44*s,hy-3*s),(hx+24*s,hy-34*s),(hx-5*s,hy-26*s)]
        draw.ellipse((hx+30*s,hy-35*s,hx+58*s,hy-7*s),fill=hair)
    draw.polygon(pts,fill=hair)
    eye_y=hy+2*s; sep=16*s; gx=gaze*4*s+facing*1.5*s
    if eyes_closed:
        draw.line((hx-sep-7*s,eye_y,hx-sep+7*s,eye_y+1*s),fill=INK,width=max(1,int(2*s)))
        draw.line((hx+sep-7*s,eye_y,hx+sep+7*s,eye_y+1*s),fill=INK,width=max(1,int(2*s)))
    else:
        for ex in [hx-sep,hx+sep]:
            draw.ellipse((ex-6*s,eye_y-3*s,ex+6*s,eye_y+4*s),fill=(231,226,215),outline=INK,width=max(1,int(s)))
            draw.ellipse((ex-2.2*s+gx,eye_y-1.8*s,ex+2.2*s+gx,eye_y+2.6*s),fill=INK)
    brow_y=eye_y-14*s; lift=(soft*3.5)*s
    draw.line((hx-sep-8*s,brow_y+lift,hx-sep+7*s,brow_y-lift),fill=hair,width=max(1,int(2*s)))
    draw.line((hx+sep-7*s,brow_y-lift,hx+sep+8*s,brow_y+lift),fill=hair,width=max(1,int(2*s)))
    draw.line((hx+2*s,eye_y+4*s,hx-1*s,eye_y+17*s,hx+4*s,eye_y+18*s),fill=(104,78,73),width=max(1,int(s)))
    my=hy+29*s; smile=soft*3.2*s; openh=mouth*7*s
    if openh>1.3: draw.ellipse((hx-10*s,my-smile,hx+10*s,my+openh-smile),fill=(61,38,39),outline=INK,width=max(1,int(s)))
    else: draw.arc((hx-11*s,my-4*s-smile,hx+11*s,my+8*s+smile),15,165,fill=(80,49,48),width=max(1,int(2*s)))

def umbrella(draw,x,y,s=1,grip=1):
    draw.arc((x-18*s,y-12*s,x+18*s,y+24*s),180,350,fill=(15,18,23),width=max(2,int(6*s)))
    draw.line((x+14*s,y+10*s,x+3*s,y+88*s),fill=(21,24,28),width=max(2,int(5*s)))
    draw.polygon([(x-2*s,y+28*s),(x+10*s,y+34*s),(x+4*s,y+90*s),(x-12*s,y+83*s)],fill=(35,43,52))
    hand_y=y+12*s
    draw.rounded_rectangle((x-12*s,hand_y-8*s,x+14*s,hand_y+10*s),radius=5*s,fill=SKIN,outline=INK,width=max(1,int(s)))
    if grip>.4:
        for j in range(3): draw.line((x-6*s+j*6*s,hand_y-5*s,x-4*s+j*6*s,hand_y+7*s),fill=(110,79,70),width=max(1,int(s)))

def foreground_shoulder(draw,side='left',who='A'):
    coat=A_COL if who=='A' else B_COL; hair=(31,30,32) if who=='A' else (34,28,33)
    if side=='left':
        draw.ellipse((-130,205,285,650),fill=coat,outline=INK,width=4); draw.ellipse((42,92,245,310),fill=hair)
    else:
        draw.ellipse((675,205,1090,650),fill=coat,outline=INK,width=4); draw.ellipse((715,92,918,310),fill=hair)

def subtitle(img,t):
    lid,item=active_line(t)
    if not item: return
    d=ImageDraw.Draw(img,'RGBA'); txt=item['text']; box=d.textbbox((0,0),txt,font=F_SUB); tw=box[2]-box[0]; th=box[3]-box[1]
    x=(W-tw)//2; y=H-68
    d.rounded_rectangle((x-14,y-8,x+tw+14,y+th+10),radius=8,fill=(8,10,14,180)); d.text((x,y),txt,font=F_SUB,fill=(240,240,235,255))

def overlay(img,t,label):
    d=ImageDraw.Draw(img,'RGBA')
    d.rounded_rectangle((16,14,330,48),radius=8,fill=(8,11,15,150)); d.text((28,21),label,font=F_SMALL,fill=(218,225,229,255))
    d.text((W-105,20),f'{int(t//60):02d}:{t%60:05.2f}',font=F_SMALL,fill=(208,216,222,235))

def shot_for(t):
    cuts=[
        (0.0,3.2,'01  WIDE — arrival'),(3.2,7.4,'02  TWO-SHOT — first exchange'),(7.4,9.9,'03  OTS A → B'),
        (9.9,12.2,'04  REVERSE OTS B → A'),(12.2,16.8,'05  MEDIUM CLOSE — B question'),(16.8,18.9,'06  CLOSE — A / no'),
        (18.9,24.6,'07  CLOSE — A / confession push'),(24.6,28.3,'08  REACTION CLOSE — B'),(28.3,30.9,'09  REVERSE CLOSE — A'),
        (30.9,34.2,'10  REACTION — B answers'),(34.2,37.5,'11  TWO-SHOT — softening'),(37.5,39.8,'12  INSERT — umbrella hand'),
        (39.8,43.3,'13  WIDE PROFILE — tram arrives'),(43.3,46.2,'14  CLOSE — A decision'),(46.2,50.01,'15  WIDE HOLD — does not board')]
    for a,b,l in cuts:
        if a<=t<b: return a,b,l
    return cuts[-1]

def render(t):
    a,b,label=shot_for(t); u=(t-a)/(b-a)
    img=Image.new('RGB',(W,H),BG); station_bg(img,t,close=('CLOSE' in label or 'OTS' in label or 'INSERT' in label)); d=ImageDraw.Draw(img,'RGBA')
    lid,item=active_line(t); energy=speech_energy(lid,t)
    A_m=energy if item and item['speaker']=='A' else 0; B_m=energy if item and item['speaker']=='B' else 0
    A_soft=smooth((t-34.5)/4.3)*.75; B_soft=smooth((t-24.8)/10.5)*.55
    A_gaze=-.4 if t<19 else lerp(-.35,.45,smooth((t-19)/5.3)); B_gaze=.1
    if 31<t<34.1: B_gaze=-.5
    if t>=34.2: B_gaze=.35

    if label.startswith('01'):
        person(d,335,310,.66,'A',1,A_gaze,-.15,A_m,A_soft); bx=lerp(1030,650,ease(clamp((t-.65)/2.2))); person(d,bx,282,.67,'B',-1,.15,.05,B_m,B_soft); umbrella(d,405,300,.62,1)
        if t<2.2:
            al=int(255*clamp((t-.25)/.6)*clamp((2.2-t)/.7)); d.text((52,63),'THE LAST TRAM',font=F_TITLE,fill=(235,233,222,al))
    elif label.startswith('02'):
        person(d,335,265,.95,'A',1,A_gaze,-.12,A_m,A_soft); by=lerp(220,265,smooth((t-5.7)/.8)); person(d,645,by,.95,'B',-1,.2,.02,B_m,B_soft); umbrella(d,468,292,.8,1)
    elif label.startswith('03'):
        foreground_shoulder(d,'left','A'); person(d,635,240,1.42,'B',-1,.15,.06,B_m,B_soft)
    elif label.startswith('04'):
        foreground_shoulder(d,'right','B'); person(d,330,240,1.42,'A',1,A_gaze,-.12,A_m,A_soft)
    elif label.startswith('05'):
        foreground_shoulder(d,'left','A'); person(d,610,245,1.48,'B',-1,.2,lerp(.02,-.08,ease(u)),B_m,B_soft)
    elif label.startswith('06'):
        person(d,460,252,1.78,'A',1,-.35,-.16,A_m,0)
    elif label.startswith('07'):
        s=lerp(1.72,1.93,smooth(u)); person(d,460,255,s,'A',1,A_gaze,lerp(-.17,-.04,smooth(u)),A_m,.05)
    elif label.startswith('08'):
        person(d,505,250,1.82,'B',-1,.15,.03,B_m,.25+u*.12)
    elif label.startswith('09'):
        person(d,455,252,1.83,'A',1,.42,-.02,A_m,.10)
    elif label.startswith('10'):
        g=-.55 if t<33.7 else lerp(-.55,.25,smooth((t-33.7)/.45)); person(d,505,250,1.82,'B',-1,g,.10,B_m,.22)
    elif label.startswith('11'):
        person(d,335,265,.98,'A',1,.35,-.02,A_m,A_soft); person(d,645,265,.98,'B',-1,.30,.02,B_m,.48); umbrella(d,470,294,.82,lerp(1,.45,smooth((t-36.1)/1.2)))
    elif label.startswith('12'):
        d.rectangle((0,0,W,H),fill=(29,37,45,215)); d.rectangle((0,330,W,H),fill=(39,45,50,255)); umbrella(d,490,210,2.1,lerp(.9,.12,smooth(u))); draw_rain(img,t,55,True)
    elif label.startswith('13'):
        person(d,335,310,.68,'A',1,.3,-.02,A_m,A_soft); person(d,640,310,.68,'B',-1,.3,.02,B_m,.5); umbrella(d,470,300,.62,.18)
        tr=smooth((t-39.8)/3.5); tx=900-180*tr; ty=266
        for rad,alpha in [(56,20),(36,35),(18,90)]: d.ellipse((tx-rad,ty-rad,tx+rad,ty+rad),fill=(255,224,159,alpha))
        d.ellipse((tx-8,ty-8,tx+8,ty+8),fill=(255,238,194,255)); d.ellipse((tx+27,ty-7,tx+41,ty+7),fill=(255,238,194,245))
    elif label.startswith('14'):
        local=(t-a)/(b-a); gaze=lerp(.7,-.1,smooth((local-.30)/.48)); person(d,455,252,1.86,'A',1,gaze,lerp(.03,-.02,smooth(local)),A_m,.62)
        d.rectangle((0,0,W,H),fill=(255,205,126,int(55*smooth((t-43.3)/2.0))))
    else:
        person(d,335,310,.68,'A',1,.32,-.02,A_m,.65); person(d,640,310,.68,'B',-1,.28,.02,B_m,.52); umbrella(d,470,300,.62,.12)
        tr=ease(clamp((t-46.2)/2.3)); tx=lerp(1080,760,tr)
        d.rounded_rectangle((tx,175,tx+330,445),radius=18,fill=(50,58,65,235),outline=(158,168,170,220),width=4)
        d.rectangle((tx+30,215,tx+115,300),fill=(114,139,148,150)); d.ellipse((tx+36,390,tx+58,412),fill=(255,231,180,255)); d.ellipse((tx+115,390,tx+137,412),fill=(255,231,180,255))
        d.rectangle((0,0,W,H),fill=(255,212,145,int(45*smooth((t-46.5)/1.6))))
    overlay(img,t,label); subtitle(img,t); return img

video_tmp=OUT/'animatic_video.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',str(video_tmp)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for i in range(int(DURATION*FPS)):
    p.stdin.write(np.asarray(render(i/FPS),dtype=np.uint8).tobytes())
p.stdin.close(); rc=p.wait()
if rc: raise SystemExit(rc)
final=OUT/'the_last_tram_animatic.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(video_tmp),'-i',str(OUT/'animatic_mix.wav'),'-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(final)],check=True)
video_tmp.unlink(missing_ok=True)
print('wrote',final)
