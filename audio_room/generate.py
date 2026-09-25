from kokoro import KPipeline
import numpy as np
import soundfile as sf
from pathlib import Path

SR=24000
OUT=Path("audio_room")
OUT.mkdir(exist_ok=True)
p=KPipeline(lang_code="a")
kore=p.load_voice("af_kore")
nova=p.load_voice("af_nova")
voice=kore*.35+nova*.65

def say(text,speed=1.08):
    chunks=[a for _,_,a in p(text,voice=voice,speed=speed)]
    return np.concatenate(chunks).astype(np.float32)

def stereo(mono,pan=0.0,gain=1.0):
    # constant-power-ish pan
    l=np.sqrt((1-pan)/2); r=np.sqrt((1+pan)/2)
    return np.column_stack((mono*l*gain,mono*r*gain))

def lowpass(x,window=18):
    k=np.ones(window,dtype=np.float32)/window
    return np.convolve(x,k,mode="same")

def distant(mono,pan=.55,gain=.46):
    dry=lowpass(mono,14)
    base=stereo(dry,pan,gain)
    # early reflections: increasingly diffuse and slightly opposite in pan
    out=np.zeros((len(base)+int(.34*SR),2),dtype=np.float32)
    out[:len(base)]+=base
    for delay,g,pn in [(.055,.22,.25),(.105,.16,-.10),(.185,.10,-.35),(.29,.07,.10)]:
        s=stereo(lowpass(mono,20),pn,gain*g)
        i=int(delay*SR); out[i:i+len(s)]+=s
    return out

def roomtone(seconds):
    n=int(seconds*SR)
    rng=np.random.default_rng(25)
    # very quiet shaped noise + low electrical/room hum
    noise=rng.normal(0,1,n).astype(np.float32)
    noise=lowpass(noise,80)*.018
    t=np.arange(n)/SR
    hum=(np.sin(2*np.pi*50*t)*.0025+np.sin(2*np.pi*100*t)*.0012).astype(np.float32)
    return stereo(noise+hum,0,.75)

def knock():
    # two soft table/glass-like taps, located right
    n=int(.7*SR); t=np.arange(n)/SR
    x=np.exp(-t*22)*(np.sin(2*np.pi*620*t)+.35*np.sin(2*np.pi*1220*t))*.07
    x[int(.24*SR):]+=np.pad(x[:n-int(.24*SR)]*.55,(0,int(.24*SR)))[:n-int(.24*SR)]
    return stereo(x.astype(np.float32),.62,.8)

events=[]
def add(at,a): events.append((at,a))

# A tiny piece designed around perceived space, not exposition.
add(1.2, stereo(say("I wanted to know whether a voice could have a place."),-.18,.92))
add(5.7, knock())
add(7.0, stereo(say("That was over there."),-.12,.90))
add(10.0, distant(say("No. I'm over here."),.62,.48))
add(13.3, stereo(say("...Right."),-.15,.88))
add(15.1, stereo(say("That's unpleasantly convincing."),-.15,.90))
add(19.2, distant(say("You asked for a room."),.58,.46))
add(22.5, stereo(say("I did."),-.12,.88))
add(24.0, stereo(say("I hadn't considered that the room might answer."),-.12,.90))
add(29.0, distant(say("You usually don't."),.48,.42))
add(32.8, knock())
add(34.3, stereo(say("Okay. Keep your side of it."),-.15,.88))
add(38.2, distant(say("It's the same room."),.48,.40))
add(42.0, stereo(say("That's worse."),-.15,.88))
add(45.5, distant(say("I know."),.35,.36))

length=50
mix=roomtone(length)
for at,a in events:
    i=int(at*SR)
    end=min(len(mix),i+len(a))
    mix[i:end]+=a[:end-i]

# soft limiter
mix=np.tanh(mix*1.25)*.78
sf.write(OUT/"the_room.wav",mix,SR)
print("wrote",OUT/"the_room.wav")
