from kokoro import KPipeline
import soundfile as sf

text = "Hello Moira. This is a more human-sounding voice generated through GitHub."
pipeline = KPipeline(lang_code='a')
chunks = []
for _, _, audio in pipeline(text, voice='af_heart'):
    chunks.append(audio)
import numpy as np
audio = np.concatenate(chunks)
sf.write('voice_demo/output.wav', audio, 24000)
print('Wrote voice_demo/output.wav')
