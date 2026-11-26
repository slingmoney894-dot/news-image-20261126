#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news front page (1024x1024 JPEG).

Deterministic: no randomness, no network, no clock. Writes entry.png to
MAKEFUN_OUTPUT_DIR (default /output).
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (163, 18, 18)
BLUE = (30, 64, 175)
GREY = (120, 113, 108)
RULE = (90, 84, 78)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PANELS = [
    {
        "kicker": "MIDDLE EAST",
        "color": RED,
        "flag": "yemen",
        "headline": "Houthis claim strikes on Saudi refinery",
        "body": "Yemen's Houthi forces claim attacks on Saudi Arabia's largest "
                "refinery, Ras Tanura, and Riyadh's financial district. Brent "
                "crude tops $94 as Saudi defences intercept three missiles "
                "aimed at Riyadh.",
    },
    {
        "kicker": "TRADE",
        "color": BLUE,
        "flag": "usa",
        "headline": "Trump unveils sweeping new tariffs",
        "body": "Trump announces new tariffs on Japan, China, the EU and others. "
                "The US proposes up to 15% tariffs on Taiwan goods in a "
                "Section 301 probe, with 14 trading partners facing new duties.",
    },
    {
        "kicker": "UKRAINE",
        "color": BLUE,
        "flag": "russia",
        "headline": "Russia's own toll: nearly 500,000 dead",
        "body": "Russia's own figures show it has lost nearly 500,000 people in "
                "the Ukraine war. The UN verified 15 attacks on Black Sea "
                "shipping out of 164 reported on commercial vessels.",
    },
    {
        "kicker": "EGYPT",
        "color": RED,
        "flag": "egypt",
        "headline": "Tanker inferno kills 30 on Cairo ring road",
        "body": "A fuel tanker overturns and bursts into flames on Cairo's ring "
                "road in Giza's Al-Warraq district, killing 30 people and "
                "injuring 21.",
    },
    {
        "kicker": "MARKETS",
        "color": BLUE,
        "flag": "taiwan",
        "headline": "AI bubble fears rattle markets",
        "body": "Economists warn an AI bubble burst could exceed the dot-com "
                "crisis. Taiwan shares fall 1,927 points as the US tariff plan "
                "weighs, and Washington tightens remote AI chip access rules.",
    },
    {
        "kicker": "TECH",
        "color": RED,
        "flag": "usa",
        "headline": "Nvidia turmoil as Huang resigns",
        "body": "Jensen Huang resigns amid espionage probes and the scramble for "
                "Nvidia begins. The US attorney general dodges questions about "
                "the Nvidia investigation.",
    },
]

MORE_NEWS = [
    "US Air Force unveils F-15EX fighters at Kadena, Okinawa",
    "EU seeks new ECB chief as Lagarde resigns",
    "Norway court voids climate-disputed oil licences",
    "Kenya discharges last Ebola patient; DRC toll tops 5,300",
    "Democrats reclaim US Congress in midterm victory",
    "Ghana unveils banknotes honouring Nkrumah, Annan",
    "UN warns of crimes risk for stateless people",
    "UN: Russia may put a nuclear weapon in space soon",
    "China consortium to invest $50bn in Indonesia city",
    "Hera to image asteroid hit to test Earth's defences",
    "Zambia bans protests on presidential term limits",
    "France probes officials over leaks to Le Pen party",
    "Brazil pulls ambassador to Argentina for good",
    "US hacking suspected, initial trace points to China",
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines fitting width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_flag(draw, kind, x, y, w=44, h=30):
    """Simple flat flag sketches, drawn with rectangles only."""
    draw.rectangle([x, y, x + w, y + h], outline=(60, 60, 60), width=1)
    if kind == "yemen":  # red / white / black horizontal tricolour
        draw.rectangle([x + 1, y + 1, x + w - 1, y + h // 3], fill=(206, 17, 38))
        draw.rectangle([x + 1, y + 2 * h // 3, x + w - 1, y + h - 1], fill=(0, 0, 0))
    elif kind == "usa":  # stripes + blue canton with white dots
        for i in range(7):
            if i % 2 == 0:
                draw.rectangle([x + 1, y + 1 + i * h // 7, x + w - 1,
                                y + (i + 1) * h // 7], fill=(178, 34, 52))
        draw.rectangle([x + 1, y + 1, x + w * 2 // 5, y + 4 * h // 7],
                       fill=(60, 59, 110))
        for r in range(3):
            for c in range(4):
                cx = x + 4 + c * 8
                cy = y + 4 + r * 5
                draw.ellipse([cx, cy, cx + 2, cy + 2], fill=(255, 255, 255))
    elif kind == "russia":  # white / blue / red horizontal tricolour
        draw.rectangle([x + 1, y + 1 + h // 3, x + w - 1, y + 2 * h // 3],
                       fill=(0, 57, 166))
        draw.rectangle([x + 1, y + 2 * h // 3, x + w - 1, y + h - 1],
                       fill=(213, 0, 50))
    elif kind == "egypt":  # red / white / black with gold disc
        draw.rectangle([x + 1, y + 1, x + w - 1, y + h // 3], fill=(206, 17, 38))
        draw.rectangle([x + 1, y + 2 * h // 3, x + w - 1, y + h - 1], fill=(0, 0, 0))
        draw.ellipse([x + w // 2 - 4, y + h // 2 - 4, x + w // 2 + 4,
                      y + h // 2 + 4], fill=(200, 160, 30))
    elif kind == "taiwan":  # red field, blue canton, white sun
        draw.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(254, 0, 0))
        draw.rectangle([x + 1, y + 1, x + w // 2, y + h // 2], fill=(0, 0, 149))
        draw.ellipse([x + 5, y + 4, x + 15, y + 14], fill=(255, 255, 255))


def draw_panel(draw, panel, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    kicker_f = font(SANS_B, 14)
    draw.text((x + 12, y + 10), panel["kicker"], font=kicker_f,
              fill=panel["color"])
    draw_flag(draw, panel["flag"], x + w - 12 - 44, y + 8)
    head_f = font(SANS_B, 21)
    head_lines = wrap(draw, panel["headline"], head_f, w - 24)[:2]
    hy = y + 42
    for line in head_lines:
        draw.text((x + 12, hy), line, font=head_f, fill=INK)
        hy += 26
    body_f = font(SANS, 16)
    body_lines = wrap(draw, panel["body"], body_f, w - 24)[:4]
    by = hy + 6
    for line in body_lines:
        draw.text((x + 12, by), line, font=body_f, fill=INK)
        by += 20


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead.
    title_f = font(SERIF_B, 62)
    title = "THE WORLD TODAY"
    tw = draw.textlength(title, font=title_f)
    draw.text(((W - tw) / 2, 14), title, font=title_f, fill=INK)
    date_f = font(SANS_B, 30)
    date = "THURSDAY, 26 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_f)
    draw.text(((W - dw) / 2, 88), date, font=date_f, fill=RED)
    draw.line([(24, 132), (1000, 132)], fill=INK, width=3)
    draw.line([(24, 138), (1000, 138)], fill=INK, width=1)

    # Six panels: 2 columns x 3 rows.
    px, py = 24, 152
    pw, ph, gap = 476, 192, 12
    for i, panel in enumerate(PANELS):
        col, row = i % 2, i // 2
        draw_panel(draw, panel, px + col * (pw + 24), py + row * (ph + gap),
                   pw, ph)

    # MORE NEWS band.
    my = 762
    more_f = font(SANS_B, 20)
    draw.text((24, my), "MORE NEWS", font=more_f, fill=RED)
    draw.line([(170, my + 13), (1000, my + 13)], fill=INK, width=2)
    item_f = font(SANS, 15)
    iy = my + 34
    for col in range(2):
        cy = iy
        for item in MORE_NEWS[col * 7:(col + 1) * 7]:
            lines = wrap(draw, item, item_f, pw - 16)[:2]
            draw.text((24 + col * (pw + 24), cy), "\u2022", font=item_f,
                      fill=RED)
            ly = cy
            for line in lines:
                draw.text((40 + col * (pw + 24), ly), line, font=item_f,
                          fill=INK)
                ly += 19
            cy = ly + 8
        # second column starts at the same top
        cy = iy

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img.save(path, "JPEG", quality=90)
    with open(path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(f"wrote {path} sha256={digest}")


if __name__ == "__main__":
    main()
