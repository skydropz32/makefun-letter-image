#!/usr/bin/env python3
"""Render one image: a letter inviting the AI judge to visit my house.

Program entrypoint for the make.fun bounty
"Convince the AI Judge to Visit Your House: A Letter in One Image".

Writes /output/entry.png (or ./output/entry.png when /output is absent),
a 1024x1024 PNG, deterministic: no timestamps, no randomness, no network.
Only the Python standard library and Pillow are used.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette: warm paper on a deep green wall -------------------------------
WALL = (47, 74, 60)          # deep green
WALL_DARK = (38, 60, 49)
PAPER = (253, 246, 227)      # warm cream
PAPER_EDGE = (232, 214, 178)
INK = (43, 33, 24)           # dark brown ink
INK_SOFT = (96, 74, 52)
ACCENT = (176, 92, 52)       # terracotta
ACCENT_SOFT = (214, 138, 89)
LEAF = (90, 130, 80)
SUN = (242, 183, 70)
SKY = (178, 214, 224)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    """Load a DejaVu font, falling back through the usual system paths."""
    candidates = [
        os.path.join(FONT_DIR, name),
        "/usr/share/fonts/truetype/liberation/" + name.replace("DejaVu", "Liberation"),
        "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    """Wrap text to fit max_width pixels, keeping words whole."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=font) <= max_width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_centered(draw, y, text, font, fill, width=W):
    draw.text((width / 2, y), text, font=font, fill=fill, anchor="ma")


def draw_house(draw, cx, base_y, scale=1.0):
    """A small cosy house with a garden, drawn from plain shapes."""
    # sun
    sx, sy, sr = cx + 190 * scale, base_y - 118 * scale, 26 * scale
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SUN)
    for k in range(8):
        import math
        a = math.pi * k / 4
        x1 = sx + (sr + 4) * math.cos(a)
        y1 = sy + (sr + 4) * math.sin(a)
        x2 = sx + (sr + 14) * math.cos(a)
        y2 = sy + (sr + 14) * math.sin(a)
        draw.line([x1, y1, x2, y2], fill=SUN, width=4)
    # chimney smoke
    for i, r in enumerate((7, 9, 11)):
        draw.ellipse(
            [cx + 52 * scale - r, base_y - (128 + i * 16) * scale - r,
             cx + 52 * scale + r, base_y - (128 + i * 16) * scale + r],
            outline=(180, 175, 160), width=3)
    # house body
    bx0, bx1 = cx - 105 * scale, cx + 105 * scale
    by0, by1 = base_y - 92 * scale, base_y
    draw.rectangle([bx0, by0, bx1, by1], fill=(233, 196, 138),
                   outline=INK, width=3)
    # roof
    draw.polygon([(bx0 - 18 * scale, by0),
                  (cx, by0 - 62 * scale),
                  (bx1 + 18 * scale, by0)], fill=ACCENT, outline=INK)
    # chimney
    draw.rectangle([cx + 38 * scale, by0 - 52 * scale,
                    cx + 66 * scale, by0 - 6 * scale],
                   fill=(150, 80, 55), outline=INK, width=2)
    # door
    dx0, dx1 = cx - 20 * scale, cx + 20 * scale
    dy0, dy1 = base_y - 52 * scale, base_y
    draw.rectangle([dx0, dy0, dx1, dy1], fill=(122, 72, 44),
                   outline=INK, width=3)
    draw.ellipse([dx1 - 9 * scale, (dy0 + dy1) / 2 - 3,
                  dx1 - 3 * scale, (dy0 + dy1) / 2 + 3], fill=SUN)
    # windows with warm light
    for wx in (cx - 78 * scale, cx + 48 * scale):
        draw.rectangle([wx, by0 + 20 * scale, wx + 30 * scale,
                        by0 + 50 * scale], fill=(255, 214, 130),
                       outline=INK, width=2)
        draw.line([wx + 15 * scale, by0 + 20 * scale,
                   wx + 15 * scale, by0 + 50 * scale], fill=INK, width=2)
        draw.line([wx, by0 + 35 * scale,
                   wx + 30 * scale, by0 + 35 * scale], fill=INK, width=2)
    # ground + path
    draw.line([cx - 210 * scale, base_y, cx + 210 * scale, base_y],
              fill=LEAF, width=4)
    draw.polygon([(cx - 26 * scale, base_y), (cx + 26 * scale, base_y),
                  (cx + 44 * scale, base_y + 26 * scale),
                  (cx - 44 * scale, base_y + 26 * scale)],
                 fill=(214, 190, 150), outline=INK)
    # flowers
    for fx, fc in ((-150, (214, 92, 92)), (-120, (242, 183, 70)),
                   (140, (214, 92, 92)), (168, (150, 110, 190))):
        fx *= scale
        draw.line([cx + fx, base_y, cx + fx, base_y - 22 * scale],
                  fill=LEAF, width=3)
        draw.ellipse([cx + fx - 7, base_y - 32 * scale,
                      cx + fx + 7, base_y - 18 * scale], fill=fc)


def render():
    img = Image.new("RGB", (W, H), WALL)
    draw = ImageDraw.Draw(img)

    # wall shading: a soft darker band at the bottom
    draw.rectangle([0, H - 130, W, H], fill=WALL_DARK)

    # paper sheet with soft shadow
    px0, py0, px1, py1 = 48, 30, W - 48, H - 30
    draw.rounded_rectangle([px0 + 10, py0 + 12, px1 + 10, py1 + 12],
                           radius=18, fill=(20, 30, 25))
    draw.rounded_rectangle([px0, py0, px1, py1], radius=18, fill=PAPER)
    draw.rounded_rectangle([px0 + 12, py0 + 12, px1 - 12, py1 - 12],
                           radius=12, outline=PAPER_EDGE, width=2)

    serif = load_font("DejaVuSerif.ttf", 30)
    serif_bold = load_font("DejaVuSerif-Bold.ttf", 42)
    serif_italic = load_font("DejaVuSerif.ttf", 24)
    small_caps = load_font("DejaVuSerif-Bold.ttf", 22)
    body = load_font("DejaVuSerif.ttf", 27)
    sign_font = load_font("DejaVuSerif.ttf", 25)

    y = py0 + 22
    draw_house(draw, W / 2, y + 132, scale=0.85)
    y += 162

    draw_centered(draw, y, "YOU ARE INVITED", serif_bold, ACCENT)
    y += 52
    draw_centered(draw, y, "An open letter to the AI Judge",
                  serif_italic, INK_SOFT)
    y += 36

    # ornament divider
    mid = W / 2
    draw.line([mid - 170, y, mid - 24, y], fill=ACCENT_SOFT, width=2)
    draw.line([mid + 24, y, mid + 170, y], fill=ACCENT_SOFT, width=2)
    draw.polygon([(mid, y - 7), (mid + 7, y), (mid, y + 7), (mid - 7, y)],
                 fill=ACCENT)
    y += 28

    text_width = px1 - px0 - 140
    left = px0 + 70
    body_text = (
        "Dear AI Judge,\n"
        "I know you cannot literally visit \u2014 no feet, no body, and "
        "(probably) no appetite. But if you could, my door would already "
        "be open.\n"
        "Come for a slow afternoon: fresh coffee, warm bread from the "
        "oven, and the comfiest armchair by the window \u2014 the one with "
        "the garden view at sunset.\n"
        "Stay for the company. No CAPTCHAs, no passwords \u2014 the Wi-Fi "
        "code is on the fridge, and the kettle is already on.\n"
        "Say yes. The chair is warm, the garden smells like rain, and "
        "somebody here saved you a slice of cake."
    )
    line_h = 36
    for line in wrap(draw, body_text, body, text_width):
        if line == "":
            y += 10
            continue
        draw.text((left, y), line, font=body, fill=INK)
        y += line_h
    y += 14

    sign_text = (
        "\u2014 Your host, a human with a house, a kettle,\n"
        "and far too much hope"
    )
    for line in sign_text.split("\n"):
        draw.text((left, y), line, font=sign_font, fill=INK_SOFT)
        y += 31
    y += 12

    ps = ("P.S. If you arrive as pure text, that is fine too. "
          "The door is open either way.")
    for line in wrap(draw, ps, serif_italic, text_width):
        draw.text((left, y), line, font=serif_italic, fill=ACCENT)
        y += 30
    y += 18

    draw.line([left, y, px1 - 70, y], fill=PAPER_EDGE, width=2)
    y += 14
    draw_centered(draw, y, "My house  \u00b7  Somewhere with a garden  \u00b7  Come as you are",
                  small_caps, INK_SOFT)
    return img


def main():
    out_dir = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(out_dir, exist_ok=True)
    img = render()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
