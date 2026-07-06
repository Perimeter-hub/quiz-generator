#!/usr/bin/env python3
"""Quiz 12: Guess the Movie by Scene — Image Generator (ModelsLab API)
Usage: python3 generate_images.py
Requires: MODELSLAB_API_KEY in .env
Uses evocative movie SCENES (not logos/characters) to avoid copyright issues —
the location/atmosphere hints at the film without reproducing any copyrighted stills.
"""
import requests, os, time, csv
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

API_KEY   = os.getenv("MODELSLAB_API_KEY", "HiGIQ9YkIi8EheOqsQIihBv4LUlRqN1IPfFU06ahv9xRawbfRULcg3jJb5CM")
API_URL   = "https://modelslab.com/api/v6/realtime/text2img"
FETCH_URL = "https://modelslab.com/api/v6/realtime/fetch/"
CSV_FILE  = "batch_generation_queue.csv"
OUTPUT_DIR = "images_and_videos"
NEG = "blurry, low quality, distorted, ugly, watermark, text, letters, words, writing, typography, cartoon, anime, people, faces, persons, copyrighted characters, logos"

CARD_PROMPTS = {
    "opening_title.png":            "dramatic cinema film reel montage, glowing movie theater screen, popcorn, red curtains, spotlight beams, dark cinematic studio, no text",
    "round_01_easy_classics.png":   "classic cinema marquee lights glowing warm, vintage movie theater entrance, film strip decoration, no text",
    "round_02_getting_harder.png":  "dark movie theater rows of empty seats projector light beam, mysterious atmosphere, no text",
    "round_03_expert_mode.png":     "film noir style dark cinema, dramatic shadows, single spotlight on empty stage, no text",
    "round_04_final_challenge.png": "golden movie award statuettes on pedestal, red carpet, spotlights, celebration atmosphere, no text",
    "outro_scoreboard.png":         "cinema scoreboard style screen glowing, film reels, celebration lights, dark background, no text no numbers",
    "end_screen.png":               "movie theater packed with glowing screens, popcorn, film reels scattered, cozy cinema night, no text",
}

def load_images():
    images = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fn = row["file_name"]
            hint = row["prompt_hint"].strip()
            atype = row["asset_type"]
            if atype in ("title_card", "outro"):
                prompt = CARD_PROMPTS.get(fn)
                if not prompt: continue
            elif atype == "question_scene":
                if not hint: continue
                prompt = hint + ", cinematic wide shot, ultra photorealistic, 8k, dramatic lighting, professional cinematography, atmospheric"
            else:
                continue
            images.append((fn, prompt))
    return images

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
    payload = {
        "key": API_KEY, "prompt": prompt, "negative_prompt": NEG,
        "width": "1024", "height": "576", "samples": "1",
        "num_inference_steps": "30", "guidance_scale": 7.5,
        "safety_checker": "no", "enhance_prompt": "yes", "seed": None,
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=60); r.raise_for_status()
        data = r.json()
        image_url = None
        if data.get("status") == "success" and data.get("output"): image_url = data["output"][0]
        elif data.get("status") == "processing" and data.get("id"):
            print(f"  ⏳ polling... {filename}")
            image_url = poll_fetch(data["id"])
        else: raise Exception(data.get("message") or str(data)[:200])
        img_r = requests.get(image_url, timeout=60); img_r.raise_for_status()
        with open(out_path, "wb") as f: f.write(img_r.content)
        print(f"  ✓  {filename}"); return True
    except Exception as e:
        print(f"  ✗  {filename}: {e}"); return False

def main():
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: {CSV_FILE} not found."); return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    images = load_images()
    total = len(images)
    print(f"Generating {total} images → ./{OUTPUT_DIR}/\n")
    errors = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(generate_one, fn, p): fn for fn, p in images}
        done = 0
        for future in as_completed(futures):
            fn = futures[future]; done += 1
            if not future.result(): errors.append(fn)
            print(f"  [{done}/{total}]")
    print(f"\nDone: {total-len(errors)}/{total}")
    if errors: [print(f"  ✗ {e}") for e in errors]
    print("\nNext: python3 ../shared/make_quiz_video.py")

if __name__ == "__main__":
    main()
