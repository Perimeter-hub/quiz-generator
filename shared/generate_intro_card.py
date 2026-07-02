#!/usr/bin/env python3
"""
Quiz Blitz — Intro Card Generator (Style 3: Big number + bold text)
Creates a bright 3-second intro screen prepended to the video.
Run from any quiz folder.
Usage: python3 ../shared/generate_intro_card.py
"""

import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720

QUIZ_CONFIGS = {
    "quiz1": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "US STATES",
        "line2":    "CAN YOU NAME THEM ALL?",
        "line3":    "BY CLUE ALONE?",
        "badge":    "ONLY 4% PASS!",
        "badge_bg": "#CC0000",
    },
    "quiz2": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "US STATES",
        "line2":    "CAN YOU NAME THEM ALL",
        "line3":    "BY SHAPE ALONE?",
        "badge":    "ONLY 4% PASS!",
        "badge_bg": "#3B6DFF",
    },
    "quiz3": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "FUSSBALL-FRAGEN",
        "line2":    "SCHAFFST DU ALLE",
        "line3":    "NUR EXPERTEN BESTEHEN!",
        "badge":    "NUR 3% SCHAFFEN ES!",
        "badge_bg": "#CC0000",
    },
    "quiz4": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "ICONIC TV SHOWS",
        "line2":    "CAN YOU NAME THEM ALL?",
        "line3":    "ONLY TRUE FANS PASS!",
        "badge":    "ONLY 5% SCORE 50/50!",
        "badge_bg": "#CC0000",
    },
    "quiz5": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "COUNTRY FLAGS",
        "line2":    "CAN YOU NAME THEM ALL?",
        "line3":    "ONLY GEOGRAPHY EXPERTS PASS!",
        "badge":    "ONLY 5% SCORE 50/50!",
        "badge_bg": "#CC0000",
    },
    "quiz6": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "30",
        "line1":    "WORLD CAPITALS",
        "line2":    "CAN YOU NAME THEM ALL?",
        "line3":    "ONLY TRUE EXPERTS PASS!",
        "badge":    "ONLY 4% SCORE 30/30!",
        "badge_bg": "#3B6DFF",
    },
    "quiz8": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "GUESS THE BRAND",
        "line2":    "CAN YOU NAME THEM ALL",
        "line3":    "BY EMOJI ALONE?",
        "badge":    "ONLY 5% SCORE 50/50!",
        "badge_bg": "#CC0000",
    },
    "quiz10": {
        "bg":       "#1A1A1A",
        "accent":   "#FFCC00",
        "number":   "50",
        "line1":    "GUESS THE SPORT",
        "line2":    "CAN YOU NAME THEM ALL",
        "line3":    "BY EMOJI ALONE?",
        "badge":    "ONLY 5% SCORE 50/50!",
        "badge_bg": "#3B6DFF",
    },
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

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

def center_text(draw, text, y, font, color, shadow=False):
    bb = draw.textbbox((0, 0), text, font=font)
    x = (W - (bb[2] - bb[0])) // 2
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=color)

def make_intro(config, out_path):
    bg = hex_to_rgb(config["bg"])
    acc = hex_to_rgb(config["accent"])
    badge_bg = hex_to_rgb(config["badge_bg"])

    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = bg
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    # Subtle grid lines
    gc = tuple(min(255, c + 18) for c in bg)
    for x in range(0, W, 80): draw.line([(x, 0), (x, H)], fill=gc, width=1)
    for y in range(0, H, 80): draw.line([(0, y), (W, y)], fill=gc, width=1)

    # Top label
    f_brand = load_font(34, bold=True)
    center_text(draw, "QUIZ BLITZ", 22, f_brand, acc)

    # BIG number
    f_num = load_font(240, bold=True)
    bb = draw.textbbox((0, 0), config["number"], font=f_num)
    nx = (W - (bb[2] - bb[0])) // 2
    # Shadow
    draw.text((nx+5, 63), config["number"], font=f_num, fill=(0, 0, 0))
    draw.text((nx, 60), config["number"], font=f_num, fill=acc)

    # Line 1 — white, bold
    f_lg = load_font(58, bold=True)
    center_text(draw, config["line1"], 318, f_lg, (255, 255, 255), shadow=True)

    # Divider line
    draw.rectangle([(W//2 - 200, 392), (W//2 + 200, 396)], fill=acc)

    # Line 2 — accent color
    f_md = load_font(46, bold=True)
    center_text(draw, config["line2"], 408, f_md, acc, shadow=True)

    # Line 3 — grey
    f_sm = load_font(34, bold=False)
    center_text(draw, config["line3"], 466, f_sm, (150, 150, 150))

    # Badge bottom right
    f_badge = load_font(28, bold=True)
    badge_text = config["badge"]
    bb_b = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw = bb_b[2] - bb_b[0]
    bx = W - bw - 48
    by = H - 56
    draw.rounded_rectangle([(bx - 12, by - 8), (bx + bw + 12, by + 36)],
                             radius=6, fill=badge_bg)
    draw.text((bx, by), badge_text, font=f_badge, fill=(255, 255, 255))

    img.save(out_path, "PNG")
    print(f"  ✓  Saved: {out_path}")
    return img


def prepend_to_video(intro_img, duration_sec=3):
    try:
        from moviepy import ImageSequenceClip, VideoFileClip, concatenate_videoclips
    except ImportError:
        os.system(f"{sys.executable} -m pip install moviepy -q")
        from moviepy import ImageSequenceClip, VideoFileClip, concatenate_videoclips

    FPS = 30
    folder_name = os.path.basename(os.path.abspath("."))

    # Find the video
    video_path = None
    for candidate in [f"{folder_name}.mp4", "quiz_video.mp4"]:
        if os.path.exists(candidate):
            video_path = candidate
            break

    if not video_path:
        print(f"  ✗  No video found. Run make_quiz_video.py first.")
        return

    print(f"  Loading: {video_path}")
    arr = np.array(intro_img)
    intro_clip = ImageSequenceClip([arr] * (duration_sec * FPS), fps=FPS)
    main_clip = VideoFileClip(video_path)

    # Match audio: intro is silent, main has music
    final = concatenate_videoclips([intro_clip, main_clip])

    out_path = f"{folder_name}_final.mp4"
    print(f"  Writing: {out_path}")
    final.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p"],
        logger=None,
    )
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\n  ✅  Done! → {out_path} ({size_mb:.1f} MB)")
    print(f"  First frame = YouTube thumbnail 🎯")
    print(f"  Upload this file to YouTube!")


def main():
    folder = os.path.basename(os.path.abspath("."))
    config = QUIZ_CONFIGS.get(folder)

    if not config:
        print(f"Quiz '{folder}' not recognized.")
        print(f"Available: {list(QUIZ_CONFIGS.keys())}")
        print("Add your quiz config to QUIZ_CONFIGS in this script.")
        return

    os.makedirs("images_and_videos", exist_ok=True)
    out_png = "images_and_videos/intro_card.png"

    print(f"Quiz Blitz — Intro Card Generator")
    print(f"Style: Big number + bold text")
    print(f"Quiz: {folder}\n")

    print("Step 1: Generating intro card...")
    intro_img = make_intro(config, out_png)

    print("\nStep 2: Prepending to video...")
    prepend_to_video(intro_img)


if __name__ == "__main__":
    main()
