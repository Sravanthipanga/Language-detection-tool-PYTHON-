import json

import pytest

from langlens import translate as tr
from langlens.cli import main
from langlens.quiz import PHRASES, make_question, play
from langlens.web import handle_api


@pytest.fixture(autouse=True)
def fake_network(monkeypatch):
    calls = []

    def fake_fetch(url, timeout=10.0):
        calls.append(url)
        return json.dumps({"responseStatus": 200, "responseData": {"translatedText": "Hello friends"}})

    monkeypatch.setattr(tr, "fetch", fake_fetch)
    monkeypatch.setenv("LANGLENS_BACKEND", "mymemory")
    tr.translate.cache_clear()
    return calls


def test_translate_detects_source(fake_network):
    t = tr.translate("Hola amigos, ¿cómo estáis todos hoy?", "en")
    assert (t.source, t.target, t.translated, t.backend) == ("es", "en", "Hello friends", "mymemory")
    assert "langpair=es%7Cen" in fake_network[0]


def test_translate_same_language_is_noop(fake_network):
    t = tr.translate("Good morning to everyone", "en")
    assert t.translated == "Good morning to everyone" and t.backend == "none" and not fake_network


def test_translate_is_cached(fake_network):
    tr.translate("Bonjour tout le monde, comment allez-vous?", "en")
    tr.translate("Bonjour tout le monde, comment allez-vous?", "en")
    assert len(fake_network) == 1


def test_translate_errors(monkeypatch):
    monkeypatch.setattr(tr, "fetch", lambda *a, **k: json.dumps({"responseStatus": 403, "responseDetails": "quota"}))
    with pytest.raises(tr.TranslationError, match="quota"):
        tr.translate("Hallo zusammen, wie geht es euch?", "en")
    with pytest.raises(tr.TranslationError):
        tr.translate("   ", "en")


def test_chunks_respect_limit():
    text = "Sentence number one is here. " * 60
    parts = tr.chunks(text, 120)
    assert all(len(p) <= 120 for p in parts)
    assert " ".join(parts).split() == text.split()


def test_web_api():
    status, data = handle_api("POST", "/api/analyze", {"text": "Guten Morgen, wie geht es dir?"})
    assert status == 200 and data["best"]["code"] == "de"
    status, data = handle_api("POST", "/api/translate", {"text": "Hola amigos, ¿qué tal?", "target": "English"})
    assert status == 200 and data["translated"] == "Hello friends"
    assert handle_api("POST", "/api/translate", {"text": "x", "target": "klingon"})[0] == 400
    assert handle_api("GET", "/api/languages", {})[1]["languages"]
    quiz = handle_api("GET", "/api/quiz", {})[1]
    assert quiz["answer"] in [o["code"] for o in quiz["options"]]
    assert handle_api("GET", "/nope", {})[0] == 404


def test_web_page_is_packaged():
    from langlens.web import _page

    assert b"LangLens" in _page()


def test_quiz_game():
    import random

    q = make_question(random.Random(1))
    assert q.answer in q.options and len(set(q.options)) == 4 and q.phrase in PHRASES[q.answer]
    answers = iter(["1", "2", "q"])
    out = []
    score = play(rounds=5, seed=3, ask=lambda _: next(answers), say=out.append)
    assert 0 <= score <= 2 and out[-1].startswith("Final score")


def test_cli_detect_json(capsys):
    assert main(["detect", "--json", "Bonjour", "tout", "le", "monde"]) == 0
    assert json.loads(capsys.readouterr().out)["best"]["code"] == "fr"


def test_cli_translate(capsys):
    assert main(["translate", "--to", "english", "Hola", "amigos"]) == 0
    assert "Hello friends" in capsys.readouterr().out


def test_cli_file(tmp_path, capsys):
    src = tmp_path / "lines.txt"
    src.write_text("Hello there my friend\n\nBonjour mon ami\nПривет, мой друг\n", encoding="utf-8")
    out = tmp_path / "out.csv"
    assert main(["file", str(src), "-o", str(out)]) == 0
    rows = out.read_text(encoding="utf-8").splitlines()
    assert rows[0].startswith("line,code") and len(rows) == 4
    assert [r.split(",")[1] for r in rows[1:]] == ["en", "fr", "ru"]


def test_cli_languages(capsys):
    assert main(["languages"]) == 0
    assert "Telugu" in capsys.readouterr().out
