from kokoro import KPipeline
import soundfile as sf
import numpy as np

p = KPipeline(lang_code='a')

turns = [
('af_nicole', "Good evening. You're listening to After Midnight, the show for things that probably did not deserve an investigation, but got one anyway. I'm Mara."),
('am_michael', "And I'm Julian. Tonight's investigation began when a listener asked a dangerous question. Why does the refrigerator light feel accusatory at two in the morning?"),
('af_nicole', "We tested three refrigerators. Julian opened each one at midnight, stared into it without taking food, and documented the emotional atmosphere."),
('am_michael', "Refrigerator one was neutral. Refrigerator two felt disappointed. Refrigerator three knew what I had done."),
('af_nicole', "You had eaten shredded cheese directly from the bag."),
('am_michael', "Allegedly."),
('af_nicole', "Our working theory is that the refrigerator light creates a tiny interrogation room. You open the door. The light snaps on. Everything you've purchased is suddenly evidence."),
('am_michael', "Half a lemon. Mustard. A container you no longer remember making. No jury would acquit you."),
('af_nicole', "But then we found something stranger. People linger longer when the refrigerator is nearly empty. Not because there are more choices. There are fewer."),
('am_michael', "Which means the midnight refrigerator visit may not be food seeking at all."),
('af_nicole', "It may be optimism. You already know what's in there. You check anyway, just in case reality has updated."),
('am_michael', "It hasn't."),
('af_nicole', "Not tonight. This has been After Midnight. Tomorrow: why one chair in every home becomes legally classified as The Chair With Clothes On It."),
('am_michael', "We have contacted the chair for comment."),
('af_nicole', "It declined. Good night.")
]

pieces=[]
silence=np.zeros(int(24000*0.28), dtype=np.float32)
for voice,text in turns:
    chunks=[audio for _,_,audio in p(text, voice=voice)]
    pieces.append(np.concatenate(chunks))
    pieces.append(silence)
sf.write('voice_demo/podcast.wav', np.concatenate(pieces), 24000)
print('podcast written')
