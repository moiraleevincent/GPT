from pathlib import Path
import json, subprocess
import numpy as np
import soundfile as sf
from kokoro import KPipeline

out = Path(__file__).resolve().parent
p = KPipeline(lang_code='a')
voices = {'Nell':p.load_voice('af_kore'), 'Kit':p.load_voice('af_nicole')}
# One shot per group. Pauses allow the other sister to act first.
scenes = [
[('Nell',"We had permission to take one thing. Kit brought a saw. I brought the little blue bowl.",1.4)],
[('Kit',"Count from the chimney. Four rows east.",.6),('Nell',"You can put that map away. I know where I fell out of a tree.",1.2)],
[('Nell',"Under the boat it was still autumn. Leaves caught flat against the wire. A wasp inside a pear, perfectly still.",2.2)],
[('Kit',"Two tugs if you want me to pull.",1),('Nell',"I went down with the saw between my knees. The brass plate was exactly where we'd left it.",1.4)],
[('Nell',"Kit. September, four feet one. Nell. September, four feet one and a half. She'd scratched that half in herself, for me.",1.6)],
[('Nell',"I put the saw to the bark. Then something hit the back of my hand. A pear, coming up. And then another.",2.1)],
[('Kit',"Where's the plate?",.8),('Nell',"Still on the tree.",1.0),('Kit',"You made me row six miles.",1.5),('Nell',"Hold out the bowl.",1.3)],
[('Nell',"We split the last pear with her thumbnail. The flesh was salt all the way through. In the middle, six brown seeds.",1.6)],
[('Kit',"Your kitchen gets the morning sun.",1.6),('Nell',"She pushed five seeds across the table. The sixth she slid into her shirt pocket.",2.6)]
]
sr=24000
parts=[]; timeline=[]; caps=[]; clock=0
def append(a):
    global clock
    parts.append(a)
    clock+=len(a)/sr
def rest(s):
    append(np.zeros(round(sr*s),dtype='float32'))
for i,lines in enumerate(scenes):
    start=clock
    rest(3.6 if i==0 else .85)
    for who,line,pause in lines:
        a=np.concatenate([np.asarray(x.audio) for x in p(line,voice=voices[who],speed=.95 if who=='Nell' else 1.01)]).astype('float32')
        caps.append(dict(start=clock,end=clock+len(a)/sr,text=line,speaker=who))
        append(a); rest(pause)
    if i==8: rest(3)
    timeline.append([start,clock])
a=np.concatenate(parts); t=np.arange(len(a))/sr
rng=np.random.default_rng(17)
from scipy.signal import butter,sosfilt
water=sosfilt(butter(3,680,fs=sr,output='sos'),rng.normal(size=len(t)))
bed=water*(.013+.013*np.sin(2*np.pi*t/5)**2)
for i,(start,end) in enumerate(timeline):
    k=(t>=start)&(t<end); u=t[k]-start
    for j,note in enumerate([50,57,65,69] if i<6 else [53,60,64,69]):
        f=440*2**((note-69)/12)
        z=np.maximum(0,u-j*.91)
        bed[k]+=.022*np.sin(2*np.pi*f*z)*np.exp(-z/3.4)*(1-np.exp(-z*8))
bed*=np.minimum(1,np.minimum(t,len(a)/sr-t)/1.4)
sf.write('/tmp/orchard.wav',np.clip(a*.88+bed,-.99,.99),sr)
subprocess.run(['ffmpeg','-loglevel','error','-y','-i','/tmp/orchard.wav','-b:a','128k',str(out/'sound.mp3')],check=True)
(out/'timing.json').write_text(json.dumps(dict(shots=timeline,captions=caps)))
