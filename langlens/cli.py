"""Command-line interface: ``langlens`` / ``python -m langlens``."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

from . import __version__
from .detector import Analysis, analyze
from .languages import LANGUAGES, get, resolve
from .translate import TranslationError, translate

_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def bar(p: float, width: int = 24) -> str:
    full = round(p * width)
    return _c("█" * full, "32") + _c("░" * (width - full), "2")


def render(a: Analysis, show_segments: bool = True) -> str:
    out = []
    if a.best.code == "und":
        return _c("🤔 Not enough letters to detect a language.", "33")
    best = a.best
    lang = best.language
    tag = "" if best.reliable else _c("  (low confidence: try a longer text)", "33")
    out.append(f"{lang.flag}  {_c(best.name, '1')} · {lang.native} · {best.code}{tag}")
    out.append("")
    for d in a.candidates:
        out.append(f"   {d.language.flag} {d.name:<22} {bar(d.confidence)} {d.confidence * 100:5.1f}%")
    if len(a.scripts) > 0:
        out.append("")
        out.append("   Scripts: " + ", ".join(f"{s} {p * 100:.0f}%" for s, p in a.scripts.items()))
    if show_segments and a.mixed:
        out.append("")
        out.append(_c("   Mixed-language text:", "1"))
        for seg in a.segments:
            out.append(f"   {seg.detection.language.flag} {seg.detection.code:<7} {seg.text}")
    return "\n".join(out)


def _read_text(args: argparse.Namespace) -> str:
    if getattr(args, "text", None):
        return " ".join(args.text)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit('Give some text, e.g.  langlens detect "Bonjour tout le monde"')


def cmd_detect(args: argparse.Namespace) -> int:
    a = analyze(_read_text(args))
    a.candidates = a.candidates[: args.top]
    print(json.dumps(a.to_dict(), ensure_ascii=False, indent=2) if args.json else render(a))
    return 0 if a.best.code != "und" else 1


def _target(name: str) -> str:
    code = resolve(name)
    if not code:
        raise SystemExit(f"Unknown language “{name}”. See: langlens languages")
    return code


def cmd_translate(args: argparse.Namespace) -> int:
    text = _read_text(args)
    try:
        t = translate(text, _target(args.to), _target(args.source) if args.source else None)
    except TranslationError as exc:
        print(_c(f"Translation failed: {exc}", "31"), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
    else:
        s, d = get(t.source), get(t.target)
        print(f"{s.flag} {s.name} → {d.flag} {d.name}  {_c('(' + t.backend + ')', '2')}")
        print(_c(t.translated, "1"))
    return 0


def cmd_file(args: argparse.Namespace) -> int:
    """Detect the language of every non-empty line of a file (or stdin)."""
    src = open(args.path, encoding="utf-8") if args.path != "-" else sys.stdin
    rows = []
    with src:
        for n, line in enumerate(src, 1):
            line = line.strip()
            if line:
                d = analyze(line).best
                rows.append(
                    {"line": n, "code": d.code, "language": d.name, "confidence": round(d.confidence, 3), "text": line}
                )
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            if args.output.endswith(".json"):
                json.dump(rows, fh, ensure_ascii=False, indent=2)
            else:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["line"])
                w.writeheader()
                w.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.output}")
    else:
        for r in rows:
            print(
                f"{r['line']:>5}  {get(r['code']).flag} {r['code']:<7} {r['confidence'] * 100:5.1f}%  {r['text'][:70]}"
            )
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["language"]] = counts.get(r["language"], 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    print(_c(f"\nSummary: {summary}", "2"), file=sys.stderr)
    return 0


def cmd_languages(args: argparse.Namespace) -> int:
    for lang in sorted(LANGUAGES.values(), key=lambda lang: lang.name):
        print(f"{lang.flag}  {lang.code:<4} {lang.name:<18} {lang.native}")
    print(f"\n{len(LANGUAGES)} languages, plus romanized Hindi (hi-Latn) and Telugu (te-Latn).")
    return 0


def cmd_quiz(args: argparse.Namespace) -> int:
    from .quiz import play

    play(rounds=args.rounds, seed=args.seed)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .web import serve

    serve(args.host, args.port, open_browser=not args.no_browser)
    return 0


def repl() -> int:
    print(_c(f"LangLens {__version__}", "1") + " · type any text to detect its language.")
    print(_c("Commands: :to <language> translate the last text · :quiz · :q to quit", "2"))
    last = ""
    while True:
        try:
            line = input(_c("› ", "36")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line in (":q", ":quit", "exit"):
            return 0
        if line == ":quiz":
            cmd_quiz(argparse.Namespace(rounds=5, seed=None))
            continue
        if line.startswith(":to "):
            if not last:
                print("Type some text first.")
                continue
            try:
                t = translate(last, _target(line[4:]))
                print(_c(t.translated, "1"))
            except (TranslationError, SystemExit) as exc:
                print(_c(str(exc), "31"))
            continue
        last = line
        print(render(analyze(line)))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="langlens", description="Detect and translate languages.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")

    d = sub.add_parser("detect", help="detect the language of some text")
    d.add_argument("text", nargs="*")
    d.add_argument("--json", action="store_true")
    d.add_argument("--top", type=int, default=3, help="how many candidates to show")
    d.set_defaults(func=cmd_detect)

    t = sub.add_parser("translate", help="translate text")
    t.add_argument("text", nargs="*")
    t.add_argument("--to", default="en", help="target language (code or name)")
    t.add_argument("--from", dest="source", help="source language (auto-detected by default)")
    t.add_argument("--json", action="store_true")
    t.set_defaults(func=cmd_translate)

    f = sub.add_parser("file", help="detect each line of a file ('-' for stdin)")
    f.add_argument("path")
    f.add_argument("-o", "--output", help="write results to .csv or .json")
    f.set_defaults(func=cmd_file)

    sub.add_parser("languages", help="list supported languages").set_defaults(func=cmd_languages)

    q = sub.add_parser("quiz", help="play “guess the language”")
    q.add_argument("--rounds", type=int, default=10)
    q.add_argument("--seed", type=int)
    q.set_defaults(func=cmd_quiz)

    s = sub.add_parser("serve", help="start the web app")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--no-browser", action="store_true")
    s.set_defaults(func=cmd_serve)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not getattr(args, "func", None):
        return repl()
    return args.func(args)
