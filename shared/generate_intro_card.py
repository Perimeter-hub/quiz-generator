#!/usr/bin/env python3
"""
Quiz Blitz — Intro Card Generator
Creates a bright 3-second intro screen to use as YouTube thumbnail (first frame).
Run from any quiz folder.
Usage: python3 ../shared/generate_intro_card.py
"""

import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720

QUIZ_CONFIGS = {
    "quiz1": {
        "bg": "#CC0000",
        "accent": "#FFCC00",
        "line1": "CAN YOU NAME",
        "line2": "ALL 50 STATES?",
        "emoji": "🗺️",
        "sub": "50 QUESTIONS • 6 SECONDS EACH",
    },
    "quiz2": {
        "bg": "#0A0F2E",
        "accent": "#3B6DFF",
        "line1": "GUESS THE STATE",
        "line2": "BY ITS SHAPE!",
        "emoji": "🔷",
        "sub": "50 STATES • CAN YOU GET 50/50?",
    },
    "quiz3": {
        "bg": "#006400",
        "accent": "#FFCC00",
        "line1": "KENNST DU DEN",
        "line2": "DEUTSCHEN FUSSBALL?",
        "emoji": "⚽",
        "sub": "50 FRAGEN • NUR FÜR EXPERTEN!",
    },
    "quiz4": {
        "bg": "#1A1A1A",
        "accent": "#CC0000",
        "line1": "CAN YOU NAME THESE",
        "line2": "ICONIC TV SHOWS?",
        "emoji": "📺",
        "sub": "50 SHOWS • ONLY TRUE FANS PASS!",
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

def make_intro(config, out_path):
    bg_rgb = hex_to_rgb(config["bg"])
    acc_rgb = hex_to_rgb(config["accent"])

    # Base background
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = bg_rgb
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    # Diagonal stripes for energy
    stripe_color = tuple(min(255, c + 20) for c in bg_rgb)
    for i in range(-H, W + H, 40):
        draw.line([(i, 0), (i + H, H)], fill=stripe_color, width=20)

    # Top bar
    draw.rectangle([(0, 0), (W, 90)], fill=acc_rgb)

    # QUIZ BLITZ label in top bar
    f_brand = load_font(52, bold=True)
    bb = draw.textbbox((0,0), "QUIZ BLITZ", font=f_brand)
    draw.text(((W - (bb[2]-bb[0])) // 2, 18), "QUIZ BLITZ", font=f_brand, fill=bg_rgb)

    # Main lines
    f_lg = load_font(118, bold=True)
    f_md = load_font(90, bold=True)

    # Line 1
    bb1 = draw.textbbox((0,0), config["line1"], font=f_lg)
    draw.text(((W - (bb1[2]-bb1[0])) // 2, 130), config["line1"], font=f_lg, fill=(255,255,255))

    # Line 2 in accent color
    bb2 = draw.textbbox((0,0), config["line2"], font=f_md)
    x2 = (W - (bb2[2]-bb2[0])) // 2
    # Shadow
    draw.text((x2+3, 263), config["line2"], font=f_md, fill=(0,0,0))
    draw.text((x2, 260), config["line2"], font=f_md, fill=acc_rgb)

    # Bottom bar
    draw.rectangle([(0, H-90), (W, H)], fill=acc_rgb)
    f_sub = load_font(40, bold=True)
    bb_sub = draw.textbbox((0,0), config["sub"], font=f_sub)
    draw.text(((W - (bb_sub[2]-bb_sub[0])) // 2, H-70), config["sub"], font=f_sub, fill=bg_rgb)

    # Decorative circles
    for cx, cy, r, alpha in [(100, H//2, 80, 30), (W-100, H//2, 80, 30),
                               (200, H//2, 40, 20), (W-200, H//2, 40, 20)]:
        overlay = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([(cx-r, cy-r), (cx+r, cy+r)],
                   outline=acc_rgb + (alpha,), width=4)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    img.save(out_path, "PNG")
    print(f"  ✓  {out_path}")
    return img


def prepend_to_video(intro_img, quiz_folder, duration_sec=3):
    """Prepend intro frames to existing quiz video."""
    try:
        from moviepy import ImageSequenceClip, VideoFileClip, concatenate_videoclips
    except ImportError:
        print("Installing moviepy...")
        os.system(f"{sys.executable} -m pip install moviepy -q")
        from moviepy import ImageSequenceClip, VideoFileClip, concatenate_videoclips

    FPS = 30
    folder_name = os.path.basename(os.path.abspath(quiz_folder))
    video_path = os.path.join(quiz_folder, f"{folder_name}.mp4")

    if not os.path.exists(video_path):
        # Try quiz_video.mp4 fallback
        video_path = os.path.join(quiz_folder, "quiz_video.mp4")
        if not os.path.exists(video_path):
            print(f"  ✗  Video not found in {quiz_folder}")
            return

    print(f"  Loading: {video_path}")
    arr = np.array(intro_img)
    n_frames = duration_sec * FPS
    intro_clip = ImageSequenceClip([arr] * n_frames, fps=FPS)

    main_clip = VideoFileClip(video_path)

    # Carry audio from main clip
    final = concatenate_videoclips([intro_clip, main_clip])

    out_path = video_path.replace(".mp4", "_with_intro.mp4")
    print(f"  Writing: {out_path}")
    final.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p"],
        logger=None,
    )
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"  ✅  Done! → {os.path.basename(out_path)} ({size_mb:.1f} MB)")
    print(f"  First frame = YouTube thumbnail 🎯")


def main():
    folder = os.path.basename(os.path.abspath("."))
    config = QUIZ_CONFIGS.get(folder)

    if not config:
        print(f"Quiz '{folder}' not in config. Available: {list(QUIZ_CONFIGS.keys())}")
        print("Add your quiz config to QUIZ_CONFIGS in this script.")
        return

    os.makedirs("images_and_videos", exist_ok=True)
    out_png = "images_and_videos/intro_card.png"

    print(f"Quiz Blitz — Intro Card Generator")
    print(f"Quiz: {folder}\n")

    print("Step 1: Generating intro card...")
    intro_img = make_intro(config, out_png)

    print("\nStep 2: Prepending to video...")
    prepend_to_video(intro_img, ".")

    print(f"\nDone! Upload *_with_intro.mp4 to YouTube.")
    print(f"The first frame will automatically be the thumbnail preview.")


if __name__ == "__main__":
    main()
