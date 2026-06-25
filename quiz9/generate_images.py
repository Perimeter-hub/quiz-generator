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
    ("opening_quiz9.png", "Create an original 16:9 quiz-show title card for a Would You Rather quiz. Two contrasting dramatic option panels, VS symbol in center, bold text WOULD YOU RATHER? Bright energetic colors, no copied branding."),
    ("round_01_round1.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: FOOD & DRINK. Bold clean typography, original design."),
    ("scene_q09_01_pizza_burger.png", "Create original 16:9 Would You Rather quiz graphic. Split screen: left side pizza slice on red, right side burger on yellow, VS symbol center. Bold text: Would you rather eat ONLY pizza OR only burgers forever? Dramatic food photography style illustration."),
    ("scene_q09_02_coffee_tea.png", "Create original 16:9 WYR graphic. Split: coffee steam on dark left, tea with lemon on warm right. VS center. Bold question text. Original design."),
    ("scene_q09_03_sushi_tacos.png", "Create original 16:9 WYR graphic. Split: sushi on cool blue left, tacos on warm orange right. VS center. Original illustration style."),
    ("scene_q09_04_sweet_salty.png", "Create original 16:9 WYR graphic. Split: candy and sweets on pink left, chips and popcorn on yellow right. VS center. Bold readable text."),
    ("scene_q09_05_never_cook.png", "Create original 16:9 WYR graphic. Split: cozy home kitchen left, fancy restaurant right. VS center. Original design."),
    ("round_02_round2.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 2: TRAVEL & ADVENTURE. Bold clean typography, original design."),
    ("scene_q09_06_beach_mountain.png", "Create original 16:9 WYR graphic. Split: tropical beach with waves on blue left, snowy mountain peak on white right. VS center. Beautiful landscape style."),
    ("scene_q09_07_fly_drive.png", "Create original 16:9 WYR graphic. Split: airplane in clouds left, car on open highway right. VS center. Original illustration."),
    ("scene_q09_08_nyc_la.png", "Create original 16:9 WYR graphic. Split: NYC skyline at night left, Hollywood hills and palm trees right. VS center. Original cityscape illustration."),
    ("scene_q09_09_camping_hotel.png", "Create original 16:9 WYR graphic. Split: campfire and tent in forest left, luxury hotel pool right. VS center."),
    ("scene_q09_10_explore_relax.png", "Create original 16:9 WYR graphic. Split: adventure explorer with map left, hammock on beach right. VS center."),
    ("round_03_round3.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 3: SUPERPOWERS & FUN. Bold clean typography, original design."),
    ("scene_q09_11_fly_invisible.png", "Create original 16:9 WYR graphic. Split: person flying through clouds left, invisible person silhouette right. VS center. Superhero energy."),
    ("scene_q09_12_rich_famous.png", "Create original 16:9 WYR graphic. Split: gold coins and money left, spotlight and cameras right. VS center."),
    ("scene_q09_13_dog_cat.png", "Create original 16:9 WYR graphic. Split: happy dog on warm yellow left, elegant cat on cool purple right. VS center."),
    ("scene_q09_14_past_future.png", "Create original 16:9 WYR graphic. Split: ancient Roman/Egyptian scene left, futuristic sci-fi city right. VS center."),
    ("scene_q09_15_winter_summer.png", "Create original 16:9 WYR graphic. Split: blazing sunny summer beach left, cozy snowy winter scene right. VS center."),
    ("outro_quiz9.png", "Create an original 16:9 quiz-show outro celebration scoreboard. Confetti, festive energy, no copied branding."),
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
