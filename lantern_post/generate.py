from kokoro import KPipeline
from pathlib import Path
import numpy as np, soundfile as sf, json
P=Path('lantern_post'); out=P/'audio'; out.mkdir(exist_ok=True)
p=KPipeline(lang_code='a'); voices={'M':p.load_voice('af_nicole'),'R':p.load_voice('am_michael')}
lines=[('M','The tide was early again.'),('M','It left a letter on the steps.'),('R','That one is addressed to the sea.'),('M','Everything here is addressed to the sea.'),('R','Most people use a bottle.'),('M','Most people have never met the sea.'),('R','Is it going to answer?'),('M','It already did.'),('M','Look. The ink has come back.'),('R','What does it say?'),('M','It says: I remember the blue coat.'),('R','That is all?'),('M','Sometimes that is enough.'),('R','Can I leave mine too?'),('M','You can. But you have to let it go.'),('R','I think I can do that.'),('M','Then put it where the water can reach.')]
manifest=[]
for i,(speaker,phrase) in enumerate(lines):
    parts=[]
    for _,_,a in p(phrase,voice=voices[speaker],speed=.94):
        if hasattr(a,'detach'): a=a.detach().cpu().numpy()
        parts.append(np.asarray(a,dtype=np.float32))
    if not parts: raise RuntimeError('empty speech '+phrase)
    a=np.concatenate(parts); n=min(600,len(a)//4); a[:n]*=np.linspace(0,1,n); a[-n:]*=np.linspace(1,0,n)
    name=f'{i:02}.wav'; sf.write(out/name,a,24000)
    manifest.append({'id':i,'speaker':speaker,'text':phrase,'file':'audio/'+name,'duration':round(len(a)/24000,3),'pause':1.05 if i in (1,6,8,12,15) else .55})
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
