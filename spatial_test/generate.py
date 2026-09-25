from kokoro import KPipeline
import numpy as np, soundfile as sf
from pathlib import Path
SR=24000; OUT=Path("spatial_test"); OUT.mkdir(exist_ok=True)
p=KPipeline(lang_code="a"); v=p.load_voice("af_kore")*.35+p.load_voice("af_nova")*.65
def say(t): return np.concatenate([a for _,_,a in p(t,voice=v,speed=1.08)]).astype(np.float32)
def st(x,pan=0,g=.8):
 l=np.sqrt((1-pan)/2); r=np.sqrt((1+pan)/2); return np.column_stack((x*l*g,x*r*g))
def lp(x,n):
 k=np.ones(n,dtype=np.float32)/n; return np.convolve(x,k,mode="same")
def refl(x,pan,g,refs):
 b=st(x,pan,g); N=len(b)+int(.5*SR); o=np.zeros((N,2),np.float32); o[:len(b)]+=b
 for d,rg,rp,f in refs:
  y=st(lp(x,f),rp,g*rg); i=int(d*SR); o[i:i+len(y)]+=y
 return o
def beside(x):
 # intimate/direct: high direct-to-room ratio, mild ear-to-ear asymmetry, tiny nearby reflection
 return refl(x,-.42,.92,[(.018,.07,-.15,3),(.041,.035,.10,4)])
def across(x):
 # same room: preserve intelligibility, less direct energy, more early wall reflections
 return refl(lp(x,5),.48,.58,[(.032,.18,.22,7),(.071,.15,-.18,9),(.128,.10,.05,11),(.205,.055,-.30,13)])
def nextroom(x):
 # obstruction + mostly diffuse reflected energy; strongly reduced highs
 return refl(lp(x,22),.30,.34,[(.058,.28,.08,26),(.118,.22,-.22,30),(.205,.16,.20,34),(.34,.10,-.12,38)])
def tone(sec):
 n=int(sec*SR); rng=np.random.default_rng(925); q=lp(rng.normal(size=n).astype(np.float32),100)*.009
 t=np.arange(n)/SR; q+=(np.sin(2*np.pi*50*t)*.0018).astype(np.float32); return st(q,0,.7)
lines=["I'm standing here. Tell me where you think I am.","Same voice. Different place. Where am I now?","And one more. Don't think about the effect; think about the room."]
processors=[beside,across,nextroom]
# intentionally permuted so page labels reveal nothing
order=[1,2,0]
for i,idx in enumerate(order,1):
 x=processors[idx](say(lines[i-1])); bed=tone((len(x)/SR)+1.2); bed[int(.55*SR):int(.55*SR)+len(x)]+=x
 sf.write(OUT/f"position_{i}.wav",np.tanh(bed*1.18)*.8,SR)
print("rendered blind spatial test")
