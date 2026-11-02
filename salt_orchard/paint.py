"""Layered engraved illustrations for The Salt Orchard, on a 960 × 540 artboard."""
import math, random, subprocess
from pathlib import Path
from PIL import Image
import numpy as np

OUT=Path(__file__).parent/'plates'
OUT.mkdir(exist_ok=True)
R=random.Random(19)
def path(d,fill='none',stroke='none',w=1,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def oval(x,y,rx,ry,c,op=1):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{op}"/>'
def group(body,x=0,y=0,s=1,angle=0):
    return f'<g transform="translate({x} {y}) rotate({angle}) scale({s})">{body}</g>'
def grad(id,colors):
    return f'<linearGradient id="{id}" x2="0" y2="1" gradientUnits="objectBoundingBox" gradientTransform="scale(1 1)">'+''.join(f'<stop offset="{i/(len(colors)-1):.3f}" stop-color="{c}"/>' for i,c in enumerate(colors))+'</linearGradient>'
def paint(id): return f'url(#{id})'
defs=''.join(grad(k,v.split()) for k,v in {
'sky':'#4e6480 #b9a1a2 #f4c09a #f7d2a3','water':'#c0a6a0 #798e98 #466c7d #233c56','deep':'#a3c3ab #669d94 #366e72 #233e51 #181f39','pear':'#f6d994 #dba653 #a76a37 #74443e','bowl':'#76aea9 #426d80 #253c59','skin':'#f6c898 #c58e79 #905c63','coat':'#b66b50 #804756 #482e48','gold':'#ddc686 #b99156 #78684c','wood':'#bb8166 #855554 #433749','wall':'#738987 #b3ae94 #e9c99b','leaf':'#db9957 #a85940 #633944','shirt':'#738a8e #486474 #28374b'}.items())
def rect(x,y,w,h,c):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'
def leaf(x,y,s,a,c):
    d=path('M0 0 Q7 -8 21 -3 Q14 5 0 0Z',c)+path('M1 0 Q10 -2 18 -3','none','#ebba78',.55)
    return group(d,x,y,s,a)
def pear(x,y,s,a=0):
    d=path('M-1 -25 C-9 -24 -6 -12 -13 -3 C-24 12 -17 24 -3 26 C11 29 23 19 18 5 C16 -3 7 -9 6 -18 Q4 -26 -1 -25Z',paint('pear'),'#775643',.9)
    d+=path('M1 -24 Q-2 -32 4 -39','none','#473c37',2.4)+leaf(1,-30,.68,163,'#84834e')
    rr=random.Random(447)
    for _ in range(55):
        xx=rr.uniform(-13,14); yy=rr.uniform(-5,21)
        d+=oval(xx,yy,rr.uniform(.25,.8),.5,'#775039',.6)
    d+=path('M-12 2 Q-16 9 -14 15','none','#f7d091',1.5)
    return group(d,x,y,s,a)
def tree(x,y,s,seed,colors,fruit=False):
    rng=random.Random(seed); d=[]
    def twig(x,y,angle,L,w,n):
        end=(x+L*math.cos(angle),y+L*math.sin(angle))
        ex,ey=end; midx=(x+ex)/2+rng.uniform(-.13,.13)*L; midy=(y+ey)/2
        d.append(path(f'M{x-w*.48} {y} Q{midx-w*.42} {midy} {ex-w*.26} {ey} L{ex+w*.26} {ey} Q{midx+w*.43} {midy} {x+w*.52} {y}Z',colors[0]))
        if w>3:d.append(path(f'M{x-w*.25} {y} Q{midx-w*.2} {midy} {ex} {ey}', 'none',colors[1],max(.6,w*.09)))
        if n:
            for sign in (-1,1):
                twig(ex,ey,angle+sign*rng.uniform(.16,.69),L*rng.uniform(.55,.79),w*.61,n-1)
        else:
            for j in range(3):
                d.append(leaf(ex+rng.uniform(-7,7),ey+rng.uniform(-4,3),rng.uniform(.25,.62),rng.uniform(-165,165),rng.choice(colors[2:])))
            if fruit and rng.random()<.09:d.append(pear(ex,ey+9,.28))
    twig(0,0,-1.64,82,26,6)
    return group(''.join(d),x,y,s)
def shore():
    d=rect(0,0,960,540,paint('sky'))+oval(739,167,49,49,'#f8d6a9')
    for k in range(3):
        points=' '.join(f'{x},{230+k*14+12*math.sin(x/105+k)+7*math.cos(x/47+2*k)}' for x in range(-20,1001,12))
        d+=path('M-20 320 L'+points+' L1000 320Z',['#a3969a','#85838e','#676e80'][k])
    d+=path('M243 261v-46h12v47 M241 214h16v5h-16Z','#575969')
    d+=rect(0,270,960,270,paint('water'))
    for i in range(900):
        y=R.uniform(271,540);x=R.uniform(-20,960);w=R.uniform(2,26)*(1+(y-270)/250)
        c=R.choice(['#c4b1a6','#688696','#e2ba99','#465f77'])
        d+=path(f'M{x:.1f} {y:.1f} q{w*.4:.1f} -1 {w:.1f} -.3','none',c,R.uniform(.4,1.5),f'opacity="{R.uniform(.17,.56)}"')
    return d
def depths(seed):
    rng=random.Random(seed); d=rect(0,0,960,540,paint('deep'))
    for _ in range(32):
        x=rng.uniform(-80,1060);w=rng.uniform(4,40)
        d+=path(f'M{x} 0 h{w} l-190 430Z','#e4e0ac',extra='opacity=".045"')
    for i in range(7):
        d+=tree(i*165+rng.uniform(-25,25),420+rng.uniform(-20,35),rng.uniform(.58,1.09),i+seed,['#467477','#628783','#58817b','#6f8e80'])
    for _ in range(320):
        x,y=rng.uniform(0,960),rng.uniform(0,540);r=rng.uniform(.3,1.2)
        d+=oval(x,y,r,r,'#d8dbad',rng.uniform(.14,.48))
    for j in range(4):
        y=368+33*j; d+=path(f'M-10 {y} Q300 {y+50} 530 {y+16} T980 {y-6} V550H-10Z',['#416465','#34565c','#294650','#223645'][j])
    return d
def sister(x,y,s,kit=False):
    # Profile, three-quarter shoulders, hair mass, turned cheek and a narrow lid.
    hair='#443344' if not kit else '#523c39'; coat=paint('shirt' if kit else 'coat')
    d=path('M-36 91 Q-36 48 -26 33 L-13 23 L-12 13 L3 9 L6 26 Q23 29 30 48 L39 91Z',coat)
    d+=path('M-12 13 L-9 29 Q-4 34 4 28 L2 11Z',paint('skin'))
    d+=path('M-20 -20 Q-12 -35 5 -28 Q15 -25 16 -13 L16 -6 L21 1 L16 3 L16 9 L13 11 Q13 19 5 20 Q-6 19 -15 9Z',paint('skin'))
    d+=path('M-22 -20 Q-12 -39 8 -30 Q16 -28 18 -18 Q6 -21 0 -12 L-5 -1 Q-9 -7 -12 -2 Q-15 2 -10 7 L-12 16 Q-27 14 -27 -1Z',hair)
    d+=oval(-25,3,9,12,hair)+path('M6 -7 Q10 -10 15 -7 M8 -4 Q12 -5 15 -4 M14 8 l-5 .6','none','#613e45',1.2)
    d+=path('M-20 -17 Q-12 -28 0 -27 M-22 -9 Q-15 -24 -4 -24 M-23 -4 Q-18 -15 -11 -18','none','#97665b',1)
    d+=path('M-13 24 l8 11 10 -8 -3 10 -7 5 -12 -11Z','#ccab87')+path('M-24 40 Q-16 45 -14 69 L3 73 l-1 10 -28 -3 Q-33 62 -24 40Z',coat,'#554450',1.2)
    return group(d,x,y,s)
def boat():
    d=sister(-53,-33,.78)+group(sister(0,0,.72,True),54,-30)
    d+=path('M-134 9 Q-44 27 132 3 Q114 44 64 53 Q-14 64 -81 48 Q-116 39 -134 9Z',paint('wood'),'#423744',2.4)
    for y in [18,24,32,40]:d+=path(f'M-118 {y} Q-26 {y+40} 114 {y-3}','none','#d39b79',.95)
    d+=path('M-134 9 Q-28 32 132 3','none','#f0c396',3)
    return d
def bowl(x,y,s):
    d=path('M-54 -4 Q-49 31 -17 39 Q-8 45 15 39 Q43 34 54 -4Z',paint('bowl'),'#324d60',1.6)+oval(0,-4,54,10,'#bcd0b9')+oval(0,-4,48,6,'#3e6575')
    for i in range(-4,5):d+=path(f'M{i*10} 8 q4 9 9 0 q-3 13 -9 0Z','#b6c9b5')
    return group(d,x,y,s)
def kitchen():
    d=rect(0,0,960,540,paint('wall'))
    d+=rect(84,-20,289,382,'#506965')+rect(96,0,265,346,'#efcc98')+tree(210,343,1.15,6,['#a89a78','#c3ad80','#b19668','#af8f62'])
    d+=rect(222,0,8,351,'#626f65')+rect(93,153,270,8,'#626f65')
    d+=path('M0 399 L960 344 V540 H0Z',paint('wood'))
    for i in range(50):
        x=R.randrange(960); y=R.randrange(407,550)
        d+=path(f'M{x} {y} q71 -6 102 -6','none','#bb8971',.9)
    return d
def seed(x,y,s,angle=0):
    return group(path('M0 -10 C-1 -6 -9 -1 -7 5 C-5 12 4 11 6 6 Q9 0 0 -10Z','#583a36')+path('M-4 5 Q-5 1 0 -5','none','#bc895c',1.2),x,y,s,angle)
def label(x,y,t,sz,c,spacing=0,italic=False):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Serif" font-style="{("italic" if italic else "normal")}" font-size="{sz}" letter-spacing="{spacing}" fill="{c}">{t}</text>'
def art(i):
    R.seed(400+i); moving=''
    if i in (0,1,6):
        bg=shore()
        if i==0:
            bg+=label(67,77,'S O U N D I N G S     /     0 1',13,'#3a394b')+label(62,158,'The Salt Orchard',60,'#363448')
            moving=group(boat(),625,338,1.05)
        elif i==1:
            bg+=group(boat(),580,340,2.1)
            moving=group(path('M0 0 l-106 137 -14 7 5 -17 110 -132Z','#936b55','#553f41',2),517,352)
        else:
            bg+=group(boat(),503,325,2.6)
            bg+=bowl(513,355,.86)
            moving=pear(477,319,.62,-19)
    elif i in (2,3,4,5):
        bg=depths(4 if i!=5 else 8)
        if i==2:
            bg+=tree(655,497,1.94,7,['#313f48','#8d8870','#bd7952','#a26149','#c8935e'],True)
            bg+=tree(121,558,1.35,17,['#283c45','#66766b','#a37152','#965c49'],True)
            moving=group(''.join(leaf(k*77,k%3*37,.8,k*23,'#b58654') for k in range(6)),151,250)
        if i==3:
            bg+=tree(247,578,2.4,11,['#363e43','#88826c','#bc805a','#b66c51'],True)
            # diver in side silhouette, swimming down towards the trunk.
            diver=path('M-8 2 Q6 -14 34 -10 L73 -1 L99 -7 L134 -2 L132 4 L99 4 L72 12 L40 13 L15 15 L0 13Z',paint('coat'),'#39444b',2)+path('M40 9 L80 19 L112 13 L147 23 L145 28 L111 22 L80 29 L35 19Z','#424b56')+oval(-8,0,16,14,'#4c3c44')+path('M-22 -3 Q-25 6 -18 11 l7 2 4 -6Z','#cba387')+path('M15 5 Q8 19 -28 34 L-34 30 L1 6Z',paint('skin'))
            moving=group(diver,507,238,1.45,-28)
        if i==4:
            bg+=path('M180 -10 Q300 170 166 550 H713 Q590 289 758 -10Z',paint('wood'))
            for j in range(54):
                x=220+8*j; bg+=path(f'M{x} -8 q-41 110 -9 181 t-25 370','none','#d59d78',.8,extra='opacity=".42"')
            plate=rect(0,0,321,148,paint('gold'))+path('M10 9H311V139H10Z','none','#716349',1.2)
            for x in (15,306):
                for y in (15,133):plate+=oval(x,y,4,4,'#645c49')+path(f'M{x-2} {y+1}l4 -2','none','#cbbb84',1)
            plate+=label(38,61,'KIT       4′ 1″',27,'#514e42',2)+label(38,111,'NELL    4′ 1½″',27,'#514e42',1)
            bg+=group(plate,311,208,1,-5)
            moving=leaf(715,193,2.5,-42,'#ae7753')
        if i==5:
            bg+=tree(914,657,2.2,13,['#263f46','#677265','#9f6a4c','#a97950'],True)
            moving=pear(493,287,2.75,-17)+pear(703,447,1.17,23)+pear(326,504,.8,-9)
    elif i==7:
        bg=kitchen()+bowl(210,420,1.37)
        half=path('M0 -79 C-25 -78 -15 -43 -37 -16 C-74 31 -60 79 -12 85 C33 91 74 66 60 21 C51 -8 16 -37 16 -65 Q12 -82 0 -79Z','#d69a56','#876541',3)
        half+=path('M1 -72 C-19 -68 -10 -41 -30 -14 C-60 29 -52 71 -10 77 C29 80 65 58 52 22 C39 -7 11 -37 11 -63Z','#eed39a')
        half+=path('M5 -61 Q-1 -23 6 24 Q-10 32 -10 45 Q4 62 17 40 Q18 29 8 23Z','#c8aa76')+seed(2,36,.95,-17)+seed(12,40,.88,24)
        bg+=group(half,599,367,1.47,-62)
        moving=seed(457,426,.8,-60)+seed(434,433,.77,22)+seed(471,444,.68,-36)
    else:
        bg=kitchen()+sister(710,165,2.2,True)+bowl(373,416,1.12)
        for j,(x,y) in enumerate([(529,413),(553,418),(536,429),(565,406),(575,422)]):bg+=seed(x,y,.62,j*41)
        moving=seed(697,319,.68,15)
    return bg,moving
def save_svg(svg,filename,transparent=False):
    src=OUT/(filename+'.svg')
    src.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 960 540"><defs>'+defs+'</defs>'+svg+'</svg>')
    out=src.with_suffix('.png')
    subprocess.run(['inkscape',str(src),'--export-filename='+str(out)],check=True,stdout=subprocess.DEVNULL)
    src.unlink()
    if not transparent:
        im=np.asarray(Image.open(out).convert('RGB')).astype('int16')
        rng=np.random.default_rng(29)
        grain=rng.normal(0,1.9,im.shape[:2])[:,:,None]
        Image.fromarray(np.clip(im+grain,0,255).astype('uint8')).save(out)
if __name__=='__main__':
    for i in range(9):
        bg,fg=art(i);save_svg(bg,f'b{i}');save_svg(fg,f'f{i}',True)
