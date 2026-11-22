#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news broadsheet (1024x1024 PNG).

Everything is drawn from fixed coordinates with Pillow: no photos, no
network, no clock, no randomness, so the output bytes are identical on
every run. Run from the entry repo root:

    python3 tools/make_image.py
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "entry.png")

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (24, 24, 28)
NAVY = (20, 33, 61)
NAVY_LT = (38, 58, 94)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
RED_DK = (122, 20, 20)
TEAL = (18, 92, 86)
CREAM = (250, 246, 236)
GREY = (90, 90, 96)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width` px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, fill, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    leading = leading or int(fnt.size * 1.35)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, color=RED):
    draw.text((x, y), text, font=SANS_B(15), fill=color)
    return y + 22


def headline(draw, x, y, text, fnt, width, fill=INK):
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * 1.08)
    return y


def vgrad(draw, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for yy in range(y0, y1):
        t = (yy - y0) / span
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=col)


def burst(draw, cx, cy, r, colour, spikes=12):
    """Starburst explosion centred on (cx, cy)."""
    pts = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=colour)
    draw.ellipse([cx - r * 0.34, cy - r * 0.34, cx + r * 0.34, cy + r * 0.34],
                 fill=(255, 236, 170))


def arc_trail(draw, pts, colour, width=4):
    draw.line(pts, fill=colour, width=width, joint="curve")
    hx, hy = pts[-1]
    draw.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=(255, 255, 255))
    draw.ellipse([hx - 3, hy - 3, hx + 3, hy + 3], fill=colour)


def curve_points(x0, y0, x1, y1, lift, n=28):
    """Points of a quadratic arc from (x0, y0) to (x1, y1), lifted by `lift`."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - lift
    out = []
    for i in range(n + 1):
        t = i / n
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t ** 2 * x1
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t ** 2 * y1
        out.append((bx, by))
    return out


def skyline(draw, x0, base, widths, heights, colour):
    x = x0
    for w, h in zip(widths, heights):
        draw.rectangle([x, base - h, x + w, base], fill=colour)
        x += w + 3


def masthead(draw):
    draw.rectangle([0, 0, W, 112], fill=NAVY)
    draw.rectangle([0, 112, W, 116], fill=GOLD)
    draw.text((24, 18), "THE WORLD IN ONE IMAGE", font=SERIF_B(52), fill=CREAM)
    draw.text((24, 80), "SUNDAY, 22 NOVEMBER 2026  —  THE DAY IN FIVE STORIES",
              font=SANS_B(17), fill=GOLD)
    draw.text((W - 24, 80), "No. 326", font=SANS(15), fill=(180, 190, 210),
              anchor="ra")


def lead_scene(draw, box):
    """Night sky over the Poland-Ukraine border: missile arcs, impacts."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (16, 24, 52), (58, 72, 110))
    for sx, sy, sr in [(70, 20, 2), (180, 48, 1), (300, 16, 2), (420, 40, 1),
                       (540, 22, 2), (120, 70, 1), (360, 66, 1), (480, 78, 2)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                     fill=(220, 225, 240))
    # ground: dark landmass along the bottom of the scene
    draw.polygon([(x0, y1), (x0, y1 - 52), (x0 + 150, y1 - 88),
                  (x0 + 320, y1 - 60), (x0 + 470, y1 - 96), (x1, y1 - 64),
                  (x1, y1)], fill=(28, 34, 44))
    # dashed border line across the landmass
    bx = x0 + 250
    for yy in range(y1 - 92, y1 - 8, 14):
        draw.line([(bx, yy), (bx, yy + 8)], fill=(240, 220, 130), width=2)
    draw.text((bx - 8, y1 - 100), "POLAND", font=SANS_B(13),
              fill=(240, 220, 130), anchor="ra")
    draw.text((bx - 8, y1 - 28), "UKRAINE", font=SANS_B(13),
              fill=(200, 205, 220), anchor="ra")
    # missile arcs and impacts
    arc_trail(draw, curve_points(x0 + 40, y0 + 150, x0 + 300, y1 - 66, 120),
              (255, 120, 40))
    arc_trail(draw, curve_points(x0 + 560, y0 + 120, x0 + 380, y1 - 78, 100),
              (255, 170, 60))
    burst(draw, x0 + 300, y1 - 66, 26, (255, 90, 30))
    burst(draw, x0 + 380, y1 - 78, 20, (255, 140, 50))
    for ix, iy, lab in [(x0 + 300, y1 - 66, ""), (x0 + 380, y1 - 78, "")]:
        draw.ellipse([ix - 5, iy - 5, ix + 5, iy + 5], outline=(255, 255, 255),
                     width=2)
    draw.text((x0 + 14, y0 + 8), "MISSILES CROSS INTO NATO TERRITORY",
              font=SANS_B(14), fill=(255, 210, 120))


def cop_panel(draw, box):
    """COP31: smokestacks under a hazy sun, talks in overtime."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (214, 196, 160), (240, 226, 196))
    draw.ellipse([x1 - 62, y0 + 10, x1 - 18, y0 + 54], fill=(226, 150, 60))
    base = y1 - 18
    skyline(draw, x0 + 12, base, [34, 26, 40, 30], [34, 48, 28, 40],
            (74, 74, 70))
    for sx, sh in ((x0 + 20, 34), (x0 + 80, 48), (x0 + 128, 28)):
        draw.ellipse([sx, base - sh - 16, sx + 20, base - sh + 2],
                     fill=(150, 148, 140))
    draw.rectangle([x0, base, x1, y1], fill=(60, 60, 56))
    draw.text((x0 + 10, base + 2), "ANTALYA — DAY 2 OF OVERTIME",
              font=SANS_B(11), fill=(240, 230, 200))


def gulf_panel(draw, box):
    """Gulf night: Riyadh skyline, interceptors meeting incoming fire."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (14, 20, 44), (52, 44, 78))
    for sx, sy in [(30, 10), (90, 24), (160, 8), (230, 20)]:
        draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                     fill=(220, 225, 240))
    base = y1 - 18
    skyline(draw, x0 + 10, base, [30, 22, 44, 26, 36], [30, 46, 26, 38, 32],
            (10, 12, 22))
    draw.rectangle([x0 + 132, base - 58, x0 + 138, base], fill=(10, 12, 22))
    draw.polygon([(x0 + 126, base - 58), (x0 + 144, base - 58),
                  (x0 + 135, base - 70)], fill=(10, 12, 22))
    arc_trail(draw, curve_points(x0 + 30, base - 6, x0 + 200, y0 + 34, 26),
              (150, 220, 255), width=3)
    arc_trail(draw, curve_points(x0 + 300, y0 + 12, x0 + 212, y0 + 36, 14),
              (255, 90, 60), width=3)
    burst(draw, x0 + 206, y0 + 35, 13, (255, 160, 70))
    draw.rectangle([x0, base, x1, y1], fill=(10, 12, 22))
    draw.text((x0 + 10, base + 2), "RIYADH UNDER FIRE",
              font=SANS_B(11), fill=(255, 210, 120))


def mexico_panel(draw, box):
    """Desert road at dusk, badge star: the cartel kingpin's capture."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (232, 148, 72), (146, 74, 44))
    draw.ellipse([x1 - 110, y0 + 16, x1 - 30, y0 + 96], fill=(255, 214, 130))
    draw.polygon([(x0, y1 - 70), (x1, y1 - 70), (x1, y1), (x0, y1)],
                 fill=(96, 52, 30))
    draw.polygon([(x0 + 200, y1 - 70), (x0 + 260, y1 - 70), (x0 + 330, y1),
                  (x0 + 150, y1)], fill=(52, 36, 26))
    for i, yy in enumerate(range(y1 - 58, y1 - 4, 18)):
        draw.line([(x0 + 216 + i * 3, yy), (x0 + 240 + i * 3, yy)],
                  fill=(240, 220, 130), width=3)
    cx, cy = x0 + 62, y0 + 62
    star = []
    for i in range(10):
        ang = -math.pi / 2 + math.pi * i / 5
        rr = 34 if i % 2 == 0 else 15
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(star, fill=GOLD, outline=(120, 90, 20))
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=NAVY)
    draw.text((cx - 4, cy - 8), "$", font=SANS_B(15), fill=CREAM)


def sport_panel(draw, box):
    """Tennis court from above: the ATP Finals title decider."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(34, 110, 68))
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=CREAM, width=3)
    draw.line([(x0 + 16, (y0 + y1) // 2), (x1 - 16, (y0 + y1) // 2)],
              fill=CREAM, width=3)
    draw.line([((x0 + x1) // 2, y0 + 16), ((x0 + x1) // 2, y1 - 16)],
              fill=CREAM, width=2)
    arc_trail(draw, curve_points(x0 + 60, y1 - 60, x0 + 300, y0 + 70, 90),
              (255, 235, 90), width=3)
    bx, by = x0 + 300, y0 + 70
    draw.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(235, 250, 90),
                 outline=(180, 190, 40), width=2)
    draw.arc([bx - 16, by - 16, bx + 16, by + 16], 200, 340, fill=(180, 190, 40),
             width=2)
    draw.text((x0 + 18, y1 - 42), "TURIN — THE FINAL", font=SANS_B(13),
              fill=CREAM)


def story_box(draw, box, kicker_text, head, body, head_size=30, body_size=16):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=(200, 192, 172), width=2, fill=CREAM)
    return x0 + 16, y0 + 14, x1 - 16


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)

    # ---- lead story: Poland / NATO (left, tall) ----
    lx0, ly0, lx1, ly1 = 24, 130, 640, 596
    d.rectangle([lx0, ly0, lx1, ly1], outline=(200, 192, 172), width=2,
                fill=CREAM)
    lead_scene(d, (lx0 + 2, ly0 + 2, lx1 - 2, ly0 + 230))
    ty = ly0 + 246
    ty = kicker(d, lx0 + 16, ty, "LEAD  •  WAR IN EUROPE")
    ty = headline(d, lx0 + 16, ty, "RUSSIAN MISSILES LAND IN POLAND",
                  SERIF_B(34), lx1 - lx0 - 32)
    ty += 6
    ty = para(d, lx0 + 16, ty,
              "Russia fired 400+ drones and 110 missiles at Ukraine — its "
              "biggest attack of the year, killing 8. Two missiles and a "
              "drone then fell inside Poland. Tusk calls it deliberate "
              "provocation; NATO vows to defend \"every inch\" of allied "
              "land.", SANS(16), lx1 - lx0 - 32, INK)
    d.text((lx0 + 16, ly1 - 26), "KYIV  •  WARSAW", font=SANS_B(13),
           fill=GREY)

    # ---- right column: COP31, then the Gulf ----
    rx0, rx1 = 656, 1000
    cx0, cy0, cy1 = rx0, 130, 356
    d.rectangle([cx0, cy0, rx1, cy1], outline=(200, 192, 172), width=2,
                fill=CREAM)
    cop_panel(d, (cx0 + 2, cy0 + 2, rx1 - 2, cy0 + 86))
    ty = cy0 + 100
    ty = kicker(d, cx0 + 14, ty, "CLIMATE  •  ANTALYA", color=TEAL)
    ty = headline(d, cx0 + 14, ty, "COP31 DEADLOCK",
                  SERIF_B(26), rx1 - cx0 - 28)
    para(d, cx0 + 14, ty + 4,
         "Fossil-fuel talks run into a second day of overtime as the "
         "draft drops all mention of coal, oil and gas. 130+ nations "
         "demand a phase-out; oil producers refuse.", SANS(14),
         rx1 - cx0 - 28, INK)

    gx0, gy0, gy1 = rx0, 368, 596
    d.rectangle([gx0, gy0, rx1, gy1], outline=(200, 192, 172), width=2,
                fill=CREAM)
    gulf_panel(d, (gx0 + 2, gy0 + 2, rx1 - 2, gy0 + 88))
    ty = gy0 + 102
    ty = kicker(d, gx0 + 14, ty, "MIDDLE EAST  •  GULF")
    ty = headline(d, gx0 + 14, ty, "MISSILES OVER RIYADH",
                  SERIF_B(22), rx1 - gx0 - 28)
    para(d, gx0 + 14, ty + 4,
         "Houthi missiles target the Saudi capital; defences intercept "
         "them. Iran claims strikes on US Patriot radars.", SANS(14),
         rx1 - gx0 - 28, INK)

    # ---- bottom row: Mexico, then sport ----
    bx0, by0, by1 = 24, 612, 884
    mx0, mx1 = bx0, 506
    d.rectangle([mx0, by0, mx1, by1], outline=(200, 192, 172), width=2,
                fill=CREAM)
    mexico_panel(d, (mx0 + 2, by0 + 2, mx1 - 2, by0 + 118))
    ty = by0 + 132
    ty = kicker(d, mx0 + 14, ty, "MEXICO  •  CARTELS")
    ty = headline(d, mx0 + 14, ty, "'EL CHAPO ISIDRO' CAPTURED",
                  SERIF_B(24), mx1 - mx0 - 28)
    para(d, mx0 + 14, ty + 4,
         "Mexico seizes the FBI's most-wanted drug lord in Sinaloa — then "
         "deadly cartel violence erupts across the state.", SANS(14),
         mx1 - mx0 - 28, INK)

    sx0, sx1 = 522, 1000
    d.rectangle([sx0, by0, sx1, by1], outline=(200, 192, 172), width=2,
                fill=CREAM)
    sport_panel(d, (sx0 + 2, by0 + 2, sx1 - 2, by0 + 118))
    ty = by0 + 132
    ty = kicker(d, sx0 + 14, ty, "SPORT  •  TENNIS")
    ty = headline(d, sx0 + 14, ty, "ALCARAZ v ZVEREV FOR THE TITLE",
                  SERIF_B(24), sx1 - sx0 - 28)
    para(d, sx0 + 14, ty + 4,
         "Carlos Alcaraz fights back past Ben Shelton to set up an ATP "
         "Finals decider against world No. 1 Alexander Zverev in Turin.",
         SANS(14), sx1 - sx0 - 28, INK)

    # ---- ticker ----
    d.rectangle([0, 900, W, 968], fill=RED_DK)
    d.text((24, 916),
           "ALSO TODAY:  Norway court voids disputed oil licences  ◆  Kenya "
           "clears its last Ebola patient  ◆  DRC toll passes 5,300",
           font=SANS_B(15), fill=(255, 240, 230))
    d.text((24, 940),
           "EU hunts new ECB chief as Lagarde resigns  ◆  M4.1 quake "
           "shakes Myanmar  ◆  Smith out for Australia v South Africa",
           font=SANS_B(15), fill=(255, 210, 190))
    d.text((W // 2, 982),
           "Drawn for this page — no photographs  •  Sunday 22 November 2026",
           font=SANS(13), fill=GREY, anchor="ma")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
