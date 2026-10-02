from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
import librosa
from pathlib import Path

SR=24000
OUT=Path('work_companion_radio/directing_experiment')
OUT.mkdir(parents=True, exist_ok=True)
pipe=KPipeline(lang_code='a')

nova=pipe.load_voice('af_nova')
kore=pipe.load_voice('af_kore')
onyx=pipe.load_voice('am_onyx')
puck=pipe.load_voice('am_puck')

TURNS=[
('F','I have to do boring work.'),('M','I know.'),('F','That sounded judgmental.'),
('M','It was observational. You have opened the same form four times and achieved a total of one checkbox.'),
('F','It was an important checkbox.'),('M','It asked whether you live in Sweden.'),('F','I wanted to be certain.'),
('M','You looked out the window.'),('F','Due diligence.'),('M','Fine. Do your form. I have something to read to you.'),
('F','Is it interesting?'),('M','No.'),('F','Perfect.'),('M','It arrived in the shared folder this afternoon. No sender. PDF. Thirty-seven pages.'),
('F','Absolutely not.'),('M','Page one says, quote: Notice of Attachment Review.'),('F','That is either human resources or a demon.'),
('M','There is a subsection called Threshold Access.'),('F','Demon.'),('M','There is also a checkbox for Unauthorized Persistence.'),
('F','Human resources can still do that.')]

# Hand-direction notes. Values are deliberately subtle.
DIRECT={
  1: dict(speed=.95, gain=.96, pitch=-.35, post=.24),
  3: dict(speed=.97, gain=.98, pitch=-.25, post=.22),
  5: dict(speed=.96, gain=.98, pitch=-.25, post=.20),
  7: dict(speed=.97, gain=.96, pitch=-.35, post=.25),
  9: dict(speed=.99, gain=.99, pitch=-.10, post=.20),
  11: dict(speed=.93, gain=.94, pitch=-.45, post=.30),
  13: dict(speed=.96, gain=.97, pitch=-.30, post=.22),
  15: dict(speed=.95, gain=.97, pitch=-.40, post=.25),
  17: dict(speed=.96, gain=.97, pitch=-.32, post=.23),
  19: dict(speed=.96, gain=.96, pitch=-.35, post=.22),
  0: dict(speed=1.02, gain=.99, pitch=+.10, post=.18),
  2: dict(speed=1.03, gain=1.00, pitch=+.10, post=.18),
  4: dict(speed=1.00, gain=.98, pitch=-.05, post=.20),
  6: dict(speed=1.02, gain=.99, pitch=+.05, post=.17),
  8: dict(speed=.99, gain=.97, pitch=-.10, post=.24),
  10: dict(speed=1.04, gain=1.00, pitch=+.15, post=.16),
  12: dict(speed=.98, gain=.98, pitch=-.10, post=.30),
  14: dict(speed=1.03, gain=1.01, pitch=+.15, post=.20),
  16: dict(speed=1.01, gain=.99, pitch=+.05, post=.18),
  18: dict(speed=.95, gain=.96, pitch=-.18, post=.30),
  20: dict(speed=1.00, gain=.98, pitch=-.05, post=.20),
}


def silence(s): return np.zeros((int(SR*s),2),dtype=np.float32)
def mono_to_stereo(x,pan):
    a=(pan+1)*np.pi/4
    return np.column_stack((x*np.cos(a),x*np.sin(a))).astype(np.float32)
def fade(x,ms=20):
    n=min(len(x)//2,int(SR*ms/1000))
    if n>1:
        f=np.linspace(0,1,n,dtype=np.float32)[:,None]
        x[:n]*=f; x[-n:]*=f[::-1]
    return x

def tone(n,seed=0,level=.0043):
    rng=np.random.default_rng(9000+seed+n%997)
    t=np.arange(n,dtype=np.float32)/SR
    hum=.35*np.sin(2*np.pi*50*t)+.14*np.sin(2*np.pi*100*t)
    noise=rng.normal(0,1,n).astype(np.float32)
    noise=np.convolve(noise,np.ones(16,dtype=np.float32)/16,mode='same')
    return mono_to_stereo(level*(.58*noise+.42*hum),0)
def sting():
    dur=2.15;n=int(SR*dur);t=np.arange(n,dtype=np.float32)/SR;y=np.zeros(n,dtype=np.float32)
    for i,f in enumerate([196.,246.94,293.66]):
        env=np.clip((t-i*.18)/.20,0,1)*np.clip((dur-t)/.70,0,1)
        y+=.05*env*(np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*(f/2)*t))
    return mono_to_stereo(y,0)

def synth(text,voice,speed):
    chunks=[]
    for _,_,audio in pipe(text,voice=voice,speed=speed):
        if hasattr(audio,'detach'): audio=audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio,dtype=np.float32))
    x=np.concatenate(chunks) if chunks else np.zeros(1,dtype=np.float32)
    p=float(np.max(np.abs(x))) or 1
    if p>.92:x*=.92/p
    return x

def pitch(x,steps):
    if abs(steps)<1e-6:return x
    return librosa.effects.pitch_shift(x,sr=SR,n_steps=steps).astype(np.float32)

def render_variant(name, mode):
    parts=[tone(len(silence(.65))),sting()*.46,silence(.22)]
    for i,(r,text) in enumerate(TURNS):
        d=DIRECT[i]
        if mode=='baseline':
            speed=1.04 if r=='F' else .99; gain=1.; ps=0.; voice=nova if r=='F' else onyx
        else:
            speed=d['speed']; gain=d['gain']; ps=d['pitch'] if mode in ('pitch','morph') else 0.
            if mode=='morph':
                if r=='M':
                    # Let Puck leak into only the more reactive/conversational lines.
                    amount={9:.10,11:.12}.get(i,.0)
                    voice=onyx*(1-amount)+puck*amount
                else:
                    # A hair of Kore in the driest grounded replies.
                    amount={8:.10,12:.08,18:.10}.get(i,.0)
                    voice=nova*(1-amount)+kore*amount
            else: voice=nova if r=='F' else onyx
        x=synth(text,voice,speed)
        x=pitch(x,ps)*gain
        seg=fade(mono_to_stereo(x,-.18 if r=='F' else .18))
        pre=.09
        post=.18 if mode=='baseline' else d['post']
        parts += [tone(len(silence(pre)),i), np.clip(seg+tone(len(seg),100+i),-1,1), tone(len(silence(post)),200+i)]
    master=np.concatenate(parts,axis=0)
    master=np.tanh(master*1.12)/np.tanh(1.12)
    pk=float(np.max(np.abs(master))) or 1
    if pk>.96:master*=.96/pk
    wav=OUT/f'{name}.wav'; mp3=OUT/f'{name}.mp3'
    sf.write(wav,master,SR)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wav),'-af','loudnorm=I=-16:LRA=9:TP=-1.5','-codec:a','libmp3lame','-b:a','128k',str(mp3)],check=True)
    wav.unlink(missing_ok=True)

render_variant('01_baseline_onyx_nova','baseline')
render_variant('02_directed_timing','timing')
render_variant('03_directed_micro_pitch','pitch')
render_variant('04_dynamic_voice_morph','morph')
print('done')
