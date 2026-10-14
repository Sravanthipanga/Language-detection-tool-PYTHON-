"""Fast Unicode script classification using a sorted range table + bisect."""

from __future__ import annotations

from bisect import bisect_right
from collections import Counter

# (start, end, script) — sorted by start, non-overlapping.
_RANGES = sorted(
    [
        (0x0041, 0x005A, "Latin"),
        (0x0061, 0x007A, "Latin"),
        (0x00C0, 0x024F, "Latin"),
        (0x1E00, 0x1EFF, "Latin"),
        (0x0370, 0x03FF, "Greek"),
        (0x1F00, 0x1FFF, "Greek"),
        (0x0400, 0x052F, "Cyrillic"),
        (0x0530, 0x058F, "Armenian"),
        (0x0590, 0x05FF, "Hebrew"),
        (0x0600, 0x06FF, "Arabic"),
        (0x0750, 0x077F, "Arabic"),
        (0xFB50, 0xFDFF, "Arabic"),
        (0xFE70, 0xFEFF, "Arabic"),
        (0x0900, 0x097F, "Devanagari"),
        (0x0980, 0x09FF, "Bengali"),
        (0x0A00, 0x0A7F, "Gurmukhi"),
        (0x0A80, 0x0AFF, "Gujarati"),
        (0x0B00, 0x0B7F, "Odia"),
        (0x0B80, 0x0BFF, "Tamil"),
        (0x0C00, 0x0C7F, "Telugu"),
        (0x0C80, 0x0CFF, "Kannada"),
        (0x0D00, 0x0D7F, "Malayalam"),
        (0x0D80, 0x0DFF, "Sinhala"),
        (0x0E00, 0x0E7F, "Thai"),
        (0x0E80, 0x0EFF, "Lao"),
        (0x1000, 0x109F, "Myanmar"),
        (0x10A0, 0x10FF, "Georgian"),
        (0x1100, 0x11FF, "Hangul"),
        (0x3130, 0x318F, "Hangul"),
        (0xAC00, 0xD7AF, "Hangul"),
        (0x1200, 0x139F, "Ethiopic"),
        (0x1780, 0x17FF, "Khmer"),
        (0x3040, 0x309F, "Hiragana"),
        (0x30A0, 0x30FF, "Katakana"),
        (0x31F0, 0x31FF, "Katakana"),
        (0x3400, 0x4DBF, "Han"),
        (0x4E00, 0x9FFF, "Han"),
        (0xF900, 0xFAFF, "Han"),
    ]
)
_STARTS = [r[0] for r in _RANGES]

# Scripts used by exactly one language in our set.
SINGLE_LANGUAGE = {
    "Greek": "el",
    "Armenian": "hy",
    "Hebrew": "he",
    "Bengali": "bn",
    "Gurmukhi": "pa",
    "Gujarati": "gu",
    "Odia": "or",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Sinhala": "si",
    "Thai": "th",
    "Lao": "lo",
    "Myanmar": "my",
    "Georgian": "ka",
    "Hangul": "ko",
    "Ethiopic": "am",
    "Khmer": "km",
}


def script_of(ch: str) -> str | None:
    cp = ord(ch)
    if cp < 0x41:
        return None
    i = bisect_right(_STARTS, cp) - 1
    if i >= 0:
        start, end, name = _RANGES[i]
        if start <= cp <= end:
            return name
    return None


def script_counts(text: str) -> Counter[str]:
    """Count letters per script, ignoring digits, punctuation and spaces."""
    counts: Counter[str] = Counter()
    for ch in text:
        if ch.isalpha():
            s = script_of(ch)
            if s:
                counts[s] += 1
    return counts


def script_breakdown(text: str) -> dict[str, float]:
    counts = script_counts(text)
    total = sum(counts.values()) or 1
    return {s: round(n / total, 4) for s, n in counts.most_common()}
