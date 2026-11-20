#!/usr/bin/env python3
"""Compose the final 1024x1024 news front page for news-image-20261120.

Build-time only: takes the generated 2x2 panel artwork (artwork.png),
crops each quadrant, and overlays a newspaper masthead, per-panel
headlines/captions and a bottom news ticker with PIL. Output is
entry.png (PNG if it fits in 1 MiB, else JPEG bytes under the same name).
Deterministic: no timestamps, no randomness, fixed fonts and layout.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "artwork.png")
OUT = os.path.join(HERE, "entry.png")

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

W = H = 1024
NAVY = (13, 24, 43)
GOLD = (212, 160, 23)
WHITE = (255, 255, 255)
OFFWHITE = (232, 232, 232)
DARK = (12, 12, 14)

HEADER_H = 92
PANEL_W, PANEL_H = 512, 400
TICKER_TOP = 904

PANELS = [
    # (quadrant box in 1600x1600 artwork, vertical bias, kicker, headline, sub)
    ((8, 8, 792, 792), 0.30, "SHENZHEN  \u2022  DIPLOMACY",
     "THREE POWERS, ONE TABLE",
     "Trump, Xi and Putin hold the first-ever trilateral summit \u2014 and talk nuclear risk"),
    ((808, 8, 1592, 792), 0.30, "THE HAGUE  \u2022  JUSTICE",
     "GENOCIDE, THE COURT RULES",
     "World court: Myanmar committed genocide against the Rohingya in 2017"),
    ((8, 808, 792, 1592), 0.45, "ODISHA  \u2022  WEATHER",
     "300,000 FLEE CYCLONE AKVAN",
     "Severe storm bears down on India\u2019s east coast; schools shut, trains halted"),
    ((808, 808, 1592, 1592), 0.45, "DEEP SPACE  \u2022  SCIENCE",
     "ONE LIGHT-DAY FROM HOME",
     "Voyager 1: a radio signal now takes a full day to reach the probe"),
]

TICKER = [
    "Trump delays Iran decision to 2027",
    "Europe open to Ukraine talks",
    "Russian strikes hit EU embassies in Kyiv",
    "GTA 6 outsells The Odyssey",
    "Hayabusa2 landing called off",
    "Kushner: Russia open to Article 5 deal",
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured width."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_shadow(d, xy, s, fnt, fill):
    """Crisp text with a 1px dark offset so it stays legible over bright photo areas."""
    d.text((xy[0] + 1, xy[1] + 1), s, font=fnt, fill=(0, 0, 0))
    d.text(xy, s, font=fnt, fill=fill)


def scrim(panel):
    """Bottom-up black gradient overlay, 170px tall."""
    grad = Image.new("L", (1, 170))
    for y in range(170):
        grad.putpixel((0, y), int(205 * (y / 169.0) ** 1.4))
    grad = grad.resize((PANEL_W, 170))
    black = Image.new("RGB", (PANEL_W, 170), (0, 0, 0))
    panel.paste(black, (0, PANEL_H - 170), grad)
    return panel


def main():
    art = Image.open(SRC).convert("RGB")
    canvas = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(canvas)

    # Header band
    draw.rectangle([0, 0, W, HEADER_H], fill=NAVY)
    draw.rectangle([0, HEADER_H, W, HEADER_H + 3], fill=GOLD)
    mast = font(SERIF_BOLD, 40)
    date_f = font(BOLD, 24)
    draw.text((20, 24), "THE WORLD IN ONE IMAGE", font=mast, fill=WHITE)
    date_txt = "FRIDAY  20 NOVEMBER 2026"
    draw.text((W - 20 - draw.textlength(date_txt, font=date_f), 32),
              date_txt, font=date_f, fill=GOLD)

    # Panels
    kick_f = font(BOLD, 16)
    head_f = font(BOLD, 29)
    sub_f = font(REG, 18)
    for i, (box, bias, kicker, headline, sub) in enumerate(PANELS):
        quad = art.crop(box)
        panel = ImageOps.fit(quad, (PANEL_W, PANEL_H),
                             method=Image.LANCZOS, centering=(0.5, bias))
        panel = scrim(panel)
        px = (i % 2) * PANEL_W
        py = HEADER_H + 4 + (i // 2) * (PANEL_H + 4)
        canvas.paste(panel, (px, py))
        d = ImageDraw.Draw(canvas)
        tx = px + 16
        base = py + PANEL_H
        text_shadow(d, (tx, base - 164), kicker, kick_f, GOLD)
        text_shadow(d, (tx, base - 140), headline, head_f, WHITE)
        lines = wrap(d, sub, sub_f, PANEL_W - 32)
        for j, line in enumerate(lines[:2]):
            text_shadow(d, (tx, base - 102 + j * 23), line, sub_f, OFFWHITE)

    # Ticker band
    draw.rectangle([0, TICKER_TOP, W, H], fill=NAVY)
    draw.rectangle([0, TICKER_TOP, W, TICKER_TOP + 3], fill=GOLD)
    tick_f = None
    sep = "   \u2022   "
    # Split items into two balanced lines, each fitting the width.
    line1_items, line2_items = TICKER[:3], TICKER[3:]
    line1 = sep.join(line1_items)
    line2 = sep.join(line2_items)
    for size in (19, 18, 17, 16):
        tick_f = font(REG, size)
        if (draw.textlength(line1, font=tick_f) <= W - 40
                and draw.textlength(line2, font=tick_f) <= W - 40):
            break
    band_h = H - TICKER_TOP - 3
    total_h = 2 * size + 12
    y0 = TICKER_TOP + 3 + (band_h - total_h) // 2
    draw.text((20, y0), line1, font=tick_f, fill=WHITE)
    draw.text((20, y0 + size + 12), line2, font=tick_f, fill=WHITE)

    # Save: PNG first; fall back to JPEG bytes (still named entry.png) if over 1 MiB.
    canvas.save(OUT, format="PNG", optimize=True)
    if os.path.getsize(OUT) > 1048576:
        canvas.save(OUT, format="JPEG", quality=90, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
