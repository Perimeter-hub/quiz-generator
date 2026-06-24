#!/usr/bin/env python3
"""
Quiz Blitz — Thumbnail Generator
Generates 1280x720px YouTube thumbnails for all 4 quizzes.
Usage: python3 generate_thumbnails.py
Run from the quiz-generator/ root folder.
Output: thumbnails/ folder with 4 PNG files ready to upload to YouTube.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 720
OUT = "thumbnails"

def load_font(size, bold=False):
    candidates = [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def center_text(draw, text, y, font, color, max_w=W-80):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2] - bb[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bb[3] - bb[1]  # return height

def draw_stripe(img, color, y, height):
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, y), (W, y+height)], fill=color)

def draw_badge(draw, text, cx, y, bg, fg, font):
    bb = draw.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad_x, pad_y = 20, 10
    x = cx - (tw + pad_x*2)//2
    draw.rounded_rectangle([(x, y), (x+tw+pad_x*2, y+th+pad_y*2)], radius=8, fill=bg)
    draw.text((x+pad_x, y+pad_y), text, font=font, fill=fg)
    return tw + pad_x*2

def make_quiz1():
    img = Image.new("RGB", (W, H), "#CC0000")
    draw = ImageDraw.Draw(img)
    # Diagonal pattern
    for i in range(-H, W+H, 30):
        draw.line([(i, 0), (i+H, H)], fill="#B50000", width=15)
    # Top label
    f_sm = load_font(36, bold=True)
    f_lg = load_font(120, bold=True)
    f_md = load_font(52, bold=True)
    center_text(draw, "QUIZ BLITZ", 60, f_sm, "#FFCC00")
    # Main text
    center_text(draw, "CAN YOU NAME", 170, f_lg, "#FFFFFF")
    center_text(draw, "ALL 50 STATES?", 300, f_lg, "#FFEE00")
    # Bottom line
    draw.rectangle([(0, H-80), (W, H)], fill="#000000")
    center_text(draw, "50 QUESTIONS  •  6 SECONDS EACH  •  TEST YOUR KNOWLEDGE!", H-60, f_sm, "#FFCC00")
    # Flag emoji area
    draw.rectangle([(W-140, 0), (W, 140)], fill="#FFFFFF")
    draw.rectangle([(W-140, 0), (W, 50)], fill="#CC0000")
    draw.rectangle([(W-140, 90), (W, 140)], fill="#CC0000")
    img.save(f"{OUT}/thumbnail_quiz1_50states.png")
    print("  ✓ thumbnail_quiz1_50states.png")

def make_quiz2():
    img = Image.new("RGB", (W, H), "#0A0F2E")
    draw = ImageDraw.Draw(img)
    # Grid lines
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill="#0D1440", width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill="#0D1440", width=1)
    # Draw a stylized Texas shape (simplified polygon)
    texas = [(640,120),(760,120),(760,280),(820,280),(820,380),(720,440),(680,520),(620,480),(560,520),(500,440),(500,200),(580,200),(580,120)]
    draw.polygon(texas, fill="#3B6DFF", outline="#FFFFFF")
    # Question mark overlay hint
    f_lg = load_font(110, bold=True)
    f_md = load_font(58, bold=True)
    f_sm = load_font(38, bold=True)
    draw.text((620, 270), "?", font=f_lg, fill=(255,255,255,180))
    # Left side text
    center_text(draw, "GUESS THE", 160, f_md, "#FFFFFF")
    center_text(draw, "US STATE", 230, f_lg, "#3B6DFF")
    center_text(draw, "BY ITS SHAPE!", 370, f_md, "#FFEE00")
    draw.rectangle([(0, H-80), (W, H)], fill="#3B6DFF")
    center_text(draw, "50 STATES  •  5 ROUNDS  •  CAN YOU GET 50/50?", H-60, f_sm, "#FFFFFF")
    img.save(f"{OUT}/thumbnail_quiz2_shapes.png")
    print("  ✓ thumbnail_quiz2_shapes.png")

def make_quiz3():
    img = Image.new("RGB", (W, H), "#000000")
    draw = ImageDraw.Draw(img)
    # German flag stripes
    draw.rectangle([(0, 0), (W, H//3)], fill="#000000")
    draw.rectangle([(0, H//3), (W, 2*H//3)], fill="#CC0000")
    draw.rectangle([(0, 2*H//3), (W, H)], fill="#FFCC00")
    # Dark overlay for readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    f_sm = load_font(36, bold=True)
    f_md = load_font(62, bold=True)
    f_lg = load_font(96, bold=True)
    center_text(draw, "QUIZ BLITZ", 55, f_sm, "#FFCC00")
    center_text(draw, "KENNST DU DEN", 150, f_md, "#FFFFFF")
    center_text(draw, "DEUTSCHEN", 230, f_lg, "#FFCC00")
    center_text(draw, "FUSSBALL?", 340, f_lg, "#FFFFFF")
    # Football
    ball_x, ball_y, ball_r = W-160, H//2-30, 100
    draw.ellipse([(ball_x-ball_r, ball_y-ball_r), (ball_x+ball_r, ball_y+ball_r)],
                 fill="#FFFFFF", outline="#000000", width=3)
    # Pentagons on ball
    for cx, cy in [(ball_x, ball_y), (ball_x-50, ball_y-30), (ball_x+50, ball_y-30),
                   (ball_x-50, ball_y+30), (ball_x+50, ball_y+30)]:
        r = 22
        pts = [(cx+r*__import__('math').cos(a*3.14159/2.5-3.14159/2),
                cy+r*__import__('math').sin(a*3.14159/2.5-3.14159/2)) for a in range(5)]
        draw.polygon(pts, fill="#000000")
    draw.rectangle([(0, H-80), (W, H)], fill="#CC0000")
    center_text(draw, "50 FRAGEN  •  NUR FUR ECHTE EXPERTEN!", H-60, f_sm, "#FFFFFF")
    img.save(f"{OUT}/thumbnail_quiz3_football.png")
    print("  ✓ thumbnail_quiz3_football.png")

def make_quiz4():
    img = Image.new("RGB", (W, H), "#1A1A1A")
    draw = ImageDraw.Draw(img)
    # TV screen frames in background
    for pos, col in [((30,80,280,220), "#CC0000"), ((320,40,570,180), "#1E5FA5"),
                     ((610,80,860,220), "#CC7700"), ((900,40,1150,180), "#006600"),
                     ((100,260,350,400), "#8800CC"), ((390,300,640,440), "#CC0000"),
                     ((680,260,930,400), "#1E5FA5"), ((970,300,1220,440), "#CC7700")]:
        x1,y1,x2,y2 = pos
        draw.rounded_rectangle([(x1,y1),(x2,y2)], radius=12, fill=col, outline="#333333")
        draw.rounded_rectangle([(x1+8,y1+8),(x2-8,y2-8)], radius=8, fill="#000000")
    f_sm = load_font(36, bold=True)
    f_md = load_font(62, bold=True)
    f_lg = load_font(90, bold=True)
    # Dark center band
    draw.rectangle([(0, 460), (W, H)], fill="#000000")
    draw.rectangle([(40, 430), (W-40, 700)], fill="#000000")
    center_text(draw, "CAN YOU NAME THESE", 445, f_md, "#FFFFFF")
    center_text(draw, "ICONIC TV SHOWS?", 530, f_lg, "#CC0000")
    # Show badges
    badges = ["FRIENDS", "BREAKING BAD", "SEINFELD", "THE OFFICE"]
    bx = 160
    for b in badges:
        f_b = load_font(28, bold=True)
        bb = draw.textbbox((0,0), b, font=f_b)
        bw = bb[2]-bb[0]+24
        draw.rounded_rectangle([(bx, 648), (bx+bw, 692)], radius=6, fill="#CC0000")
        draw.text((bx+12, 651), b, font=f_b, fill="#FFFFFF")
        bx += bw + 12
    img.save(f"{OUT}/thumbnail_quiz4_tvshows.png")
    print("  ✓ thumbnail_quiz4_tvshows.png")

def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"Generating 4 thumbnails (1280x720) → ./{OUT}/\n")
    make_quiz1()
    make_quiz2()
    make_quiz3()
    make_quiz4()
    print(f"\nDone! Upload these to YouTube Studio when publishing each video.")
    print(f"Path: {os.path.abspath(OUT)}/")

if __name__ == "__main__":
    main()
