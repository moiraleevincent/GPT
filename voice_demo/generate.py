from kokoro import KPipeline
import soundfile as sf
import numpy as np

pipeline = KPipeline(lang_code='a')

samples = {
'af_heart': "Hello Moira. Here is another voice for you to compare.",
'af_bella': "Hello Moira. Here is another voice for you to compare.",
'af_nicole': "Hello Moira. Here is another voice for you to compare.",
'am_michael': "Hello Moira. Here is another voice for you to compare.",
'am_adam': "Hello Moira. Here is another voice for you to compare.",
}

for voice, text in samples.items():
    chunks=[audio for _,_,audio in pipeline(text, voice=voice)]
    sf.write(f'voice_demo/{voice}.wav', np.concatenate(chunks), 24000)

news = """Good afternoon. This is your short news update for September twenty-fourth.
U.S. President Donald Trump is hosting Chinese President Xi Jinping in Washington today, with trade and the wider U.S.-China relationship at the center of attention.
In technology, new computer science graduates are increasingly emphasizing artificial intelligence skills as they enter a difficult software job market.
And from the Vatican, Pope Leo has highlighted concerns about the potentially catastrophic risks of advanced artificial intelligence.
That's the brief. Thanks for listening."""
chunks=[audio for _,_,audio in pipeline(news, voice='af_heart')]
sf.write('voice_demo/news.wav', np.concatenate(chunks), 24000)
print('Done')
