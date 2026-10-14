"""The LangLens detector.

1. Count letters per Unicode script (O(n), bisect lookup per char).
2. Scripts used by one language (Telugu, Thai, Korean...) decide immediately.
3. Shared scripts (Latin, Cyrillic, Devanagari, Arabic) are scored with an
   inverted index of function words and distinctive letters, each weighted by
   how many languages share it (an IDF-style weight), so "de" counts for
   little while "und" or "ñ" count for a lot.
Deterministic, dependency-free and fast: one pass over the text.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from .languages import UNKNOWN, Language, get
from .profiles import DISTINCT_CHARS, SCRIPT_CANDIDATES, SCRIPT_DEFAULT, SIGNATURE_CHARS, STOPWORDS, VOCAB
from .scripts import SINGLE_LANGUAGE, script_breakdown, script_counts, script_of

# Split on spaces, digits and punctuation rather than matching \w: Python's \w
# excludes combining vowel signs, which would cut Hindi or Telugu words apart.
_SPLIT = re.compile(r"[\s\d.,!?;:\"()\[\]{}<>«»„“”‘’'`¿¡、。，！？：；…\-–—/\\|@#$%^&*+=~_।॥؟،]+")


def words(text: str) -> list[str]:
    return [t for t in _SPLIT.split(text) if t and t[0].isalpha()]


_SENTENCE = re.compile(r"(?<=[.!?।॥。！？\n])\s*")


def _build_word_index() -> dict[str, tuple[tuple[str, float], ...]]:
    owners: dict[str, list[str]] = defaultdict(list)
    for lang, words in STOPWORDS.items():
        for w in words:
            owners[w].append(lang)
    return {w: tuple((lang, 1.0 / len(langs)) for lang in langs) for w, langs in owners.items()}


def _build_char_index() -> dict[str, tuple[tuple[str, float], ...]]:
    owners: dict[str, list[str]] = defaultdict(list)
    for lang, chars in DISTINCT_CHARS.items():
        for c in set(chars):
            owners[c].append(lang)
    return {c: tuple((lang, 0.6 / len(langs)) for lang in langs) for c, langs in owners.items()}


def trigrams(word: str) -> set[str]:
    padded = f" {word} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def _build_trigram_index() -> dict[str, tuple[tuple[str, float], ...]]:
    """Letter trigrams of each profile's words capture spelling habits
    (Hungarian "sz", Dutch "ij", Swahili "ku"...) so even proverbs with no
    function words get evidence."""
    owners: dict[str, set[str]] = defaultdict(set)
    for source in (STOPWORDS, VOCAB):
        for lang, ws in source.items():
            for w in ws:
                for g in trigrams(w):
                    owners[g].add(lang)
    return {g: tuple((lang, 0.25 / len(langs)) for lang in sorted(langs)) for g, langs in owners.items()}


WORD_INDEX = _build_word_index()
CHAR_INDEX = _build_char_index()
TRIGRAM_INDEX = _build_trigram_index()


@dataclass(frozen=True)
class Detection:
    code: str
    confidence: float

    @property
    def language(self) -> Language:
        return get(self.code)

    @property
    def romanized(self) -> bool:
        return self.code.endswith("-Latn")

    @property
    def name(self) -> str:
        return self.language.name + (" (romanized)" if self.romanized else "")

    @property
    def reliable(self) -> bool:
        return self.confidence >= 0.5

    def to_dict(self) -> dict:
        lang = self.language
        return {
            "code": self.code,
            "name": self.name,
            "native": lang.native,
            "flag": lang.flag,
            "confidence": round(self.confidence, 4),
            "reliable": self.reliable,
        }


UNDETERMINED = Detection(UNKNOWN.code, 0.0)


@dataclass
class Segment:
    text: str
    detection: Detection

    def to_dict(self) -> dict:
        return {"text": self.text, **self.detection.to_dict()}


@dataclass
class Analysis:
    text: str
    best: Detection
    candidates: list[Detection]
    scripts: dict[str, float]
    segments: list[Segment] = field(default_factory=list)

    @property
    def mixed(self) -> bool:
        return len({s.detection.code for s in self.segments if s.detection.reliable}) > 1

    def to_dict(self) -> dict:
        return {
            "best": self.best.to_dict(),
            "candidates": [c.to_dict() for c in self.candidates],
            "scripts": self.scripts,
            "segments": [s.to_dict() for s in self.segments],
            "mixed": self.mixed,
            "stats": {"characters": len(self.text), "words": len(words(self.text))},
        }


def _score_shared(text: str, script: str) -> dict[str, float]:
    """Evidence per candidate language for text written in a shared script."""
    allowed = set(SCRIPT_CANDIDATES[script])
    scores: dict[str, float] = defaultdict(float)
    tokens = [t.lower() for t in words(text) if script_of(t[0]) == script]
    for tok in tokens:
        for lang, w in WORD_INDEX.get(tok, ()):
            if lang in allowed:
                scores[lang] += w
        for g in trigrams(tok):
            for lang, w in TRIGRAM_INDEX.get(g, ()):
                if lang in allowed:
                    scores[lang] += w
    lowered = text.lower()
    for ch in lowered:
        for lang, w in CHAR_INDEX.get(ch, ()):
            if lang in allowed:
                scores[lang] += w
    if script == "Arabic":  # the definite article "ال" is a hallmark of Arabic
        scores["ar"] += 0.5 * sum(t.startswith("ال") for t in tokens)
    if sum(len(t) for t in tokens) >= 25:
        for lang, sig in SIGNATURE_CHARS.items():
            if lang in scores and not any(c in lowered for c in sig):
                scores[lang] *= 0.4
    return dict(scores)


def _rank(scores: dict[str, float], evidence_scale: float) -> list[Detection]:
    """Turn raw scores into confidences that sum to <= 1.

    Squaring sharpens the winner; `evidence_scale` (0..1) shrinks everything
    when there is little evidence, e.g. a two-word input.
    """
    sq = {k: v * v for k, v in scores.items() if v > 0}
    total = sum(sq.values())
    if not total:
        return []
    ranked = sorted(sq.items(), key=lambda kv: -kv[1])
    return [Detection(code, (v / total) * evidence_scale) for code, v in ranked]


class Detector:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def detect_all(self, text: str) -> list[Detection]:
        counts = script_counts(text)
        letters = sum(counts.values())
        if not letters:
            return []
        combined: dict[str, float] = defaultdict(float)
        kana = counts.get("Hiragana", 0) + counts.get("Katakana", 0)
        for script, n in counts.items():
            share = n / letters
            if script in ("Hiragana", "Katakana") or (script == "Han" and kana):
                combined["ja"] += share
            elif script == "Han":
                combined["zh"] += share
            elif script in SINGLE_LANGUAGE:
                combined[SINGLE_LANGUAGE[script]] += share
            elif script in SCRIPT_CANDIDATES:
                scores = _score_shared(text, script)
                hits = sum(scores.values())
                evidence = min(1.0, 0.35 + hits / 4)
                ranked = _rank(scores, evidence)
                if not ranked and script in SCRIPT_DEFAULT:
                    ranked = [Detection(SCRIPT_DEFAULT[script], 0.4)]
                for d in ranked:
                    combined[d.code] += d.confidence * share
        out = sorted((Detection(c, min(1.0, v)) for c, v in combined.items()), key=lambda d: -d.confidence)
        return out[: self.top_k]

    def detect(self, text: str) -> Detection:
        found = self.detect_all(text)
        return found[0] if found else UNDETERMINED

    def segments(self, text: str) -> list[Segment]:
        """Detect sentence by sentence and merge neighbours in the same language."""
        merged: list[Segment] = []
        for part in filter(None, (p.strip() for p in _SENTENCE.split(text))):
            d = self.detect(part)
            if merged and merged[-1].detection.code == d.code:
                prev = merged[-1]
                joined = f"{prev.text} {part}"
                merged[-1] = Segment(joined, Detection(d.code, max(prev.detection.confidence, d.confidence)))
            else:
                merged.append(Segment(part, d))
        return merged

    def analyze(self, text: str) -> Analysis:
        candidates = self.detect_all(text)
        return Analysis(
            text=text,
            best=candidates[0] if candidates else UNDETERMINED,
            candidates=candidates,
            scripts=script_breakdown(text),
            segments=self.segments(text),
        )


_default = Detector()
detect = _default.detect
detect_all = _default.detect_all
analyze = _default.analyze
