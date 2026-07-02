#!/usr/bin/env python3
"""
Local image generator for quiz5-10 (no API needed).
Reads batch_generation_queue.csv and generates PNG images locally using PIL.
Supports: silhouettes, flags, emoji quizzes, would-you-rather, etc.

Usage: python3 ../shared/generate_local_images.py
Run from inside a quiz folder (quiz5/, quiz6/, etc.)
"""

import csv, os, re
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1280, 720
OUTPUT_DIR = "images_and_videos"
CSV_PATH = "batch_generation_queue.csv"

# ── Color palettes ────────────────────────────────────────────────────────────
PALETTES = [
    ("#1a0a3d", "#6B35A8"),  # purple
    ("#0a1a3d", "#1560BD"),  # blue
    ("#1a0a0a", "#8B1A1A"),  # dark red
    ("#0a2a0a", "#1a6B1a"),  # green
    ("#2a1a0a", "#8B5A1A"),  # brown
]

BG_COLORS = [
    "#FF6B35", "#FF3D3D", "#FFD700", "#4CAF50", "#2196F3",
    "#9C27B0", "#FF5722", "#00BCD4", "#E91E63", "#3F51B5",
]

def load_font(size, bold=False):
    candidates = [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def draw_centered_text(draw, text, y, font, color, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill=(0,0,0,120))
    draw.text((x, y), text, font=font, fill=color)

def draw_pill(draw, text, cx, cy, bg_color, text_color, font_size=72, padding_x=50, padding_y=20):
    font = load_font(font_size, bold=True)
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    rx1 = cx - tw//2 - padding_x
    ry1 = cy - th//2 - padding_y
    rx2 = cx + tw//2 + padding_x
    ry2 = cy + th//2 + padding_y
    r = (ry2-ry1)//2
    draw.rounded_rectangle([rx1,ry1,rx2,ry2], radius=r, fill=bg_color)
    draw.text((cx - tw//2, ry1+padding_y), text, font=font, fill=text_color)

def gradient_bg(colors=("#1a0a3d","#4B1A8E")):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    c1 = tuple(int(colors[0].lstrip('#')[i:i+2],16) for i in (0,2,4))
    c2 = tuple(int(colors[1].lstrip('#')[i:i+2],16) for i in (0,2,4))
    for y in range(H):
        t = y/H
        r = int(c1[0]*(1-t)+c2[0]*t)
        g = int(c1[1]*(1-t)+c2[1]*t)
        b = int(c1[2]*(1-t)+c2[2]*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

# ── TITLE CARD ────────────────────────────────────────────────────────────────
def make_title_card(row, idx):
    text = row.get("question_text","").strip()
    img = gradient_bg(("#1a0a3d","#4B1A8E"))
    draw = ImageDraw.Draw(img)

    # Decorative circles
    for cx,cy,r,alpha in [(150,150,200,30),(W-150,H-150,250,25),(W//2,H//2,350,10)]:
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255,alpha))
        img = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Lightning bolt decoration
    bolt = [(W//2+20,-10),(W//2-40,H//2-50),(W//2,H//2-50),(W//2-30,H+10),(W//2+80,H//2+30),(W//2+30,H//2+30),(W//2+70,-10)]
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.polygon(bolt, fill=(255,215,0,25))
    img = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Main title text
    if text:
        lines = text.split("\n") if "\n" in text else [text]
        font_big = load_font(90, bold=True)
        font_med = load_font(64, bold=True)
        
        # Try to fit on screen
        font = font_big if len(text) < 25 else font_med
        
        # Split long text into 2 lines
        words = text.split()
        if len(words) > 4 and len(text) > 30:
            mid = len(words)//2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        else:
            lines = [text]
        
        total_h = len(lines) * 110
        start_y = H//2 - total_h//2
        
        for i, line in enumerate(lines):
            # pill background for each line
            bbox = draw.textbbox((0,0), line, font=font)
            tw = bbox[2]-bbox[0]
            px, py = 40, 18
            pill_colors = ["#FF3D3D","#FFD700","#4CAF50","#2196F3","#9C27B0"]
            pcol = pill_colors[idx % len(pill_colors)]
            tcol = "#FFFFFF" if pcol != "#FFD700" else "#1a0a3d"
            x1 = W//2 - tw//2 - px
            y1 = start_y + i*110 - py
            x2 = W//2 + tw//2 + px
            y2 = start_y + i*110 + 85 + py
            r = (y2-y1)//2
            draw.rounded_rectangle([x1,y1,x2,y2], radius=r, fill=pcol)
            draw.text((W//2 - tw//2, start_y + i*110), line, font=font, fill=tcol)

    # QUIZ GO badge bottom
    font_badge = load_font(42, bold=True)
    badge_text = "QUIZ ⚡ GO!"
    bbox = draw.textbbox((0,0), badge_text, font=font_badge)
    tw = bbox[2]-bbox[0]
    bx = W//2 - tw//2 - 30
    draw.rounded_rectangle([bx, H-100, bx+tw+60, H-30], radius=35, fill="#FFD700")
    draw.text((W//2 - tw//2, H-94), badge_text, font=font_badge, fill="#1a0a3d")

    return img

# ── QUESTION SCENE: ANIMAL SILHOUETTE ────────────────────────────────────────
ANIMAL_SVG_PATHS = {
    "elephant": "M200,300 Q180,200 220,150 Q260,100 320,120 Q380,100 400,150 L420,200 Q460,180 480,220 Q500,260 470,300 L460,380 Q440,420 400,430 L350,440 Q300,450 250,440 L220,420 Q190,400 200,380 Z M220,150 Q200,130 195,100 Q190,80 210,70 Q230,60 240,80 L245,120 M320,120 L310,80 Q305,60 325,55 Q345,50 348,70 L345,110",
}

BG_COLORS_BY_IDX = [
    "#FF6B35","#2196F3","#4CAF50","#FF3D3D","#9C27B0",
    "#FF5722","#00BCD4","#E91E63","#3F51B5","#FF9800",
    "#8BC34A","#F44336","#03A9F4","#E040FB","#FFEB3B",
    "#26C6DA","#EF5350","#7E57C2","#66BB6A","#FFA726",
]

def make_question_scene(row, idx):
    question = row.get("question_text","").strip()
    answer = row.get("answer","").strip()
    clue = row.get("main_visual_clue","").strip()
    fname = row.get("file_name","")
    
    bg_col = BG_COLORS_BY_IDX[idx % len(BG_COLORS_BY_IDX)]
    
    # Detect quiz type from filename/clue
    is_flag = "flag" in fname.lower() or "flag" in clue.lower()
    is_emoji = any(c > '\U0001F300' for c in question+clue) or "emoji" in clue.lower()
    is_wyr = "would you rather" in question.lower() or "wyr" in fname.lower()
    is_silhouette = "silhouette" in clue.lower() or "scene_q0" in fname and "quiz5" not in fname
    is_animal = "animal" in question.lower() or "scene_q" in fname
    
    if is_wyr:
        return make_wyr_scene(row, idx)
    elif is_flag:
        return make_flag_scene(row, idx)
    else:
        return make_generic_question(row, idx, bg_col)

def make_generic_question(row, idx, bg_col):
    question = row.get("question_text","").strip()
    answer = row.get("answer","").strip()
    qnum = row.get("question_number","").strip()
    clue = row.get("main_visual_clue","").strip()

    # Background
    img = gradient_bg(("#0d0d2b","#1a0a3d"))
    draw = ImageDraw.Draw(img)

    # Big question number watermark
    if qnum and qnum.isdigit():
        font_wm = load_font(400, bold=True)
        bbox = draw.textbbox((0,0), qnum, font=font_wm)
        tw = bbox[2]-bbox[0]
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.text((W-tw-20, H//2-220), qnum, font=font_wm, fill=(255,255,255,12))
        img = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Color accent bar left
    accent = bg_col
    draw.rectangle([0,0,12,H], fill=accent)

    # Question number badge
    if qnum:
        font_num = load_font(48, bold=True)
        draw.rounded_rectangle([30,30,120,90], radius=20, fill=accent)
        bbox = draw.textbbox((0,0), f"#{qnum}", font=font_num)
        tw = bbox[2]-bbox[0]
        draw.text((75-tw//2, 42), f"#{qnum}", font=font_num, fill="#FFFFFF")

    # Big colorful question mark or emoji in center
    font_big_emoji = load_font(200, bold=True)
    draw.text((W//2-80, H//2-160), "?", font=font_big_emoji, fill=accent)

    # Question text pill
    font_q = load_font(54, bold=True)
    words = question.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur+[w])
        bbox = draw.textbbox((0,0), test, font=font_q)
        if bbox[2]-bbox[0] > W-120 and cur:
            lines.append(" ".join(cur)); cur=[w]
        else:
            cur.append(w)
    if cur: lines.append(" ".join(cur))
    
    lh = 70
    total_h = len(lines)*lh + 40
    qy = 80
    draw.rounded_rectangle([40, qy, W-40, qy+total_h], radius=20, fill=(10,10,60,200))
    for i,line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font_q)
        tw = bbox[2]-bbox[0]
        draw.text((W//2-tw//2, qy+20+i*lh), line, font=font_q, fill="#FFFFFF")

    # Answer area (revealed) — shown as "?" covered
    font_a = load_font(72, bold=True)
    bbox = draw.textbbox((0,0), answer, font=font_a)
    tw = bbox[2]-bbox[0]
    ax = W//2 - tw//2
    ay = H - 160
    # Answer pill
    draw.rounded_rectangle([ax-40, ay-20, ax+tw+40, ay+90], radius=40, fill=accent)
    draw.text((ax, ay), answer, font=font_a, fill="#FFFFFF" if accent != "#FFD700" else "#1a0a3d")

    # QUIZ GO badge
    font_badge = load_font(32, bold=True)
    badge = "QUIZ ⚡ GO!"
    bbox = draw.textbbox((0,0), badge, font=font_badge)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-70, H-70, W-20, H-10], radius=25, fill="#FFD700")
    draw.text((W-bw-40, H-64), badge, font=font_badge, fill="#1a0a3d")

    return img

def make_flag_scene(row, idx):
    question = row.get("question_text","").strip()
    answer = row.get("answer","").strip()
    clue = row.get("main_visual_clue","").strip()
    
    img = gradient_bg(("#0d0d2b","#1a1a4d"))
    draw = ImageDraw.Draw(img)

    # Flag area: centered rectangle
    fw, fh = 700, 420
    fx = W//2 - fw//2
    fy = H//2 - fh//2 - 40
    
    # Draw flag based on answer
    draw_flag(draw, img, answer.lower(), fx, fy, fw, fh)
    
    # Shadow under flag
    draw.rectangle([fx+8, fy+fh+2, fx+fw+8, fy+fh+14], fill=(0,0,0,80))

    # Question text
    font_q = load_font(52, bold=True)
    bbox = draw.textbbox((0,0), question, font=font_q)
    tw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-tw//2-40, 30, W//2+tw//2+40, 100], radius=30, fill=(255,61,61,220))
    draw.text((W//2-tw//2, 42), question, font=font_q, fill="#FFFFFF")

    # Answer pill
    font_a = load_font(62, bold=True)
    clean_answer = answer.split()[0] if answer else answer  # remove emoji for sizing
    bbox = draw.textbbox((0,0), answer, font=font_a)
    tw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-tw//2-40, H-130, W//2+tw//2+40, H-30], radius=40, fill="#FFD700")
    draw.text((W//2-tw//2, H-122), answer, font=font_a, fill="#1a0a3d")

    return img

def draw_flag(draw, img, answer, fx, fy, fw, fh):
    """Draw simplified flag based on country name"""
    a = answer.lower().split()[0]  # first word of answer
    
    # Draw border
    draw.rectangle([fx-3,fy-3,fx+fw+3,fy+fh+3], outline="#FFFFFF", width=3)
    
    if "united states" in answer.lower() or "usa" in answer.lower():
        # US Flag: stripes + canton
        stripe_h = fh // 13
        for i in range(13):
            color = "#B22234" if i%2==0 else "#FFFFFF"
            draw.rectangle([fx, fy+i*stripe_h, fx+fw, fy+(i+1)*stripe_h], fill=color)
        # Canton
        canton_w, canton_h = int(fw*0.4), stripe_h*7
        draw.rectangle([fx, fy, fx+canton_w, fy+canton_h], fill="#3C3B6E")
        # Stars (simplified 3x3 grid hint)
        for si in range(4):
            for sj in range(5):
                sx = fx + 20 + sj*(canton_w-30)//4
                sy = fy + 15 + si*(canton_h-30)//3
                draw.text((sx,sy), "★", font=load_font(18), fill="#FFFFFF")
    elif "japan" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#FFFFFF")
        cx,cy,r = fx+fw//2, fy+fh//2, min(fw,fh)//4
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill="#BC002D")
    elif "canada" in answer.lower():
        third = fw//3
        draw.rectangle([fx,fy,fx+third,fy+fh], fill="#FF0000")
        draw.rectangle([fx+third,fy,fx+2*third,fy+fh], fill="#FFFFFF")
        draw.rectangle([fx+2*third,fy,fx+fw,fy+fh], fill="#FF0000")
        # Maple leaf hint
        cx,cy = fx+fw//2, fy+fh//2
        draw.text((cx-30,cy-50), "🍁", font=load_font(80), fill="#FF0000")
    elif "france" in answer.lower():
        third = fw//3
        draw.rectangle([fx,fy,fx+third,fy+fh], fill="#002395")
        draw.rectangle([fx+third,fy,fx+2*third,fy+fh], fill="#FFFFFF")
        draw.rectangle([fx+2*third,fy,fx+fw,fy+fh], fill="#ED2939")
    elif "germany" in answer.lower():
        third = fh//3
        draw.rectangle([fx,fy,fx+fw,fy+third], fill="#000000")
        draw.rectangle([fx,fy+third,fx+fw,fy+2*third], fill="#DD0000")
        draw.rectangle([fx,fy+2*third,fx+fw,fy+fh], fill="#FFCE00")
    elif "ukraine" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh//2], fill="#005BBB")
        draw.rectangle([fx,fy+fh//2,fx+fw,fy+fh], fill="#FFD500")
    elif "china" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#DE2910")
        draw.text((fx+30,fy+20), "★", font=load_font(80), fill="#FFDE00")
        for i in range(4):
            draw.text((fx+130,fy+15+i*40), "★", font=load_font(32), fill="#FFDE00")
    elif "brazil" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#009C3B")
        # Diamond
        cx,cy = fx+fw//2, fy+fh//2
        diamond = [(cx,fy+30),(fx+fw-30,cy),(cx,fy+fh-30),(fx+30,cy)]
        draw.polygon(diamond, fill="#FFDF00")
        draw.ellipse([cx-fh//4,cy-fh//4,cx+fh//4,cy+fh//4], fill="#002776")
    elif "australia" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#00008B")
        # Union Jack hint top left
        uj_w, uj_h = fw//3, fh//2
        draw.rectangle([fx,fy,fx+uj_w,fy+uj_h], fill="#012169")
        draw.line([fx,fy,fx+uj_w,fy+uj_h], fill="#FFFFFF", width=6)
        draw.line([fx+uj_w,fy,fx,fy+uj_h], fill="#FFFFFF", width=6)
        draw.line([fx+uj_w//2,fy,fx+uj_w//2,fy+uj_h], fill="#FFFFFF", width=5)
        draw.line([fx,fy+uj_h//2,fx+uj_w,fy+uj_h//2], fill="#FFFFFF", width=5)
        # Southern cross stars
        for sx,sy in [(fx+fw-100,fy+80),(fx+fw-160,fy+180),(fx+fw-80,fy+200),(fx+fw-200,fy+100)]:
            draw.text((sx,sy), "★", font=load_font(36), fill="#FFFFFF")
    elif "norway" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#EF2B2D")
        cw = fw//5
        draw.rectangle([fx+cw,fy,fx+cw*2,fy+fh], fill="#FFFFFF")
        draw.rectangle([fx,fy+fh//2-fh//8,fx+fw,fy+fh//2+fh//8], fill="#FFFFFF")
        draw.rectangle([fx+cw+10,fy,fx+cw*2-10,fy+fh], fill="#002868")
        draw.rectangle([fx,fy+fh//2-fh//12,fx+fw,fy+fh//2+fh//12], fill="#002868")
    elif "switzerland" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#FF0000")
        cw = int(fw*0.2); ch = int(fh*0.6); arm = int(fh*0.2)
        cx,cy = fx+fw//2, fy+fh//2
        draw.rectangle([cx-arm//2, cy-ch//2, cx+arm//2, cy+ch//2], fill="#FFFFFF")
        draw.rectangle([cx-ch//2+arm, cy-arm//2, cx+ch//2-arm, cy+arm//2], fill="#FFFFFF")
    elif "turkey" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#E30A17")
        cx,cy = fx+fw//2-40, fy+fh//2
        r = fh//4
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill="#FFFFFF")
        draw.ellipse([cx-r+20,cy-r+5,cx+r+20,cy+r-5], fill="#E30A17")
        draw.text((cx+r-10,cy-30),"★",font=load_font(60),fill="#FFFFFF")
    elif "south korea" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#FFFFFF")
        cx,cy = fx+fw//2, fy+fh//2
        r = min(fw,fh)//5
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill="#CD2E3A")
        draw.ellipse([cx-r,cy,cx+r,cy+2*r], fill="#0047A0")
    elif "nepal" in answer.lower():
        # Nepal - unique pennant shape
        draw.polygon([fx,fy, fx+fw//2,fy+fh//2, fx,fy+fh], fill="#003893")
        draw.polygon([fx,fy, fx+fw//2,fy+fh//2, fx,fy+fh], outline="#FFFFFF", width=4)
        draw.polygon([fx,fy+fh//2, fx+fw*2//3,fy+fh, fx,fy+fh], fill="#003893")
        draw.polygon([fx,fy+fh//2, fx+fw*2//3,fy+fh, fx,fy+fh], outline="#FFFFFF", width=4)
        draw.text((fx+60,fy+fh//4), "☽", font=load_font(50), fill="#FFFFFF")
        draw.text((fx+60,fy+fh*2//3), "☀", font=load_font(50), fill="#FFFFFF")
    elif "india" in answer.lower():
        third = fh//3
        draw.rectangle([fx,fy,fx+fw,fy+third], fill="#FF9933")
        draw.rectangle([fx,fy+third,fx+fw,fy+2*third], fill="#FFFFFF")
        draw.rectangle([fx,fy+2*third,fx+fw,fy+fh], fill="#138808")
        cx,cy = fx+fw//2, fy+fh//2
        r = fh//7
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline="#000080", width=3)
        draw.text((cx-20,cy-25),"✦",font=load_font(40),fill="#000080")
    elif "argentina" in answer.lower():
        third = fh//3
        draw.rectangle([fx,fy,fx+fw,fy+third], fill="#74ACDF")
        draw.rectangle([fx,fy+third,fx+fw,fy+2*third], fill="#FFFFFF")
        draw.rectangle([fx,fy+2*third,fx+fw,fy+fh], fill="#74ACDF")
        draw.text((fx+fw//2-30,fy+fh//2-40),"☀",font=load_font(80),fill="#F6B40E")
    elif "south africa" in answer.lower():
        # Y shape flag
        third_h = fh//3
        draw.rectangle([fx,fy,fx+fw,fy+third_h], fill="#007A4D")
        draw.rectangle([fx,fy+2*third_h,fx+fw,fy+fh], fill="#FF0000" )
        draw.rectangle([fx,fy+third_h,fx+fw,fy+2*third_h], fill="#FFFFFF")
        # Black triangle
        draw.polygon([fx,fy, fx+fw//3,fy+fh//2, fx,fy+fh], fill="#000000")
        draw.polygon([fx,fy, fx+fw//3,fy+fh//2, fx,fy+fh], outline="#FFB81C", width=8)
    elif "ukraine" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh//2], fill="#005BBB")
        draw.rectangle([fx,fy+fh//2,fx+fw,fy+fh], fill="#FFD500")
    elif "mexico" in answer.lower():
        third = fw//3
        draw.rectangle([fx,fy,fx+third,fy+fh], fill="#006847")
        draw.rectangle([fx+third,fy,fx+2*third,fy+fh], fill="#FFFFFF")
        draw.rectangle([fx+2*third,fy,fx+fw,fy+fh], fill="#CE1126")
        draw.text((fx+fw//2-25,fy+fh//2-40),"🦅",font=load_font(70),fill="#000000")
    elif "portugal" in answer.lower():
        split = int(fw*0.38)
        draw.rectangle([fx,fy,fx+split,fy+fh], fill="#006600")
        draw.rectangle([fx+split,fy,fx+fw,fy+fh], fill="#FF0000")
        draw.ellipse([fx+split-40,fy+fh//2-50,fx+split+40,fy+fh//2+50], fill="#FFD700", outline="#003399",width=3)
    elif "albania" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#E41E20")
        draw.text((fx+fw//2-60,fy+fh//2-80),"🦅",font=load_font(160),fill="#000000")
    elif "bhutan" in answer.lower():
        draw.polygon([fx,fy,fx+fw,fy+fh,fx,fy+fh], fill="#FF8000")
        draw.polygon([fx,fy,fx+fw,fy,fx+fw,fy+fh], fill="#FFD700")
        draw.text((fx+fw//2-40,fy+fh//2-50),"🐉",font=load_font(100),fill="#FFFFFF")
    elif "new zealand" in answer.lower():
        draw.rectangle([fx,fy,fx+fw,fy+fh], fill="#00247D")
        uj_w,uj_h = fw//3,fh//2
        draw.rectangle([fx,fy,fx+uj_w,fy+uj_h], fill="#012169")
        draw.line([fx,fy,fx+uj_w,fy+uj_h],fill="#FFFFFF",width=5)
        draw.line([fx+uj_w,fy,fx,fy+uj_h],fill="#FFFFFF",width=5)
        draw.line([fx+uj_w//2,fy,fx+uj_w//2,fy+uj_h],fill="#FFFFFF",width=4)
        draw.line([fx,fy+uj_h//2,fx+uj_w,fy+uj_h//2],fill="#FFFFFF",width=4)
        for sx,sy in [(fx+fw-80,fy+60),(fx+fw-150,fy+160),(fx+fw-70,fy+190)]:
            draw.text((sx,sy),"✦",font=load_font(40),fill="#CC0000")
    else:
        # Generic colorful fallback flag
        colors = ["#FF3D3D","#FFFFFF","#3D3DFF"]
        third = fh//3
        for i,c in enumerate(colors):
            draw.rectangle([fx,fy+i*third,fx+fw,fy+(i+1)*third], fill=c)
        font_f = load_font(60, bold=True)
        # Show emoji from answer if present
        emoji_chars = [c for c in answer if c > '\U0001F300']
        if emoji_chars:
            draw.text((fx+fw//2-40, fy+fh//2-40), emoji_chars[0], font=load_font(80), fill="#000000")

def make_wyr_scene(row, idx):
    question = row.get("question_text","").strip()
    
    img = gradient_bg(("#0d0d2b","#2a0a2a"))
    draw = ImageDraw.Draw(img)

    # Split screen: left red, right yellow
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0,0,W//2-5,H], fill=(255,61,61,60))
    od.rectangle([W//2+5,0,W,H], fill=(255,215,0,60))
    img = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # VS in center
    font_vs = load_font(120, bold=True)
    vs_bbox = draw.textbbox((0,0),"VS",font=font_vs)
    vsw = vs_bbox[2]-vs_bbox[0]
    draw.rounded_rectangle([W//2-vsw//2-20,H//2-70,W//2+vsw//2+20,H//2+70], radius=20, fill="#FFFFFF")
    draw.text((W//2-vsw//2, H//2-60), "VS", font=font_vs, fill="#FF3D3D")

    # Would You Rather header
    font_h = load_font(52, bold=True)
    header = "WOULD YOU RATHER?"
    bbox = draw.textbbox((0,0),header,font=font_h)
    hw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W//2-hw//2-30,20,W//2+hw//2+30,90], radius=30, fill="#FF3D3D")
    draw.text((W//2-hw//2,28),header,font=font_h,fill="#FFFFFF")

    # Parse OR from question
    parts = re.split(r'\bOR\b', question, flags=re.IGNORECASE)
    if len(parts) >= 2:
        opt_a = parts[0].replace("Would you rather","").replace("would you rather","").strip().strip("?")
        opt_b = " OR ".join(parts[1:]).strip().strip("?")
    else:
        opt_a = question[:len(question)//2]
        opt_b = question[len(question)//2:]

    font_opt = load_font(42, bold=True)
    def wrap(text, max_w):
        words = text.split(); lines=[]; cur=[]
        for w in words:
            test=" ".join(cur+[w])
            bb=draw.textbbox((0,0),test,font=font_opt)
            if bb[2]-bb[0]>max_w and cur: lines.append(" ".join(cur)); cur=[w]
            else: cur.append(w)
        if cur: lines.append(" ".join(cur))
        return lines

    # Option A (left)
    lines_a = wrap(opt_a, W//2-60)
    lh = 56
    ty = H//2 - len(lines_a)*lh//2
    for i,line in enumerate(lines_a):
        bbox = draw.textbbox((0,0),line,font=font_opt)
        tw = bbox[2]-bbox[0]
        draw.text((W//4-tw//2, ty+i*lh), line, font=font_opt, fill="#FFFFFF")

    # Option B (right)
    lines_b = wrap(opt_b, W//2-60)
    ty = H//2 - len(lines_b)*lh//2
    for i,line in enumerate(lines_b):
        bbox = draw.textbbox((0,0),line,font=font_opt)
        tw = bbox[2]-bbox[0]
        draw.text((W*3//4-tw//2, ty+i*lh), line, font=font_opt, fill="#1a0a3d")

    # Divider line
    draw.line([W//2,100,W//2,H-50], fill="#FFFFFF", width=3)

    return img

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found — run from inside a quiz folder"); return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    print(f"Generating {len(rows)} images locally (no API needed)...\n")
    
    for idx, row in enumerate(rows):
        fname = row.get("file_name","").strip()
        if not fname: continue
        
        out_path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(out_path):
            print(f"  ⏭  skip: {fname}"); continue
        
        asset_type = row.get("asset_type","").strip()
        
        try:
            if asset_type == "title_card":
                img = make_title_card(row, idx)
            else:
                img = make_question_scene(row, idx)
            
            img.save(out_path)
            print(f"  ✅  {fname}")
        except Exception as e:
            print(f"  ❌  {fname}: {e}")
    
    print(f"\n✅ Done! Images saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
