#!/usr/bin/env python3
"""
Premium emoji quiz generator for quiz7 (movies) & quiz10 (sports).
Downloads Twemoji PNGs (colorful Twitter emoji) and composes
energetic, scroll-stopping quiz scenes.

Run from quiz7/ or quiz10/ folder:
  python3 ../shared/generate_emoji_quiz.py
"""

import csv, os, re, urllib.request, ssl
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
OUTPUT_DIR = "images_and_videos"
CSV_PATH = "batch_generation_queue.csv"
EMOJI_CACHE = "/tmp/twemoji_cache"
os.makedirs(EMOJI_CACHE, exist_ok=True)

TWEMOJI_BASE = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/"

# ── Round color themes (background gradient + accent) ──────────────────────────
ROUND_THEMES = {
    "1": {"bg1": (20, 30, 80),  "bg2": (60, 20, 110), "accent": "#00E5FF", "name_col": "#00E5FF"},
    "2": {"bg1": (80, 20, 80),  "bg2": (120, 30, 70), "accent": "#FF4D9D", "name_col": "#FF4D9D"},
    "3": {"bg1": (90, 30, 20),  "bg2": (130, 60, 20), "accent": "#FFB300", "name_col": "#FFB300"},
    "4": {"bg1": (20, 60, 70),  "bg2": (20, 100, 90), "accent": "#1DE9B6", "name_col": "#1DE9B6"},
    "5": {"bg1": (50, 20, 90),  "bg2": (90, 30, 130), "accent": "#B388FF", "name_col": "#B388FF"},
}
DEFAULT_THEME = {"bg1": (25, 25, 70), "bg2": (60, 30, 100), "accent": "#FFD700", "name_col": "#FFD700"}

def load_font(size, bold=True):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def emoji_to_codepoint(emoji_char):
    """Convert emoji to twemoji filename codepoint."""
    cps = []
    for ch in emoji_char:
        cps.append(f"{ord(ch):x}")
    # Remove variation selector fe0f for most
    cps_clean = [c for c in cps if c != "fe0f"]
    return "-".join(cps_clean) if cps_clean else "-".join(cps)

def extract_emojis(text):
    """Extract emoji characters from text."""
    emojis = []
    i = 0
    while i < len(text):
        ch = text[i]
        cp = ord(ch)
        # Emoji ranges
        if (0x1F300 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 
            0x1F000 <= cp <= 0x1F02F or 0x1F900 <= cp <= 0x1F9FF or
            cp in (0x2B50, 0x2764, 0x2728, 0x26BD, 0x26BE, 0x26F3, 0x26F7, 0x26F8)):
            # Check for variation selector or ZWJ sequences
            emoji = ch
            j = i + 1
            while j < len(text) and ord(text[j]) in (0xFE0F, 0x200D, 0x20E3):
                emoji += text[j]
                if ord(text[j]) == 0x200D and j+1 < len(text):
                    j += 1
                    emoji += text[j]
                j += 1
            emojis.append(emoji)
            i = j
        else:
            i += 1
    return emojis

def download_emoji(emoji_char):
    """Download a single emoji PNG from Twemoji, return PIL Image."""
    cp = emoji_to_codepoint(emoji_char)
    cache_path = os.path.join(EMOJI_CACHE, f"{cp}.png")
    
    if os.path.exists(cache_path):
        try: return Image.open(cache_path).convert("RGBA")
        except: pass
    
    # Try several CDNs — first that works wins
    urls = [
        TWEMOJI_BASE + cp + ".png",
        f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@14.1.2/assets/72x72/{cp}.png",
        f"https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/{cp}.png",
        f"https://raw.githubusercontent.com/jdecked/twemoji/main/assets/72x72/{cp}.png",
    ]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    last_err = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
                data = r.read()
            if len(data) < 100:
                raise Exception("empty response")
            with open(cache_path, "wb") as f:
                f.write(data)
            return Image.open(cache_path).convert("RGBA")
        except Exception as e:
            last_err = e
            continue
    print(f"      ⚠️  emoji {cp} failed on ALL CDNs: {last_err}")
    return None

def vertical_gradient(c1, c2):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def add_glow_circles(img, accent_rgb):
    """Add soft decorative glow circles."""
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    spots = [(150,150,180),(W-180,200,160),(W-150,H-150,200),(200,H-180,150)]
    for cx,cy,r in spots:
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*accent_rgb, 22))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def rounded_pill(draw, cx, cy, text, font, fill, text_col, pad_x=45, pad_y=22):
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x1, y1 = cx-tw//2-pad_x, cy-th//2-pad_y
    x2, y2 = cx+tw//2+pad_x, cy+th//2+pad_y
    r = (y2-y1)//2
    # shadow
    draw.rounded_rectangle([x1+4,y1+5,x2+4,y2+5], radius=r, fill=(0,0,0,90))
    draw.rounded_rectangle([x1,y1,x2,y2], radius=r, fill=fill)
    draw.text((cx-tw//2, cy-th//2-bbox[1]), text, font=font, fill=text_col)
    return y2

def make_emoji_scene(emojis, question_label, answer, q_num, theme, out_path):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow_circles(img, rgb_accent)
    draw = ImageDraw.Draw(img, "RGBA")

    # Top question label
    font_q = load_font(46, bold=True)
    rounded_pill(draw, W//2, 75, question_label, font_q, (0,0,0,150), "#FFFFFF")

    # Question number — top left circle
    font_num = load_font(40, bold=True)
    draw.ellipse([35,35,105,105], fill=theme["accent"])
    nbbox = draw.textbbox((0,0), str(q_num), font=font_num)
    nw, nh = nbbox[2]-nbbox[0], nbbox[3]-nbbox[1]
    draw.text((70-nw//2, 70-nh//2-nbbox[1]), str(q_num), font=font_num, fill="#1a0a2e")

    # ── BIG EMOJIS in center ──
    if emojis:
        emoji_imgs = []
        for em in emojis:
            ei = download_emoji(em)
            if ei: emoji_imgs.append(ei)
        
        if emoji_imgs:
            target = 200  # each emoji size
            gap = 50
            total_w = len(emoji_imgs)*target + (len(emoji_imgs)-1)*gap
            # scale down if too wide
            if total_w > W-160:
                target = int((W-160 - (len(emoji_imgs)-1)*gap) / len(emoji_imgs))
                total_w = len(emoji_imgs)*target + (len(emoji_imgs)-1)*gap
            
            start_x = W//2 - total_w//2
            cy = H//2 - 20
            
            for ei in emoji_imgs:
                big = ei.resize((target, target), Image.LANCZOS)
                # soft shadow behind emoji
                shadow = Image.new("RGBA",(W,H),(0,0,0,0))
                sd = ImageDraw.Draw(shadow)
                sd.ellipse([start_x+10, cy-target//2+15, start_x+target+10, cy+target//2+15], fill=(0,0,0,70))
                shadow = shadow.filter(ImageFilter.GaussianBlur(20))
                img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
                img.paste(big, (start_x, cy-target//2), big)
                start_x += target + gap
            draw = ImageDraw.Draw(img, "RGBA")

    # Answer pill at bottom (revealed via overlay normally, but we bake position)
    # NOTE: answer NOT drawn here — make_quiz_video overlays it.

    # QUIZ GO badge bottom-right
    font_badge = load_font(30, bold=True)
    btxt = "QUIZ GO!"
    bbox = draw.textbbox((0,0), btxt, font=font_badge)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-75, H-65, W-25, H-15], radius=25, fill=theme["accent"])
    draw.text((W-bw-50, H-58), btxt, font=font_badge, fill="#1a0a2e")

    img.save(out_path)

def make_wyr_scene(clue, q_num, theme, out_path):
    """Would You Rather: two emoji options split left/right with VS."""
    # Parse clue: "OptA|emojiA|OptB|emojiB"
    parts = clue.split("|")
    if len(parts) == 4:
        opt_a, em_a, opt_b, em_b = parts
    else:
        opt_a, em_a, opt_b, em_b = "Option A", "", "Option B", ""

    # Split background: left warm red, right cool blue
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        # left gradient
        lr = int(180*(1-t*0.3)); lg = int(40+20*t); lb = int(60+20*t)
        draw.line([(0,y),(W//2,y)], fill=(min(255,lr),lg,lb))
        rr = int(30+10*t); rg = int(80+30*t); rb = int(150+40*t)
        draw.line([(W//2,y),(W,y)], fill=(rr,rg,min(255,rb)))
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # Center divider
    draw.rectangle([W//2-3,0,W//2+3,H], fill=(255,255,255,180))

    # Top question label
    font_q = load_font(46, bold=True)
    rounded_pill(draw, W//2, 70, "Would You Rather?", font_q, (0,0,0,160), "#FFFFFF")

    # Emoji A (left center)
    if em_a:
        ems = extract_emojis(em_a)
        if ems:
            ei = download_emoji(ems[0])
            if ei:
                big = ei.resize((220,220), Image.LANCZOS)
                img.paste(big, (W//4-110, H//2-140), big)
    # Emoji B (right center)
    if em_b:
        ems = extract_emojis(em_b)
        if ems:
            ei = download_emoji(ems[0])
            if ei:
                big = ei.resize((220,220), Image.LANCZOS)
                img.paste(big, (W*3//4-110, H//2-140), big)
    draw = ImageDraw.Draw(img, "RGBA")

    # Option labels
    font_opt = load_font(50, bold=True)
    def draw_centered(text, cx, cy, col):
        bbox = draw.textbbox((0,0), text, font=font_opt)
        tw = bbox[2]-bbox[0]
        draw.text((cx-tw//2, cy), text, font=font_opt, fill=col)
    draw_centered(opt_a, W//4, H//2+130, "#FFFFFF")
    draw_centered(opt_b, W*3//4, H//2+130, "#FFFFFF")

    # VS badge center
    font_vs = load_font(56, bold=True)
    vbbox = draw.textbbox((0,0),"VS",font=font_vs)
    vw,vh = vbbox[2]-vbbox[0], vbbox[3]-vbbox[1]
    draw.ellipse([W//2-55,H//2-55,W//2+55,H//2+55], fill="#FFD700", outline="#FFFFFF", width=4)
    draw.text((W//2-vw//2, H//2-vh//2-vbbox[1]), "VS", font=font_vs, fill="#1a0a2e")

    # QUIZ GO badge
    font_badge = load_font(30, bold=True)
    btxt = "QUIZ GO!"
    bbox = draw.textbbox((0,0), btxt, font=font_badge)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-75, H-65, W-25, H-15], radius=25, fill="#FFD700")
    draw.text((W-bw-50, H-58), btxt, font=font_badge, fill="#1a0a2e")

    img.save(out_path)

def make_title_card(text, theme, out_path, big_emoji=None):
    rgb_accent = hex_to_rgb(theme["accent"])
    img = vertical_gradient(theme["bg1"], theme["bg2"])
    img = add_glow_circles(img, rgb_accent)
    draw = ImageDraw.Draw(img, "RGBA")

    # Big emoji decoration top
    if big_emoji:
        ems = extract_emojis(big_emoji)
        if ems:
            x = W//2 - (len(ems)*120)//2
            for em in ems[:5]:
                ei = download_emoji(em)
                if ei:
                    big = ei.resize((110,110), Image.LANCZOS)
                    img.paste(big, (x, 110), big)
                    x += 120
            draw = ImageDraw.Draw(img, "RGBA")

    # Title text
    font = load_font(80, bold=True)
    words = text.split()
    if len(text) > 18 and len(words) > 1:
        mid = (len(words)+1)//2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text]

    cy = H//2 + 20
    for i, line in enumerate(lines):
        y = cy - (len(lines)-1)*65 + i*130
        rounded_pill(draw, W//2, y, line, font, theme["accent"], "#1a0a2e", pad_x=50, pad_y=25)

    # QUIZ GO badge
    font_badge = load_font(38, bold=True)
    btxt = "QUIZ ⚡ GO!"
    bbox = draw.textbbox((0,0), btxt, font=font_badge)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-bw//2-30, H-95, W//2+bw//2+30, H-25], radius=35, fill="#FFD700")
    draw.text((W//2-bw//2, H-87), btxt, font=font_badge, fill="#1a0a2e")

    img.save(out_path)

def round_num_from_label(label, q_number):
    """Determine round theme from round label or question number."""
    # Try to find round number in label
    m = re.search(r"ROUND\s*(\d+)", label, re.IGNORECASE)
    if m:
        return m.group(1)
    # Fallback by question number ranges
    if q_number:
        n = int(q_number)
        if n <= 10: return "1"
        elif n <= 20: return "2"
        elif n <= 30: return "3"
        elif n <= 40: return "4"
        else: return "5"
    return "1"

def main():
    if not os.path.exists(CSV_PATH):
        print("ERROR: run from inside quiz7/ or quiz10/ folder"); return
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"🎬 Premium Emoji Quiz Generator — {len(rows)} assets\n")

    for row in rows:
        fname = row.get("file_name","").strip()
        if not fname: continue
        out_path = os.path.join(OUTPUT_DIR, fname)
        
        asset_type = row.get("asset_type","").strip()
        round_label = row.get("round","").strip()
        q_num = row.get("question_number","").strip()
        theme_key = round_num_from_label(round_label, q_num)
        theme = ROUND_THEMES.get(theme_key, DEFAULT_THEME)

        if asset_type == "title_card":
            text = row.get("question_text","").strip()
            # opening card gets emoji decoration
            big_emoji = text if any(ord(c)>0x2600 for c in text) else None
            # Remove emoji from title text for clean rendering
            clean_text = "".join(c for c in text if ord(c) < 0x2600).strip()
            if "ROUND" in clean_text.upper():
                clean_text = clean_text  # keep round text
            make_title_card(clean_text or "QUIZ TIME", theme, out_path, big_emoji)
            print(f"  ✅ {fname}")
        elif asset_type == "wyr_scene" or "|" in row.get("main_visual_clue",""):
            clue = row.get("main_visual_clue","").strip()
            make_wyr_scene(clue, q_num, theme, out_path)
            print(f"  ✅ {fname}  (WYR)")
        else:
            question = row.get("question_text","")
            answer = row.get("answer","").strip()
            emojis = extract_emojis(question)
            # Clean question label (remove emojis)
            q_label = "".join(c for c in question if ord(c) < 0x2600).strip()
            if not q_label: q_label = "What is this?"
            make_emoji_scene(emojis, q_label, answer, q_num, theme, out_path)
            print(f"  ✅ {fname}  {''.join(emojis)}")

    print(f"\n✅ Done! Premium scenes in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
