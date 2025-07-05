#!/usr/bin/env python3
"""
mdcat.py  —  “cat, but pretty-prints Markdown (and friends)”

• If file args are given, render each in turn.
• If no args, read stdin until EOF.
• If the format can't be detected, fall back to plain cat.
"""

from __future__ import annotations
import sys, argparse, json, pathlib, typing as T
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console(highlight=False)  # -> let renderers decide colours


# ---------- renderers -------------------------------------------------

def render_markdown(text: str) -> None:
    console.print(Markdown(text, code_theme="ansi_light"))

def render_json(text: str) -> None:
    parsed = json.loads(text)
    console.print(Syntax(json.dumps(parsed, indent=2), "json", word_wrap=False))

def render_plain(text: str) -> None:
    console.print(text, end="")


RENDERERS: dict[str, T.Callable[[str], None]] = {
    "md": render_markdown,
    "markdown": render_markdown,
    "json": render_json,
    "txt": render_plain,
}


# ---------- helpers ---------------------------------------------------

def detect_format(path: pathlib.Path | None, forced: str | None) -> str:
    if forced:
        return forced
    if path:
        ext = path.suffix.lower().lstrip(".")
        if ext in RENDERERS:
            return ext
    return "txt"  # default fallback


def consume(path: pathlib.Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


# ---------- CLI -------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Pretty-print to the terminal.")
    ap.add_argument("files", nargs="*", help="files to render; omit for stdin")
    ap.add_argument("-f", "--format",
                    choices=sorted(RENDERERS.keys()),
                    help="force input format (md, json, txt, …)")
    ns = ap.parse_args(argv)

    if not ns.files:
        text = consume(None)
        fmt = detect_format(None, ns.format)
        RENDERERS.get(fmt, render_plain)(text)
        return

    for fname in ns.files:
        path = pathlib.Path(fname)
        try:
            text = consume(path)
        except FileNotFoundError as e:
            console.print(f"[red]error:[/] {e}", file=sys.stderr)
            continue
        fmt = detect_format(path, ns.format)
        RENDERERS.get(fmt, render_plain)(text)


if __name__ == "__main__":
    main()
