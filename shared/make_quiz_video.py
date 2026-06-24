#!/usr/bin/env python3
"""
Universal Quiz Video Generator — with background music support
Works for any quiz folder containing:
  batch_generation_queue.csv
  images_and_videos/
  music_question.mp3   (optional — background during question)
  music_countdown.mp3  (optional — tension during countdown)
  music_answer.mp3     (optional — reveal fanfare)

Usage: python make_quiz_video.py
Output: quiz_video.mp4
"""

import csv, os, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── CONFIG ────────────────────────────────────────────────────────────────────
CSV_PATH    = "batch_generation_queue.csv"
IMAGES_DIR  = "images_and_videos"
OUTPUT      = "quiz_video.mp4"
FPS         = 30
W, H        = 1280, 720

# Timings (seconds)
T_TITLE     = 4.0
T_QUESTION  = 5.0
T_THINKING  = 6.0
T_ANSWER    = 4.0
T_OUTRO     = 6.0

# Music files (optional — place in same folder as this script)
MUSIC_QUESTION  = "music_question.mp3"
MUSIC_COUNTDOWN = "music_countdown.mp3"
MUSIC_ANSWER    = "music_answer.mp3"

# Volume levels (0.0 - 1.0)
VOL_QUESTION  = 0.4
VOL_COUNTDOWN = 0.6
VOL_ANSWER    = 0.7

# Colors
COL_Q_BAR  = (10,  20,  80,  185)
COL_A_BAR  = (10,  90,  20,  210)
COL_T_BAR  = (10,  10,  10,  170)
COL_WHITE  = (255, 255, 255)
COL_YELLOW = (255, 230,  50)
COL_CYAN   = (100, 230, 255)
# ─────────────────────────────────────────────────────────────────────────────

def load_font(size, bold=False):
    candidates = [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'Bold' if bold else ''}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def wrap_text(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bb = draw.textbbox((0, 0), test, font=font)
        if (bb[2] - bb[0]) > max_w and cur:
            lines.append(" ".join(cur)); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(" ".join(cur))
    return lines

def draw_bar(img, text, y_frac, bar_color, text_color, fsize=38, bold=True, pad=24):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(fsize, bold)
    lines = wrap_text(text, font, W - 80, draw)
    lh = fsize + 12
    bh = len(lines) * lh + pad * 2
    by = int(y_frac * H) - bh // 2
    by = max(4, min(H - bh - 4, by))
    draw.rectangle([(0, by), (W, by + bh)], fill=bar_color)
    y = by + pad
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=font, fill=text_color)
        y += lh
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def draw_countdown(img, sec):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(60, bold=True)
    txt = str(sec)
    cx, cy, r = W - 90, 90, 52
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(0, 0, 0, 190))
    bb = draw.textbbox((0, 0), txt, font=font)
    draw.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-4), txt, font=font, fill=COL_YELLOW)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def load_base(img_path):
    if os.path.exists(img_path):
        return Image.open(img_path).convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = [20, 20, 60]
    return Image.fromarray(arr)

def make_segments(row):
    """Returns list of (PIL.Image, duration_sec, music_tag) tuples.
    music_tag: 'question' | 'countdown' | 'answer' | 'title' | None
    """
    img_path = os.path.join(IMAGES_DIR, row["file_name"])
    atype    = row["asset_type"]
    qtext    = row["question_text"].strip()
    answer   = row["answer"].strip()
    qnum     = row["question_number"].strip()
    base     = load_base(img_path)
    segs     = []

    if atype == "title_card":
        img = draw_bar(base, qtext, 0.88, COL_T_BAR, COL_WHITE, fsize=44, bold=True) if qtext else base.copy()
        segs.append((img, T_TITLE, "title"))

    elif atype == "question_scene":
        # Phase 1: question
        img_q = base.copy()
        if qnum:
            img_q = draw_bar(img_q, f"Q{qnum}", 0.10, (0,0,60,160), COL_CYAN, fsize=26, bold=False, pad=10)
        img_q = draw_bar(img_q, qtext, 0.82, COL_Q_BAR, COL_WHITE, fsize=36, bold=True)
        segs.append((img_q, T_QUESTION, "question"))

        # Phase 2: countdown (1 sec per tick)
        for s in range(int(T_THINKING), 0, -1):
            segs.append((draw_countdown(img_q, s), 1.0, "countdown"))

        # Phase 3: answer reveal
        img_a = base.copy()
        if qnum:
            img_a = draw_bar(img_a, f"Q{qnum}", 0.10, (0,0,60,160), COL_CYAN, fsize=26, bold=False, pad=10)
        img_a = draw_bar(img_a, qtext,          0.55, COL_Q_BAR, COL_WHITE, fsize=30, bold=False)
        img_a = draw_bar(img_a, f"✓  {answer}", 0.80, COL_A_BAR, COL_YELLOW, fsize=46, bold=True)
        segs.append((img_a, T_ANSWER, "answer"))

    elif atype == "outro":
        img = draw_bar(base, qtext, 0.88, COL_T_BAR, COL_WHITE, fsize=34, bold=True) if qtext else base.copy()
        segs.append((img, T_OUTRO, "title"))

    return segs


def load_music_clip(path, duration, volume):
    """Load and prepare a music clip for given duration."""
    try:
        from moviepy import AudioFileClip
        if not os.path.exists(path):
            return None
        clip = AudioFileClip(path).with_effects(
            [__import__('moviepy.audio.fx', fromlist=['MultiplyVolume']).MultiplyVolume(volume)]
        )
        # Loop if needed
        if clip.duration < duration:
            loops = int(duration / clip.duration) + 1
            from moviepy import concatenate_audioclips
            clip = concatenate_audioclips([clip] * loops)
        return clip.subclipped(0, duration)
    except Exception as e:
        print(f"  ⚠  Music load failed ({path}): {e}")
        return None


def loop_audio(clip, duration):
    """Loop an audio clip to fill the required duration."""
    from moviepy import concatenate_audioclips
    if clip.duration >= duration:
        return clip.subclipped(0, duration)
    loops = int(duration / clip.duration) + 2
    return concatenate_audioclips([clip] * loops).subclipped(0, duration)


def build_audio_track(segments_with_music):
    """Build composite audio track — loads each MP3 only once to avoid 'too many open files'."""
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
        import moviepy.audio.fx as afx

        has_q  = os.path.exists(MUSIC_QUESTION)
        has_cd = os.path.exists(MUSIC_COUNTDOWN)
        has_an = os.path.exists(MUSIC_ANSWER)

        if not any([has_q, has_cd, has_an]):
            print("  ℹ  No music files found — building silent video")
            return None

        print("  🎵 Music files found:")
        if has_q:  print(f"     ✓ {MUSIC_QUESTION}")
        if has_cd: print(f"     ✓ {MUSIC_COUNTDOWN}")
        if has_an: print(f"     ✓ {MUSIC_ANSWER}")

        # Load each file ONCE and apply volume — key fix for 'too many open files'
        clips_cache = {}
        if has_q:
            c = AudioFileClip(MUSIC_QUESTION)
            clips_cache["question"] = c.with_effects([afx.MultiplyVolume(VOL_QUESTION)])
            clips_cache["title"]    = c.with_effects([afx.MultiplyVolume(0.25)])
        if has_cd:
            c = AudioFileClip(MUSIC_COUNTDOWN)
            clips_cache["countdown"] = c.with_effects([afx.MultiplyVolume(VOL_COUNTDOWN)])
        if has_an:
            c = AudioFileClip(MUSIC_ANSWER)
            clips_cache["answer"] = c.with_effects([afx.MultiplyVolume(VOL_ANSWER)])

        # Build one segment per phase, placed at the right time offset
        audio_clips = []
        current_time = 0.0

        for img, dur, tag in segments_with_music:
            base_clip = clips_cache.get(tag)
            if base_clip is not None:
                segment = loop_audio(base_clip, dur).with_start(current_time)
                audio_clips.append(segment)
            current_time += dur

        if not audio_clips:
            return None

        return CompositeAudioClip(audio_clips)

    except Exception as e:
        print(f"  ⚠  Audio build failed: {e}")
        return None


def main():
    try:
        from moviepy import ImageSequenceClip, CompositeAudioClip
    except ImportError:
        print("Installing moviepy...")
        os.system(f"{sys.executable} -m pip install moviepy pillow -q")
        from moviepy import ImageSequenceClip

    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found.")
        sys.exit(1)

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} assets\n")

    missing = [r["file_name"] for r in rows
               if not os.path.exists(os.path.join(IMAGES_DIR, r["file_name"]))]
    if missing:
        print(f"⚠  {len(missing)} missing images (color fallback)")

    print("Building frames...")
    all_segments = []
    all_frames   = []

    for i, row in enumerate(rows, 1):
        segs = make_segments(row)
        for img, dur, tag in segs:
            all_segments.append((img, dur, tag))
            arr = np.array(img)
            n = max(1, round(dur * FPS))
            all_frames.extend([arr] * n)
        print(f"  [{i:2d}/{len(rows)}] {row['asset_id']}")

    total_sec = len(all_frames) / FPS
    print(f"\nFrames: {len(all_frames)} = {total_sec/60:.1f} min")

    # Build audio
    print("\nBuilding audio track...")
    audio = build_audio_track(all_segments)

    # Build video
    print(f"\nWriting {OUTPUT}...")
    from moviepy import ImageSequenceClip
    clip = ImageSequenceClip(all_frames, fps=FPS)

    if audio:
        clip = clip.with_audio(audio)
        print("  🎵 Audio track attached")
    else:
        print("  🔇 No audio (silent video)")

    clip.write_videofile(
        OUTPUT,
        codec="libx264",
        audio_codec="aac" if audio else None,
        ffmpeg_params=["-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n✅  Done! → {OUTPUT}  ({size_mb:.1f} MB)")
    if audio:
        print("    🎵 With background music")
    else:
        print("    🔇 Silent — add music files and re-run to enable audio")


if __name__ == "__main__":
    main()
