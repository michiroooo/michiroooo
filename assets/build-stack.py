#!/usr/bin/env python3
"""Render assets/tech-stack.svg from simple-icons brand paths.

The tech stack is drawn into a committed SVG rather than fetched from a badge
service at page-view time, so the profile cannot break on someone else's
rate limit. Edit STACK below and re-run:

    npm pack simple-icons && tar xzf simple-icons-*.tgz
    python3 assets/build-stack.py package > assets/tech-stack.svg

An entry whose slug is None is drawn as a text-only chip (used for names that
have no brand mark in simple-icons, such as Objective-C).
"""
import json
import sys

# (group label, [(simple-icons slug or None, display name), ...])
STACK = [
    ("LANGUAGES", [
        ("python", "Python"),
        ("cplusplus", "C++"),
        (None, "Objective-C"),
    ]),
    ("VISION", [
        ("opencv", "OpenCV"),
        ("onnx", "ONNX"),
        ("mediapipe", "MediaPipe"),
    ]),
    ("TRAINING", [
        ("pytorch", "PyTorch"),
        ("lightning", "Lightning"),
        ("huggingface", "Hugging Face"),
        ("weightsandbiases", "W&B"),
        ("mlflow", "MLflow"),
    ]),
    ("SERVING", [
        ("vllm", "vLLM"),
        ("fastapi", "FastAPI"),
        ("docker", "Docker"),
        ("googlecloud", "Google Cloud"),
    ]),
    ("AGENTS", [
        ("claudecode", "Claude Code"),
        ("modelcontextprotocol", "MCP"),
        ("langgraph", "LangGraph"),
        ("pydantic", "Pydantic"),
        ("opentelemetry", "OpenTelemetry"),
    ]),
    ("TOOLING", [
        ("uv", "uv"),
        ("ruff", "Ruff"),
        ("github", "GitHub"),
    ]),
]

WIDTH = 900
LABEL_W = 108
PAD_X = 28
PAD_TOP = 26
ROW_H = 40
CHIP_H = 30
ICON = 17
GAP = 9
CHAR_W = 7.05
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(text):
    """Escape text for both element content and attribute values."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def lift(hex_color, floor=0.42):
    """Blend a brand color toward white until it reads on a dark card."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum < floor:
        t = (floor - lum) / (1 - lum) if lum < 1 else 0
        r, g, b = (c + (1 - c) * t for c in (r, g, b))
    return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))


def main(pkg):
    meta = json.load(open(f"{pkg}/data/simple-icons.json"))
    icons = meta["icons"] if isinstance(meta, dict) else meta
    by_title = {i["title"]: i for i in icons}
    by_slug = {i.get("slug"): i for i in icons if i.get("slug")}

    def brand(slug):
        rec = by_slug.get(slug) or next(
            (i for t, i in by_title.items() if t.lower().replace(" ", "") == slug), None)
        if rec is None:
            sys.exit(f"unknown simple-icons slug: {slug}")
        return rec["hex"]

    def path(slug):
        raw = open(f"{pkg}/icons/{slug}.svg").read()
        start = raw.index('d="') + 3
        return raw[start:raw.index('"', start)]

    out = []
    y = PAD_TOP
    for label, entries in STACK:
        out.append(
            f'<text x="{PAD_X}" y="{y + CHIP_H / 2 + 3.5}" font-family="{SANS}" font-size="10" '
            f'font-weight="600" fill="#64748b" letter-spacing="1.3">{esc(label)}</text>')
        x = PAD_X + LABEL_W
        for slug, name in entries:
            text_w = len(name) * CHAR_W
            chip_w = 13 + (ICON + GAP if slug else 0) + text_w + 14
            if x + chip_w > WIDTH - PAD_X:          # wrap within the group
                y += ROW_H
                x = PAD_X + LABEL_W
            out.append(
                f'<g><title>{esc(name)}</title>'
                f'<rect x="{x:.1f}" y="{y}" width="{chip_w:.1f}" height="{CHIP_H}" rx="{CHIP_H / 2}" '
                f'fill="#151d38" stroke="#26314f" stroke-width="1"/>')
            tx = x + 13
            if slug:
                s = ICON / 24
                out.append(
                    f'<g transform="translate({tx:.1f},{y + (CHIP_H - ICON) / 2:.1f}) scale({s:.4f})">'
                    f'<path d="{path(slug)}" fill="{lift(brand(slug))}"/></g>')
                tx += ICON + GAP
            out.append(
                f'<text x="{tx:.1f}" y="{y + CHIP_H / 2 + 4.5}" font-family="{SANS}" font-size="13" '
                f'fill="#cbd5e1">{esc(name)}</text></g>')
            x += chip_w + 8
        y += ROW_H

    height = y + 10
    print(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
          f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Tech stack">')
    print('  <title>Tech stack</title>')
    print('  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
          '<stop offset="0%" stop-color="#0b1020"/><stop offset="100%" stop-color="#101a38"/>'
          '</linearGradient></defs>')
    print(f'  <rect width="{WIDTH}" height="{height}" rx="18" fill="url(#bg)"/>')
    print("  " + "\n  ".join(out))
    print("</svg>")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "package")
