#!/usr/bin/env python3
"""
Quiz Generator — Music Generator via ElevenLabs API
Generates 3 royalty-free music tracks for quiz videos:
  - music_question.mp3   (background during questions)
  - music_countdown.mp3  (tension during countdown)
  - music_answer.mp3     (victory fanfare on answer reveal)

Usage: python generate_music.py
Place in your quiz folder and run before make_quiz_video.py
Requires: ELEVENLABS_API_KEY in .env
"""

import os, requests, time
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
API_URL = "https://api.elevenlabs.io/v1/sound-generation"
MUSIC_URL = "https://api.elevenlabs.io/v1/text-to-music"

TRACKS = [
    {
        "filename": "music_question.mp3",
        "desc": "Question background",
        "endpoint": "sound",
        "prompt": "upbeat quiz show background music, light friendly energy, no vocals, TV game show style, fun and playful, loopable",
        "duration": 30,
    },
    {
        "filename": "music_countdown.mp3",
        "desc": "Countdown tension",
        "endpoint": "sound",
        "prompt": "tense suspenseful countdown timer music, building dramatic tension, pulse beat, no vocals, quiz show clock ticking, urgent",
        "duration": 10,
    },
    {
        "filename": "music_answer.mp3",
        "desc": "Answer reveal fanfare",
        "endpoint": "sound",
        "prompt": "short triumphant victory fanfare, uplifting brass celebration, correct answer reveal, no vocals, quiz show win jingle",
        "duration": 4,
    },
]


def generate_sound(prompt, duration_seconds, filename):
    """Generate using ElevenLabs Sound Effects API."""
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": prompt,
        "duration_seconds": duration_seconds,
        "prompt_influence": 0.7,
    }
    print(f"  Generating ({duration_seconds}s): {prompt[:60]}...")
    r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        size_kb = len(r.content) // 1024
        print(f"  ✓  Saved: {filename} ({size_kb}KB)")
        return True
    else:
        print(f"  ✗  Error {r.status_code}: {r.text[:200]}")
        return False


def generate_music(prompt, filename):
    """Generate using ElevenLabs Music API (if sound effects not sufficient)."""
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": prompt,
        "make_instrumental": True,
    }
    print(f"  Generating music: {prompt[:60]}...")
    r = requests.post(MUSIC_URL, headers=headers, json=payload, timeout=120)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        size_kb = len(r.content) // 1024
        print(f"  ✓  Saved: {filename} ({size_kb}KB)")
        return True
    else:
        print(f"  ✗  Error {r.status_code}: {r.text[:200]}")
        return False


def main():
    if not API_KEY:
        print("ERROR: Set ELEVENLABS_API_KEY in .env file")
        print("Get your free key at: https://elevenlabs.io → Profile → API Keys")
        return

    print("Quiz Generator — Music Generator")
    print("Using: ElevenLabs Sound Effects API")
    print("Output: royalty-free, commercially licensed\n")

    done, errors = 0, []
    for track in TRACKS:
        fn = track["filename"]
        if os.path.exists(fn):
            print(f"  ⏭  skip (exists): {fn}")
            done += 1
            continue

        print(f"\n[{track['desc']}] → {fn}")
        ok = generate_sound(track["prompt"], track["duration"], fn)

        if not ok:
            # Fallback to Music API
            print("  Trying Music API fallback...")
            ok = generate_music(track["prompt"], fn)

        if ok:
            done += 1
        else:
            errors.append(fn)
        time.sleep(2)  # rate limit

    print(f"\n{'='*40}")
    print(f"Done: {done}/{len(TRACKS)} tracks")
    if errors:
        print(f"Failed: {errors}")
        print("\nTip: Check your API key and plan credits at elevenlabs.io")
    else:
        print("\nAll tracks ready! Now run:")
        print("  python ../shared/make_quiz_video.py")
        print("\nThe video assembler will automatically pick up:")
        print("  music_question.mp3  → plays during questions (40% volume)")
        print("  music_countdown.mp3 → plays during countdown (60% volume)")
        print("  music_answer.mp3    → plays during answer reveal (70% volume)")


if __name__ == "__main__":
    main()
