#!/usr/bin/env python3
"""
Premium flag quiz generator for quiz6.
Renders large country flags (from Twemoji regional-indicator flag emojis)
on energetic gradient backgrounds. Viral-style design matching emoji quizzes.

Run from quiz6/ folder:
  python3 ../shared/generate_flag_quiz.py
"""

import csv, os, re, urllib.request, ssl
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
OUTPUT_DIR = "images_and_videos"
CSV_PATH = "batch_generation_queue.csv"
EMOJI_CACHE = "/tmp/twemoji_cache"
os.makedirs(EMOJI_CACHE, exist_ok=True)

TWEMOJI_BASE = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/"

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

def flag_emoji_to_codepoint(text):
    """Extract regional indicator pair from text → twemoji filename."""
    cps = []
    for ch in text:
        cp = ord(ch)
        if 0x1F1E6 <= cp <= 0x1F1FF:  # regional indicator symbols
            cps.append(f"{cp:x}")
    return "-".join(cps) if cps else None

def download_flag(text):
    cp = flag_emoji_to_codepoint(text)
    if not cp: return None
    cache_path = os.path.join(EMOJI_CACHE, f"{cp}.png")
    if os.path.exists(cache_path):
        try: return Image.open(cache_path).convert("RGBA")
        except: pass
    url = TWEMOJI_BASE + cp + ".png"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = r.read()
        with open(cache_path,"wb") as f: f.write(data)
        return Image.open(cache_path).convert("RGBA")
    except Exception as e:
        print(f"      ⚠️  flag {cp} failed: {e}")
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

def strip_flag_emoji(text):
    return "".join(c for c in text if not (0x1F1E6 <= ord(c) <= 0x1F1FF)).strip()

def make_flag_scene(answer_with_flag, q_num, theme, out_path):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow(img, rgb_accent)
    draw = ImageDraw.Draw(img, "RGBA")

    # Top question label
    font_q = load_font(46, bold=True)
    rounded_pill(draw, W//2, 75, "Which country is this?", font_q, (0,0,0,150), "#FFFFFF")

    # Question number circle
    font_num = load_font(40, bold=True)
    draw.ellipse([35,35,105,105], fill=theme["accent"])
    nbbox = draw.textbbox((0,0),str(q_num),font=font_num)
    nw,nh = nbbox[2]-nbbox[0],nbbox[3]-nbbox[1]
    draw.text((70-nw//2,70-nh//2-nbbox[1]), str(q_num), font=font_num, fill="#1a0a2e")

    # BIG FLAG in center
    flag = download_flag(answer_with_flag)
    if flag:
        # Twemoji flags are wide (e.g. 72x54). Scale up keeping aspect.
        fw, fh = flag.size
        target_w = 560
        target_h = int(fh * target_w / fw)
        big = flag.resize((target_w, target_h), Image.LANCZOS)
        # White border frame
        border = 8
        frame = Image.new("RGBA", (target_w+border*2, target_h+border*2), (255,255,255,255))
        frame.paste(big, (border,border), big)
        # shadow
        shadow = Image.new("RGBA",(W,H),(0,0,0,0))
        sd = ImageDraw.Draw(shadow)
        fx = W//2 - frame.width//2
        fy = H//2 - frame.height//2 - 10
        sd.rounded_rectangle([fx+8,fy+12,fx+frame.width+8,fy+frame.height+12], radius=12, fill=(0,0,0,90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        img = Image.alpha_composite(img.convert("RGBA"),shadow).convert("RGB")
        img.paste(frame,(fx,fy),frame)
        draw = ImageDraw.Draw(img,"RGBA")

    # QUIZ GO badge
    font_badge = load_font(30, bold=True)
    btxt = "QUIZ GO!"
    bbox = draw.textbbox((0,0),btxt,font=font_badge); bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-75,H-65,W-25,H-15], radius=25, fill=theme["accent"])
    draw.text((W-bw-50,H-58), btxt, font=font_badge, fill="#1a0a2e")

    img.save(out_path)

def make_title_card(text, theme, out_path, big_emoji=None):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow(img, rgb_accent)
    draw = ImageDraw.Draw(img,"RGBA")

    # decorative flags row for opening
    if big_emoji:
        flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', big_emoji)
        if flags:
            x = W//2 - (len(flags)*120)//2
            for fl in flags[:5]:
                fi = download_flag(fl)
                if fi:
                    fw,fh = fi.size
                    big = fi.resize((110, int(fh*110/fw)), Image.LANCZOS)
                    img.paste(big,(x,120),big)
                    x += 120
            draw = ImageDraw.Draw(img,"RGBA")

    font = load_font(80, bold=True)
    words = text.split()
    if len(text) > 18 and len(words) > 1:
        mid = (len(words)+1)//2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text]
    cy = H//2 + 20
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
        n = int(q_number)
        return str(min(5, (n-1)//10 + 1))
    return "1"

def main():
    if not os.path.exists(CSV_PATH):
        print("ERROR: run from quiz6/ folder"); return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"🚩 Premium Flag Quiz Generator — {len(rows)} assets\n")

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
            big_emoji = text if re.search(r'[\U0001F1E6-\U0001F1FF]', text) else None
            clean = strip_flag_emoji("".join(c for c in text if ord(c)<0x1F1E6 or ord(c)>0x1F1FF))
            clean = "".join(c for c in clean if ord(c) < 0x2600).strip()
            make_title_card(clean or "FLAG QUIZ", theme, out_path, big_emoji)
            print(f"  ✅ {fname}")
        else:
            answer = row.get("answer","").strip()
            make_flag_scene(answer, q_num, theme, out_path)
            print(f"  ✅ {fname}  {answer}")

    print(f"\n✅ Done! Flag scenes in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
