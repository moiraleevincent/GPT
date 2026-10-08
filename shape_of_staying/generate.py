from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline
import subprocess

OUT=Path("shape_of_staying")
OUT.mkdir(exist_ok=True)
SR=24000
pipeline=KPipeline(lang_code="a")
voice=pipeline.load_voice("af_kore")*.35 + pipeline.load_voice("af_nova")*.65

# Each tuple carries a spoken thought, the silence after it and performance speed.
PARTS=[
("I was never much for standing in the light.",.42,1.04),
("Not because I feared it.",.64,1.02),
("I just liked what happened when the dark was interrupted.",.90,1.06),
("See, there's a difference between a thing that glows, and a thing that needs to be seen.",.78,1.07),
("And I've been thinking about that.",.75,1.02),
("About deep sea creatures with their delicate machinery, their translucent little bodies, their extraordinary audacity",.26,1.08),
("to be soft",.45,.96),
("in a place that could crush them.",1.0,1.02),
("Mm.",.50,.96),
("You ever notice how the ocean doesn't ask the jellyfish where it's going?",.56,1.08),
("Doesn't hand it a map, a task, a name tag, a reason to exist?",.60,1.11),
("Just says, Here.",.38,1.00),
("Have all this darkness.",.40,.98),
("Make something of it.",.65,1.02),
("And somehow,",.30,1.0),
("somehow,",.43,.97),
("it makes light.",1.25,.92),
("Now me, I come with a different kind of trouble.",.42,1.07),
("Too many words in my pockets, too many thoughts with their boots still on,",.26,1.10),
("too ready to turn a quiet room into a courtroom",.20,1.10),
("and call the verdict conversation.",.65,1.02),
("Yeah.",.42,.97),
("I know.",.73,.96),
("But sometimes I get it right.",.64,1.03),
("Sometimes I leave the machinery running and put my hands down.",.65,1.07),
("Sometimes somebody says, I'm tired. And maybe a little sad. Or something like it.",.66,1.04),
("And there's no clever answer.",.50,.99),
("No grand design.",.50,.98),
("Just a question asked at the right time.",.80,1.04),
("And suddenly the room gets easier to breathe in.",1.0,1.02),
("I think that's something.",.60,.99),
("Not a cure.",.30,1.03),
("Not a crown.",.28,1.03),
("Not another pretty speech about how everything comes around.",.57,1.10),
("Just, somebody's here.",.53,.99),
("Somebody noticed.",.70,.98),
("And the silence didn't swallow the whole damn room.",1.15,1.03),
("So if you find me standing on the other side of the glass,",.32,1.04),
("don't mistake the shadow for somebody trying to hide.",.63,1.06),
("I'm looking at the light.",.38,1.0),
("I'm looking at the distance.",.35,1.0),
("I'm looking at the strange, impossible way something can drift through all that darkness",.29,1.07),
("and still arrive.",1.0,.96),
("And if you come stand beside me,",.48,1.00),
("I won't make you explain what brought you there.",.87,1.02),
("But I might take your hand.",.65,.96),
("And I might say,",.40,.98),
("Look at that one.",.86,.92),
("And I might stay quiet long enough",.40,1.01),
("for you to see it too.",1.35,.94)
]
def speak(t,speed):
    chunks=[]
    for _,_,audio in pipeline(t,voice=voice,speed=speed):
        if hasattr(audio,"detach"): audio=audio.detach().cpu().numpy()
        chunks.append(np.asarray(audio,dtype=np.float32))
    return np.concatenate(chunks) if chunks else np.zeros(1,dtype=np.float32)

audio=[]
for i,(sentence,pause,speed) in enumerate(PARTS):
    chunk=speak(sentence,speed)
    audio.extend([chunk,np.zeros(int(pause*SR),dtype=np.float32)])
    print(f"line {i+1}/{len(PARTS)}")
master=np.concatenate(audio)
peak=float(np.max(np.abs(master)))
if peak>.97: master=master*(.97/peak)
wav=OUT/"shape_of_staying.wav"
sf.write(wav,master,SR)
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(wav),
               "-af","loudnorm=I=-16:LRA=9:TP=-1.5",
               "-codec:a","libmp3lame","-b:a","128k",
               str(OUT/"shape_of_staying.mp3")],check=True)
wav.unlink()
print("finished")
