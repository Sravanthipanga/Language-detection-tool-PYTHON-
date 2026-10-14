import pytest

from langlens import analyze, detect, detect_all, resolve
from langlens.scripts import script_breakdown, script_of

CASES = {
    "en": "I would like a cup of coffee, please.",
    "es": "Me gusta mucho leer libros por la noche.",
    "fr": "Nous allons au marché ce matin.",
    "de": "Ich trinke gern Kaffee mit Milch.",
    "it": "Mi piace molto la pizza con il formaggio.",
    "pt": "Nós vamos à praia amanhã de manhã.",
    "nl": "Ik drink graag koffie in de ochtend.",
    "sv": "Jag tycker om att läsa böcker på kvällen.",
    "fi": "Minä juon kahvia joka aamu.",
    "pl": "Lubię czytać książki wieczorem.",
    "cs": "Rád čtu knihy večer před spaním.",
    "hu": "Jó napot, hogy van?",
    "ro": "Îmi place să citesc cărți seara.",
    "tr": "Akşamları kitap okumayı severim.",
    "id": "Saya suka membaca buku di malam hari.",
    "vi": "Tôi thích đọc sách vào buổi tối.",
    "sw": "Habari yako? Mimi ni mzima, asante sana.",
    "ru": "Я люблю читать книги по вечерам.",
    "uk": "Я люблю читати книжки ввечері.",
    "hi": "मुझे शाम को किताबें पढ़ना पसंद है।",
    "mr": "मी आज खूप आनंदी आहे, तुम्ही कसे आहात?",
    "ar": "أحب قراءة الكتب في المساء.",
    "fa": "من دوست دارم شب‌ها کتاب بخوانم.",
    "ur": "آپ کیسے ہیں؟ میں بہت خوش ہوں",
    "te": "నమస్కారం, మీరు ఎలా ఉన్నారు?",
    "ta": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
    "ja": "こんにちは、お元気ですか？",
    "zh": "你好，你今天怎么样？",
    "ko": "안녕하세요, 잘 지내세요?",
    "el": "Καλημέρα, τι κάνεις;",
    "he": "שלום, מה שלומך היום?",
    "th": "สวัสดีครับ วันนี้เป็นอย่างไรบ้าง",
    "hi-Latn": "kya haal hai yaar, main theek hoon",
    "te-Latn": "nenu bagunnanu, meeru ela unnaru",
}


@pytest.mark.parametrize("code, text", CASES.items())
def test_detects_language(code, text):
    d = detect(text)
    assert d.code == code
    assert d.reliable


def test_danish_and_norwegian_are_close_neighbours():
    top = {d.code for d in detect_all("Jeg kan godt lide at læse bøger om aftenen.")[:2]}
    assert top == {"da", "no"}


def test_empty_and_symbols_are_undetermined():
    for text in ("", "   ", "12345 !!!", "🙂🙂"):
        assert detect(text).code == "und"


def test_short_text_is_flagged_low_confidence():
    assert not detect("ok").reliable


def test_deterministic():
    text = "Ciao, come stai?"
    assert {detect(text) for _ in range(20)} == {detect(text)}


def test_confidences_are_sorted_and_bounded():
    cands = detect_all("Hello everyone. Hola a todos, ¿qué tal?")
    confs = [c.confidence for c in cands]
    assert confs == sorted(confs, reverse=True)
    assert all(0 <= c <= 1 for c in confs) and sum(confs) <= 1.0001


def test_mixed_text_segments():
    a = analyze("Hello everyone, how are you? Hola a todos, ¿qué tal? नमस्ते दोस्तों, आप कैसे हैं?")
    assert a.mixed
    assert [s.detection.code for s in a.segments] == ["en", "es", "hi"]


def test_segments_merge_neighbours():
    a = analyze("Bonjour à tous. Je suis très content.")
    assert len(a.segments) == 1 and a.segments[0].detection.code == "fr"


def test_script_helpers():
    assert script_of("a") == "Latin" and script_of("я") == "Cyrillic" and script_of("న") == "Telugu"
    assert script_breakdown("abc абв") == {"Latin": 0.5, "Cyrillic": 0.5}


def test_analysis_dict_shape():
    d = analyze("Guten Morgen").to_dict()
    assert d["best"]["name"] == "German" and d["best"]["flag"] == "🇩🇪"
    assert set(d) == {"best", "candidates", "scripts", "segments", "mixed", "stats"}


@pytest.mark.parametrize(
    "q, code", [("te", "te"), ("Telugu", "te"), ("telugu", "te"), ("తెలుగు", "te"), ("klingon", None)]
)
def test_resolve(q, code):
    assert resolve(q) == code


def test_romanized_name():
    assert detect("kya haal hai yaar").name == "Hindi (romanized)"


def test_long_text_is_fast():
    import time

    text = "The quick brown fox jumps over the lazy dog. " * 2000  # ~90 KB
    start = time.perf_counter()
    assert detect(text).code == "en"
    assert time.perf_counter() - start < 1.5
