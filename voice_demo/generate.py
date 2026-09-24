from kokoro import KPipeline
import soundfile as sf
import numpy as np

text = "Hello Moira. Here is another voice for you to compare."
pipeline = KPipeline(lang_code='a')
voices = ['af_heart','af_bella','af_nicole','am_michael','am_adam']

for voice in voices:
    chunks = []
    for _, _, audio in pipeline(text, voice=voice):
        chunks.append(audio)
    sf.write(f'voice_demo/{voice}.wav', np.concatenate(chunks), 24000)
    print(f'Wrote {voice}')
