#!/usr/bin/env python3
"""
Universal Quiz Video Generator v2
- Channel avatar watermark on every frame (bottom-left, circular)
- Bright finale screen with fireworks + subscribe CTA (replaces broken last question)
- Output named after quiz folder

Usage: python3 ../shared/make_quiz_video.py
Place avatar: shared/channel_avatar.png
"""

import csv, os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ── CONFIG ────────────────────────────────────────────────────────────────────
CSV_PATH    = "batch_generation_queue.csv"
IMAGES_DIR  = "images_and_videos"
AVATAR_PATH = "../shared/channel_avatar.png"   # shared across all quizzes
CHANNEL_NAME = "@QuizBlitzGo"
FPS         = 30
W, H        = 1280, 720

_folder  = os.path.basename(os.path.abspath("."))
OUTPUT   = f"{_folder}.mp4"

T_TITLE    = 4.0
T_QUESTION = 5.0
T_THINKING = 6.0
T_ANSWER   = 4.0
T_OUTRO    = 6.0
T_FINALE   = 8.0   # bright finale screen duration

MUSIC_QUESTION  = "music_question.mp3"
MUSIC_COUNTDOWN = "music_countdown.mp3"
MUSIC_ANSWER    = "music_answer.mp3"
VOL_QUESTION    = 0.4
VOL_COUNTDOWN   = 0.6
VOL_ANSWER      = 0.7

COL_Q_BAR  = (10,  20,  80,  185)
COL_A_BAR  = (10,  90,  20,  210)
COL_T_BAR  = (10,  10,  10,  170)
COL_WHITE  = (255, 255, 255)
COL_YELLOW = (255, 230,  50)
COL_CYAN   = (100, 230, 255)
# ─────────────────────────────────────────────────────────────────────────────

def load_font(size, bold=False):
    for p in [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'Bold' if bold else ''}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def wrap_text(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bb = draw.textbbox((0,0), test, font=font)
        if (bb[2]-bb[0]) > max_w and cur:
            lines.append(" ".join(cur)); cur = [w]
        else: cur.append(w)
    if cur: lines.append(" ".join(cur))
    return lines

def draw_bar(img, text, y_frac, bar_color, text_color, fsize=38, bold=True, pad=24):
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(fsize, bold)
    lines = wrap_text(text, font, W-80, draw)
    lh = fsize + 12
    bh = len(lines)*lh + pad*2
    by = int(y_frac*H) - bh//2
    by = max(4, min(H-bh-4, by))
    draw.rectangle([(0, by), (W, by+bh)], fill=bar_color)
    y = by + pad
    for line in lines:
        bb = draw.textbbox((0,0), line, font=font)
        x = (W-(bb[2]-bb[0]))//2
        draw.text((x, y), line, font=font, fill=text_color)
        y += lh
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def draw_countdown(img, sec):
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(60, bold=True)
    txt = str(sec)
    cx, cy, r = W-90, 90, 52
    draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=(0,0,0,190))
    bb = draw.textbbox((0,0), txt, font=font)
    draw.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-4), txt, font=font, fill=COL_YELLOW)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

# ── AVATAR WATERMARK ──────────────────────────────────────────────────────────
_avatar_cache = None

def get_avatar():
    global _avatar_cache
    if _avatar_cache is not None:
        return _avatar_cache
    size = 72
    if os.path.exists(AVATAR_PATH):
        av = Image.open(AVATAR_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
    else:
        # Fallback: draw purple circle with Q
        av = Image.new("RGBA", (size, size), (0,0,0,0))
        d = ImageDraw.Draw(av)
        d.ellipse([(0,0),(size-1,size-1)], fill=(100,30,180,220))
        f = load_font(28, bold=True)
        d.text((22, 18), "Q", font=f, fill=(255,220,0))

    # Circular mask
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([(0,0),(size-1,size-1)], fill=255)
    av.putalpha(mask)

    # White ring
    ring = Image.new("RGBA", (size+6, size+6), (0,0,0,0))
    ImageDraw.Draw(ring).ellipse([(0,0),(size+5,size+5)], fill=(255,255,255,200))
    ring.paste(av, (3,3), av)
    _avatar_cache = ring
    return _avatar_cache

def add_avatar(img):
    """Paste circular avatar watermark bottom-left."""
    av = get_avatar()
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    overlay.paste(av, (16, H - av.height - 16), av)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

# ── FINALE SCREEN ─────────────────────────────────────────────────────────────
def make_finale_frames(n_frames):
    """Generate n_frames of bright finale with animated fireworks + subscribe CTA."""
    frames = []
    rng = np.random.default_rng(42)

    # Firework burst positions (fixed so they look intentional)
    bursts = [
        (220, 200, (255, 80, 80)),
        (640, 150, (255, 220, 0)),
        (1060, 200, (80, 180, 255)),
        (380, 380, (0, 220, 120)),
        (900, 360, (255, 120, 255)),
        (640, 500, (255, 180, 0)),
    ]

    f_big  = load_font(90, bold=True)
    f_md   = load_font(52, bold=True)
    f_sm   = load_font(34, bold=True)
    f_sub  = load_font(44, bold=True)

    for fi in range(n_frames):
        t = fi / FPS  # seconds

        # Dark purple background
        arr = np.zeros((H, W, 3), dtype=np.uint8)
        arr[:, :] = [20, 5, 40]
        img = Image.fromarray(arr, "RGB").convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Animated firework particles
        for bx, by, col in bursts:
            phase = (t * 1.5 + bursts.index((bx,by,col)) * 0.4) % 2.0
            if phase < 1.2:
                n_particles = 20
                for p in range(n_particles):
                    angle = (2 * math.pi * p / n_particles)
                    speed = 120 + 60 * math.sin(p * 1.3)
                    r = speed * phase
                    px = bx + r * math.cos(angle)
                    py = by + r * math.sin(angle)
                    alpha = max(0, int(255 * (1 - phase / 1.2)))
                    size = max(1, int(4 * (1 - phase/1.5)))
                    c = col + (alpha,)
                    draw.ellipse([(px-size,py-size),(px+size,py+size)], fill=c)

        # Stars twinkling
        for i in range(30):
            sx = (i * 137 + 50) % W
            sy = (i * 97 + 80) % (H - 200)
            alpha = int(128 + 127 * math.sin(t * 3 + i))
            draw.ellipse([(sx-2,sy-2),(sx+2,sy+2)], fill=(255,255,255,alpha))

        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        # Central content
        # Glowing "QUIZ COMPLETE!" 
        pulse = int(220 + 35 * math.sin(t * 4))
        center_y = 200

        # Shadow
        bb = draw.textbbox((0,0), "QUIZ COMPLETE!", font=f_big)
        tx = (W-(bb[2]-bb[0]))//2
        draw.text((tx+3, center_y+3), "QUIZ COMPLETE!", font=f_big, fill=(0,0,0))
        draw.text((tx, center_y), "QUIZ COMPLETE!", font=f_big, fill=(pulse, pulse, 50))

        # Score line
        bb2 = draw.textbbox((0,0), "How many did you get right?", font=f_md)
        tx2 = (W-(bb2[2]-bb2[0]))//2
        draw.text((tx2, 310), "How many did you get right?", font=f_md, fill=(200,200,255))

        # Score prompt box
        draw.rounded_rectangle([(W//2-280, 375),(W//2+280, 445)],
                                radius=12, fill=(50,20,90))
        bb3 = draw.textbbox((0,0), "Drop your score in the comments! 👇", font=f_sm)
        tx3 = (W-(bb3[2]-bb3[0]))//2
        draw.text((tx3, 393), "Drop your score in the comments! 👇", font=f_sm, fill=(255,230,100))

        # Subscribe CTA — pulsing
        sub_alpha = int(200 + 55 * math.sin(t * 5))
        draw.rounded_rectangle([(W//2-340, 475),(W//2+340, 555)],
                                radius=16, fill=(200,20,20))
        bb4 = draw.textbbox((0,0), f"🔔 SUBSCRIBE → {CHANNEL_NAME}", font=f_sub)
        tx4 = (W-(bb4[2]-bb4[0]))//2
        draw.text((tx4+2, 494), f"🔔 SUBSCRIBE → {CHANNEL_NAME}", font=f_sub, fill=(0,0,0))
        draw.text((tx4, 492), f"🔔 SUBSCRIBE → {CHANNEL_NAME}", font=f_sub, fill=(255,255,255))

        # Avatar bottom-left
        img = add_avatar(img)
        frames.append(np.array(img))

    return frames

# ─────────────────────────────────────────────────────────────────────────────

def load_base(img_path):
    if os.path.exists(img_path):
        return Image.open(img_path).convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:,:] = [15, 20, 50]
    return Image.fromarray(arr)

def make_segments(row):
    img_path = os.path.join(IMAGES_DIR, row["file_name"])
    atype    = row["asset_type"]
    qtext    = row["question_text"].strip()
    answer   = row["answer"].strip()
    qnum     = row["question_number"].strip()
    base     = load_base(img_path)
    segs     = []

    if atype == "title_card":
        img = draw_bar(base, qtext, 0.88, COL_T_BAR, COL_WHITE, fsize=44, bold=True) if qtext else base.copy()
        img = add_avatar(img)
        segs.append((img, T_TITLE, "title"))

    elif atype == "question_scene":
        img_q = base.copy()
        if qnum:
            img_q = draw_bar(img_q, f"Q{qnum}", 0.10, (0,0,60,160), COL_CYAN, fsize=26, bold=False, pad=10)
        img_q = draw_bar(img_q, qtext, 0.82, COL_Q_BAR, COL_WHITE, fsize=36, bold=True)
        img_q = add_avatar(img_q)
        segs.append((img_q, T_QUESTION, "question"))

        for s in range(int(T_THINKING), 0, -1):
            segs.append((draw_countdown(add_avatar(img_q.copy()), s), 1.0, "countdown"))

        img_a = base.copy()
        if qnum:
            img_a = draw_bar(img_a, f"Q{qnum}", 0.10, (0,0,60,160), COL_CYAN, fsize=26, bold=False, pad=10)
        img_a = draw_bar(img_a, qtext,          0.55, COL_Q_BAR, COL_WHITE, fsize=30, bold=False)
        img_a = draw_bar(img_a, f"✓  {answer}", 0.80, COL_A_BAR, COL_YELLOW, fsize=46, bold=True)
        img_a = add_avatar(img_a)
        segs.append((img_a, T_ANSWER, "answer"))

    elif atype == "outro":
        # Replace outro with animated finale
        return None  # Signal to use animated finale instead

    return segs


def loop_audio(clip, duration):
    from moviepy import concatenate_audioclips
    if clip.duration >= duration:
        return clip.subclipped(0, duration)
    loops = int(duration / clip.duration) + 2
    return concatenate_audioclips([clip] * loops).subclipped(0, duration)


def build_audio_track(segments_with_music, total_frames):
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
        import moviepy.audio.fx as afx

        has_q  = os.path.exists(MUSIC_QUESTION)
        has_cd = os.path.exists(MUSIC_COUNTDOWN)
        has_an = os.path.exists(MUSIC_ANSWER)

        if not any([has_q, has_cd, has_an]):
            print("  ℹ  No music files — silent video")
            return None

        print("  🎵 Music files found:")
        if has_q:  print(f"     ✓ {MUSIC_QUESTION}")
        if has_cd: print(f"     ✓ {MUSIC_COUNTDOWN}")
        if has_an: print(f"     ✓ {MUSIC_ANSWER}")

        clips_cache = {}
        if has_q:
            c = AudioFileClip(MUSIC_QUESTION)
            clips_cache["question"] = c.with_effects([afx.MultiplyVolume(VOL_QUESTION)])
            clips_cache["title"]    = c.with_effects([afx.MultiplyVolume(0.25)])
            clips_cache["finale"]   = c.with_effects([afx.MultiplyVolume(0.8)])
        if has_cd:
            clips_cache["countdown"] = AudioFileClip(MUSIC_COUNTDOWN).with_effects([afx.MultiplyVolume(VOL_COUNTDOWN)])
        if has_an:
            clips_cache["answer"] = AudioFileClip(MUSIC_ANSWER).with_effects([afx.MultiplyVolume(VOL_ANSWER)])

        audio_clips = []
        current_time = 0.0
        for img, dur, tag in segments_with_music:
            base_clip = clips_cache.get(tag)
            if base_clip is not None:
                segment = loop_audio(base_clip, dur).with_start(current_time)
                audio_clips.append(segment)
            current_time += dur

        return CompositeAudioClip(audio_clips) if audio_clips else None

    except Exception as e:
        print(f"  ⚠  Audio build failed: {e}")
        return None


def main():
    try:
        from moviepy import ImageSequenceClip
    except ImportError:
        os.system(f"{sys.executable} -m pip install moviepy pillow -q")
        from moviepy import ImageSequenceClip

    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found. Run from inside a quiz folder.")
        sys.exit(1)
    if not os.path.isdir(IMAGES_DIR):
        print(f"ERROR: '{IMAGES_DIR}/' not found. Run generate_images.py first.")
        sys.exit(1)

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} assets")
    print(f"Output: {OUTPUT}")
    print(f"Avatar: {'✓ found' if os.path.exists(AVATAR_PATH) else '✗ not found (using fallback)'}\n")

    missing = [r["file_name"] for r in rows
               if not os.path.exists(os.path.join(IMAGES_DIR, r["file_name"]))]
    if missing:
        print(f"⚠  {len(missing)} images missing (dark placeholder)")
        for m in missing[:5]: print(f"   ✗ {m}")
        print()
    else:
        print(f"✓  All images found\n")

    print("Building frames...")
    all_segments = []
    all_frames   = []
    has_outro    = False

    for i, row in enumerate(rows, 1):
        if row["asset_type"] == "outro":
            has_outro = True
            print(f"  [{i:2d}/{len(rows)}] {row['asset_id']} → replaced with animated finale")
            continue  # Will add finale at end

        segs = make_segments(row)
        if segs:
            for img, dur, tag in segs:
                all_segments.append((img, dur, tag))
                arr = np.array(img)
                n = max(1, round(dur * FPS))
                all_frames.extend([arr] * n)
        print(f"  [{i:2d}/{len(rows)}] {row['asset_id']}")

    # Add animated finale
    print(f"\n  🎆 Generating animated finale ({T_FINALE}s)...")
    n_finale = round(T_FINALE * FPS)
    finale_frames = make_finale_frames(n_finale)
    all_frames.extend(finale_frames)
    # Add finale segment info for audio
    all_segments.append((None, T_FINALE, "finale"))

    total_sec = len(all_frames) / FPS
    print(f"\nFrames: {len(all_frames)} = {total_sec/60:.1f} min")

    print("\nBuilding audio track...")
    audio = build_audio_track(all_segments, len(all_frames))

    print(f"\nWriting {OUTPUT}...")
    clip = ImageSequenceClip(all_frames, fps=FPS)
    if audio:
        clip = clip.with_audio(audio)
        print("  🎵 Audio attached")
    else:
        print("  🔇 Silent")

    clip.write_videofile(
        OUTPUT,
        codec="libx264",
        audio_codec="aac" if audio else None,
        ffmpeg_params=["-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n✅  Done! → {OUTPUT} ({size_mb:.1f} MB)")
    print(f"   🎆 Animated finale with fireworks")
    print(f"   👤 Avatar watermark on every frame")
    print(f"   🔔 Subscribe CTA: {CHANNEL_NAME}")

if __name__ == "__main__":
    main()
