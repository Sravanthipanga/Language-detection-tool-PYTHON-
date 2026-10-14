"""Language metadata: ISO 639-1 code -> (English name, native name, flag)."""

from __future__ import annotations

from typing import NamedTuple


class Language(NamedTuple):
    code: str
    name: str
    native: str
    flag: str


_RAW = """
af|Afrikaans|Afrikaans|🇿🇦
am|Amharic|አማርኛ|🇪🇹
ar|Arabic|العربية|🇸🇦
bg|Bulgarian|Български|🇧🇬
bn|Bengali|বাংলা|🇧🇩
be|Belarusian|Беларуская|🇧🇾
ca|Catalan|Català|🏳️
cs|Czech|Čeština|🇨🇿
cy|Welsh|Cymraeg|🏴
da|Danish|Dansk|🇩🇰
de|German|Deutsch|🇩🇪
el|Greek|Ελληνικά|🇬🇷
en|English|English|🇬🇧
es|Spanish|Español|🇪🇸
et|Estonian|Eesti|🇪🇪
eu|Basque|Euskara|🏳️
fa|Persian|فارسی|🇮🇷
fi|Finnish|Suomi|🇫🇮
fr|French|Français|🇫🇷
ga|Irish|Gaeilge|🇮🇪
gu|Gujarati|ગુજરાતી|🇮🇳
he|Hebrew|עברית|🇮🇱
hi|Hindi|हिन्दी|🇮🇳
hr|Croatian|Hrvatski|🇭🇷
hu|Hungarian|Magyar|🇭🇺
hy|Armenian|Հայերեն|🇦🇲
id|Indonesian|Bahasa Indonesia|🇮🇩
is|Icelandic|Íslenska|🇮🇸
it|Italian|Italiano|🇮🇹
ja|Japanese|日本語|🇯🇵
ka|Georgian|ქართული|🇬🇪
km|Khmer|ខ្មែរ|🇰🇭
kn|Kannada|ಕನ್ನಡ|🇮🇳
ko|Korean|한국어|🇰🇷
lo|Lao|ລາວ|🇱🇦
lt|Lithuanian|Lietuvių|🇱🇹
lv|Latvian|Latviešu|🇱🇻
mk|Macedonian|Македонски|🇲🇰
ml|Malayalam|മലയാളം|🇮🇳
mr|Marathi|मराठी|🇮🇳
my|Burmese|မြန်မာ|🇲🇲
ne|Nepali|नेपाली|🇳🇵
nl|Dutch|Nederlands|🇳🇱
no|Norwegian|Norsk|🇳🇴
or|Odia|ଓଡ଼ିଆ|🇮🇳
pa|Punjabi|ਪੰਜਾਬੀ|🇮🇳
pl|Polish|Polski|🇵🇱
pt|Portuguese|Português|🇵🇹
ro|Romanian|Română|🇷🇴
ru|Russian|Русский|🇷🇺
si|Sinhala|සිංහල|🇱🇰
sk|Slovak|Slovenčina|🇸🇰
sl|Slovenian|Slovenščina|🇸🇮
sq|Albanian|Shqip|🇦🇱
sr|Serbian|Српски|🇷🇸
sv|Swedish|Svenska|🇸🇪
sw|Swahili|Kiswahili|🇰🇪
ta|Tamil|தமிழ்|🇮🇳
te|Telugu|తెలుగు|🇮🇳
th|Thai|ไทย|🇹🇭
tl|Tagalog|Tagalog|🇵🇭
tr|Turkish|Türkçe|🇹🇷
uk|Ukrainian|Українська|🇺🇦
ur|Urdu|اردو|🇵🇰
vi|Vietnamese|Tiếng Việt|🇻🇳
zh|Chinese|中文|🇨🇳
"""

LANGUAGES: dict[str, Language] = {
    code: Language(code, name, native, flag)
    for code, name, native, flag in (line.split("|") for line in _RAW.strip().splitlines())
}
UNKNOWN = Language("und", "Unknown", "?", "🌐")


def get(code: str) -> Language:
    return LANGUAGES.get(code.lower().split("-")[0], UNKNOWN)


def resolve(name_or_code: str) -> str | None:
    """Accept 'te', 'Telugu', 'telugu', 'తెలుగు' and return the ISO code."""
    q = name_or_code.strip().lower()
    if q in LANGUAGES:
        return q
    for lang in LANGUAGES.values():
        if q in (lang.name.lower(), lang.native.lower()):
            return lang.code
    if q in ("chinese (simplified)", "mandarin"):
        return "zh"
    return None
