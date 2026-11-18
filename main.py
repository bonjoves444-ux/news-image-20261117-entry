"""Tuesday 17 November 2026 — the world's news in one picture.

A deterministic broadsheet drawn with Pillow: three illustrated lead
stories, ten illustrated tiles, a numbered world map and a numbered list
of the rest of the day — 46 stories from six continents, every one of
them from Tuesday 17 November 2026. No network, no clock, no randomness:
two runs write identical bytes.

Writes only to $MAKEFUN_OUTPUT_DIR (default /output) as entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 14

PAPER = (247, 242, 228)
PANEL = (255, 253, 246)
INK = (22, 21, 19)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
GOLD = (146, 104, 12)
GREY = (107, 101, 88)
SKY = (196, 222, 235)
SEA = (178, 210, 224)
LAND = (233, 214, 170)
LAND_EDGE = (190, 168, 128)
RULE = (60, 55, 45)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Split text into lines that fit width, keeping whole words."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; return the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.22)
    lines = wrap(d, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hline(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def flag_us(d, x, y, w, h):
    stripe = max(2, h // 13)
    for i in range(13):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=(255, 255, 255) if i % 2 else (178, 34, 52))
    d.rectangle([x, y, x + int(w * 0.4), y + stripe * 7], fill=(60, 59, 110))


def flag_india(d, x, y, w, h):
    third = h // 3
    d.rectangle([x, y, x + w, y + third], fill=(255, 153, 51))
    d.rectangle([x, y + third, x + w, y + 2 * third], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * third, x + w, y + h], fill=(19, 136, 8))
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(0, 0, 128), width=1)


def flag_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    cx, cy = x + w // 2, y + h // 2
    r = h // 3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))


def flag_aus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 0, 139))
    d.rectangle([x, y, x + w // 2, y + h // 2], fill=(200, 210, 230))
    d.line([(x, y), (x + w // 2, y + h // 2)], fill=(180, 0, 0), width=2)
    d.line([(x + w // 2, y), (x, y + h // 2)], fill=(180, 0, 0), width=2)
    for sx, sy in ((w * 3 // 4, h // 4), (w * 3 // 4, h * 3 // 4),
                   (w * 7 // 8, h // 2)):
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                  fill=(255, 255, 255))


def flag_mexico(d, x, y, w, h):
    third = w // 3
    d.rectangle([x, y, x + third, y + h], fill=(0, 104, 71))
    d.rectangle([x + third, y, x + 2 * third, y + h], fill=(255, 255, 255))
    d.rectangle([x + 2 * third, y, x + w, y + h], fill=(206, 17, 38))


def flag_bolivia(d, x, y, w, h):
    third = h // 3
    d.rectangle([x, y, x + w, y + third], fill=(215, 0, 51))
    d.rectangle([x, y + third, x + w, y + 2 * third], fill=(247, 224, 0))
    d.rectangle([x, y + 2 * third, x + w, y + h], fill=(0, 122, 61))


def burst(d, cx, cy, r, fill):
    """A jagged starburst, for explosions and impacts."""
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)

# ---------------------------------------------------------------- stories
# Every story below happened, or was first reported, on Tuesday
# 17 November 2026. Contested claims name their source. Two stories
# from neighbouring days were deliberately left out: the US bank glitch
# (Monday 16 November) and the FAA ground stop (Friday 13 November).

LEADS = [
    {
        "num": 1, "kicker": "EUROPE · UKRAINE WAR", "art": "bridge",
        "head": "Ukraine says a Crimean Bridge road span fell into the sea",
        "deck": "Second strike in two days; Zelensky hails an "
                "\u201cunprecedented operation\u201d. Two killed; "
                "traffic halted.",
    },
    {
        "num": 2, "kicker": "MIDDLE EAST · IRAN WAR", "art": "gulf",
        "head": "Iran fires drones at a US radar in Bahrain; US jets hit Qeshm",
        "deck": "Bahrain and CENTCOM say all drones were intercepted. "
                "US jets strike an IRGC missile site on Qeshm Island; "
                "Iran says it shot down a US drone.",
    },
    {
        "num": 3, "kicker": "ASIA · DIPLOMACY", "art": "quad",
        "head": "Trump holds his first Quad summit, in Manila",
        "deck": "US, India, Japan and Australia agree minerals deals; "
                "first meeting since 2024. Trump meets Xi and Putin "
                "Thursday.",
    },
]

TILES = [
    {
        "num": 4, "kicker": "US · BUSINESS", "art": "chip",
        "head": "Nvidia\u2019s quarterly sales double to $115.8bn",
        "deck": "Reported after the close, up 103% on a year ago.",
    },
    {
        "num": 5, "kicker": "AFRICA · HEALTH", "art": "ebola",
        "head": "Ebola cases in DR Congo top 11,000, WHO says",
        "deck": "Cases more than doubled in three months; about "
                "5,400 have died.",
    },
    {
        "num": 6, "kicker": "AMERICAS · HEALTH", "art": "measles",
        "head": "US, Mexico and Bolivia lose measles-free status",
        "deck": "PAHO cites a year of spread; the US has 5,700+ "
                "cases in 2026.",
    },
    {
        "num": 7, "kicker": "GLOBAL · CLIMATE", "art": "cop",
        "head": "COP31 divided over a fossil-fuel phase-out",
        "deck": "Nations weigh the first draft; the Antalya talks "
                "end Friday.",
    },
    {
        "num": 8, "kicker": "MIDDLE EAST · POLITICS", "art": "knesset",
        "head": "Netanyahu rival wins Knesset speaker vote",
        "deck": "Matan Kahana elected speaker, 66\u201352, after a "
                "six-hour filibuster.",
    },
    {
        "num": 9, "kicker": "EUROPE · POLITICS", "art": "serbia",
        "head": "Serbia\u2019s student-led majority takes its seats",
        "deck": "Student List holds 140 of 250 seats; Vu\u010di\u0107\u2019s "
                "bloc is out.",
    },
    {
        "num": 10, "kicker": "ASIA · LABOUR", "art": "factory",
        "head": "Bangladesh police tear-gas garment workers",
        "deck": "They want Tk 30,000 a month, up from 12,500; "
                "37 factories shut.",
    },
    {
        "num": 11, "kicker": "RUSSIA · AIR CRASH", "art": "plane",
        "head": "Russian An-12 crash in Siberia kills all 19",
        "deck": "The air force plane came down near Kemerovo.",
    },
    {
        "num": 12, "kicker": "AFRICA · JUSTICE", "art": "court",
        "head": "Mozambique puts opposition leader on trial",
        "deck": "Ven\u00e2ncio Mondlane faces 5 charges over deadly "
                "2024 protests.",
    },
    {
        "num": 13, "kicker": "ASIA · WEATHER", "art": "cyclone",
        "head": "Cyclone Akvan bears down on India\u2019s east coast",
        "deck": "Odisha evacuates; landfall expected around "
                "20 November.",
    },
]

BRIEFS = [
    (14, "Kyiv: Russia hits two Dnipro bridges; power cut"),
    (15, "UN: Ukraine civilian deaths top all of 2025"),
    (16, "Kuwait: air defences repel drones"),
    (17, "Hormuz: Iran says mines hit two ships; unverified"),
    (18, "Gaza: truce at risk of collapse, UN is told"),
    (19, "West Bank: settlers kill a woman, 72, near Jericho"),
    (20, "Oman: Iran\u2019s Araghchi holds shipping-safety talks"),
    (21, "France: strike; 146,000 march, CGT says 500,000"),
    (22, "Poland: Tusk survives a no-confidence vote"),
    (23, "Moldova: shuts its airspace over a Russian drone"),
    (24, "Prague: two trains collide; 46 injured"),
    (25, "Turkey: police seize S\u00f6zc\u00fc TV, opposition channel"),
    (26, "UK: sanctions 8 settlement firms and Tzav 9"),
    (27, "EU: five states plan a Rwanda migrant hub"),
    (28, "Germany: Deutsche Bank shares fall on data leak"),
    (29, "Japan: scrambles jets over Russian airspace breach"),
    (30, "China\u2013Canada: Xi and Carney agree tariff cuts"),
    (31, "Malaysia: Macron visit seals strategic partnership"),
    (32, "Thailand: pledges to scrap tariffs on US goods"),
    (33, "South Korea: IMF lifts 2026 growth forecast to 3.9%"),
    (34, "India: bus falls into an Uttarakhand gorge, 8 dead"),
    (35, "Sudan: UN verifies 2,230 civilian deaths, Jan\u2013Oct"),
    (36, "Kenya: WFP aids 30,000 who fled Ethiopia clashes"),
    (37, "Guinea: 224 jailed in a gold-mining crackdown"),
    (38, "Haiti: Aristide\u2019s party will field no candidates"),
    (39, "Australia: eases planned backpacker visa curbs"),
    (40, "Indonesia: M6.6 quake felt in Darwin; no tsunami"),
    (41, "Pacific: Cyclone Xavier nears Cook Islands, Cat 3"),
    (42, "PNG: Auckland flights resume after 26 years"),
    (43, "US: NSA network degraded; \u201cnot a cyberattack\u201d"),
    (44, "US: California sues OpenAI"),
    (45, "Football: India beat Pakistan 2\u20131 in SAFF final"),
    (46, "Football: Brazil 7\u20130 Singapore; Vin\u00edcius hat-trick"),
]

STATS = [
    ("11,000+", "Ebola cases, DR Congo"),
    ("$115.8bn", "Nvidia quarter"),
    ("\u2212849", "Dow points"),
    ("1,441", "drones Russia says it downed"),
    ("2m+ barrels", "tanker Iran says hit"),
    ("1 light-day", "Voyager 1 nears"),
]

# ------------------------------------------------------------- illustrations

def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA)
    for i in range(5):
        yy = y + h * 0.66 + i * 5
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(140, 185, 205), width=2)
    d.rectangle([x + 14, y + h * 0.42, x + w - 14, y + h * 0.50],
                fill=(70, 70, 78))
    d.rectangle([x + 30, y + h * 0.18, x + 38, y + h * 0.50],
                fill=(70, 70, 78))
    d.rectangle([x + w - 40, y + h * 0.18, x + w - 32, y + h * 0.50],
                 fill=(70, 70, 78))
    # the fallen span, tilted down into the strait
    d.polygon([(x + w * 0.52, y + h * 0.46), (x + w * 0.72, y + h * 0.50),
               (x + w * 0.66, y + h * 0.72), (x + w * 0.50, y + h * 0.66)],
              fill=(90, 90, 98))
    burst(d, x + w * 0.55, y + h * 0.40, 13, (255, 170, 0))
    burst(d, x + w * 0.55, y + h * 0.40, 6, (255, 90, 0))
    d.ellipse([x + w * 0.60, y + h * 0.12, x + w * 0.66, y + h * 0.26],
              fill=(120, 120, 120))
    d.ellipse([x + w * 0.66, y + h * 0.18, x + w * 0.74, y + h * 0.36],
              fill=(100, 100, 100))
    d.text((x + 8, y + 6), "CRIMEA", font=font(SANS_B, 11), fill=INK)
    d.text((x + w - 62, y + 6), "RUSSIA", font=font(SANS_B, 11), fill=INK)
    d.polygon([(x + w * 0.50, y + h * 0.52), (x + w * 0.88, y + h * 0.52),
               (x + w * 0.88, y + h * 0.68), (x + w * 0.50, y + h * 0.68)],
              fill=(255, 255, 255))
    d.text((x + w * 0.52, y + h * 0.55), "ROAD SPAN DOWN",
           font=font(SANS_B, 10), fill=RED)


def art_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 190))
    d.rectangle([x, y + h * 0.30, x + w, y + h], fill=SEA)
    d.polygon([(x + w * 0.55, y + h * 0.30), (x + w, y + h * 0.30),
               (x + w, y + h * 0.62), (x + w * 0.72, y + h * 0.78),
               (x + w * 0.60, y + h * 0.55)], fill=(222, 205, 165))
    d.text((x + 8, y + 6), "IRAN", font=font(SANS_B, 11), fill=INK)
    d.text((x + 10, y + h * 0.52), "BAHRAIN", font=font(SANS_B, 11), fill=INK)
    d.text((x + w - 58, y + h - 22), "QESHM", font=font(SANS_B, 11), fill=INK)
    d.text((x + w - 68, y + h * 0.52), "HORMUZ",
           font=font(SANS_B, 10), fill=INK)
    # dashed drone path Bahrain -> Qeshm
    for i in range(9):
        t = i / 8
        px = x + w * (0.22 + 0.55 * t)
        py = y + h * (0.78 - 0.28 * t) - 8 * t * (1 - t) * 4
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    burst(d, x + w * 0.78, y + h * 0.52, 11, (255, 170, 0))
    d.ellipse([x + w * 0.18, y + h * 0.70, x + w * 0.26, y + h * 0.80],
              outline=RED, width=3)
    d.line([(x + w * 0.18, y + h * 0.70), (x + w * 0.26, y + h * 0.80)],
           fill=RED, width=3)
    d.line([(x + w * 0.26, y + h * 0.70), (x + w * 0.18, y + h * 0.80)],
           fill=RED, width=3)
    d.rectangle([x + w * 0.30, y + h * 0.06, x + w * 0.70, y + h * 0.24],
                fill=RED)
    d.text((x + w * 0.32, y + h * 0.09), "DRONES DOWNED",
           font=font(SANS_B, 11), fill=(255, 255, 255))


def art_quad(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 250))
    d.rectangle([x, y, x + w, y + h * 0.30], fill=(88, 40, 140))
    d.text((x + w // 2 - 78, y + 8), "QUAD LEADERS\u2019 SUMMIT \u00b7 MANILA",
           font=font(SANS_B, 12), fill=(255, 255, 255))
    fw, fh = 58, 34
    gap = (w - 4 * fw) // 5
    for i, fn in enumerate((flag_us, flag_india, flag_japan, flag_aus)):
        fx = x + gap + i * (fw + gap)
        fn(d, fx, y + h * 0.38, fw, fh)
    labels = ["US", "INDIA", "JAPAN", "AUSTRALIA"]
    for i, lab in enumerate(labels):
        fx = x + gap + i * (fw + gap)
        d.text((fx + fw // 2 - 14, y + h * 0.38 + fh + 4), lab,
               font=font(SANS_B, 10), fill=INK)
    # table line below the flags


def art_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 40, 24))
    d.rectangle([x + 8, y + 8, x + 40, y + 40], fill=(30, 90, 50),
                outline=(80, 200, 120), width=2)
    d.rectangle([x + 17, y + 17, x + 31, y + 31], fill=(140, 230, 160))
    bars = [8, 13, 18, 24, 30]
    for i, bh in enumerate(bars):
        bx = x + 52 + i * 20
        d.rectangle([bx, y + h - 8 - bh, bx + 13, y + h - 8],
                    fill=(60, 200, 110))
    d.text((x + 52, y + 4), "$115.8bn", font=font(SANS_B, 15),
           fill=(120, 255, 150))


def art_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
    d.polygon([(x + 20, y + h - 14), (x + 70, y + 16), (x + 120, y + h - 14)],
              fill=(255, 255, 255), outline=(150, 140, 120))
    d.rectangle([x + 60, y + 34, x + 80, y + 46], fill=RED)
    d.rectangle([x + 66, y + 28, x + 74, y + 52], fill=RED)
    bars = [8, 16, 26]
    for i, bh in enumerate(bars):
        bx = x + 128 + i * 18
        d.rectangle([bx, y + h - 8 - bh, bx + 13, y + h - 8],
                    fill=(179, 38, 30) if i == 2 else (200, 120, 110))
    d.text((x + 118, y + 4), "11,000+", font=font(SANS_B, 13), fill=RED)


def art_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 230))
    flag_us(d, x + 10, y + 10, 46, 26)
    flag_mexico(d, x + 66, y + 10, 46, 26)
    flag_bolivia(d, x + 122, y + 10, 46, 26)
    for cx, cy, r in ((30, 46, 7), (95, 48, 8), (155, 46, 6)):
        burst(d, x + cx, y + cy, r, (200, 40, 40))


def art_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 238, 245))
    d.ellipse([x + 12, y + 12, x + 62, y + 62], fill=(90, 160, 200))
    d.ellipse([x + 22, y + 22, x + 52, y + 52], fill=(140, 200, 120))
    d.rectangle([x + 78, y + 14, x + 168, y + 58], fill=(255, 255, 255),
                outline=(120, 120, 120))
    d.text((x + 84, y + 18), "DRAFT", font=font(SANS_B, 12), fill=INK)
    d.text((x + 84, y + 36), "FOSSIL FUELS?", font=font(SANS_B, 11),
           fill=RED)


def art_knesset(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 240, 248))
    import math
    for i in range(11):
        ang = math.pi * (0.12 + 0.76 * i / 10)
        cx = x + w // 2 + int(46 * math.cos(ang))
        cy = y + 50 - int(24 * math.sin(ang))
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5],
                  fill=BLUE if i < 7 else (180, 60, 60))
    d.rectangle([x + 20, y + h - 8, x + w - 20, y + h - 4],
                fill=(120, 100, 60))
    d.text((x + 10, y + 6), "66\u201352", font=font(SANS_B, 14), fill=INK)


def art_serbia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 250))
    d.polygon([(x + 40, y + 18), (x + 96, y + 18), (x + 110, y + 34),
               (x + 26, y + 34)], fill=(90, 90, 100))
    d.rectangle([x + 34, y + 34, x + 102, y + 62], fill=(200, 200, 210))
    for cx in (44, 60, 76, 92):
        d.rectangle([cx, y + 40, cx + 8, y + 62], fill=(120, 120, 135))
    d.rectangle([x + 122, y + 30, x + 172, y + 62], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.text((x + 128, y + 34), "140 / 250", font=font(SANS_B, 13), fill=BLUE)
    d.text((x + 128, y + 50), "STUDENTS", font=font(SANS_B, 10), fill=INK)


def art_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    d.rectangle([x + 12, y + 30, x + 90, y + 64], fill=(150, 150, 160))
    d.polygon([(x + 12, y + 30), (x + 30, y + 12), (x + 48, y + 30)],
              fill=(120, 120, 130))
    d.rectangle([x + 96, y + 18, x + 104, y + 64], fill=(120, 120, 130))
    for cx in (30, 55, 80):
        d.ellipse([x + cx - 5, y + 52, x + cx + 5, y + 62], fill=(60, 60, 70))
    d.rectangle([x + 116, y + 16, x + 178, y + 44], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.text((x + 120, y + 20), "TK 30,000", font=font(SANS_B, 12), fill=INK)
    d.text((x + 120, y + 34), "A MONTH", font=font(SANS_B, 9), fill=GREY)


def art_plane(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 232, 240))
    d.polygon([(x + 96, y + 52), (x + 116, y + 52), (x + 126, y + 40),
               (x + 136, y + 30), (x + 148, y + 32), (x + 138, y + 44),
               (x + 126, y + 58), (x + 106, y + 60)], fill=(150, 150, 160))
    d.polygon([(x + 20, y + h - 14), (x + 60, y + h - 40),
               (x + 100, y + h - 14)], fill=(170, 180, 190))
    d.polygon([(x + 90, y + h - 14), (x + 130, y + h - 46),
               (x + 175, y + h - 14)], fill=(150, 160, 170))
    d.ellipse([x + 152, y + 6, x + 178, y + 30], fill=(200, 200, 205))
    d.ellipse([x + 162, y + 16, x + 186, y + 40], fill=(185, 185, 190))
    d.text((x + 8, y + 6), "ALL 19 ABOARD",
           font=font(SANS_B, 11), fill=RED)


def art_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(242, 240, 232))
    d.polygon([(x + 40, y + 16), (x + 96, y + 16), (x + 110, y + 30),
               (x + 26, y + 30)], fill=(100, 90, 70))
    for cx in (42, 62, 82):
        d.rectangle([cx, y + 30, cx + 8, y + 58], fill=(140, 130, 110))
    d.rectangle([x + 26, y + 58, x + 110, y + 64], fill=(100, 90, 70))
    d.rectangle([x + 120, y + 22, x + 190, y + 50], fill=RED)
    d.text((x + 125, y + 28), "5 CHARGES", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 228, 240))
    import math
    cx, cy = x + w // 2 + 20, y + h // 2 + 2
    for k in range(3):
        pts = []
        for i in range(40):
            t = i / 39
            ang = t * math.pi * 3.2 + k * 0.7
            rr = 6 + t * (20 - k * 4)
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.line(pts, fill=(255, 255, 255), width=5 - k)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(240, 240, 240))
    d.text((x + 8, y + 6), "BAY OF", font=font(SANS_B, 10), fill=BLUE)
    d.text((x + 8, y + 20), "BENGAL", font=font(SANS_B, 10), fill=BLUE)


ART = {
    "bridge": art_bridge, "gulf": art_gulf, "quad": art_quad,
    "chip": art_chip, "ebola": art_ebola, "measles": art_measles,
    "cop": art_cop, "knesset": art_knesset, "serbia": art_serbia,
    "factory": art_factory, "plane": art_plane, "court": art_court,
    "cyclone": art_cyclone,
}

# ------------------------------------------------------------------- map

LAND_POLYS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 72), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-85, 29), (-90, 21), (-95, 19), (-97, 16), (-92, 15),
     (-86, 13), (-83, 9), (-79, 9), (-85, 11), (-90, 14), (-97, 16),
     (-105, 20), (-110, 23), (-114, 28), (-120, 34), (-125, 40),
     (-124, 48), (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-25, 76),
     (-40, 80), (-55, 76), (-60, 70)],
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-65, -45), (-68, -52), (-70, -55), (-73, -50),
     (-73, -40), (-72, -30), (-70, -20), (-75, -15), (-80, -6),
     (-81, 0), (-80, 5)],
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (38, 22), (43, 12), (48, 11), (51, 10), (44, 0),
     (40, -10), (35, -20), (32, -29), (28, -33), (20, -35), (15, -27),
     (12, -18), (9, -2), (9, 4), (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (40, 68), (55, 68), (68, 72), (80, 73), (100, 76), (110, 74),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 52), (150, 59), (142, 55), (140, 50), (135, 43), (130, 42),
     (127, 40), (122, 38), (120, 32), (115, 23), (108, 18), (105, 10),
     (100, 8), (98, 12), (95, 16), (92, 21), (89, 22), (86, 20),
     (80, 15), (77, 8), (74, 20), (70, 25), (66, 25), (62, 25),
     (58, 26), (55, 26), (52, 28), (50, 29), (48, 30), (44, 29),
     (40, 31), (36, 36), (30, 36), (26, 38), (23, 36), (19, 40),
     (15, 44), (12, 44), (8, 44), (3, 42), (0, 40), (-2, 37),
     (-6, 36), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (132, -32), (136, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -9), (130, -3), (135, -4), (140, -8), (138, -2), (132, 0),
     (128, 2), (125, 5), (120, 0), (115, 2), (110, 1), (105, 0),
     (100, 5)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (141, 40),
     (142, 43), (144, 44), (141, 42), (139, 38), (136, 36), (133, 34)],
    [(167, -45), (170, -42), (174, -40), (177, -38), (175, -37),
     (172, -41), (168, -44)],
]

# (number, lat, lon, colour, nudge dx, dy)
PINS = [
    (1, 45.3, 36.4, BLUE, 0, 0),
    (2, 26.2, 50.6, (200, 120, 20), 16, 6),
    (3, 14.6, 121.0, (120, 60, 160), 0, 0),
    (4, 40.7, -74.0, RED, 0, 0),
    (5, -2.9, 23.7, (30, 140, 70), 0, 0),
    (6, 19.4, -99.1, RED, 0, 0),
    (7, 36.9, 30.7, GREY, -9, 9),
    (8, 31.8, 35.2, (200, 120, 20), 9, 11),
    (9, 44.8, 20.5, BLUE, -11, -7),
    (10, 23.8, 90.4, (120, 60, 160), 0, 0),
    (11, 55.4, 86.1, BLUE, 0, 0),
    (12, -26.0, 32.6, (30, 140, 70), 0, 0),
    (13, 20.0, 86.4, (120, 60, 160), 11, 5),
]


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(205, 225, 235))
    def mx(lon):
        return x0 + (lon + 168) / 360.0 * (x1 - x0)
    def my(lat):
        return y0 + (78 - lat) / 136.0 * (y1 - y0)
    for poly in LAND_POLYS:
        pts = [(mx(lon), my(lat)) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for num, lat, lon, col, dx, dy in PINS:
        cx, cy = mx(lon) + dx, my(lat) + dy
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=col,
                  outline=(255, 255, 255), width=2)
        label = str(num)
        tw = d.textlength(label, font=font(SANS_B, 10))
        d.text((cx - tw / 2, cy - 7), label, font=font(SANS_B, 10),
               fill=(255, 255, 255))


def num_badge(d, x, y, num, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
    label = str(num)
    fnt = font(SANS_B, 11 if num < 10 else 10)
    tw = d.textlength(label, font=fnt)
    ty = y - 7 if num < 10 else y - 6
    d.text((x - tw / 2, ty), label, font=fnt, fill=(255, 255, 255))


def draw_lead(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    ART[story["art"]](d, x + 1, y + 1, w - 2, 80)
    num_badge(d, x + 14, y + 98, story["num"])
    d.text((x + 28, y + 90), story["kicker"], font=font(SANS_B, 11),
           fill=RED)
    after_head = para(d, x + 8, y + 108, story["head"], font(SERIF, 18),
                      w - 16, leading=21, max_lines=2)
    para(d, x + 8, after_head + 3, story["deck"], font(SANS, 12), w - 16,
         leading=15, max_lines=3)


def draw_tile(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    ART[story["art"]](d, x + 1, y + 1, w - 2, 58)
    num_badge(d, x + 12, y + 72, story["num"], r=9)
    d.text((x + 25, y + 65), story["kicker"], font=font(SANS_B, 9),
           fill=RED)
    after_head = para(d, x + 7, y + 82, story["head"], font(SERIF, 14),
                      w - 14, leading=17, max_lines=2)
    para(d, x + 7, after_head + 2, story["deck"], font(SANS, 11), w - 14,
         leading=14, max_lines=2)


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    d.text((MARGIN, 8), "THE WORLD\u2019S NEWS IN ONE PICTURE",
           font=font(SANS_B, 12), fill=RED)
    right = "46 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY"
    tw = d.textlength(right, font=font(SANS_B, 12))
    d.text((W - MARGIN - tw, 8), right, font=font(SANS_B, 12), fill=INK)
    d.text((MARGIN, 26), "Tuesday 17 November 2026",
           font=font(SERIF, 60), fill=INK)
    hline(d, MARGIN, W - MARGIN, 96, fill=INK, width=3)
    hline(d, MARGIN, W - MARGIN, 101, fill=INK, width=1)

    # by-the-numbers strip
    sx = MARGIN
    sw = (W - 2 * MARGIN - 5 * 6) / 6
    for i, (big, small) in enumerate(STATS):
        bx = sx + i * (sw + 6)
        d.text((bx, 108), big, font=font(SANS_B, 16), fill=RED)
        d.text((bx, 128), small, font=font(SANS, 10), fill=GREY)

    # leads
    lw = (W - 2 * MARGIN - 2 * 10) / 3
    for i, story in enumerate(LEADS):
        draw_lead(d, MARGIN + i * (lw + 10), 148, lw, 200, story)

    # tiles, two rows of five
    twd = (W - 2 * MARGIN - 4 * 8) / 5
    for i, story in enumerate(TILES):
        row, col = divmod(i, 5)
        draw_tile(d, MARGIN + col * (twd + 8), 356 + row * 164, twd, 156,
                  story)

    # bottom band: map + the rest of the day
    d.text((MARGIN, 686), "WHERE IT HAPPENED",
           font=font(SANS_B, 13), fill=RED)
    d.text((MARGIN, 686 + 16), "Pins: stories 1\u201313",
           font=font(SANS, 10), fill=GREY)
    draw_map(d, MARGIN, 712, 352, 936)
    legend = [("Europe", BLUE), ("Middle East", (200, 120, 20)),
              ("Asia", (120, 60, 160)), ("Africa", (30, 140, 70)),
              ("Americas", RED), ("Global", GREY)]
    lx = MARGIN
    for name, col in legend:
        d.ellipse([lx, 946, lx + 9, 955], fill=col)
        d.text((lx + 12, 944), name, font=font(SANS, 10), fill=INK)
        lx += 12 + d.textlength(name, font=font(SANS, 10)) + 12

    bx = 366
    d.text((bx, 686), "ALSO ON TUESDAY 17 NOVEMBER",
           font=font(SANS_B, 13), fill=RED)
    d.text((bx, 686 + 16), "Stories 14\u201346, in brief",
           font=font(SANS, 10), fill=GREY)
    col_w = (W - MARGIN - bx - 16) / 2
    for i, (num, text) in enumerate(BRIEFS):
        col, row = divmod(i, 17)
        x = bx + col * (col_w + 16)
        yy = 712 + row * 15
        d.text((x, yy), str(num), font=font(SANS_B, 11), fill=RED)
        para(d, x + 24, yy, text, font(SANS, 11), col_w - 24, leading=15,
             max_lines=1)

    # footer
    hline(d, MARGIN, W - MARGIN, 988, fill=RULE, width=1)
    d.text((MARGIN, 994),
           "DATE CHECK \u2014 Left out on purpose: the US bank glitch was "
           "Monday 16 November; the FAA ground stop was Friday 13 November.",
           font=font(SANS_B, 11), fill=INK)
    d.text((MARGIN, 1009),
           "Every story here happened or was first reported on Tuesday "
           "17 November 2026. Contested claims are marked as claims. "
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN News. "
           "Original drawings.",
           font=font(SANS, 10), fill=GREY)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img = draw_page()
    img.save(os.path.join(outdir, "entry.png"), "PNG")


if __name__ == "__main__":
    main()
