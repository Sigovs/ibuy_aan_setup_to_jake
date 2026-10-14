#!/usr/bin/env python3
"""
Generates scss/_theme-parity.scss — the light-section / dark-island colour layer.

Why: the vanilla design (Sigovs/ibuy, 04-build) themes sections with CSS custom
properties — `.theme-light` re-defines --c-text, --c-line, --c-brand… and every
rule inside re-colours itself. The AAN kit forbids CSS-var theming, so the port
compiled everything with the DARK values and hand-patched only a few selectors
for light sections. Result: dozens of elements inside light sections kept dark
colours.

This script reads the vanilla CSS, finds every declaration whose value uses a
theme variable, resolves it with the light (or dark-island) token values and
emits the same selector scoped under `.aan-section--light` (and
`.aan-section--light .aan-section--dark` for the dark card inside a light
section). Plain literal values — no CSS variables reach the output.

Usage:  python3 tools/gen-theme-parity.py <path-to-vanilla-04-build/css>
"""
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "scss" / "_theme-parity.scss"

FILES = ["base.css", "page.css", "sections/network.css", "sections/transport.css",
         "sections/process.css", "sections/buy.css", "sections/reviews.css",
         "sections/footer.css", "footer3.css"]

LIGHT, DARK = ".aan-section--light", ".aan-section--dark"


def strip_comments(t):
    return re.sub(r"/\*.*?\*/", "", t, flags=re.S)


def parse(text):
    """Tiny block parser → list of (prelude, body|children). Nested for @-rules."""
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j < 0:
            break
        prelude = text[i:j].strip()
        # matching brace
        depth, k = 1, j + 1
        while depth and k < n:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        body = text[j + 1:k - 1]
        if prelude.startswith("@media") or prelude.startswith("@supports"):
            out.append((prelude, parse(body)))
        elif prelude.startswith("@"):
            pass  # keyframes / font-face — not themed
        else:
            out.append((prelude, body))
        i = k
    return out


def decls(body):
    res = []
    for d in body.split(";"):
        if ":" in d:
            p, v = d.split(":", 1)
            res.append((p.strip(), v.strip()))
    return res


def token_map(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", css, flags=re.S)
    return {p: v for p, v in decls(m.group(1)) if p.startswith("--")}


tokens_css = strip_comments((SRC / "tokens.css").read_text())
ROOT = token_map(tokens_css, ":root")
L = {**ROOT, **token_map(tokens_css, ".theme-light")}
D = {**ROOT, **token_map(tokens_css, ".theme-dark")}
THEMED = set(token_map(tokens_css, ".theme-light")) | set(token_map(tokens_css, ".theme-dark"))

VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\))?[^()]*))?\)")


def resolve(v, m, depth=0):
    if depth > 8:
        return v
    def sub(mt):
        name, fb = mt.group(1), mt.group(2)
        return m.get(name, fb.strip() if fb else mt.group(0))
    nv = VAR.sub(sub, v)
    return resolve(nv, m, depth + 1) if "var(" in nv and nv != v else nv


def uses_theme(v, depth=0):
    for name in re.findall(r"var\(\s*(--[\w-]+)", v):
        if name in THEMED:
            return True
        if depth < 6 and name in ROOT and uses_theme(ROOT[name], depth + 1):
            return True
    return False


def rename(s):
    """Vanilla button classes → AAN kit classes (the only renames in the port)."""
    s = re.sub(r"\.btn--primary(?![\w-])", ".btn-1", s)
    s = re.sub(r"\.btn--ghost(?![\w-])", ".btn-3", s)
    s = re.sub(r"\.btn--block(?![\w-])", ".btn-block", s)
    s = re.sub(r"\.btn(?![\w-])", ":is(.btn-1, .btn-3)", s)
    return s


def scoped(sel, scope, theme_cls):
    """Selector list → scoped list. `.theme-light/.theme-dark` in vanilla
    selectors map to the AAN classes."""
    out = []
    for s in [x.strip() for x in sel.split(",") if x.strip()]:
        s = s.replace(".theme-light", LIGHT).replace(".theme-dark", DARK)
        s = rename(s)
        if s.startswith(":root") or s.startswith("html") or s.startswith("body") or s.startswith("*"):
            continue
        if LIGHT in s or DARK in s:
            out.append(s if s.startswith(scope.split()[0]) else f"{scope} {s}")
            continue
        out.append(f"{scope} {s}")
        # the section/island element itself carries the class
        if re.fullmatch(r"[\w.#\-\[\]='\"]+", s) and not s.startswith("#"):
            out.append(f"{s}{theme_cls}" if scope == LIGHT else f"{LIGHT} {s}{DARK}")
    return out


def emit(nodes, ind=""):
    lines = []
    for prelude, body in nodes:
        if isinstance(body, list):
            inner = emit(body, ind + "  ")
            if inner:
                lines.append(f"{ind}{prelude} {{")
                lines += inner
                lines.append(f"{ind}}}")
            continue
        themed = [(p, v) for p, v in decls(body) if not p.startswith("--") and uses_theme(v)]
        if not themed:
            continue
        for scope, m, cls in ((LIGHT, L, LIGHT), (f"{LIGHT} {DARK}", D, DARK)):
            sels = scoped(prelude, scope, cls)
            if not sels:
                continue
            lines.append(f"{ind}{(',' + chr(10) + ind).join(sels)} {{")
            for p, v in themed:
                lines.append(f"{ind}  {p}: {resolve(v, m)};")
            lines.append(f"{ind}}}")
    return lines


header = """// ============================================================================
//  _theme-parity.scss — GENERATED by tools/gen-theme-parity.py. Do not hand-edit.
//  Light sections (.aan-section--light) and the dark island inside them
//  (.aan-section--dark) get exactly the colours the vanilla design resolves
//  from its theme tokens — as literal values, no CSS variables.
// ============================================================================
"""
body = [
    f"{LIGHT} {{ background: {L['--c-bg']}; color: {L['--c-text']}; }}",
    f"{LIGHT} {DARK} {{ background: {D['--c-void']}; color: {D['--c-text']}; }}",
]
for f in FILES:
    nodes = parse(strip_comments((SRC / f).read_text()))
    chunk = emit(nodes)
    if chunk:
        body.append(f"\n// --- {f}")
        body += chunk
OUT.write_text(header + "\n".join(body) + "\n")
print(f"wrote {OUT} ({len(body)} lines)")
