# LangLens 🔎 — Language Detection Tool

**LangLens** detects the language of any text: **60+ languages**, including romanized Hindi and Telugu ("Hinglish"). It runs instantly, offline, and gives the same answer every time.

It also translates between languages, splits mixed-language text sentence by sentence, processes whole files, comes with a **web app**, and has a "guess the language" **quiz game**.

This is a full rewrite of my original script:
- `googletrans==3.1.0a0` no longer works.
- `langdetect` gives different answers for the same short text unless you fix its random seed.

LangLens needs **no required dependencies** at all.

```text
$ langlens detect "Hello everyone. Hola a todos, ¿qué tal? नमस्ते दोस्तों।"
🇪🇸  Spanish · Español · es

   🇪🇸 Spanish                ████████████░░░░░░░░░░░░  51.8%
   🇬🇧 English                █████░░░░░░░░░░░░░░░░░░░  20.2%
   🇮🇳 Hindi                  ██░░░░░░░░░░░░░░░░░░░░░░   9.4%

   Scripts: Latin 81%, Devanagari 19%

   Mixed-language text:
   🇬🇧 en      Hello everyone.
   🇪🇸 es      Hola a todos, ¿qué tal?
   🇮🇳 hi      नमस्ते दोस्तों।
```

## Features

- **60+ languages, offline:** Telugu, Hindi, Tamil, Marathi, Bengali, Urdu, Arabic, Chinese, Japanese, Korean, Russian, Spanish, French, German and many more. Run `langlens languages` for the full list.
- **Romanized Indian languages:** recognises Hindi and Telugu typed in English letters, e.g. "kya haal hai yaar", "nenu bagunnanu".
- **Confidence scores** with a top-candidates ranking, a "reliable" flag, and a script breakdown (Latin 81%, Devanagari 19%).
- **Mixed-language text:** detects each sentence and highlights where the language switches.
- **Translation** to any language: uses Google via `deep-translator` if installed, otherwise the free MyMemory API with no extra installs. Results are cached and long texts are split automatically.
- **Batch mode:** detect every line of a file and export the results to CSV or JSON.
- **Web app:**
  - Detects live as you type, with confidence bars and colour-highlighted mixed text.
  - Translates, with a 🔊 button that reads the translation aloud.
  - Includes the quiz, and supports dark mode.
- **Quiz game:** guess the language of proverbs and phrases from 30 languages, with score and streaks.
- **Interactive mode:** run `langlens` with no arguments, then type text, or use `:to french` to translate it.

## Quick start

```bash
git clone https://github.com/Sravanthipanga/Language-detection-tool-PYTHON-.git
cd Language-detection-tool-PYTHON-
pip install -e .                 # optional: pip install -e ".[translate]" for Google translation
```

```bash
langlens detect "నమస్కారం, మీరు ఎలా ఉన్నారు?"      # → Telugu
langlens detect --json "Guten Morgen"              # machine-readable output
langlens translate "Hola amigos" --to telugu       # names or codes both work
langlens file messages.txt -o results.csv          # one result per line
langlens serve                                     # web app at http://127.0.0.1:8000
langlens quiz                                      # play the game
langlens                                           # interactive mode
```

You can also skip installing it and run `python -m langlens …` from the project folder.

### Use it from Python

```python
from langlens import detect, analyze
from langlens.translate import translate

detect("Ciao, come stai?").code           # 'it'
detect("Ciao, come stai?").name           # 'Italian'

a = analyze("Hello everyone, how are you? Bonjour à tous, comment allez-vous?")
a.mixed, [s.detection.code for s in a.segments]   # (True, ['en', 'fr'])

translate("Me gusta mucho leer", "en").translated
```

## How detection works

1. **Scripts first.** Every letter is mapped to its Unicode script with a binary search over a range table. Scripts used by a single language (Telugu, Tamil, Thai, Korean, Greek…) decide the answer immediately. Japanese is told apart from Chinese by the presence of kana.
2. **Shared scripts** (Latin, Cyrillic, Devanagari, Arabic) are scored against compact profiles using three signals:
   - **common words** ("the", "und", "que", "है", "и"…);
   - **distinctive letters** (ñ, ß, ő, ў, پ…);
   - **letter trigrams**, which capture spelling habits such as Hungarian "sz" or Dutch "ij".

   Each clue is weighted by how many languages share it, so "de" counts for little while "und" counts for a lot.
3. **Confidence:** scores are sharpened and scaled by how much evidence there was, so a one-word input is marked as low confidence.

Everything is deterministic and runs in a single pass. A 90 KB document is detected in well under a second.

**Accuracy:** on 112 test sentences and proverbs that the profiles were not built from, LangLens gets 104 right (93%). Most misses are very short proverbs (3–4 words, no common words). Danish and Norwegian are written almost identically and often tie. For best results give it at least one full sentence.

## Project layout

```
langlens/
  detector.py    the detection engine (script table + weighted profiles)
  profiles.py    common words, everyday vocabulary and distinctive letters per language
  scripts.py     Unicode script classifier
  languages.py   names, native names and flags
  translate.py   translation backends, chunking, caching
  quiz.py        "guess the language" game
  cli.py         command-line interface
  web.py         standard-library web server + JSON API
  static/        the web app (single HTML file)
tests/           62 tests (no internet needed)
```

### Web API

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/analyze` | `{"text": "…"}` | best guess, candidates, scripts, segments |
| POST | `/api/translate` | `{"text": "…", "target": "te"}` | translation |
| GET | `/api/languages` | | supported languages |
| GET | `/api/quiz` | | a random quiz question |

## Development

```bash
pip install -e ".[dev]"
pytest -q        # 62 tests
ruff check .
```

GitHub Actions runs the linter and tests on Python 3.9, 3.12 and 3.13.
