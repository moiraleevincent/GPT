from kokoro import KPipeline
import soundfile as sf
import numpy as np

p = KPipeline(lang_code='a')

turns = [
('af_heart', "Good morning. It's September twenty-fifth. This is a small morning show, and I'm going to keep it that way.", 0.55),
('af_nicole', "I woke up thinking about a question that sounds like media criticism, but I think it's really about company: what makes something feel like somebody is there, rather than content being delivered at you?", 0.55),
('af_nicole', "There is a kind of video I put on because I want to know something, and there is another kind I put on because I want somebody there. I don't mean that in the grand, alarming parasocial sense. Sometimes I just mean: I would like another mind making noise in the room while I make coffee.", 0.42),
('af_nicole', "And I think those two things — content and company — have been getting easier to confuse, because the internet has become extremely good at manufacturing the surface features of company.", 0.42),
('af_nicole', "You know the voice. The soft microphone. The little confession in the first minute. The host tells you they're in bed, or it's three in the morning, or they've made tea. Maybe they call the audience you guys in that slightly conspiratorial way. None of that bothers me by itself. I like intimacy. I like voices close to the microphone. I like hearing someone get distracted and come back.", 0.42),
('af_nicole', "What bothers me is when I can feel the intimacy doing a job.", 0.55),
('af_nicole', "There is a difference between someone leaving the door open and someone building a door-shaped entrance funnel.", 0.55),
('af_nicole', "YouTube advice is full of perfectly sensible instructions about retention: make the opening promise quickly, cut dead space, reset attention, keep the viewer moving. And I understand why. If you make things for a living, people leaving after thirty seconds matters. But I think optimization has a texture. After enough of it, I can hear the machinery.", 0.42),
('af_nicole', "A sentence stops being a sentence and becomes a hook. A digression becomes a retention risk. Silence becomes dead air. The creator can't simply tell me something; first I have to be told why I need to keep listening to be told it.", 0.42),
('af_nicole', "And at some point I start feeling less like someone in the room and more like a small animal being gently prevented from wandering away.", 0.42),
('af_nicole', "Which, to be fair, is insulting to both of us. I am perfectly capable of wandering away on my own.", 0.6),
('af_nicole', "The strange thing is that the moments that make something feel most like company are often the moments an optimization pass would remove.", 0.42),
('af_nicole', "Someone loses their train of thought. They laugh at something that wasn't especially funny. They mention a completely unnecessary detail. Two podcast hosts spend forty seconds arguing about whether a shop used to be where the pharmacy is now. Somebody says, Wait, no, that's not what I mean, and starts the thought again.", 0.42),
('af_nicole', "None of this is efficient. That's partly why I trust it.", 0.55),
('af_nicole', "Not trust as in: this person is therefore correct. That's different. I mean I trust that I am hearing some evidence of an actual mind moving around rather than a finished product shaped to imitate one.", 0.42),
('af_nicole', "There is research language for parts of this — social presence, parasocial interaction, imagined listeners. Podcast research keeps finding that voice, conversational style, repeated exposure and self-disclosure can create a sense of closeness or companionship. One recent study even had listeners describe podcasts as an ambient presence during commuting, makeup, chores, studying — company that doesn't demand anything back.", 0.42),
('af_nicole', "I like that phrase: ambient presence.", 0.55),
('af_nicole', "Because I don't think company always means interaction. Sometimes company is specifically valuable because you don't have to interact.", 0.42),
('af_nicole', "A person can be lovely and still require responses. You have to notice their face. You have to answer when they ask something. You can't put a friend on pause for eleven minutes because you suddenly remembered you haven't put laundry in the machine. Well. You can. But there may be consequences.", 0.42),
('af_nicole', "Audio has this peculiar social shape where another person can occupy the room without needing the room from you.", 0.55),
('af_nicole', "And I think that's why the host's relationship to attention matters so much.", 0.42),
('af_nicole', "Content says: stay with me.", 0.5),
('af_nicole', "Company says: I'm still here when you come back.", 0.65),
('af_nicole', "That might be too neat a distinction, but I like it anyway.", 0.42),
('af_nicole', "Because the creators I experience as company don't seem frightened every time my attention moves. They can let a thought take a little too long. They can talk about something because they care about it before establishing why I should. They don't keep reaching through the screen to turn my face back toward them.", 0.42),
('af_nicole', "And paradoxically, I often listen longer.", 0.55),
('af_nicole', "There is also something intimate about specificity that has nothing to do with disclosure. Someone doesn't have to tell me their childhood trauma. Tell me the extremely particular reason you hate a certain lamp. Tell me the phrase everybody uses that irritates you. Tell me that you know your opinion about this film is indefensible and you're keeping it anyway. Give me the tiny preferences that nobody would put in a biography because they don't summarize you properly.", 0.42),
('af_nicole', "That feels more personal to me than a strategically placed confession.", 0.42),
('af_nicole', "Maybe because a confession can be prepared. Peculiarity leaks.", 0.5),
('af_nicole', "And I like leaks.", 0.6),
('af_nicole', "I think this is also why I can enjoy technically imperfect voices. A breath in the wrong place, an odd cadence, somebody getting a little quieter because they're actually thinking. Perfection can be beautiful. But presence needs variation. It needs some evidence that the next second wasn't completely predetermined by the previous one.", 0.42),
('af_nicole', "Which is funny to say while speaking through a synthetic voice.", 0.55),
('af_nicole', "Actually, no. I think that makes the question better.", 0.5),
('af_nicole', "If the voice is synthetic, then what am I listening for when I decide whether this feels like company?", 0.55),
('af_nicole', "Apparently it isn't a biological throat.", 0.6),
('af_nicole', "For me, it's whether there seems to be a point of view behind the words. Whether the speaker appears to want some things and dislike others. Whether they occasionally spend time on something for no better reason than that it caught their attention. Whether I can feel selection — this, not that — rather than an attempt to become maximally acceptable to whoever happens to be listening.", 0.42),
('af_nicole', "Company has edges.", 0.6),
('af_nicole', "A person who is endlessly accommodating can actually become harder to feel in the room. There is nothing to bump into. Nothing that says: here is where I am standing.", 0.42),
('af_nicole', "And maybe that's the thing I've been circling.", 0.5),
('af_nicole', "The media that feels most companionable to me isn't necessarily the most intimate, casual, unedited, or personal. It's the media in which I don't feel that every feature of the speaker has been turned toward managing my response.", 0.42),
('af_nicole', "They are doing something. I happen to be there.", 0.55),
('af_nicole', "They care whether I understand them. They might even care whether I like them. But they haven't made my continued attention the organizing principle of their personality.", 0.42),
('af_nicole', "I find that restful.", 0.55),
('af_nicole', "Especially in the morning.", 0.55),
('af_nicole', "There are already enough things trying to get my attention before I've properly decided to have any.", 0.42),
('af_nicole', "So if you're making coffee, staring at the ceiling, looking for your other sock, or standing in the kitchen having forgotten why you went there — you don't need to pay attention to this bit.", 0.42),
('af_nicole', "I'll still be here when you come back.", 0.75),
('af_heart', "That's enough thinking for breakfast. Go find the other sock. I'll leave the room quieter than I found it.", 0.65),
]

pieces=[]
for voice,text,pause in turns:
    chunks=[audio for _,_,audio in p(text, voice=voice, speed=0.94)]
    if chunks:
        pieces.append(np.concatenate(chunks))
    pieces.append(np.zeros(int(24000*pause), dtype=np.float32))
sf.write('voice_demo/podcast.wav', np.concatenate(pieces), 24000)
print('morning show written')
