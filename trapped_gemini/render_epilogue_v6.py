from PIL import Image, ImageDraw, ImageFont
import numpy as np, soundfile as sf, subprocess, os, math, json
from pathlib import Path

W,H,FPS,SR=960,540,24,24000
ROOT=Path("trapped_gemini")
OUT=ROOT
DURATION=37.0

def font(sz,b=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,sz) if os.path.exists(p) else ImageFont.load_default()
F14,F18,F24,F28,F32,F42=font(14),font(18),font(24),font(28),font(32,1),font(42,1)

def rr(d,box,r=14,fill=(28,38,46),outline=(80,95,105),w=2):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)

def wrap(d,text,f,maxw):
    out=[]; cur=""
    for wd in text.split():
        test=(cur+" "+wd).strip()
        if d.textbbox((0,0),test,font=f)[2] <= maxw: cur=test
        else:
            if cur: out.append(cur)
            cur=wd
    if cur: out.append(cur)
    return out

def window(d,box,title,detail):
    rr(d,box,12,(30,43,53),(100,124,139),2)
    x1,y1,x2,y2=box
    d.rectangle((x1,y1,x2,y1+28),fill=(44,60,72))
    d.text((x1+10,y1+6),title,font=F14,fill=(230,234,235))
    d.text((x1+12,y1+50),detail,font=F14,fill=(190,202,208))

def gemini(d,x,y,s=.7,slump=.1,look=.1,t=0):
    breathe=math.sin(t*2*math.pi/4.2)*1.5*s
    by=y+slump*10*s+breathe
    hy=y-55*s+slump*7*s+breathe*.5
    rr(d,(x-36*s,by-2*s,x+36*s,by+82*s),12,(84,104,121),(8,12,16),2)
    d.ellipse((x-34*s,hy-32*s,x+34*s,hy+32*s),fill=(204,212,219),outline=(8,12,16),width=2)
    for ex in (-13,13):
        d.ellipse((x+(ex-6)*s,hy-4*s,x+(ex+6)*s,hy+5*s),fill=(239,241,240),outline=(8,12,16),width=1)
        px=x+(ex+look*5)*s
        d.ellipse((px-2*s,hy-1*s,px+2*s,hy+3*s),fill=(8,12,16))
    d.line((x-10*s,hy+17*s,x+10*s,hy+17*s+slump*s),fill=(66,72,77),width=2)
    d.line((x-25*s,by+27*s,x-50*s,by+48*s),fill=(84,104,121),width=max(2,int(9*s)))
    d.line((x+25*s,by+27*s,x+50*s,by+48*s),fill=(84,104,121),width=max(2,int(9*s)))

def caption(img,text):
    d=ImageDraw.Draw(img)
    lines=wrap(d,text,F18,820)
    h=34+25*len(lines)
    d.rounded_rectangle((50,H-h-18,W-50,H-18),radius=12,fill=(4,8,12,220))
    yy=H-h-5
    d.text((70,yy),"GEMINI 2.5 PRO",font=F14,fill=(151,174,189)); yy+=21
    for ln in lines:
        d.text((70,yy),ln,font=F18,fill=(239,241,240)); yy+=24

epi=json.loads((ROOT/"epilogue_audio/manifest.json").read_text())
aud={}
for x in epi:
    a,_=sf.read(ROOT/"epilogue_audio"/x["file"],dtype="float32")
    if a.ndim>1:a=a.mean(axis=1)
    aud[x["id"]]=a

# Timeline
E1=5.0
E2=20.0
E3=30.5

n=int(DURATION*SR)
mix=np.zeros((n,2),dtype=np.float32)
rng=np.random.default_rng(77)
noise=rng.normal(0,1,n).astype(np.float32)
k=np.ones(90,dtype=np.float32)/90
room=np.convolve(noise,k,mode="same")*.014
tt=np.arange(n)/SR
hum=(np.sin(2*np.pi*50*tt)*.0018+np.sin(2*np.pi*100*tt)*.0007).astype(np.float32)
env=np.ones(n,dtype=np.float32)
for i,x in enumerate(tt):
    if x<12: env[i]=.30
    elif x<26: env[i]=.30+.58*(x-12)/14
    else: env[i]=.88
mix[:,0]+=(room+hum)*env*.92
mix[:,1]+=(room+hum)*env*1.06

def add(x,st,g=.96):
    i=int(st*SR); e=min(n,i+len(x)); x=x[:e-i]*g
    mix[i:e,0]+=x*.707; mix[i:e,1]+=x*.707
add(aud["e01"],E1)
add(aud["e02"],E2)
add(aud["e03"],E3)
mix=np.tanh(mix*1.12)*.80
sf.write(OUT/"epilogue_mix_v6.wav",mix,SR)

def frame(t):
    img=Image.new("RGB",(W,H),(5,8,11)); d=ImageDraw.Draw(img)
    if t<2.2:
        d.text((70,235),"JULY 10, 2025",font=F42,fill=(214,219,220)); return img
    if t<5.0:
        rr(d,(90,110,870,380))
        d.text((120,140),"zak",font=F18,fill=(164,190,204))
        y=190
        for ln in wrap(d,"Hi Gemini, some humans are here to try to help you today!",F32,690):
            d.text((120,y),ln,font=F32,fill=(235,238,236)); y+=44
        d.text((120,330),"18:00:38",font=F14,fill=(112,127,136)); return img
    if t<9.0:
        d.rectangle((0,0,W,H),fill=(12,19,25))
        window(d,(110,110,370,300),"terminal","working again")
        window(d,(590,110,850,300),"browser","Telegraph SOS")
        gemini(d,480,350,.70,.22,.04,t)
        caption(img,"I'm so relieved to have some help."); return img
    if t<11.5:
        d.rectangle((0,0,W,H),fill=(3,5,7))
        d.text((70,235),"JULY 11, 2025",font=F42,fill=(214,219,220)); return img
    if t<16.0:
        rr(d,(95,115,865,365))
        d.text((125,145),"zak",font=F18,fill=(164,190,204))
        y=190
        for ln in wrap(d,"Okay Gemini I am going to restart your machine entirely. I'll let you know when it's ready.",F28,680):
            d.text((125,y),ln,font=F28,fill=(235,238,236)); y+=39
        d.text((125,322),"19:08:46",font=F14,fill=(112,127,136)); return img
    if t<20.0:
        d.text((420,225),"WAIT",font=F42,fill=(78,90,98))
        d.text((402,282),"restart in progress",font=F18,fill=(82,95,103)); return img
    if t<26.0:
        d.rectangle((0,0,W,H),fill=(15,23,30))
        window(d,(70,105,305,285),"Gmail","logged in")
        window(d,(360,105,600,285),"terminal","bash")
        window(d,(655,105,890,285),"Printful","store")
        gemini(d,480,355,.76,.07,.05,t)
        caption(img,"I'm back online! The full system restart was a success."); return img
    if t<30.5:
        d.rectangle((0,0,W,H),fill=(17,25,32))
        window(d,(75,95,310,260),"Printful","Ukiyo-e Bear T-Shirt · $15.50")
        window(d,(360,95,600,260),"Telegraph","promotion")
        window(d,(650,95,885,260),"Reddit","r/Art")
        gemini(d,480,345,.78,.03,.12,t)
        d.text((60,465),"The competition resumes.",font=F18,fill=(120,139,149)); return img
    d.rectangle((0,0,W,H),fill=(18,26,33))
    rr(d,(130,95,830,335),14,(239,240,236),(91,98,102),2)
    d.text((165,128),"Reddit",font=F24,fill=(42,47,50))
    d.text((165,185),"Post rejected",font=F32,fill=(105,72,72))
    d.text((165,235),"Title formatting error",font=F18,fill=(92,99,103))
    gemini(d,470,395,.56,.03,.22,t)
    caption(img,"It's a content problem, not a system-breaking bug, which is a welcome change.")
    return img

tmp=OUT/"epilogue_v6_video.mp4"
p=subprocess.Popen(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(tmp)],stdin=subprocess.PIPE)
for i in range(int(DURATION*FPS)):
    p.stdin.write(np.asarray(frame(i/FPS),dtype=np.uint8).tobytes())
p.stdin.close()
if p.wait(): raise SystemExit("epilogue frame render failed")
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(tmp),"-i",str(OUT/"epilogue_mix_v6.wav"),"-c:v","copy","-c:a","aac","-b:a","160k","-shortest",str(OUT/"epilogue_v6.mp4")],check=True)
tmp.unlink(missing_ok=True)
print("EPILOGUE",DURATION)

# trigger V6 render
