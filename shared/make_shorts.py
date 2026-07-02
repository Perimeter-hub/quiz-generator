#!/usr/bin/env python3
"""
Quiz Blitz — YouTube Shorts Generator
Converts the first N questions of a quiz into a punchy vertical (9:16) Short.
Fast pace, big bold hook, quick countdown, strong CTA to watch the full quiz.

Usage: python3 ../shared/make_shorts.py
Run from inside a quiz folder (same one used for make_quiz_video.py).
Output: <folder>_short.mp4  (9:16, ~45-60 sec)
"""

import csv, os, sys, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── CONFIG ────────────────────────────────────────────────────────────────────
CSV_PATH    = "batch_generation_queue.csv"
IMAGES_DIR  = "images_and_videos"
AVATAR_PATH = "../shared/channel_avatar.png"
CHANNEL_NAME = "@QuizBlitzGo"
FPS         = 30
W, H        = 1080, 1920          # 9:16 vertical

N_QUESTIONS = 5                    # how many questions go into the Short
T_HOOK      = 2.5                  # opening hook card
T_QUESTION  = 3.0                  # faster than long-form (was 5.0)
T_THINKING  = 3.0                  # faster countdown (was 6.0)
T_ANSWER    = 2.0                  # snappier reveal (was 4.0)
T_CTA       = 4.0                  # end card — "watch full quiz"

MUSIC_QUESTION  = "music_question.mp3"
MUSIC_COUNTDOWN = "music_countdown.mp3"
MUSIC_ANSWER    = "music_answer.mp3"
VOL_QUESTION    = 0.45
VOL_COUNTDOWN   = 0.65
VOL_ANSWER      = 0.75

COL_Q_BAR  = (10,  20,  80,  200)
COL_A_BAR  = (10,  90,  20,  220)
COL_HOOK   = (0, 0, 0, 0)
COL_WHITE  = (255, 255, 255)
COL_YELLOW = (255, 230,  50)
COL_CYAN   = (100, 230, 255)

_folder = os.path.basename(os.path.abspath("."))
OUTPUT  = f"{_folder}_short.mp4"

# Same CLEAN_STYLE list as make_quiz_video.py
CLEAN_STYLE = _folder in ("quiz2", "quiz5", "quiz6", "quiz7", "quiz8", "quiz9", "quiz10")

# Hook lines per quiz — the crucial first 1.5 seconds that stop the scroll
HOOK_LINES = {
    "quiz1":  ("CAN YOU NAME", "ALL 50 STATES?"),
    "quiz2":  ("GUESS THE STATE", "BY SHAPE!"),
    "quiz3":  ("FUSSBALL-QUIZ", "NUR FUR EXPERTEN!"),
    "quiz4":  ("NAME THESE", "ICONIC TV SHOWS!"),
    "quiz5":  ("GUESS THE", "COUNTRY FLAG!"),
    "quiz6":  ("NAME THESE", "WORLD CAPITALS!"),
    "quiz8":  ("GUESS THE BRAND", "BY EMOJI!"),
    "quiz10": ("GUESS THE SPORT", "BY EMOJI!"),
}
HOOK_SUB = "Most people fail Q3..."
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
        bb = draw.textbbox((0, 0), test, font=font)
        if (bb[2] - bb[0]) > max_w and cur:
            lines.append(" ".join(cur)); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(" ".join(cur))
    return lines


def strip_emoji(text):
    import re
    p = re.compile(
        "[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U0001F1E6-\U0001F1FF"
        "\U00002B00-\U00002BFF\U0001F000-\U0001F0FF\U0000FE00-\U0000FE0F"
        "\U00002190-\U000021FF]+", flags=re.UNICODE)
    return p.sub("", text).strip()


def draw_bar(img, text, y_frac, bar_color, text_color, fsize=48, bold=True, pad=28):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(fsize, bold)
    lines = wrap_text(text, font, W - 100, draw)
    lh = fsize + 14
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
    font = load_font(72, bold=True)
    txt = str(sec)
    cx, cy, r = W - 100, 140, 64
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(0, 0, 0, 200))
    bb = draw.textbbox((0, 0), txt, font=font)
    draw.text((cx - (bb[2]-bb[0])//2, cy - (bb[3]-bb[1])//2 - 6), txt, font=font, fill=COL_YELLOW)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def draw_qnum_badge(img, qnum, total=5):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy, r = 100, 140, 68
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(90, 30, 160, 240))
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=(255, 230, 50, 255), width=5)
    f_num = load_font(48, bold=True)
    txt = str(qnum)
    bb = draw.textbbox((0, 0), txt, font=f_num)
    draw.text((cx-(bb[2]-bb[0])//2, cy-28), txt, font=f_num, fill=(255,255,255))
    f_small = load_font(24, bold=True)
    sub = f"/{total}"
    bb2 = draw.textbbox((0, 0), sub, font=f_small)
    draw.text((cx-(bb2[2]-bb2[0])//2, cy+18), sub, font=f_small, fill=(255,230,50))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


_avatar_cache = None
def get_avatar():
    global _avatar_cache
    if _avatar_cache is not None:
        return _avatar_cache
    size = 96
    if os.path.exists(AVATAR_PATH):
        av = Image.open(AVATAR_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
    else:
        av = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(av)
        d.ellipse([(0,0),(size-1,size-1)], fill=(100,30,180,220))
        f = load_font(36, bold=True)
        d.text((30, 24), "Q", font=f, fill=(255,220,0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([(0,0),(size-1,size-1)], fill=255)
    av.putalpha(mask)
    ring = Image.new("RGBA", (size+8, size+8), (0,0,0,0))
    ImageDraw.Draw(ring).ellipse([(0,0),(size+7,size+7)], fill=(255,255,255,210))
    ring.paste(av, (4,4), av)
    _avatar_cache = ring
    return _avatar_cache


def add_avatar(img):
    av = get_avatar()
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    overlay.paste(av, (24, H - av.height - 220), av)  # sits above bottom CTA space
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def fit_vertical(base_img):
    """Fit a 16:9 (or any) source image into the 9:16 frame — blurred bg fill + centered crop."""
    src = base_img.convert("RGB")
    sw, sh = src.size

    # Background: scaled to fill full 1080x1920, blurred
    bg = src.resize((W, int(W * sh / sw)), Image.LANCZOS)
    if bg.height < H:
        bg = src.resize((int(H * sw / sh), H), Image.LANCZOS)
    from PIL import ImageFilter
    bg = bg.filter(ImageFilter.GaussianBlur(30))
    # Center crop bg to WxH
    left = max(0, (bg.width - W) // 2)
    top = max(0, (bg.height - H) // 2)
    bg = bg.crop((left, top, left + W, top + H))

    # Foreground: fit image centered, width-limited
    fg_w = W - 80
    fg_h = int(fg_w * sh / sw)
    if fg_h > H - 500:
        fg_h = H - 500
        fg_w = int(fg_h * sw / sh)
    fg = src.resize((fg_w, fg_h), Image.LANCZOS)

    canvas = bg.copy()
    canvas.paste(fg, ((W - fg_w)//2, (H - fg_h)//2 - 100))
    return canvas


def load_base(img_path):
    if os.path.exists(img_path):
        img = Image.open(img_path)
        return fit_vertical(img)
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = [15, 20, 50]
    return Image.fromarray(arr)


def make_hook_frame(folder):
    """Opening 2.5s hook screen — stops the scroll."""
    line1, line2 = HOOK_LINES.get(folder, ("QUIZ TIME!", "TEST YOURSELF"))
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = [26, 26, 26]
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    gc = (40, 40, 40)
    for x in range(0, W, 60): draw.line([(x,0),(x,H)], fill=gc, width=1)
    for y in range(0, H, 60): draw.line([(0,y),(W,y)], fill=gc, width=1)

    f_brand = load_font(38, bold=True)
    f_lg = load_font(72, bold=True)
    f_sub = load_font(40, bold=False)

    # QUIZ BLITZ pill
    bb = draw.textbbox((0,0), "QUIZ BLITZ", font=f_brand)
    pw, ph = bb[2]-bb[0]+70, bb[3]-bb[1]+34
    px, py = (W-pw)//2, 140
    draw.rounded_rectangle([(px,py),(px+pw,py+ph)], radius=ph//2, fill=(107,33,212))
    draw.text((px+35, py+16), "QUIZ BLITZ", font=f_brand, fill=(255,255,255))

    # Big hook text
    y = 420
    for line in [line1, line2]:
        bb = draw.textbbox((0,0), line, font=f_lg)
        x = (W-(bb[2]-bb[0]))//2
        draw.text((x+3, y+3), line, font=f_lg, fill=(0,0,0))
        draw.text((x, y), line, font=f_lg, fill=(255,204,0))
        y += 100

    bb = draw.textbbox((0,0), HOOK_SUB, font=f_sub)
    draw.text(((W-(bb[2]-bb[0]))//2, y+40), HOOK_SUB, font=f_sub, fill=(180,180,220))

    img = add_avatar(img)
    return img


def make_cta_frames(n_frames):
    """End card — punchy CTA to subscribe + watch the full 50-question quiz."""
    frames = []
    f_big = load_font(68, bold=True)
    f_md  = load_font(42, bold=True)
    f_sm  = load_font(32, bold=True)

    for fi in range(n_frames):
        t = fi / FPS
        arr = np.zeros((H, W, 3), dtype=np.uint8)
        arr[:, :] = [20, 5, 40]
        img = Image.fromarray(arr, "RGB").convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Sparkles
        for i in range(24):
            sx = (i * 97 + 40) % W
            sy = (i * 151 + 60) % H
            alpha = int(120 + 120 * math.sin(t*3 + i))
            draw.ellipse([(sx-2,sy-2),(sx+2,sy+2)], fill=(255,255,255,max(0,alpha)))

        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        pulse = int(220 + 35 * math.sin(t*4))
        bb = draw.textbbox((0,0), "50 MORE", font=f_big)
        x = (W-(bb[2]-bb[0]))//2
        draw.text((x+3, 620+3), "50 MORE", font=f_big, fill=(0,0,0))
        draw.text((x, 620), "50 MORE", font=f_big, fill=(pulse,pulse,50))

        bb = draw.textbbox((0,0), "QUESTIONS AWAIT", font=f_md)
        x = (W-(bb[2]-bb[0]))//2
        draw.text((x, 710), "QUESTIONS AWAIT", font=f_md, fill=(200,200,255))

        bb = draw.textbbox((0,0), "Full quiz on our channel", font=f_sm)
        x = (W-(bb[2]-bb[0]))//2
        draw.text((x, 780), "Full quiz on our channel", font=f_sm, fill=(180,180,220))

        # SUBSCRIBE pill — pulsing
        pw, ph = 560, 100
        px, py = (W-pw)//2, 920
        draw.rounded_rectangle([(px,py),(px+pw,py+ph)], radius=20, fill=(200,20,20))
        f_sub = load_font(44, bold=True)
        txt = f"SUBSCRIBE"
        bb = draw.textbbox((0,0), txt, font=f_sub)
        draw.text((px+(pw-(bb[2]-bb[0]))//2, py+16), txt, font=f_sub, fill=(255,255,255))
        bb2 = draw.textbbox((0,0), CHANNEL_NAME, font=f_sm)
        draw.text((px+(pw-(bb2[2]-bb2[0]))//2, py+62), CHANNEL_NAME, font=f_sm, fill=(255,220,150))

        img = add_avatar(img)
        frames.append(np.array(img))
    return frames


def make_segments(row, qnum_display):
    img_path = os.path.join(IMAGES_DIR, row["file_name"])
    qtext  = strip_emoji(row["question_text"].strip())
    answer = strip_emoji(row["answer"].strip())
    base   = load_base(img_path)
    segs   = []

    img_q = base.copy()
    img_q = draw_qnum_badge(img_q, qnum_display, N_QUESTIONS)
    img_q = draw_bar(img_q, qtext, 0.80, COL_Q_BAR, COL_WHITE, fsize=46, bold=True)
    img_q = add_avatar(img_q)
    segs.append((img_q, T_QUESTION, "question"))

    n_ticks = max(1, int(T_THINKING))
    for s in range(n_ticks, 0, -1):
        segs.append((draw_countdown(img_q.copy(), s), T_THINKING / n_ticks, "countdown"))

    img_a = base.copy()
    img_a = draw_qnum_badge(img_a, qnum_display, N_QUESTIONS)
    img_a = draw_bar(img_a, f"\u2713  {answer}", 0.80, COL_A_BAR, COL_YELLOW, fsize=54, bold=True)
    img_a = add_avatar(img_a)
    segs.append((img_a, T_ANSWER, "answer"))

    return segs


def loop_audio(clip, duration):
    from moviepy import concatenate_audioclips
    if clip.duration >= duration:
        return clip.subclipped(0, duration)
    loops = int(duration / clip.duration) + 2
    return concatenate_audioclips([clip] * loops).subclipped(0, duration)


def build_audio_track(segments_with_music):
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
        import moviepy.audio.fx as afx

        has_q  = os.path.exists(MUSIC_QUESTION)
        has_cd = os.path.exists(MUSIC_COUNTDOWN)
        has_an = os.path.exists(MUSIC_ANSWER)
        if not any([has_q, has_cd, has_an]):
            return None

        clips_cache = {}
        if has_q:
            c = AudioFileClip(MUSIC_QUESTION)
            clips_cache["question"] = c.with_effects([afx.MultiplyVolume(VOL_QUESTION)])
            clips_cache["hook"]     = c.with_effects([afx.MultiplyVolume(0.3)])
            clips_cache["cta"]      = c.with_effects([afx.MultiplyVolume(0.7)])
        if has_cd:
            clips_cache["countdown"] = AudioFileClip(MUSIC_COUNTDOWN).with_effects([afx.MultiplyVolume(VOL_COUNTDOWN)])
        if has_an:
            clips_cache["answer"] = AudioFileClip(MUSIC_ANSWER).with_effects([afx.MultiplyVolume(VOL_ANSWER)])

        audio_clips = []
        current_time = 0.0
        for _, dur, tag in segments_with_music:
            base_clip = clips_cache.get(tag)
            if base_clip is not None:
                seg = loop_audio(base_clip, dur).with_start(current_time)
                audio_clips.append(seg)
            current_time += dur
        return CompositeAudioClip(audio_clips) if audio_clips else None
    except Exception as e:
        print(f"  \u26a0  Audio build failed: {e}")
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
        all_rows = list(csv.DictReader(f))
    question_rows = [r for r in all_rows if r["asset_type"] == "question_scene"][:N_QUESTIONS]

    print(f"Quiz Blitz — Shorts Generator")
    print(f"Quiz: {_folder} | Vertical 9:16 | {N_QUESTIONS} questions\n")

    all_segments = []
    all_frames   = []

    # Hook (2.5s)
    print("Building hook...")
    hook_img = make_hook_frame(_folder)
    n_hook = round(T_HOOK * FPS)
    all_frames.extend([np.array(hook_img)] * n_hook)
    all_segments.append((None, T_HOOK, "hook"))

    # Questions
    print(f"Building {len(question_rows)} questions...")
    for i, row in enumerate(question_rows, 1):
        segs = make_segments(row, i)
        for img, dur, tag in segs:
            all_segments.append((img, dur, tag))
            arr = np.array(img)
            n = max(1, round(dur * FPS))
            all_frames.extend([arr] * n)
        print(f"  [{i}/{len(question_rows)}] done")

    # CTA (4s)
    print("Building CTA outro...")
    n_cta = round(T_CTA * FPS)
    cta_frames = make_cta_frames(n_cta)
    all_frames.extend(cta_frames)
    all_segments.append((None, T_CTA, "cta"))

    total_sec = len(all_frames) / FPS
    print(f"\nFrames: {len(all_frames)} = {total_sec:.1f} sec")

    print("\nBuilding audio track...")
    audio = build_audio_track(all_segments)

    print(f"\nWriting {OUTPUT}...")
    clip = ImageSequenceClip(all_frames, fps=FPS)
    if audio:
        clip = clip.with_audio(audio)
        print("  \U0001F3B5 Audio attached")
    else:
        print("  Silent (no music files found)")

    clip.write_videofile(
        OUTPUT,
        codec="libx264",
        audio_codec="aac" if audio else None,
        ffmpeg_params=["-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n\u2705  Done! \u2192 {OUTPUT} ({size_mb:.1f} MB, {total_sec:.0f}s, 1080x1920)")
    print(f"   Ready for YouTube Shorts, TikTok, Instagram Reels")

if __name__ == "__main__":
    main()
