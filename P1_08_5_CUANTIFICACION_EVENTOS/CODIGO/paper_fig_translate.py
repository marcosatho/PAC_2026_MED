# -*- coding: utf-8 -*-
"""Spanish version of Fig. 3 of Aristizábal et al. (2026, Natural Hazards 122:306; CC BY 4.0).

Only the text labels change: axis titles and the two English month abbreviations (Jan -> Ene, Apr -> Abr).
Data, scales, colours and layout are untouched.  The original is a 983 x 584 px raster, so the image is enlarged
3x (Lanczos) and the new labels are drawn at the enlarged size, in the same typeface (DejaVu Sans) and size as the original.

usage: paper_fig_translate.py <original.png> <out.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
from matplotlib import font_manager

SRC, OUT = sys.argv[1:3]
F = 3
FONT = font_manager.findfont("DejaVu Sans")
im = Image.open(SRC)
if im.mode == "RGBA":
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im, mask=im.split()[3])
    im = bg
im = im.convert("RGB")
W, H = im.size
big = im.resize((W * F, H * F), Image.LANCZOS)
d = ImageDraw.Draw(big)


def ink_width(text, size):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(text)
    return r - l


def fit_size(text, target_w, lo=6.0, hi=40.0):
    for _ in range(40):
        mid = (lo + hi) / 2
        if ink_width(text, mid * 10) / 10 < target_w:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# calibrate against the original English labels (ink widths measured on the original image)
# (inclusive ink threshold, measured in paper_fig_calib.py)
s_axis = np.mean([fit_size("Rainfall (mm)", 129), fit_size("Landslides", 100), fit_size("Month", 58)])
s_tick = np.mean([fit_size(t, w) for t, w in (("Feb", 27), ("Mar", 30), ("May", 32), ("Sep", 30), ("Oct", 29), ("Nov", 27))])
C_AXIS, C_TICK = (27, 27, 27), (38, 38, 38)
# month labels of the original are narrower than DejaVu at their cap height (41 px at 3x -> em_y 18.75): squeeze in x
S_TICK_Y = 18.75
S_TICK_X = s_tick / S_TICK_Y
print("font sizes (px at original scale): axis %.2f | tick %.2f" % (s_axis, s_tick))


def erase(x0, y0, x1, y1):
    d.rectangle([x0 * F, y0 * F, (x1 + 1) * F, (y1 + 1) * F], fill="white")


# 1) erase the English labels
erase(5, 196, 29, 334)          # left axis title
erase(952, 212, 974, 321)       # right axis title
erase(455, 551, 528, 572)       # x axis title
erase(122, 529, 151, 550)       # 'Jan'
erase(314, 529, 347, 550)       # 'Apr'


def draw_horizontal(text, cx, baseline, size, color, xscale=1.0):
    """Horizontal label centred on cx with its baseline at `baseline` (original-image px).
    xscale < 1 reproduces the narrow proportions of the original month labels (cap height vs. width)."""
    f = ImageFont.truetype(FONT, size * F)
    l, t, r, b = f.getbbox(text, anchor="ls")
    pad = 6
    layer = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (255, 255, 255, 0))
    ImageDraw.Draw(layer).text((pad - l, pad - t), text, font=f, fill=color, anchor="ls")
    if xscale != 1.0:
        layer = layer.resize((max(1, round(layer.width * xscale)), layer.height), Image.LANCZOS)
    x0 = cx * F - (pad + (r - l) / 2) * xscale
    y0 = baseline * F - (pad - t)
    big.paste(layer, (round(x0), round(y0)), layer)


def draw_rotated(text, cx, cy, size, angle, color=C_AXIS):
    f = ImageFont.truetype(FONT, size * F)
    l, t, r, b = f.getbbox(text, anchor="ls")
    w, h = r - l, b - t
    pad = 6
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (255, 255, 255, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad - l, pad - t), text, font=f, fill=color, anchor="ls")
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    big.paste(rot, (int(cx * F - rot.width / 2), int(cy * F - rot.height / 2)), rot)


# 2) new labels (same centres / baselines as the originals)
draw_rotated("Precipitación (mm)", 17.0, 264.5, s_axis, 90)       # reads bottom-to-top
draw_rotated("Deslizamientos", 963.0, 266.0, s_axis, 270)         # reads top-to-bottom
draw_horizontal("Mes", 491.5, 569.2, s_axis, C_TICK)
draw_horizontal("Ene", 136.5, 545.3, S_TICK_Y, C_TICK, S_TICK_X)
draw_horizontal("Abr", 330.5, 545.3, S_TICK_Y, C_TICK, S_TICK_X)
big.save(OUT, dpi=(300, 300))
print("saved", OUT, big.size)
