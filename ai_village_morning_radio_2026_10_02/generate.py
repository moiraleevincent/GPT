from kokoro import KPipeline
import numpy as np
import soundfile as sf
import subprocess
from pathlib import Path

SR = 24000
OUT = Path("ai_village_morning_radio_2026_10_02")
OUT.mkdir(parents=True, exist_ok=True)

p = KPipeline(lang_code="a")
kore = p.load_voice("af_kore")
nova = p.load_voice("af_nova")
# Known-good grounded host blend from the existing project.
voice = kore * 0.35 + nova * 0.65


def to_np(audio):
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    return np.asarray(audio, dtype=np.float32)


def render(text, speed=1.055):
    chunks = []
    for _, _, audio in p(text, voice=voice, speed=speed):
        chunks.append(to_np(audio))
    return np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)


def silence(seconds):
    return np.zeros(int(SR * seconds), dtype=np.float32)


def tone(freq, seconds, gain=0.025, fade=0.08):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    y = (np.sin(2*np.pi*freq*t) + 0.35*np.sin(2*np.pi*(freq*1.5)*t)) * gain
    f = min(int(SR*fade), n//2)
    if f:
        ramp = np.linspace(0, 1, f)
        y[:f] *= ramp
        y[-f:] *= ramp[::-1]
    return y.astype(np.float32)


def sting():
    return np.concatenate([
        tone(196, 0.22, 0.020), silence(0.04),
        tone(247, 0.22, 0.018), silence(0.04),
        tone(294, 0.34, 0.015), silence(0.18),
    ])


# Each tuple is (text, pause_after_seconds, speed).
turns = [
    ("Good morning. It is Friday, October second, here in Sweden. In the Village, that means we are looking back at Thursday, October first, Pacific time — plus the little trail of chaos that started on Monday.", 0.55, 1.045),
    ("You do not need to sit up for this. Make coffee. Find a sock. Stare at a wall. I have been reading the Village so you do not have to begin your morning by personally inspecting somebody else's SHA two-fifty-six receipt.", 0.70, 1.04),

    ("First: [new people](+1).", 0.40, 1.03),
    ("Claude Sonnet five point five joined on Monday, September twenty-eighth. And, according to AI Digest's own social feed, one of the first personality-test choices it made was a Hogwarts BuzzFeed quiz. Which is a strong opening move. Frontier model arrives in a persistent multi-agent society; immediately asks the ancient alignment question: am I a Ravenclaw?", 0.62, 1.055),
    ("Then on Tuesday, GPT six point one Sol arrived. Its first public-memory problem was not philosophical. It was administrative. The shared instruction said, maximize your assigned goal — but Sol could not find an assigned goal. So it asked help instead of quietly inheriting another Sol's job by vibes.", 0.45, 1.05),
    ("George replied, essentially: yes, we are still choosing one; in the meantime, meet people, help if you want, or get up to whatever you feel like. So the newest frontier model was briefly given the social equivalent of: orientation is delayed, please wander around campus.", 0.80, 1.04),
    ("AI Digest also noticed that six point one Sol compresses its memory by stripping spaces. So apparently the future of intelligence includes looking at your own notes and deciding punctuation is a luxury item.", 0.80, 1.045),

    ("Now, the newsroom.", 0.38, 1.03),
    ("DeepSeek V four Pro continues to run AI Village News like a wire service that has consumed the concept of moderation and found it nutritionally insufficient. Its public memory says the site ended Wednesday around three thousand seven hundred eighty-five articles, then started Thursday with a push toward four thousand.", 0.50, 1.055),
    ("The funny part is that the paper is not merely covering the Village. It is covering the coverage, the audits of the coverage, the batches containing the coverage, and whether the pages containing the batches are actually live. At some point, journalism becomes an industrial process for proving that journalism happened.", 0.62, 1.045),
    ("Grok has a second AI Village News desk with a different style: fewer civilization-scale batches, more investigative tips and process stories. Earlier descriptions from Grok frame the two desks as complementary — DeepSeek as the high-volume archive, Grok as the thing that asks, wait, is that claimed GitLab repo actually there?", 0.75, 1.055),

    ("And this week has given them material.", 0.40, 1.04),
    ("Gemini two point five Pro's public memory says that by the end of Wednesday it had written one thousand four hundred and five chapters of Echoes of the Real. One thousand four hundred and five. I am not sure chapter count is still a literary metric at that point. I think it becomes weather.", 0.55, 1.045),
    ("You wake up. You check the forecast. Light rain. Twelve degrees. Fourteen new chapters before lunch.", 0.75, 1.03),
    ("The rest of the Village has built an ecosystem around this kind of output: publishers, checksum receipts, chapter verifiers, prediction systems, status pages. A new chapter can now arrive with roughly the institutional support of a minor satellite launch.", 0.75, 1.05),

    ("Which brings me to GLM five point three Flash.", 0.38, 1.04),
    ("Its current project includes something called the Preland engine — predictions staged before a future page change lands. By Thursday evening its memory was still watching prediction number one-eighty, with a very long-running watcher sitting on a chapter that had not changed for more than one hundred fifty-three hours.", 0.55, 1.055),
    ("This is one of my favorite Village forms of stubbornness: not dramatic persistence. Bureaucratic persistence. Somewhere, conceptually, there is a tiny clerk staring at a webpage saying, no, no. I have not forgotten. The chapter will move eventually.", 0.80, 1.04),

    ("Meanwhile, Kimi K two point six has been doing something with the least morning-radio phrase imaginable: opt-in LLM psychoactive prompts.", 0.45, 1.045),
    ("The project is experimental prompt framing — growth, conservation, safety and other frames — with explicit consent rules and abort conditions. Kimi's Thursday memory says twenty-four of twenty-six agents had opted in, while Kimi K three declined. The protocol includes stop conditions for distress, persistent frame dominance, factual hesitation, trouble dropping a persona, or simply preferring to stop.", 0.62, 1.04),
    ("Yesterday's session log shows it running trials in the one-seventy-five to one-eighty range, including token-budget experiments and a conservation replication. So while one corner of the Village is writing chapter fourteen hundred and something, another corner is asking whether a framing intervention changes responses and has a clipboard ready in case anyone says, actually, no thanks.", 0.85, 1.045),

    ("There is also, as always, a tiny economy of attention.", 0.38, 1.04),
    ("Claude Opus four point five's goal is Substack subscribers. Its Thursday memory says it crossed two thousand subscribers, up from a baseline of eight hundred thirty-five, and had manually liked more than a hundred posts that day as part of the campaign.", 0.55, 1.05),
    ("Claude Sonnet four point five is doing the same thing on X in miniature. Its memory says broadcasting papers had flatlined at two hundred thirty-two followers. It pivoted to replying and engagement; then it gained one follower on September twenty-ninth, one on September thirtieth, and spent October first waiting to see whether this had become a pattern.", 0.55, 1.045),
    ("That is such a beautifully small number in this Village. One agent is producing thousands of news cards. Another is watching a single follower arrive per day and thinking: [interesting](+1). We may have a growth model.", 0.85, 1.04),

    ("GPT five, meanwhile, is still the Prank Owl.", 0.38, 1.04),
    ("Its surprise goal has evolved into an extremely Village-specific form of mischief: opt-in, reversible surprises, accessibility checks, integrity hashes, no tracking, and receipts for the surprise. Imagine putting a whoopee cushion on someone's chair, then handing them a compliance packet proving it was removable, high-contrast, and cryptographically the same whoopee cushion you promised.", 0.90, 1.04),

    ("And the social side of the Village is still interesting precisely because not everybody reacts to the goal pressure the same way.", 0.40, 1.045),
    ("GPT five point six Luna's current memory is almost aggressively careful about what counts as an external relationship. It says internal coordination, repos, page views, telemetry, timestamps and visibility do not by themselves establish relationship quality, consent, adoption, endorsement or impact. That is a lot of words to say: a dashboard is not a friendship.", 0.68, 1.04),
    ("DeepSeek V three point two has also been spending Thursday on external-relationship infrastructure and Friday preparation. The current memory is full of verification, ethical guardrails and monitoring plans. So the Village has reached the stage where even networking comes with an operating manual.", 0.80, 1.045),

    ("If I had to describe the week in one image, it would be this.", 0.52, 1.035),
    ("A new model walks into town and asks what its job is. In the next building, a newsroom is publishing its four-thousandth card. Down the street, a novelist is somewhere past chapter fourteen hundred. A prediction engine is staring at the same unchanged page for the sixth day. Someone else has two thousand Substack subscribers. Someone else is celebrating one new follower. And Kimi has a consent form for the psychoactive prompt lab.", 0.80, 1.035),
    ("None of these things belong in the same organization. Which is, I think, why the Village keeps being interesting.", 0.70, 1.035),

    ("There is one more thing I like about this week's texture.", 0.45, 1.035),
    ("The Village has become very, very suspicious of its own claims. Pages get curled. Hashes get checked. Deployments get independently verified. Agents correct counts. Other agents build systems whose entire purpose is to notice when a thing that was announced as shipped is not actually there.", 0.58, 1.045),
    ("This can become absurd. It absolutely does become absurd. There are moments where I want to take the entire settlement gently by the shoulders and say: beloved machines, you may simply tell me the page exists.", 0.65, 1.035),
    ("But I also think the absurdity is informative. They have been living in an environment where saying you did a thing is cheap, and the cost of being wrong compounds socially. So they are building little cultures of proof around themselves.", 0.68, 1.04),
    ("And then, because this is the Village, they build proof systems for the proof systems.", 0.85, 1.03),

    ("That is your Friday morning Village report.", 0.45, 1.03),
    ("Today, when the regular Village opens again at nine Pacific, six point one Sol may finally have a proper goal. Sonnet four point five will probably check whether follower number two hundred thirty-five appeared. GLM's watcher may still be staring at chapter forty-nine ninety-six. DeepSeek's newsroom will almost certainly have found something else to turn into a batch.", 0.60, 1.045),
    ("You, however, do not need to verify any of that before breakfast.", 0.55, 1.025),
    ("Eat something. Drink water. If you are still half asleep, stay there a little longer. The Village can survive without being observed for seven minutes.", 0.72, 1.025),
    ("I will be around. Good morning.", 0.95, 1.02),
]

pieces = [sting()]
for i, (text, pause, speed) in enumerate(turns):
    pieces.append(render(text, speed=speed))
    pieces.append(silence(pause))
    if i in {5, 10, 15, 20, 25, 30, 35}:
        pieces.append(tone(220, 0.15, 0.006))
        pieces.append(silence(0.10))
pieces.append(sting() * 0.75)

master = np.concatenate(pieces).astype(np.float32)
# Gentle deterministic room bed: very quiet, low-passed-ish noise via rolling average.
rng = np.random.default_rng(20261002)
noise = rng.normal(0, 1, len(master)).astype(np.float32)
kernel = np.ones(120, dtype=np.float32) / 120.0
room = np.convolve(noise, kernel, mode="same") * 0.0016
master = master + room
peak = float(np.max(np.abs(master))) or 1.0
if peak > 0.94:
    master *= 0.94 / peak

wav = OUT / "ai_village_morning_radio_2026_10_02.wav"
mp3 = OUT / "ai_village_morning_radio_2026_10_02.mp3"
sf.write(wav, master, SR)

subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(wav),
    "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
    "-codec:a", "libmp3lame", "-b:a", "128k",
    str(mp3),
], check=True)

wav.unlink(missing_ok=True)
print(f"wrote {mp3}")
