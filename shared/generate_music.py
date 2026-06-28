#!/usr/bin/env python3
"""
Quiz Generator — Music Generator via ElevenLabs API
Generates 3 royalty-free music tracks:
  music_question.mp3   — background during questions (30 sec)
  music_countdown.mp3  — tension during countdown (10 sec)
  music_answer.mp3     — victory fanfare on answer reveal (4 sec)

Usage: python3 generate_music.py
Run from any quiz folder (quiz1/, quiz2/, quiz3/, quiz4/)
"""

import os, requests, time

API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_e17e9bf41d53a46fa2d81a8ac0a88ac5ae72962849d1e035"

SOUND_URL = "https://api.elevenlabs.io/v1/sound-generation"
MUSIC_URL = "https://api.elevenlabs.io/v1/text-to-music"

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
}

TRACKS = [
    {
        "filename": "music_question.mp3",
        "desc":     "Question background (30 sec)",
        "prompt":   "upbeat quiz show background music, light friendly energy, no vocals, TV game show style, fun and playful, loopable instrumental",
        "duration": 30,
    },
    {
        "filename": "music_countdown.mp3",
        "desc":     "Countdown tension (10 sec)",
        "prompt":   "tense suspenseful countdown timer music, building dramatic tension, pulse beat, no vocals, quiz show clock ticking, urgent rhythmic",
        "duration": 10,
    },
    {
        "filename": "music_answer.mp3",
        "desc":     "Answer reveal fanfare (4 sec)",
        "prompt":   "short triumphant victory fanfare, uplifting brass celebration, correct answer reveal, no vocals, quiz show win jingle",
        "duration": 4,
    },
]


def generate_sound_effect(track):
    """Try Sound Effects API first (cheaper, faster)."""
    r = requests.post(
        SOUND_URL,
        headers=HEADERS,
        json={
            "text": track["prompt"],
            "duration_seconds": track["duration"],
            "prompt_influence": 0.7,
        },
        timeout=60,
    )
    if r.status_code == 200 and len(r.content) > 1000:
        return r.content
    print(f"    Sound Effects API: {r.status_code} — {r.text[:100]}")
    return None


def generate_music_track(track):
    """Fallback to Music Generation API."""
    r = requests.post(
        MUSIC_URL,
        headers=HEADERS,
        json={
            "text": track["prompt"],
            "make_instrumental": True,
        },
        timeout=120,
    )
    if r.status_code == 200 and len(r.content) > 1000:
        return r.content
    print(f"    Music API: {r.status_code} — {r.text[:100]}")
    return None


def main():
    print("🎵 Quiz Generator — Music Generator")
    print("   ElevenLabs API | royalty-free | commercially licensed\n")

    done, errors = 0, []

    for i, track in enumerate(TRACKS, 1):
        fn = track["filename"]
        print(f"[{i}/3] {track['desc']}")
        print(f"       → {fn}")

        if os.path.exists(fn):
            print(f"  ⏭  Already exists, skipping\n")
            done += 1
            continue

        # Try Sound Effects API first
        print("  Trying Sound Effects API...")
        audio = generate_sound_effect(track)

        # Fallback to Music API
        if not audio:
            print("  Trying Music Generation API...")
            audio = generate_music_track(track)

        if audio:
            with open(fn, "wb") as f:
                f.write(audio)
            size_kb = len(audio) // 1024
            print(f"  ✓  Saved ({size_kb} KB)\n")
            done += 1
        else:
            print(f"  ✗  Failed\n")
            errors.append(fn)

        if i < len(TRACKS):
            time.sleep(2)  # rate limit

    print("=" * 40)
    print(f"Done: {done}/{len(TRACKS)} tracks")

    if errors:
        print(f"\n⚠  Failed tracks: {errors}")
        print("   Check your credits at: https://elevenlabs.io → Usage")
    else:
        print("\n✅ All music ready!")
        print("\nNext step — assemble the video with music:")
        print("  python3 ../shared/make_quiz_video.py")
        print()
        print("Music will be applied automatically:")
        print("  music_question.mp3  → 40% volume during questions")
        print("  music_countdown.mp3 → 60% volume during countdown")
        print("  music_answer.mp3    → 70% volume on answer reveal")


if __name__ == "__main__":
    main()
