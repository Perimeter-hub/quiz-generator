#!/usr/bin/env python3
"""
Quiz 5: Guess the Country by its Shape
Generates country silhouette images using real geographic GeoJSON data.
No geopandas required — uses only json, PIL, numpy.
Run from the quiz5/ folder.
Usage: python3 generate_shapes.py
"""

import os, json, ssl, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = "images_and_videos"
W, H = 1280, 720
GEOJSON_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
GEOJSON_PATH = "/tmp/world-countries.json"

ROUND_COLORS = {
    1: (10, 20, 60),   # deep blue
    2: (40, 10, 60),   # deep purple
    3: (10, 40, 30),   # deep teal
    4: (60, 20, 10),   # deep red
    5: (10, 40, 10),   # deep green
}

# 50 countries in 5 rounds of 10, easy to hard
COUNTRIES = [
    # Round 1: Very recognizable shapes
    ("Italy",          1), ("Australia",      1), ("Japan",          1),
    ("United States of America", 1), ("Brazil", 1), ("India",         1),
    ("Chile",          1), ("Norway",          1), ("New Zealand",    1),
    ("Madagascar",     1),
    # Round 2: Medium
    ("France",         2), ("Germany",         2), ("Spain",          2),
    ("Mexico",         2), ("Argentina",       2), ("Sweden",         2),
    ("Thailand",       2), ("Vietnam",         2), ("Philippines",    2),
    ("Indonesia",      2),
    # Round 3: Tricky
    ("Canada",         3), ("Russia",          3), ("China",          3),
    ("Turkey",         3), ("Iran",            3), ("Saudi Arabia",   3),
    ("South Africa",   3), ("Kenya",           3), ("Colombia",       3),
    ("Peru",           3),
    # Round 4: Harder
    ("Poland",         4), ("Ukraine",         4), ("Morocco",        4),
    ("Iraq",           4), ("Pakistan",        4), ("Myanmar",        4),
    ("Venezuela",      4), ("Bolivia",         4), ("Paraguay",       4),
    ("Ecuador",        4),
    # Round 5: Expert
    ("Belgium",        5), ("Portugal",        5), ("Switzerland",    5),
    ("Croatia",        5), ("Nepal",           5), ("Sri Lanka",      5),
    ("Tunisia",        5), ("Panama",          5), ("Estonia",        5),
    ("Laos",           5),
]

# Map country names to GeoJSON ADMIN field names
NAME_MAP = {
    "United States of America": "United States of America",
    "South Africa": "South Africa",
    "Saudi Arabia": "Saudi Arabia",
    "New Zealand": "New Zealand",
    "Sri Lanka": "Sri Lanka",
}

def load_font(size, bold=False):
    candidates = [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def download_geojson():
    if os.path.exists(GEOJSON_PATH):
        print("  ✓ GeoJSON already cached")
    else:
        print("  Downloading world countries GeoJSON...")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(GEOJSON_URL, context=ctx) as r:
            data = r.read()
        with open(GEOJSON_PATH, 'wb') as f:
            f.write(data)
        print("  ✓ Downloaded")
    with open(GEOJSON_PATH) as f:
        return json.load(f)

def get_coords(geometry):
    rings = []
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            rings.append([(c[0], c[1]) for c in ring])
    elif geometry["type"] == "MultiPolygon":
        # Find the largest polygon by point count
        best = None
        best_len = 0
        for polygon in geometry["coordinates"]:
            for ring in polygon:
                if len(ring) > best_len:
                    best_len = len(ring)
                    best = ring
        if best:
            rings.append([(c[0], c[1]) for c in best])
    return rings

def normalize(rings, pad=80):
    all_pts = [pt for ring in rings for pt in ring]
    if not all_pts: return rings
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    scale = min((W - pad*2) / (max_x - min_x or 1),
                (H - pad*2) / (max_y - min_y or 1))
    cx = (W - scale * (max_x - min_x)) / 2
    cy = (H - scale * (max_y - min_y)) / 2
    return [[(cx + (x - min_x) * scale, cy + (max_y - y) * scale)
             for x, y in ring] for ring in rings]

def make_country_image(country, rings, round_num, q_num, out_path):
    bg = ROUND_COLORS.get(round_num, (15, 20, 50))
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    gc = tuple(min(255, c + 15) for c in bg)
    for x in range(0, W, 80): draw.line([(x,0),(x,H)], fill=gc, width=1)
    for y in range(0, H, 80): draw.line([(0,y),(W,y)], fill=gc, width=1)

    norm = normalize(rings)

    # Glow layer
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for ring in norm:
        if len(ring) > 2:
            gd.polygon(ring, fill=(100, 180, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Main white shape
    for ring in norm:
        if len(ring) > 2:
            draw.polygon(ring, fill=(240, 245, 255))
            draw.polygon(ring, outline=(150, 180, 255), width=2)

    # Question number badge
    font_num = load_font(40, bold=True)
    draw.rounded_rectangle([25,20,110,72], radius=20, fill=(0,0,0,160))
    qtext = f"#{q_num}"
    bbox = draw.textbbox((0,0), qtext, font=font_num)
    tw = bbox[2]-bbox[0]
    draw.text((67-tw//2, 28), qtext, font=font_num, fill="#FFFFFF")

    # Question text top center
    font_q = load_font(52, bold=True)
    question = "Which country is this?"
    bbox = draw.textbbox((0,0), question, font=font_q)
    tw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-tw//2-30,18,W//2+tw//2+30,82], radius=32, fill=(0,0,0,170))
    draw.text((W//2-tw//2, 26), question, font=font_q, fill="#FFFFFF")


    # QUIZ GO badge
    font_b = load_font(28, bold=True)
    badge = "QUIZ GO!"
    bbox = draw.textbbox((0,0), badge, font=font_b)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-55, H-55, W-10, H-10], radius=22, fill=(255,215,0,200))
    draw.text((W-bw-30, H-50), badge, font=font_b, fill="#1a0a3d")

    img.save(out_path)

def make_title_card(text, bg_color, out_path, accent="#FFD700"):
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # Grid
    gc = tuple(min(255, c+15) for c in bg_color)
    for x in range(0, W, 80): draw.line([(x,0),(x,H)], fill=gc, width=1)
    for y in range(0, H, 80): draw.line([(0,y),(W,y)], fill=gc, width=1)

    # World map dots decoration
    for i in range(0, W, 40):
        for j in range(0, H, 40):
            if (i+j) % 80 == 0:
                draw.ellipse([i-2,j-2,i+2,j+2], fill=tuple(min(255,c+25) for c in bg_color))

    # Main text
    font = load_font(88, bold=True)
    lines = text.split("\n") if "\n" in text else [text]
    if len(lines) == 1 and len(text) > 20:
        words = text.split()
        mid = len(words)//2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font)
        tw = bbox[2]-bbox[0]
        y = H//2 - len(lines)*55 + i*110
        draw.rounded_rectangle([W//2-tw//2-35,y-12,W//2+tw//2+35,y+95], radius=48, fill=accent)
        tcol = "#1a0a3d" if accent=="#FFD700" else "#FFFFFF"
        draw.text((W//2-tw//2, y), line, font=font, fill=tcol)

    # QUIZ GO badge
    font_b = load_font(36, bold=True)
    badge = "QUIZ ⚡ GO!"
    bbox = draw.textbbox((0,0), badge, font=font_b)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-bw//2-30, H-90, W//2+bw//2+30, H-20], radius=35, fill="#FFD700")
    draw.text((W//2-bw//2, H-82), badge, font=font_b, fill="#1a0a3d")

    img.save(out_path)
    print(f"  ✓ {os.path.basename(out_path)}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("🌍 Quiz 5: Guess the Country by Shape\n")

    # Title cards
    cards = [
        ("opening_title_country_shapes.png", "GUESS THE\nCOUNTRY!", (10,20,60), "#FFD700"),
        ("round_01_easy.png",    "ROUND 1\nEASY",    ROUND_COLORS[1], "#4CAF50"),
        ("round_02_medium.png",  "ROUND 2\nMEDIUM",  ROUND_COLORS[2], "#2196F3"),
        ("round_03_tricky.png",  "ROUND 3\nTRICKY",  ROUND_COLORS[3], "#FF9800"),
        ("round_04_harder.png",  "ROUND 4\nHARDER",  ROUND_COLORS[4], "#FF3D3D"),
        ("round_05_expert.png",  "ROUND 5\nEXPERT",  ROUND_COLORS[5], "#9C27B0"),
        ("outro_scoreboard.png", "HOW MANY\nDID YOU GET?", (10,30,20), "#FFD700"),
        ("end_screen.png",       "SUBSCRIBE\nFOR MORE!", (10,10,40), "#FF3D3D"),
    ]
    print("Making title cards...")
    for fname, text, bg, accent in cards:
        out = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(out):
            make_title_card(text, bg, out, accent)
        else:
            print(f"  ⏭  skip: {fname}")

    # Download GeoJSON
    print("\nLoading world GeoJSON...")
    geojson = download_geojson()

    # Build lookup: country name → geometry
    lookup = {}
    for feature in geojson["features"]:
        props = feature.get("properties", {})
        name = props.get("ADMIN") or props.get("NAME") or props.get("name") or ""
        if name:
            lookup[name] = feature["geometry"]

    print(f"  ✓ {len(lookup)} countries loaded\n")
    print("Generating country shapes...")

    q_num = 0
    for country, round_num in COUNTRIES:
        q_num += 1
        safe = country.lower().replace(" ", "_").replace(".", "")
        fname = f"scene_q{q_num:02d}_{safe}.png"
        out = os.path.join(OUTPUT_DIR, fname)

        if os.path.exists(out):
            print(f"  ⏭  skip: {country}"); continue

        # Find in geojson
        geo_name = NAME_MAP.get(country, country)
        geometry = lookup.get(geo_name)

        # Fuzzy match
        if not geometry:
            for k,v in lookup.items():
                if country.lower() in k.lower() or k.lower() in country.lower():
                    geometry = v; break

        if not geometry:
            print(f"  ⚠️  Not found: {country}"); continue

        rings = get_coords(geometry)
        if not rings:
            print(f"  ⚠️  No rings: {country}"); continue

        make_country_image(country, rings, round_num, q_num, out)
        print(f"  ✅ [{q_num:2d}/50] {country}")

    print(f"\n✅ Done! Images in {OUTPUT_DIR}/")
    print("\nNext: python3 ../shared/make_quiz_video.py")

if __name__ == "__main__":
    main()
