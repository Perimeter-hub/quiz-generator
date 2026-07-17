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

# CLEAN_STYLE: quizzes where the question text is already baked into the image
# (state shapes, emoji quizzes, etc). For these, don't draw duplicate text bars.
# quiz2 = state shapes, quiz5-10 = future visual quizzes
CLEAN_STYLE = _folder in ("quiz2", "quiz5", "quiz6", "quiz7", "quiz8", "quiz9", "quiz10", "quiz11", "quiz17")

T_TITLE    = 4.0
T_QUESTION = 5.0
T_THINKING = 6.0
T_ANSWER   = 4.0
T_OUTRO    = 6.0
T_FINALE   = 8.0   # bright finale screen duration
T_WYR_Q      = 4.0   # would-you-rather question display
T_WYR_THINK  = 3.0   # short thinking pause
T_WYR_REVEAL = 3.0   # stat bar reveal

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
    cx, cy, r = W - 90, 90, 52
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

def add_channel_badge(img):
    """Draw purple pill with @QuizBlitzGo at top-right — for title cards only."""
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(32, bold=True)
    text = CHANNEL_NAME
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    pad_x, pad_y = 32, 14
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    pill_x = W - pill_w - 28
    pill_y = 28
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=pill_h // 2,
        fill=(107, 33, 212, 240)
    )
    draw.text((pill_x + pad_x, pill_y + pad_y - 2), text, font=font, fill=(255, 255, 255))
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
        bb3 = draw.textbbox((0,0), "Drop your score in the comments!", font=f_sm)
        tx3 = (W-(bb3[2]-bb3[0]))//2
        draw.text((tx3, 393), "Drop your score in the comments!", font=f_sm, fill=(255,230,100))

        # Subscribe CTA — pulsing
        sub_alpha = int(200 + 55 * math.sin(t * 5))
        draw.rounded_rectangle([(W//2-340, 475),(W//2+340, 555)],
                                radius=16, fill=(200,20,20))
        bb4 = draw.textbbox((0,0), f"SUBSCRIBE  {CHANNEL_NAME}", font=f_sub)
        tx4 = (W-(bb4[2]-bb4[0]))//2
        draw.text((tx4+2, 494), f"SUBSCRIBE  {CHANNEL_NAME}", font=f_sub, fill=(0,0,0))
        draw.text((tx4, 492), f"SUBSCRIBE  {CHANNEL_NAME}", font=f_sub, fill=(255,255,255))

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

TOTAL_QUESTIONS = 50  # set dynamically in main()

def draw_qnum_badge(img, qnum, total=None):
    if total is None:
        total = TOTAL_QUESTIONS
    """Draw a clean purple circle badge with question number in top-right corner."""
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    cx, cy, r = 80, 80, 56
    # Purple circle matching brand
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(90, 30, 160, 235))
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=(255, 230, 50, 255), width=4)
    # Number
    f_num = load_font(40, bold=True)
    txt = str(qnum)
    bb = draw.textbbox((0,0), txt, font=f_num)
    draw.text((cx-(bb[2]-bb[0])//2, cy-22), txt, font=f_num, fill=(255,255,255))
    # "/50" small below
    f_small = load_font(20, bold=True)
    sub = f"/{total}"
    bb2 = draw.textbbox((0,0), sub, font=f_small)
    draw.text((cx-(bb2[2]-bb2[0])//2, cy+14), sub, font=f_small, fill=(255,230,50))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def strip_emoji(text):
    """Remove emoji characters that render as □□□ with system fonts."""
    import re
    # Remove emoji unicode ranges
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001F9FF"   # misc symbols, emoticons
        "\U00002600-\U000027BF"    # misc symbols
        "\U0001FA00-\U0001FA6F"    # chess, symbols
        "\U0001FA70-\U0001FAFF"    # symbols extended
        "\U00002702-\U000027B0"    # dingbats
        "\U0001F1E6-\U0001F1FF"    # regional indicators (flag emoji pairs)
        "\U00002B00-\U00002BFF"    # arrows, stars
        "\U0001F000-\U0001F0FF"    # mahjong/cards
        "\U0000FE00-\U0000FE0F"    # variation selectors
        "\U00002190-\U000021FF"    # arrows
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub("", text).strip()


# ── WOULD YOU RATHER WARM-UP ───────────────────────────────────────────────────
_emoji_cache = {}

def get_emoji_img(char, size=180):
    """Fetch a Twemoji PNG for a single emoji, multi-CDN fallback, memory+disk cached."""
    import ssl, urllib.request
    if char in _emoji_cache:
        return _emoji_cache[char]
    cp = "-".join(f"{ord(c):x}" for c in char if ord(c) != 0xFE0F)
    cache_dir = "/tmp/twemoji_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{cp}.png")
    img = None
    if os.path.exists(cache_path):
        try:
            img = Image.open(cache_path).convert("RGBA")
        except Exception:
            img = None
    if img is None:
        urls = [
            f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{cp}.png",
            f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@14.1.2/assets/72x72/{cp}.png",
            f"https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/{cp}.png",
            f"https://raw.githubusercontent.com/jdecked/twemoji/main/assets/72x72/{cp}.png",
        ]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
                    data = r.read()
                if len(data) < 100:
                    raise Exception("empty")
                with open(cache_path, "wb") as f:
                    f.write(data)
                img = Image.open(cache_path).convert("RGBA")
                break
            except Exception:
                continue
    if img is not None:
        img = img.resize((size, size), Image.LANCZOS)
    _emoji_cache[char] = img
    return img


def make_wyr_frame(question, opt_a, opt_b, reveal=False, pct_a=50):
    """Draw a Would-You-Rather split scene. If reveal, show percentage bars."""
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:, :] = [24, 12, 40]
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)
    gc = (40, 26, 60)
    for x in range(0, W, 70): draw.line([(x,0),(x,H)], fill=gc, width=1)

    f_q = load_font(38, bold=True)
    img = draw_bar(img, question, 0.14, (10,10,10,190), COL_WHITE, fsize=38, bold=True, pad=20)
    draw = ImageDraw.Draw(img)

    # Left / right halves
    draw.rectangle([(0, 0), (W//2, H)], fill=None)
    half_x1, half_x2 = W // 4, 3 * W // 4
    cy = H // 2 + 20

    e_a = get_emoji_img(opt_a, size=190)
    e_b = get_emoji_img(opt_b, size=190)
    img = img.convert("RGBA")
    if e_a: img.paste(e_a, (half_x1 - 95, cy - 95), e_a)
    if e_b: img.paste(e_b, (half_x2 - 95, cy - 95), e_b)
    draw = ImageDraw.Draw(img)

    # OR divider
    f_or = load_font(44, bold=True)
    bb = draw.textbbox((0,0), "OR", font=f_or)
    draw.ellipse([(W//2-42, cy-42),(W//2+42, cy+42)], fill=(107,33,212,255))
    draw.text((W//2-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-6), "OR", font=f_or, fill=(255,255,255))

    if reveal:
        pct_b = 100 - pct_a
        bar_y = cy + 150
        bar_h = 46
        # Left bar
        bw_a = int((W//2 - 60) * pct_a / 100)
        draw.rounded_rectangle([(30, bar_y), (30 + max(bw_a, 40), bar_y+bar_h)], radius=10, fill=(60,180,120,230))
        f_pct = load_font(30, bold=True)
        draw.text((40, bar_y+8), f"{pct_a}%", font=f_pct, fill=(255,255,255))
        # Right bar
        bw_b = int((W//2 - 60) * pct_b / 100)
        rx = W - 30 - max(bw_b, 40)
        draw.rounded_rectangle([(rx, bar_y), (W-30, bar_y+bar_h)], radius=10, fill=(220,90,60,230))
        draw.text((W-40-70, bar_y+8), f"{pct_b}%", font=f_pct, fill=(255,255,255))

    img = add_avatar(img.convert("RGB"))
    return img


def make_wyr_segments(row):
    """Build (question + reveal) frame segments for one Would-You-Rather row."""
    q = strip_emoji(row["question_text"].strip())
    clue = row.get("main_visual_clue", "").strip()
    parts = [p.strip() for p in clue.split("|")]
    if len(parts) != 2:
        return []
    opt_a, opt_b = parts
    try:
        pct_a = int(row.get("stat_pct", "50") or "50")
    except ValueError:
        pct_a = 50

    segs = []
    frame_q = make_wyr_frame(q, opt_a, opt_b, reveal=False)
    segs.append((frame_q, T_WYR_Q + T_WYR_THINK, "wyr_question"))
    frame_r = make_wyr_frame(q, opt_a, opt_b, reveal=True, pct_a=pct_a)
    segs.append((frame_r, T_WYR_REVEAL, "wyr_reveal"))
    return segs


def make_segments(row):
    img_path = os.path.join(IMAGES_DIR, row["file_name"])
    atype    = row["asset_type"]
    qtext    = strip_emoji(row["question_text"].strip())
    answer   = strip_emoji(row["answer"].strip())
    qnum     = row["question_number"].strip()
    base     = load_base(img_path)
    segs     = []

    if atype == "title_card":
        img = base.copy()
        if not CLEAN_STYLE and qtext:
            img = draw_bar(img, qtext, 0.88, COL_T_BAR, COL_WHITE, fsize=44, bold=True)
        # Cover the old baked-in yellow "QUIZ GO!" pill at the bottom of CLEAN_STYLE images.
        # Sample background near bottom-center-left (avoiding the pill which is centered).
        if CLEAN_STYLE:
            _bg = img.convert("RGB").getpixel((60, H - 130))
            from PIL import ImageDraw as _ID
            _ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            _ID.Draw(_ov).rectangle([(0, H - 115), (W, H)], fill=_bg + (255,))
            img = Image.alpha_composite(img.convert("RGBA"), _ov).convert("RGB")
        # Avatar (bottom-left) goes ON TOP of the cover
        img = add_avatar(img)
        # Purple pill channel badge bottom-center
        img = add_channel_badge(img)
        segs.append((img, T_TITLE, "title"))

    elif atype == "question_scene":
        # No Q-number badge anywhere (number is in the image or not needed)
        img_q = base.copy()
        if not CLEAN_STYLE:
            # Photo-scene quizzes (quiz1,3,4): question text drawn at bottom
            img_q = draw_bar(img_q, qtext, 0.82, COL_Q_BAR, COL_WHITE, fsize=36, bold=True)
        else:
            # CLEAN_STYLE (quiz2,5-10): question already baked into image, draw it at bottom anyway
            img_q = draw_bar(img_q, qtext, 0.82, COL_Q_BAR, COL_WHITE, fsize=36, bold=True)
        # Question number badge top-right (only for photo-scenes — CLEAN_STYLE has it in image)
        if qnum and not CLEAN_STYLE:
            img_q = draw_qnum_badge(img_q, qnum)
        img_q = add_avatar(img_q)
        segs.append((img_q, T_QUESTION, "question"))

        for s in range(int(T_THINKING), 0, -1):
            cd_frame = draw_countdown(img_q.copy(), s)
            segs.append((cd_frame, 1.0, "countdown"))

        img_a = base.copy()
        img_a = draw_bar(img_a, f"✓  {answer}", 0.82, COL_A_BAR, COL_YELLOW, fsize=48, bold=True)
        if qnum and not CLEAN_STYLE:
            img_a = draw_qnum_badge(img_a, qnum)
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
            clips_cache["wyr_question"] = c.with_effects([afx.MultiplyVolume(0.45)])
        if has_cd:
            clips_cache["countdown"] = AudioFileClip(MUSIC_COUNTDOWN).with_effects([afx.MultiplyVolume(VOL_COUNTDOWN)])
        if has_an:
            clips_cache["answer"] = AudioFileClip(MUSIC_ANSWER).with_effects([afx.MultiplyVolume(VOL_ANSWER)])
            clips_cache["wyr_reveal"] = AudioFileClip(MUSIC_ANSWER).with_effects([afx.MultiplyVolume(0.5)])

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
    global TOTAL_QUESTIONS
    TOTAL_QUESTIONS = sum(1 for r in rows if r["asset_type"] == "question_scene")
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

        if row["asset_type"] == "wyr_scene":
            segs = make_wyr_segments(row)
        else:
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
