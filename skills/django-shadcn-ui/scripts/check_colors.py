#!/usr/bin/env python3
"""Flag non-token colors in Django/cotton templates.

Usage: python check_colors.py <file-or-dir> [...]
Reports raw Tailwind palette classes (bg-blue-500, text-white, dark:bg-gray-800 ...),
arbitrary color values (bg-[#fff]), and inline color styles / color literals.
Exit code 1 if anything is found. Only shadcn semantic tokens should be used.
"""
import re
import sys
from pathlib import Path

PALETTE = (
    "slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|"
    "cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
)
UTIL = (
    "bg|text|border|border-[trblxy]|ring|ring-offset|outline|divide|fill|stroke|"
    "from|via|to|placeholder|caret|accent|decoration|shadow"
)
PREFIX = r"(?:(?<=[\s\"'`:])|^)(?:[\w\-\[\]&>*:.@]+:)?!?"
PATTERNS = [
    ("palette color", re.compile(PREFIX + rf"(?:{UTIL})-(?:{PALETTE})-\d{{2,3}}(?:/\d+)?\b")),
    ("black/white", re.compile(PREFIX + rf"(?:{UTIL})-(?:black|white)(?:/\d+)?\b")),
    ("arbitrary color", re.compile(rf"(?:{UTIL})-\[(?:#|rgb|hsl|oklch|color)[^\]]*\]")),
    ("inline color style", re.compile(r"style=[\"'][^\"']*(?:color|background|border-color|fill|stroke)\s*:", re.I)),
    ("hex literal", re.compile(r"(?<![\w&])#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?\b(?![\w-])")),
]
EXTS = {".html", ".htm", ".txt", ".jinja", ".djhtml"}


def files(args):
    for a in args:
        p = Path(a)
        if p.is_dir():
            yield from (f for f in p.rglob("*") if f.suffix in EXTS)
        elif p.exists():
            yield p


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    found = 0
    for f in files(argv):
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            if "check_colors: ignore" in line:
                continue
            for label, rx in PATTERNS:
                for m in rx.finditer(line):
                    tok = m.group(0)
                    # hex inside svg ids / url anchors / django template comments are rare; skip href="#..."
                    if label == "hex literal" and re.search(r"(href|url\()\s*=?\s*[\"']?" + re.escape(tok), line):
                        continue
                    found += 1
                    print(f"{f}:{n}: {label}: {tok.strip()}")
    if found:
        print(f"\n{found} non-token color(s). Use shadcn tokens (bg-primary, text-muted-foreground, border-input, ...).")
        return 1
    print("OK: only semantic color tokens found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
