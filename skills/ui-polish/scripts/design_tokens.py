#!/usr/bin/env python3
"""design_tokens.py: extract a design-token JSON from a CSS file (stdlib only).

Parses a CSS file (or any file that looks like CSS) for:
  colors       hex (#rgb/#rrggbb/#rrggbbaa), rgb()/rgba(), hsl()/hsla()
  font_sizes   every font-size declaration value
  spacing      margin/padding/gap values
  radii        border-radius values
  shadows      box-shadow declarations
  fonts        font-family stacks

Output: JSON on stdout or -o PATH.

Usage:
  python3 design_tokens.py styles.css -o tokens.json
  python3 design_tokens.py --help

Exit codes: 0 = wrote tokens (even if sparse), 1 = bad input, 2 = parse
aborted (file unreadable / not CSS at all).
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HEX_RE = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)"
)
HSL_RE = re.compile(
    r"hsla?\(\s*(\d+)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*(?:,\s*([\d.]+)\s*)?\)"
)
# a declaration follows a '{' (start of block) or ';' (previous decl);
# this picks up every property, including several on one line
DECL_RE = re.compile(
    r"[;{]\s*([a-z-]+)\s*:\s*([^;]+)"
)


def norm_hex(m: re.Match) -> str:
    v = m.group(1).lower()
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) == 8:
        v = v[:6] + v[6:]
    return "#" + v[:6]


def norm_rgb(m: re.Match) -> str:
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    a = m.group(4)
    if a is not None:
        return "rgba(%d, %d, %d, %s)" % (r, g, b, a)
    return "rgb(%d, %d, %d)" % (r, g, b)


def norm_hsl(m: re.Match) -> str:
    h = int(m.group(1)) % 360
    s, l, a = m.group(2), m.group(3), m.group(4)
    if a is not None:
        return "hsla(%d, %s%%, %s%%, %s)" % (h, s, l, a)
    return "hsl(%d, %s%%, %s%%)" % (h, s, l)


def extract_colors(css: str) -> list:
    seen, counts = set(), Counter()
    for m in HEX_RE.finditer(css):
        seen.add(norm_hex(m))
    for m in RGB_RE.finditer(css):
        seen.add(norm_rgb(m))
    for m in HSL_RE.finditer(css):
        seen.add(norm_hsl(m))
    for c in seen:
        counts[c] += 1
    return [
        {"value": c, "count": n}
        for c, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def extract_decl_values(css: str, prop: str, exact: bool = False) -> list:
    out = []
    for m in DECL_RE.finditer(css):
        if m.group(1) != prop:
            continue
        val = m.group(2).strip()
        if exact:
            out.append(val)
        else:
            out.append(val)
    return out


def collect(prop_list, css: str, top: int = 20) -> list:
    vals = Counter()
    for prop in prop_list:
        for v in extract_decl_values(css, prop):
            v = re.sub(r"\s+", " ", v)
            if not v or v in ("auto", "inherit", "unset", "none", "normal"):
                continue
            vals[v] += 1
    return [
        {"value": v, "count": n}
        for v, n in sorted(vals.items(), key=lambda kv: (-kv[1], kv[0]))[:top]
    ]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract design tokens (colors, type, spacing, radii, "
        "shadows, fonts) from a CSS file into JSON."
    )
    ap.add_argument("css", help="path to a CSS file (or a file containing CSS)")
    ap.add_argument(
        "-o",
        "--out",
        help="write JSON here instead of stdout",
    )
    ap.add_argument(
        "--top",
        type=int,
        default=20,
        help="max entries per token list (default 20)",
    )
    args = ap.parse_args()

    p = Path(args.css)
    if not p.is_file():
        print("error: %s is not a file" % args.css, file=sys.stderr)
        return 1
    try:
        css = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print("error: cannot read %s: %s" % (args.css, e), file=sys.stderr)
        return 2

    if "{" not in css and "color" not in css and "font" not in css:
        print(
            "error: %s does not look like CSS (no rules found)" % args.css,
            file=sys.stderr,
        )
        return 2

    tokens = {
        "source": str(p),
        "colors": extract_colors(css)[: args.top],
        "font_sizes": collect(["font-size"], css, args.top),
        "spacing": collect(
            ["margin", "margin-top", "margin-bottom", "margin-left",
             "margin-right", "padding", "padding-top", "padding-bottom",
             "gap", "row-gap", "column-gap"],
            css,
            args.top,
        ),
        "radii": collect(
            ["border-radius", "border-top-left-radius",
             "border-top-right-radius", "border-bottom-left-radius",
             "border-bottom-right-radius"],
            css,
            args.top,
        ),
        "shadows": collect(["box-shadow"], css, args.top),
        "fonts": collect(["font-family"], css, args.top),
    }

    out = json.dumps(tokens, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
        print("wrote %s" % args.out, file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
