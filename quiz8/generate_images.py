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
    ("opening_quiz8.png", "Create an original 16:9 quiz-show title card for a fast food logo quiz. Burgers, pizza, tacos, fries arranged colorfully. Text: GUESS THE FAST FOOD! Bright food colors, appetizing, no copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EVERYONE KNOWS THESE. Bold clean typography, original design."),
    ("scene_q08_01_mcdonalds.png", "Create original 16:9 quiz graphic. Show a bold original golden yellow M arch shape (stylized, not copied) on red background. Question: What fast food chain is this? Answer: McDonald's. Bold readable text, original design."),
    ("scene_q08_02_kfc.png", "Create original 16:9 quiz graphic. Show original striped red-white bucket icon on red background, colonel character hint. Question: What fast food chain? Answer: KFC. Original design only."),
    ("scene_q08_03_subway.png", "Create original 16:9 quiz graphic. Show stylized subway sandwich shape with yellow-green color scheme hint. Question: What fast food chain? Answer: Subway."),
    ("scene_q08_04_starbucks.png", "Create original 16:9 quiz graphic. Show stylized green circle with twin-tailed mermaid siren original illustration. Question: What fast food chain? Answer: Starbucks."),
    ("scene_q08_05_pizza_hut.png", "Create original 16:9 quiz graphic. Show stylized red pitched roof hut silhouette with pizza. Question: What fast food chain? Answer: Pizza Hut."),
    ("scene_q08_06_burger_king.png", "Create original 16:9 quiz graphic. Show stylized burger bun shape with golden crown. Question: What fast food chain? Answer: Burger King."),
    ("scene_q08_07_wendys.png", "Create original 16:9 quiz graphic. Show stylized red pigtail girl icon, old fashioned hamburgers hint. Question: What fast food chain? Answer: Wendy's."),
    ("scene_q08_08_taco_bell.png", "Create original 16:9 quiz graphic. Show stylized purple-magenta bell shape with taco. Question: What fast food chain? Answer: Taco Bell."),
    ("scene_q08_09_dunkin.png", "Create original 16:9 quiz graphic. Show stylized pink-orange donut shape with coffee cup. Question: What fast food chain? Answer: Dunkin'."),
    ("scene_q08_10_dominos.png", "Create original 16:9 quiz graphic. Show stylized blue-red domino tile shape with pizza. Question: What fast food chain? Answer: Domino's Pizza."),
    ("round_02_medium.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 2: DO YOU KNOW THESE?. Bold clean typography, original design."),
    ("scene_q08_11_chick_fil_a.png", "Create original 16:9 quiz graphic. Show stylized red chicken shape, cursive font hint. Question: What fast food chain? Answer: Chick-fil-A."),
    ("scene_q08_12_five_guys.png", "Create original 16:9 quiz graphic. Show stylized red-white checkered pattern with burger. Question: What fast food chain? Answer: Five Guys."),
    ("scene_q08_13_sonic.png", "Create original 16:9 quiz graphic. Show stylized yellow lightning bolt with roller skate hint. Question: What fast food chain? Answer: Sonic Drive-In."),
    ("scene_q08_14_popeyes.png", "Create original 16:9 quiz graphic. Show stylized orange Louisiana fleur-de-lis with fried chicken. Question: What fast food chain? Answer: Popeyes Louisiana Kitchen."),
    ("scene_q08_15_panda_express.png", "Create original 16:9 quiz graphic. Show stylized black-white panda face with orange Chinese food. Question: What fast food chain? Answer: Panda Express."),
    ("scene_q08_16_in_n_out.png", "Create original 16:9 quiz graphic. Show stylized red arrow with palm tree silhouette. Question: What fast food chain? Answer: In-N-Out Burger."),
    ("scene_q08_17_shake_shack.png", "Create original 16:9 quiz graphic. Show stylized green shack/shed building. Question: What fast food chain? Answer: Shake Shack."),
    ("scene_q08_18_whataburger.png", "Create original 16:9 quiz graphic. Show stylized orange-white flying W shape with Texas map. Question: What fast food chain? Answer: Whataburger."),
    ("scene_q08_19_jack_in_box.png", "Create original 16:9 quiz graphic. Show stylized jack-in-the-box toy with clown head. Question: What fast food chain? Answer: Jack in the Box."),
    ("scene_q08_20_hardees.png", "Create original 16:9 quiz graphic. Show stylized yellow star on red background. Question: What fast food chain? Answer: Hardee's / Carl's Jr."),
    ("outro_quiz8.png", "Create an original 16:9 quiz-show outro celebration scoreboard. Confetti, festive energy, no copied branding."),
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
