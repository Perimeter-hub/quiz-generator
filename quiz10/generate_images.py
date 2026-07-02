#!/usr/bin/env python3
"""Quiz 1: 50 States Challenge — Image Generator (ModelsLab API)
Usage: python generate_images.py
Requires: MODELSLAB_API_KEY in .env
"""
import requests, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

API_KEY   = os.getenv("MODELSLAB_API_KEY", "")
API_URL   = "https://modelslab.com/api/v6/realtime/text2img"
FETCH_URL = "https://modelslab.com/api/v6/realtime/fetch/"
OUTPUT_DIR = "images_and_videos"
NEG = "blurry, low quality, distorted, ugly, watermark, text, letters, words, writing, typography, cartoon, anime"

IMAGES = [
    ("opening_quiz10.png", "Create an original 16:9 quiz-show title card for a sports emoji quiz. Sports balls and equipment arranged dramatically. Text: GUESS THE SPORT! Energetic sports colors, stadium atmosphere, no copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EASY SPORTS. Bold clean typography, original design."),
    ("scene_q10_01_soccer.png", "Create original 16:9 quiz graphic. Large bold emojis: soccer ball, goal net, globe (⚽🥅🌍) on green field background. Question: What sport is this? Answer: Soccer / Football. Bold readable text."),
    ("scene_q10_02_basketball.png", "Create original 16:9 quiz graphic. Large emojis: basketball, stadium, trophy (🏀🏟️🏆). Question: What sport? Answer: Basketball."),
    ("scene_q10_03_baseball.png", "Create original 16:9 quiz graphic. Large emojis: baseball, glove, stadium (⚾🧤🏟️). Question: What sport? Answer: Baseball."),
    ("scene_q10_04_tennis.png", "Create original 16:9 quiz graphic. Large emojis: tennis ball, table tennis (used for court hint), trophy (🎾🏓🏆). Question: What sport? Answer: Tennis."),
    ("scene_q10_05_swimming.png", "Create original 16:9 quiz graphic. Large emojis: swimmer, waves, gold medal (🏊🌊🥇). Question: What sport? Answer: Swimming."),
    ("scene_q10_06_golf.png", "Create original 16:9 quiz graphic. Large emojis: golf hole flag, golfer, herb (⛳🏌️🌿). Question: What sport? Answer: Golf."),
    ("scene_q10_07_boxing.png", "Create original 16:9 quiz graphic. Large emojis: boxing gloves, drop (sweat/blood), flexed arm (🥊🩸💪). Question: What sport? Answer: Boxing."),
    ("scene_q10_08_skiing.png", "Create original 16:9 quiz graphic. Large emojis: skier, mountain, snowflake (⛷️🏔️❄️). Question: What sport? Answer: Skiing."),
    ("scene_q10_09_cycling.png", "Create original 16:9 quiz graphic. Large emojis: cyclist, trophy, sunrise (🚴🏆🌄). Question: What sport? Answer: Cycling."),
    ("scene_q10_10_gymnastics.png", "Create original 16:9 quiz graphic. Large emojis: cartwheel, ribbon, sports medal (🤸🎀🏅). Question: What sport? Answer: Gymnastics."),
    ("round_02_medium.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 2: MEDIUM SPORTS. Bold clean typography, original design."),
    ("scene_q10_11_american_football.png", "Create original 16:9 quiz graphic. Large emojis: american football, stadium, eagle (🏈🏟️🦅). Question: What sport? Answer: American Football."),
    ("scene_q10_12_hockey.png", "Create original 16:9 quiz graphic. Large emojis: hockey stick, goal, ice cube (🏒🥅🧊). Question: What sport? Answer: Ice Hockey."),
    ("scene_q10_13_volleyball.png", "Create original 16:9 quiz graphic. Large emojis: volleyball, beach umbrella, waves (🏐🏖️🌊). Question: What sport? Answer: Volleyball."),
    ("scene_q10_14_rowing.png", "Create original 16:9 quiz graphic. Large emojis: rower, waves, trophy (🚣🌊🏆). Question: What sport? Answer: Rowing."),
    ("scene_q10_15_archery.png", "Create original 16:9 quiz graphic. Large emojis: bow and arrow, target, eagle (🏹🎯🦅). Question: What sport? Answer: Archery."),
    ("scene_q10_16_fencing.png", "Create original 16:9 quiz graphic. Large emojis: fencer, crossed swords, gold medal (🤺⚔️🥇). Question: What sport? Answer: Fencing."),
    ("scene_q10_17_weightlifting.png", "Create original 16:9 quiz graphic. Large emojis: weightlifter, flexed bicep, gold medal (🏋️💪🥇). Question: What sport? Answer: Weightlifting."),
    ("scene_q10_18_surfing.png", "Create original 16:9 quiz graphic. Large emojis: surfer, large wave, sunrise (🏄🌊🌅). Question: What sport? Answer: Surfing."),
    ("scene_q10_19_polo.png", "Create original 16:9 quiz graphic. Large emojis: horse, field hockey stick (mallet hint), herb/grass (🐎🏑🌿). Question: What sport? Answer: Polo."),
    ("scene_q10_20_curling.png", "Create original 16:9 quiz graphic. Large emojis: curling stone, broom, ice (🥌🧹🧊). Question: What sport? Answer: Curling."),
    ("outro_quiz10.png", "Create an original 16:9 quiz-show outro celebration scoreboard. Confetti, festive energy, no copied branding."),
]

def poll_fetch(fetch_id, max_tries=20):
    for i in range(max_tries):
        time.sleep(3)
        try:
            r = requests.post(FETCH_URL + str(fetch_id), json={"key": API_KEY}, timeout=30)
            d = r.json()
            if d.get("status") == "success" and d.get("output"): return d["output"][0]
            if d.get("status") == "error": raise Exception(d.get("message", "Fetch error"))
        except Exception as e:
            if i == max_tries - 1: raise
    raise Exception("Timed out")

def generate_one(filename, prompt):
    out_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(out_path): print(f"  ⏭  skip: {filename}"); return True
    payload = {"key": API_KEY, "prompt": prompt + ", ultra photorealistic, 8k, cinematic, wide angle, professional photography",
                "negative_prompt": NEG, "width": "1024", "height": "576", "samples": "1",
                "num_inference_steps": "30", "guidance_scale": 7.5, "safety_checker": "no", "enhance_prompt": "yes", "seed": None}
    try:
        r = requests.post(API_URL, json=payload, timeout=60); r.raise_for_status()
        data = r.json()
        image_url = None
        if data.get("status") == "success" and data.get("output"): image_url = data["output"][0]
        elif data.get("status") == "processing" and data.get("id"): image_url = poll_fetch(data["id"])
        else: raise Exception(data.get("message") or str(data)[:200])
        img_r = requests.get(image_url, timeout=60); img_r.raise_for_status()
        with open(out_path, "wb") as f: f.write(img_r.content)
        print(f"  ✓  {filename}"); return True
    except Exception as e: print(f"  ✗  {filename}: {e}"); return False

def main():
    if not API_KEY: print("ERROR: Set MODELSLAB_API_KEY in .env file"); return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(IMAGES); print(f"Generating {total} images\n")
    errors = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(generate_one, fn, p): fn for fn, p in IMAGES}
        done = 0
        for future in as_completed(futures):
            fn = futures[future]; done += 1
            if not future.result(): errors.append(fn)
            print(f"  [{done}/{total}]")
    print(f"\nDone: {total-len(errors)}/{total}")
    if errors: [print(f"  ✗ {e}") for e in errors]
    print("\nNext: python ../shared/make_quiz_video.py")

if __name__ == "__main__":
    main()
