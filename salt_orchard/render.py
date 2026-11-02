"""Render the nine plates against the recorded Kokoro performances."""
import json, math, subprocess, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parent
os.chdir(root)
timeline=json.loads(Path('timing.json').read_text())
shots=timeline['shots']
fps=24
W,H=1280,720
def smooth(x):
    x=min(1,max(0,x))
    return x*x*(3-2*x)
def drift(i,u,t):
    e=smooth(u)
    if i==0:return 42*(e-.5),3*math.sin(t*1.3)
    if i==1:return 4*math.sin(t*1.2),5*math.cos(t*1.2)
    if i==2:return -42*e,14*e
    if i==3:return 70-225*e,-29+96*e
    if i==4:return -90*e,54*e
    if i==5:return 20*math.sin(u*3),180-410*e
    if i==6:return 42*smooth((u-.73)*5),39*smooth((u-.73)*5)
    if i==8:return 16*smooth((u-.52)*4),35*smooth((u-.52)*4)
    return 0,0
def stamp(t):
    ms=round(t*1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
srt='\n\n'.join(f'{n}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["speaker"]}: {c["text"]}' for n,c in enumerate(timeline['captions'],1))
Path('captions.srt').write_text(srt+'\n')
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i','sound.mp3','-i','captions.srt','-map','0:v','-map','1:a','-map','2:s','-c:v','libx264','-threads','3','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','144k','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart','the-salt-orchard.mp4']
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',32)
for i,(start,end) in enumerate(shots):
    bg=Image.open(f'plates/b{i}.png').convert('RGB')
    layer=Image.open(f'plates/f{i}.png').convert('RGBA')
    bounds=layer.getbbox(); fg=layer.crop(bounds)
    for frame in range(round(start*fps),round(end*fps)):
        t=frame/fps-start; u=t/(end-start); e=smooth(u)
        im=bg.copy()
        dx,dy=drift(i,u,t)
        if i!=8 or u<.67:
            im.paste(fg,(round(bounds[0]+dx),round(bounds[1]+dy)),fg)
        if 2<=i<=5:
            draw=ImageDraw.Draw(im,'RGBA')
            for j in range(42):
                x=(j*173+11*math.sin(t*.28+j))%W
                y=(j*83-t*(3+j%5))%H
                draw.ellipse((x,y,x+2,y+2),fill=(204,226,196,60))
        zoom=(.023 if i==0 else .058)*e
        left=W*zoom*([.28,.53,.62,.31,.5,.5,.51,.69,.72][i])
        top=H*zoom*.48
        im=im.resize((W,H),Image.Resampling.BILINEAR,box=(left,top,W-W*zoom+left,H-H*zoom+top))
        if i==8 and t>end-start-4.7:
            mix=smooth((t-(end-start-4.7))/1.2)*.86
            im=Image.blend(im,Image.new('RGB',im.size,'#1b2430'),mix)
            if mix>.8:
                d=ImageDraw.Draw(im)
                d.text((640,365),'The Salt Orchard',font=font,anchor='mm',fill='#e8cbaa')
        proc.stdin.write(im.tobytes())
proc.stdin.close()
if proc.wait():raise RuntimeError('Video encoding failed')
