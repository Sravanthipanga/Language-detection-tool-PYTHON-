"""“Guess the language” — a small game that doubles as a self-test."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .languages import get

PHRASES: dict[str, tuple[str, ...]] = {
    "en": ("The early bird catches the worm.", "Where is the nearest train station?"),
    "es": ("Más vale tarde que nunca.", "¿Dónde está la estación de tren más cercana?"),
    "fr": ("Petit à petit, l'oiseau fait son nid.", "Où est la gare la plus proche ?"),
    "de": ("Übung macht den Meister.", "Wo ist der nächste Bahnhof?"),
    "it": ("Chi dorme non piglia pesci.", "Dov'è la stazione più vicina?"),
    "pt": ("Água mole em pedra dura, tanto bate até que fura.", "Onde fica a estação de comboio mais próxima?"),
    "nl": ("Oost west, thuis best.", "Waar is het dichtstbijzijnde treinstation?"),
    "sv": ("Borta bra men hemma bäst.", "Var ligger närmaste tågstation?"),
    "pl": ("Nie ma tego złego, co by na dobre nie wyszło.", "Gdzie jest najbliższa stacja kolejowa?"),
    "tr": ("Damlaya damlaya göl olur.", "En yakın tren istasyonu nerede?"),
    "fi": ("Hiljaa hyvä tulee.", "Missä on lähin rautatieasema?"),
    "hu": ("Lassan járj, tovább érsz.", "Hol van a legközelebbi vasútállomás?"),
    "ro": ("Încetul cu încetul se face oțetul.", "Unde este cea mai apropiată gară?"),
    "vi": ("Có công mài sắt, có ngày nên kim.", "Ga tàu gần nhất ở đâu?"),
    "id": ("Sedikit demi sedikit, lama-lama menjadi bukit.", "Di mana stasiun kereta terdekat?"),
    "sw": ("Haba na haba hujaza kibaba.", "Kituo cha treni kilicho karibu kiko wapi?"),
    "ru": ("Тише едешь — дальше будешь.", "Где ближайший вокзал?"),
    "uk": ("Без праці нема калачів.", "Де найближчий вокзал?"),
    "el": ("Σιγά σιγά γίνεται η αγουρίδα μέλι.", "Πού είναι ο πλησιέστερος σταθμός τρένου;"),
    "he": ("לאט לאט מגיעים רחוק.", "איפה תחנת הרכבת הקרובה?"),
    "ar": ("الصبر مفتاح الفرج.", "أين أقرب محطة قطار؟"),
    "fa": ("قطره قطره جمع گردد، وانگهی دریا شود.", "نزدیک‌ترین ایستگاه قطار کجاست؟"),
    "hi": ("जहाँ चाह, वहाँ राह।", "सबसे नज़दीकी रेलवे स्टेशन कहाँ है?"),
    "te": ("ఆరోగ్యమే మహాభాగ్యం.", "దగ్గరలో రైల్వే స్టేషన్ ఎక్కడ ఉంది?"),
    "ta": ("கற்றது கைமண் அளவு.", "அருகிலுள்ள ரயில் நிலையம் எங்கே?"),
    "bn": ("যত গর্জে তত বর্ষে না।", "সবচেয়ে কাছের রেলস্টেশন কোথায়?"),
    "th": ("ช้าๆ ได้พร้าเล่มงาม", "สถานีรถไฟที่ใกล้ที่สุดอยู่ที่ไหน"),
    "ja": ("猿も木から落ちる。", "一番近い駅はどこですか？"),
    "zh": ("千里之行，始于足下。", "最近的火车站在哪里？"),
    "ko": ("천 리 길도 한 걸음부터.", "가장 가까운 기차역이 어디예요?"),
}


@dataclass
class Question:
    phrase: str
    answer: str
    options: list[str]


def make_question(rng: random.Random, n_options: int = 4) -> Question:
    answer = rng.choice(sorted(PHRASES))
    phrase = rng.choice(PHRASES[answer])
    others = rng.sample([c for c in PHRASES if c != answer], n_options - 1)
    options = [answer, *others]
    rng.shuffle(options)
    return Question(phrase, answer, options)


def play(rounds: int = 10, seed: int | None = None, ask=input, say=print) -> int:
    rng = random.Random(seed)
    score = streak = best = 0
    say("🌍 Guess the language! Type the number of your answer (q to quit).\n")
    for i in range(1, rounds + 1):
        q = make_question(rng)
        say(f"Round {i}/{rounds}:  “{q.phrase}”")
        for n, code in enumerate(q.options, 1):
            lang = get(code)
            say(f"   {n}. {lang.flag} {lang.name}")
        reply = ask("Your answer: ").strip().lower()
        if reply in ("q", "quit", "exit"):
            break
        chosen = q.options[int(reply) - 1] if reply.isdigit() and 1 <= int(reply) <= len(q.options) else None
        right = get(q.answer)
        if chosen == q.answer:
            score += 1
            streak += 1
            best = max(best, streak)
            say(f"   ✅ Correct! {right.native} — streak {streak}" + (" 🔥" if streak >= 3 else "") + "\n")
        else:
            streak = 0
            say(f"   ❌ It was {right.flag} {right.name} ({right.native}).\n")
    say(f"Final score: {score}/{i} · best streak {best}")
    return score
