from kokoro import KPipeline
import soundfile as sf
import numpy as np
p=KPipeline(lang_code='a')
narrator=[
"Some stories announce themselves as mysteries. This one did not. It began with an ordinary problem, the kind of problem that disappears into paperwork.",
"Years later, when the paperwork came back, one detail refused to stay small.",
]
secondary=[
"That is where the story changes. Because the version people remember is not quite the version the people who were there described.",
]
ending=["And once you notice that difference, you have to go back to the beginning."]
def make(path, second):
    turns=[('af_nicole',narrator[0]),(second,secondary[0]),('af_nicole',narrator[1]),('af_nicole',ending[0])]
    out=[]; pause=np.zeros(int(24000*.45),dtype=np.float32)
    for v,t in turns:
        chunks=[a for _,_,a in p(t,voice=v)]
        out.extend([np.concatenate(chunks),pause])
    sf.write(path,np.concatenate(out),24000)
make('voice_demo/audition_A.wav','af_heart')
make('voice_demo/audition_B.wav','am_adam')
make('voice_demo/audition_voice2.wav','af_bella')

# generate blind A/B pair

# rerun after output-save fix
