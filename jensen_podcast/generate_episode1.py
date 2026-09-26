from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
from pathlib import Path

SR = 24000
OUTDIR = Path("jensen_podcast")
OUTDIR.mkdir(exist_ok=True)

VOICE_NAMES = {'HOST': 'af_heart', 'JUDGE': 'am_michael', 'MCNEILL': 'af_bella', 'PROSECUTOR': 'af_bella', 'RENNER': 'af_sarah', 'KRAUSE': 'af_nicole', 'JAMBOIS': 'am_adam'}
SPEEDS = {'HOST': 1.04, 'JUDGE': 0.96, 'MCNEILL': 1.0, 'PROSECUTOR': 1.0, 'RENNER': 1.0, 'KRAUSE': 1.02, 'JAMBOIS': 0.99}
TURNS = [('SFX', 'COLD OPEN — quiet courtroom room tone. No music yet.'),
 ('JUDGE',
  'Ladies and gentlemen, opening statements are not evidence. They are an opportunity for the lawyers to tell you what '
  'they believe the evidence will show.'),
 ('MCNEILL',
  'This is Julie Jensen. She was thirty-nine years old when she died. The evidence will show that the defendant '
  'murdered his wife with ethylene glycol, and that this was not suicide.'),
 ('RENNER',
  "What brings us here today is Julie Jensen's suicide. And at the end of this trial, the question is whether the State "
  'proved beyond a reasonable doubt that Mark Jensen caused her death.'),
 ('HOST',
  'Same courtroom. Same dead woman. Same chemical in her body. Two opening statements, and almost nothing else in '
  'common. Welcome to The Record. This series is going to follow State of Wisconsin versus Mark Jensen one trial day at '
  'a time, because this case gets worse when you flatten it into a true-crime summary. Day One is about promises: what '
  'each side tells the jury it will prove, what the judge tells the jury not to mistake for proof, and the first '
  'evidentiary fights that show us what kind of trial this is going to be.'),
 ('HOST',
  'A note on the courtroom clips you will hear: I am using dramatized readings from the trial transcript, with different '
  "synthetic voices for the speakers. These are not recordings of the real people. When I quote or closely paraphrase an "
  "opening statement, remember the judge's instruction: an opening is advocacy, not evidence."),
 ('SFX', 'TITLE STING — restrained, two seconds. Then dry host voice.'),
 ('HOST', 'Episode One: Openings Are Not Evidence.'),
 ('HOST',
  "Before we get to antifreeze, we need about ninety seconds of appellate law, because this is not Mark Jensen's first "
  'trial. Julie Jensen died in Pleasant Prairie, Wisconsin, on December third, nineteen ninety-eight. Mark Jensen was '
  'charged years later and convicted in two thousand eight. But the case kept moving through appellate and federal '
  'courts because of statements Julie made before her death — especially a letter and statements to police that pointed '
  'toward Mark if anything happened to her.'),
 ('HOST',
  'The Sixth Amendment gives a criminal defendant the right to confront the witnesses against him. Under Crawford and '
  'the cases that followed it, that creates a special problem when an unavailable person made a testimonial statement '
  "and the defendant never had a meaningful chance to cross-examine that person. Long before this retrial, Wisconsin's "
  'highest court had classified key statements by Julie as testimonial. Federal habeas litigation later concluded that '
  'admitting those statements at the first trial was not harmless. By the time we reach January two thousand '
  'twenty-three, the new jury is hearing a case with an important piece of the old prosecution presentation fenced off.'),
 ('HOST',
  'That matters today. This trial is going to make us separate three questions that people casually collapse into one. '
  'Is a statement hearsay? If it is hearsay, does an exception let it in? And independently, if the statement is '
  'testimonial, does the Confrontation Clause bar it? Those are different gates. Day One ends with the lawyers fighting '
  'over exactly those gates.'),
 ('HOST',
  "First, the charge. Mark Jensen is on trial for first-degree intentional homicide. In the judge's preliminary "
  'instructions, the core elements are simple to say and hard to prove: the State must prove that Jensen caused '
  "Julie's death, and that he did so with intent to kill. Motive is not itself an element. The prosecution does not have "
  'to prove why a defendant killed someone. But motive evidence can make an otherwise ambiguous set of facts look '
  'coherent, which is why the opening spends so much time on the marriage.'),
 ('HOST',
  'And the burden never moves. Mark Jensen does not have to prove suicide. The defense can choose to offer a full '
  'alternative story — and it absolutely does — but legally the State still carries the burden to prove homicide and '
  'intent beyond a reasonable doubt. Watch how both sides use that asymmetry.'),
 ('SFX', 'COURTROOM TONE RETURNS.'),
 ('MCNEILL', 'The evidence will show that Julie lived for her children, and that she died because the defendant murdered her.'),
 ('HOST',
  'Deputy District Attorney Carli McNeill starts with Julie, not with a molecule. That is a choice. The State knows the '
  "defense is going to say suicide, so the opening begins by building a person whom the jury is supposed to have "
  "difficulty imagining abandoning her children. Then McNeill walks straight into the defense's best fact: Julie had a "
  'history of depression.'),
 ('HOST',
  'This is a classic opening-statement move: inoculation. Do not wait for the other side to reveal the fact that hurts '
  'you. Say it first, give it your meaning, and then tell the jury why it does not do the work your opponent says it '
  'does. The State describes treatment for depression in the early nineteen nineties, but emphasizes the absence of a '
  'prior suicide attempt and says Julie repeatedly denied suicidal thinking near the end of her life.'),
 ('HOST',
  'Then the opening widens. Julie had an affair years earlier. The State says Mark never got over it and carried out a '
  'long campaign of humiliating pornography-based harassment, while later beginning an affair of his own with Kelly '
  'Labonte. Legally, this material is doing several jobs at once: proposed motive, relationship history, identity or '
  'attribution for the harassment, and eventually a bridge to the home computer.'),
 ('KRAUSE', "Judge, I object at this point. I'd ask for a sidebar."),
 ('HOST', "And forty-six minutes into the State's opening, the defense stops the presentation. The jury leaves."),
 ('KRAUSE',
  "Unless these later pornography images can be connected to what was left around the home before Julie's death, I "
  'do not understand how they are relevant.'),
 ('JAMBOIS',
  'The relevance of this other-acts evidence has been litigated before. The State expects to connect it to the evidence '
  'in this case.'),
 ('JUDGE', "We're at opening statements. This is not my first rodeo. I don't see a lot of objections at opening statements."),
 ('JUDGE',
  'I just told the jury: opening statements are not evidence. If the State wants to offer this material, I am not going '
  'to prejudge every piece of it now.'),
 ('HOST',
  'This exchange is catnip if you watch trials for the law rather than just the story. Krause is preserving an '
  'objection: relevance is not a lifetime membership card just because evidence appeared in an earlier trial. The '
  'prosecution responds that the issue has history and that it will supply the connection. And Judge Anthony Milisauskas '
  'draws a timing line. An opening statement is a forecast. If a lawyer promises evidence and never gets it admitted, '
  'that can become a problem later. But he is not going to conduct a miniature admissibility hearing over every sentence '
  'of the forecast.'),
 ('HOST',
  'That does not mean the judge has declared the pornography admissible. It means he is declining to decide the full '
  'evidentiary question at that moment, on that record. There is a difference between overruling an objection to what '
  'counsel may say in opening and finally ruling that every underlying exhibit is coming into evidence.'),
 ('HOST',
  'The State then reaches the computer. And this is where a nineteen ninety-eight case becomes unusually modern. '
  'Prosecutors say the Jensen home computer contains material tying Mark to the harassment, emails documenting his '
  'affair, and internet activity involving poisoning and ethylene glycol. They also tell the jury that Julie barely used '
  'the internet. The defense will attack almost every part of that attribution.'),
 ('HOST',
  "Then we get to the final days. The State's medical theory is not simply: antifreeze was found, therefore murder. "
  'McNeill lays out a staged poisoning theory. Ethylene glycol can initially produce intoxication-like symptoms; later '
  'metabolism can produce severe acidosis and kidney injury. The State says Julie was progressively poisoned, that Mark '
  'obtained Ambien in her name, and that sedation helped him control the final phase. The State also tells the jury it '
  'will present evidence of suffocation.'),
 ('HOST',
  'There is a tactical tell here. The prosecution openly introduces one of its ugliest witnesses before the defense can: '
  'jail informant Aaron Dillard. It practically hangs a warning label on him — liar, con man, cheat — and then argues '
  'that parts of his account fit details investigators could not otherwise explain. That is another inoculation move. '
  'If a witness is going to be impeached, sometimes you make the impeachment part of your own story first.'),
 ('SFX', 'SHORT TRANSITION — room tone drops, one beat.'),
 ('RENNER', 'On December third, nineteen ninety-eight, Mark Jensen found his wife in their bedroom, motionless. He called nine-one-one.'),
 ('HOST',
  "Defense attorney Mackenzie Renner changes the frame immediately. The State's opening asked: why would Julie kill "
  'herself? The defense asks: can the State actually prove Mark killed her? Those are not the same question.'),
 ('RENNER',
  'Did the State prove beyond a reasonable doubt that Mr. Jensen caused Julie\'s death? Or did they prove that he was not '
  'a great husband and could be a jerk? Those are different things.'),
 ('HOST',
  "That is the defense's legal spine. Strip away moral judgment. Strip away the affair. Strip away pornography unless it "
  'proves an element. Strip away every witness you distrust. What is left that proves causation and intent? It is a very '
  'LawTube-friendly defense because it keeps dragging the listener back to the burden of proof.'),
 ('HOST',
  'But Renner does not stop at reasonable doubt. She gives the jury a complete affirmative narrative: Julie died by '
  "suicide. She previews depression, a statement at a dentist's office about taking her own life, alleged inconsistencies "
  "in things Julie told different people, and experts who will dispute the prosecution's toxicology and suffocation theory."),
 ('HOST',
  'Then the defense attacks the computer attribution with a detail that sounds small enough to be dangerous. The '
  'prosecution says the internet history points to Mark. The defense says searches on the morning of December third begin '
  'at about nine forty, after testimony will place Mark leaving the house around nine fifteen to take the children to '
  'school. If that timeline survives the evidence, somebody else had access to the machine. Renner also points to food '
  "later described in Julie's stomach and asks the jury to consider whether she was physically capable of getting up, "
  'eating, and using the computer.'),
 ('HOST',
  'Notice what has happened before the first witness. The State has made this a pattern case: marriage, harassment, '
  'affair, computers, poison, medication, physiology, demeanor, and post-death conduct all converge. The defense has made '
  'it an attribution case: who used the computer, who ingested the chemical, which witnesses can be trusted, and whether '
  'the State is turning a terrible marriage into a homicide without proving the causal step.'),
 ('HOST',
  'After openings, the jury finally starts getting evidence. Day One begins with people who knew Julie and with '
  'school-community witnesses. That sounds less glamorous than toxicology, but it is doing foundation work. The jury is '
  'learning who Julie was, what she said, how she appeared, and what the people around the family noticed in the days '
  'before she died.'),
 ('HOST',
  "This is also where evidence law starts deciding which version of Julie can exist in the courtroom. A dead person "
  "cannot take the stand. Every time another witness says, 'Julie told me,' lawyers should hear a little alarm bell. Not "
  'because the statement is automatically excluded — it is not — but because we need to ask why the statement is being '
  'offered, whether it is hearsay, whether an exception applies, and whether the Confrontation Clause is implicated.'),
 ('HOST',
  "That distinction is especially important in this retrial. Julie's formal, accusatory statements that had been treated "
  "as testimonial are one thing. An informal conversation with a friend, a description of present fear, or a child's "
  'comment to another child may be another. Same dead declarant problem; different legal analysis.'),
 ('SFX', 'LATE-DAY COURTROOM — slightly emptier room tone.'),
 ('PROSECUTOR', 'Your Honor, there is an issue the State would request to take up outside the presence of the jury before the next witness is called.'),
 ('HOST',
  'And here is our Day One cliffhanger. The proposed witness is Eric, who was the best friend of Mark and Julie\'s son '
  'David when they were in third grade. The State wants Eric to testify about something David allegedly said at school '
  'around December second or third, while Julie was gravely ill.'),
 ('PROSECUTOR', 'David said his mother was sick, that his dad would not take her to the hospital, and he demonstrated the way she was breathing.'),
 ('HOST',
  'That is hearsay if it is offered for the truth of what David said. The State offers two routes around the hearsay '
  "rule. First: excited utterance. Wisconsin's rule covers a statement relating to a startling event or condition when "
  'the speaker is still under the stress of that event. The theory is that stress can reduce the opportunity for '
  'reflective fabrication.'),
 ('HOST',
  "Second: Wisconsin's residual hearsay exception. This is the safety valve for statements that do not fit neatly into a "
  'named exception but carry comparable guarantees of trustworthiness. The prosecutor cites State versus Mercado and '
  "walks through factors such as the child's age and ability, who heard the statement, the circumstances, the content, "
  'and corroborating evidence.'),
 ('HOST',
  "Now watch the Confrontation Clause disappear from the center of the argument. The State says David's conversation with "
  'his school friend was non-testimonial. That makes intuitive sense: two third-graders talking at school are not '
  "creating evidence for prosecution. So the constitutional confrontation problem that haunted Julie's letter is not "
  "the main fight here. The fight is evidence law: does this child's statement fit an exception strongly enough for the "
  'jury to hear it?'),
 ('JUDGE',
  "Here's what happens in trials. Issues come up that nobody can predict. Attorneys cite cases. The prudent thing is for "
  'the Court to read the case and give the defense an opportunity to respond.'),
 ('HOST',
  'Milisauskas does not rule from the hip. He notices something specific in the cases giving young children greater '
  'latitude under the excited-utterance doctrine: many arise from child sexual-assault cases. This is a homicide. He '
  'wants to know whether the same reasoning carries over.'),
 ('JAMBOIS',
  'There is no Confrontation Clause issue this time because the statement is not testimonial. The question is excited '
  'utterance or the residual hearsay exception.'),
 ('JUDGE',
  "I've read a lot while you were watching the video. The cases I've found giving special consideration to minors concern "
  'sexual assault. This is a homicide case.'),
 ('HOST',
  "The lawyers go home with homework. The judge is going to read the cases overnight. The defense is going to research "
  "and respond. And the jury has no idea that, outside its presence, the next day's evidence is being shaped by a line of "
  "cases about what makes a child's out-of-court statement trustworthy enough to hear."),
 ('HOST',
  "That is where I want to stop Episode One. Not because Day One runs out of facts, but because it gives us the rule for "
  "watching the rest of this trial. Do not ask only, 'What happened?' Ask: what has actually become evidence? Who is the "
  'source? Why is the jury legally permitted to hear it? What did the lawyer promise in opening that still has to be '
  'delivered? And, most importantly, which side is quietly changing the question the jury thinks it has to answer?'),
 ('HOST',
  "Next episode, we start with the judge's ruling on the child-hearsay issue and keep moving through the witnesses, one "
  'evidentiary layer at a time. This is The Record. State of Wisconsin versus Mark Jensen. Day One is adjourned.'),
 ('SFX', 'OUTRO — restrained, five seconds. End.')]

pipeline = KPipeline(lang_code="a")
voices = {role: pipeline.load_voice(name) for role, name in VOICE_NAMES.items()}

def silence(seconds):
    return np.zeros(int(SR * seconds), dtype=np.float32)

def tone(seconds=1.0, freqs=(220.0, 330.0), gain=0.025, fade=0.08):
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    y = np.zeros(n, dtype=np.float32)
    for f in freqs:
        y += np.sin(2*np.pi*f*t).astype(np.float32)
    y *= gain / max(1, len(freqs))
    fN = min(int(SR*fade), n//2)
    if fN > 0:
        ramp = np.linspace(0, 1, fN, dtype=np.float32)
        y[:fN] *= ramp
        y[-fN:] *= ramp[::-1]
    return y

def room(seconds=1.4, gain=0.0018, seed=23):
    rng = np.random.default_rng(seed)
    n = int(SR * seconds)
    x = rng.normal(0, 1, n).astype(np.float32)
    kernel = np.ones(240, dtype=np.float32) / 240.0
    x = np.convolve(x, kernel, mode="same").astype(np.float32)
    peak = np.max(np.abs(x)) or 1.0
    return (x / peak * gain).astype(np.float32)

def render(role, text):
    chunks = []
    for _, _, audio in pipeline(text, voice=voices[role], speed=SPEEDS.get(role, 1.0)):
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        audio = np.asarray(audio, dtype=np.float32)
        chunks.append(audio)
    return np.concatenate(chunks) if chunks else silence(0.05)

pieces = []
for idx, (role, text) in enumerate(TURNS):
    if role == "SFX":
        u = text.upper()
        if "COLD OPEN" in u:
            pieces.extend([room(2.2), silence(0.35)])
        elif "TITLE STING" in u:
            pieces.extend([silence(0.25), tone(1.35, (164.81, 246.94, 329.63), 0.032), silence(0.5)])
        elif "SHORT TRANSITION" in u:
            pieces.extend([silence(0.2), tone(0.55, (196.00, 293.66), 0.022), silence(0.35)])
        elif "LATE-DAY COURTROOM" in u:
            pieces.extend([room(1.2, gain=0.0015, seed=51), silence(0.25)])
        elif "OUTRO" in u:
            pieces.extend([silence(0.25), tone(4.5, (146.83, 220.00, 293.66), 0.022, fade=0.9), silence(0.6)])
        continue

    audio = render(role, text)
    pre = 0.12 if role == "HOST" else 0.18
    post = 0.34 if role == "HOST" else 0.45
    if role in ("JUDGE", "MCNEILL", "PROSECUTOR", "RENNER", "KRAUSE", "JAMBOIS"):
        pieces.append(room(pre, gain=0.0012, seed=1000+idx))
    else:
        pieces.append(silence(pre))
    pieces.append(audio)
    pieces.append(silence(post))

master = np.concatenate(pieces).astype(np.float32)
peak = float(np.max(np.abs(master))) or 1.0
if peak > 0.95:
    master = master * (0.95 / peak)

wav_path = OUTDIR / "episode1_openings_are_not_evidence.wav"
mp3_path = OUTDIR / "episode1_openings_are_not_evidence.mp3"
sf.write(wav_path, master, SR)

subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(wav_path),
    "-af", "loudnorm=I=-16:LRA=9:TP=-1.5",
    "-codec:a", "libmp3lame", "-b:a", "128k",
    str(mp3_path)
], check=True)

print(f"Wrote {mp3_path}")
