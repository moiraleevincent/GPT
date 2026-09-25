from kokoro import KPipeline
import numpy as np, soundfile as sf, json
from pathlib import Path

OUT=Path("sound_film"); OUT.mkdir(exist_ok=True)
SR=24000
p=KPipeline(lang_code="a")
voices={"A":p.load_voice("am_michael"),"B":p.load_voice("af_nicole")}

lines=[
 {"id":"a01","speaker":"A","text":"Tea?","speed":0.90},
 {"id":"b01","speaker":"B","text":"No, thank you.","speed":0.92},
 {"id":"a02","speaker":"A","text":"You always say that after I've filled the kettle.","speed":0.96},
 {"id":"b02","speaker":"B","text":"Then stop filling it for two.","speed":0.90},
 {"id":"a03","speaker":"A","text":"Did you move the blue mug?","speed":0.95},
 {"id":"b03","speaker":"B","text":"Top shelf.","speed":0.92},
 {"id":"a04","speaker":"A","text":"You're taking the big suitcase.","speed":0.90},
 {"id":"b04","speaker":"B","text":"It's raining.","speed":0.90},
 {"id":"a05","speaker":"A","text":"Take the umbrella.","speed":0.90},
 {"id":"b05","speaker":"B","text":"It's yours.","speed":0.88},
 {"id":"a06","speaker":"A","text":"How long?","speed":0.87},
 {"id":"b06","speaker":"B","text":"I don't know.","speed":0.84},
 {"id":"a07","speaker":"A","text":"You forgot your key.","speed":0.88},
 {"id":"b07","speaker":"B","text":"No.","speed":0.80},
]

def render(text,voice,speed):
    chunks=[a for _,_,a in p(text,voice=voice,speed=speed)]
    return np.concatenate(chunks).astype(np.float32)

manifest=[]
for item in lines:
    x=render(item["text"],voices[item["speaker"]],item["speed"])
    fade=min(int(.02*SR),len(x)//5)
    if fade:
        r=np.linspace(0,1,fade,dtype=np.float32); x[:fade]*=r; x[-fade:]*=r[::-1]
    sf.write(OUT/f'{item["id"]}.wav',x,SR)
    manifest.append({**item,"duration":round(len(x)/SR,3),"file":f'{item["id"]}.wav'})
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
