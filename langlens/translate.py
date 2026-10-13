"""Translation with pluggable backends.

* ``deep-translator`` (Google, free, maintained) is used when installed.
* Otherwise the free MyMemory API is called with the standard library only.
Results are cached, and long texts are split on sentence boundaries.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from functools import lru_cache

from .detector import detect

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
_CHUNK = 450  # MyMemory accepts up to 500 bytes per request


class TranslationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Translation:
    original: str
    translated: str
    source: str
    target: str
    backend: str

    def to_dict(self) -> dict:
        return asdict(self)


def fetch(url: str, timeout: float = 10.0) -> str:
    """HTTP GET (patched in tests)."""
    req = urllib.request.Request(url, headers={"User-Agent": "LangLens/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https host
        return resp.read().decode("utf-8", "replace")


def chunks(text: str, size: int = _CHUNK) -> list[str]:
    """Split text into pieces under `size` characters, preferring sentence ends."""
    parts, buf = [], ""
    for sentence in re.split(r"(?<=[.!?。！？।\n])\s+", text):
        while len(sentence) > size:  # a single huge sentence: hard split on spaces
            cut = sentence.rfind(" ", 0, size)
            cut = cut if cut > 0 else size
            parts.append(sentence[:cut])
            sentence = sentence[cut:].lstrip()
        if len(buf) + len(sentence) + 1 > size and buf:
            parts.append(buf)
            buf = sentence
        else:
            buf = f"{buf} {sentence}".strip()
    if buf:
        parts.append(buf)
    return parts


def _mymemory(text: str, source: str, target: str) -> str:
    out = []
    for piece in chunks(text):
        query = urllib.parse.urlencode({"q": piece, "langpair": f"{source}|{target}"})
        email = os.environ.get("LANGLENS_EMAIL")  # optional: raises the free daily quota
        if email:
            query += "&" + urllib.parse.urlencode({"de": email})
        data = json.loads(fetch(f"{MYMEMORY_URL}?{query}"))
        if int(data.get("responseStatus", 200)) != 200:
            raise TranslationError(str(data.get("responseDetails") or "translation failed"))
        out.append(data["responseData"]["translatedText"])
    return " ".join(out)


def _deep_translator(text: str, source: str, target: str) -> str:
    from deep_translator import GoogleTranslator  # optional dependency

    src = "auto" if source in ("auto", "und") else source
    return GoogleTranslator(source=src, target=target).translate(text)


def _backends() -> list[tuple[str, object]]:
    preferred = os.environ.get("LANGLENS_BACKEND", "").lower()
    backends: list[tuple[str, object]] = []
    try:
        import deep_translator  # noqa: F401

        backends.append(("google", _deep_translator))
    except ImportError:
        pass
    backends.append(("mymemory", _mymemory))
    if preferred:
        backends.sort(key=lambda b: b[0] != preferred)
    return backends


@lru_cache(maxsize=512)
def translate(text: str, target: str = "en", source: str | None = None) -> Translation:
    text = text.strip()
    if not text:
        raise TranslationError("nothing to translate")
    target = target.split("-")[0]
    src = source or detect(text).code
    src = src.split("-")[0]  # romanized Hindi -> hi
    if src == target:
        return Translation(text, text, src, target, "none")
    errors = []
    for name, fn in _backends():
        try:
            return Translation(text, fn(text, src if src != "und" else "en", target), src, target, name)
        except Exception as exc:  # try the next backend
            errors.append(f"{name}: {exc}")
    raise TranslationError("all translation backends failed (" + "; ".join(errors) + ")")
