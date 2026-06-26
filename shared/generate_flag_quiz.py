#!/usr/bin/env python3
"""
Premium flag quiz generator for quiz6 — HIGH QUALITY flags from flagcdn.com.
Crisp, accurate national flags (correct star counts, fine details).

Run from quiz6/ folder:
  python3 ../shared/generate_flag_quiz.py
"""

import csv, os, re, urllib.request, ssl
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

W, H = 1280, 720
OUTPUT_DIR = "images_and_videos"
CSV_PATH = "batch_generation_queue.csv"
FLAG_CACHE = "/tmp/flagcdn_cache"
os.makedirs(FLAG_CACHE, exist_ok=True)

# flagcdn.com provides crisp PNGs: https://flagcdn.com/w1280/us.png
FLAGCDN = "https://flagcdn.com/w1280/"

# Country name → ISO 3166-1 alpha-2
ISO = {
    "united states": "us", "japan": "jp", "canada": "ca", "united kingdom": "gb",
    "brazil": "br", "australia": "au", "france": "fr", "germany": "de",
    "china": "cn", "india": "in", "turkey": "tr", "south korea": "kr",
    "mexico": "mx", "switzerland": "ch", "south africa": "za", "norway": "no",
    "argentina": "ar", "portugal": "pt", "new zealand": "nz", "ukraine": "ua",
    "nepal": "np", "bhutan": "bt", "cambodia": "kh", "mozambique": "mz",
    "kiribati": "ki", "sri lanka": "lk", "albania": "al", "papua new guinea": "pg",
    "trinidad and tobago": "tt", "lesotho": "ls",
}

ROUND_THEMES = {
    "1": {"bg1": (20, 30, 80),  "bg2": (60, 20, 110), "accent": "#00E5FF"},
    "2": {"bg1": (80, 20, 80),  "bg2": (120, 30, 70), "accent": "#FF4D9D"},
    "3": {"bg1": (90, 30, 20),  "bg2": (130, 60, 20), "accent": "#FFB300"},
    "4": {"bg1": (20, 60, 70),  "bg2": (20, 100, 90), "accent": "#1DE9B6"},
    "5": {"bg1": (50, 20, 90),  "bg2": (90, 30, 130), "accent": "#B388FF"},
}
DEFAULT_THEME = {"bg1": (25, 25, 70), "bg2": (60, 30, 100), "accent": "#FFD700"}

def load_font(size, bold=True):
    for p in ["/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def country_to_iso(answer):
    clean = "".join(c for c in answer if ord(c) < 0x1F1E6 or ord(c) > 0x1F1FF).strip().lower()
    for name, code in ISO.items():
        if name in clean or clean in name:
            return code
    return None

def download_flag(answer):
    iso = country_to_iso(answer)
    if not iso: return None
    cache_path = os.path.join(FLAG_CACHE, f"{iso}.png")
    if os.path.exists(cache_path):
        try: return Image.open(cache_path).convert("RGBA")
        except: pass
    url = FLAGCDN + iso + ".png"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            data = r.read()
        with open(cache_path,"wb") as f: f.write(data)
        return Image.open(BytesIO(data)).convert("RGBA")
    except Exception as e:
        print(f"      ⚠️  flag {iso} failed: {e}")
        return None

def vertical_gradient(c1, c2):
    img = Image.new("RGB", (W, H)); draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        draw.line([(0,y),(W,y)], fill=(int(c1[0]*(1-t)+c2[0]*t),
                                       int(c1[1]*(1-t)+c2[1]*t),
                                       int(c1[2]*(1-t)+c2[2]*t)))
    return img

def add_glow(img, accent_rgb):
    overlay = Image.new("RGBA",(W,H),(0,0,0,0)); od = ImageDraw.Draw(overlay)
    for cx,cy,r in [(150,150,180),(W-180,200,160),(W-150,H-150,200),(200,H-180,150)]:
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*accent_rgb,22))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")

def rounded_pill(draw, cx, cy, text, font, fill, text_col, pad_x=45, pad_y=22):
    bbox = draw.textbbox((0,0),text,font=font); tw,th = bbox[2]-bbox[0],bbox[3]-bbox[1]
    x1,y1,x2,y2 = cx-tw//2-pad_x, cy-th//2-pad_y, cx+tw//2+pad_x, cy+th//2+pad_y
    r = (y2-y1)//2
    draw.rounded_rectangle([x1+4,y1+5,x2+4,y2+5], radius=r, fill=(0,0,0,90))
    draw.rounded_rectangle([x1,y1,x2,y2], radius=r, fill=fill)
    draw.text((cx-tw//2, cy-th//2-bbox[1]), text, font=font, fill=text_col)

def make_flag_scene(answer, q_num, theme, out_path):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow(img, rgb_accent)
    draw = ImageDraw.Draw(img, "RGBA")

    font_q = load_font(46, bold=True)
    rounded_pill(draw, W//2, 75, "Which country is this?", font_q, (0,0,0,150), "#FFFFFF")

    font_num = load_font(40, bold=True)
    draw.ellipse([35,35,105,105], fill=theme["accent"])
    nbbox = draw.textbbox((0,0),str(q_num),font=font_num)
    nw,nh = nbbox[2]-nbbox[0],nbbox[3]-nbbox[1]
    draw.text((70-nw//2,70-nh//2-nbbox[1]), str(q_num), font=font_num, fill="#1a0a2e")

    flag = download_flag(answer)
    if flag:
        fw, fh = flag.size
        target_w = 600
        target_h = int(fh * target_w / fw)
        if target_h > 380:
            target_h = 380
            target_w = int(fw * target_h / fh)
        big = flag.resize((target_w, target_h), Image.LANCZOS)
        border = 6
        frame = Image.new("RGBA", (target_w+border*2, target_h+border*2), (255,255,255,255))
        frame.paste(big, (border,border), big)
        fx = W//2 - frame.width//2
        fy = H//2 - frame.height//2 - 10
        shadow = Image.new("RGBA",(W,H),(0,0,0,0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([fx+8,fy+12,fx+frame.width+8,fy+frame.height+12], radius=12, fill=(0,0,0,100))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        img = Image.alpha_composite(img.convert("RGBA"),shadow).convert("RGB")
        img.paste(frame,(fx,fy),frame)
        draw = ImageDraw.Draw(img,"RGBA")

    font_badge = load_font(30, bold=True)
    btxt = "QUIZ GO!"
    bbox = draw.textbbox((0,0),btxt,font=font_badge); bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-75,H-65,W-25,H-15], radius=25, fill=theme["accent"])
    draw.text((W-bw-50,H-58), btxt, font=font_badge, fill="#1a0a2e")

    img.save(out_path)

def make_title_card(text, theme, out_path, flag_answers=None):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow(img, rgb_accent)
    draw = ImageDraw.Draw(img,"RGBA")

    # decorative flags row for opening
    if flag_answers:
        x = W//2 - (len(flag_answers)*130)//2
        for ans in flag_answers[:5]:
            fi = download_flag(ans)
            if fi:
                fw,fh = fi.size
                bw_ = 120; bh_ = int(fh*bw_/fw)
                big = fi.resize((bw_,bh_), Image.LANCZOS)
                img.paste(big,(x,120),big)
                x += 130
        draw = ImageDraw.Draw(img,"RGBA")

    font = load_font(80, bold=True)
    words = text.split()
    if len(text) > 18 and len(words) > 1:
        mid = (len(words)+1)//2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text]
    cy = H//2 + 30
    for i,line in enumerate(lines):
        y = cy - (len(lines)-1)*65 + i*130
        rounded_pill(draw, W//2, y, line, font, theme["accent"], "#1a0a2e", pad_x=50, pad_y=25)

    font_badge = load_font(38, bold=True)
    btxt = "QUIZ ⚡ GO!"
    bbox = draw.textbbox((0,0),btxt,font=font_badge); bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-bw//2-30,H-95,W//2+bw//2+30,H-25], radius=35, fill="#FFD700")
    draw.text((W//2-bw//2,H-87), btxt, font=font_badge, fill="#1a0a2e")
    img.save(out_path)

def round_num_from_label(label, q_number):
    m = re.search(r"ROUND\s*(\d+)", label, re.IGNORECASE)
    if m: return m.group(1)
    if q_number and q_number.isdigit():
        return str(min(5, (int(q_number)-1)//10 + 1))
    return "1"

def main():
    if not os.path.exists(CSV_PATH):
        print("ERROR: run from quiz6/ folder"); return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"🚩 HQ Flag Quiz Generator (flagcdn.com) — {len(rows)} assets\n")

    # collect some answers for opening card decoration
    sample_flags = [r["answer"] for r in rows if r["asset_type"]=="question_scene"][:5]

    for row in rows:
        fname = row.get("file_name","").strip()
        if not fname: continue
        out_path = os.path.join(OUTPUT_DIR, fname)
        asset_type = row.get("asset_type","").strip()
        round_label = row.get("round","").strip()
        q_num = row.get("question_number","").strip()
        theme = ROUND_THEMES.get(round_num_from_label(round_label, q_num), DEFAULT_THEME)

        if asset_type == "title_card":
            text = row.get("question_text","").strip()
            clean = "".join(c for c in text if ord(c) < 0x1F1E6 or ord(c) > 0x1F1FF)
            clean = "".join(c for c in clean if ord(c) < 0x2600).strip()
            is_opening = "opening" in fname.lower()
            make_title_card(clean or "FLAG QUIZ", theme, out_path,
                            sample_flags if is_opening else None)
            print(f"  ✅ {fname}")
        else:
            answer = row.get("answer","").strip()
            make_flag_scene(answer, q_num, theme, out_path)
            print(f"  ✅ {fname}  {answer}")

    print(f"\n✅ Done! HQ flag scenes in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
