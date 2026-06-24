#!/usr/bin/env python3
"""
Quiz DE Fußball — Image Generator via ModelsLab API
Run from your quiz folder (where images_and_videos/ will be created).
Usage: python generate_images_de_fussball.py
"""

import requests, os, time, csv
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY   = "HiGIQ9YkIi8EheOqsQIihBv4LUlRqN1IPfFU06ahv9xRawbfRULcg3jJb5CM"
API_URL   = "https://modelslab.com/api/v6/realtime/text2img"
FETCH_URL = "https://modelslab.com/api/v6/realtime/fetch/"
CSV_FILE  = "batch_generation_queue.csv"
OUTPUT_DIR = "images_and_videos"
NEG = "blurry, low quality, distorted, ugly, watermark, text, letters, words, writing, typography, cartoon, anime"

# Card images (no prompt in CSV — defined here)
CARD_PROMPTS = {
    "opening_title.png":           "dramatic football stadium at night, floodlights blazing, German flag colors black red gold, confetti falling, epic wide cinematic shot, no text",
    "round_01_aufwaermen.png":     "warm cozy football fan zone pub, big screen showing match, enthusiastic crowd, golden lighting, German flags, wide shot, no text",
    "round_02_wird_schwerer.png":  "intense football match action, players sprinting under stadium lights, dramatic shadows, cinematic wide shot, no text",
    "round_03_experten_modus.png": "historic football archive room, old trophies and medals on shelves, black and white photos on walls, dramatic lighting, no text",
    "round_04_harte_nuesse.png":   "dark dramatic football stadium, single spotlight on empty pitch, fog machine, intense atmosphere, wide cinematic, no text",
    "round_05_finale.png":         "golden World Cup trophy on pedestal, confetti explosion black red gold, spotlights, dark stadium background, epic cinematic, no text",
    "outro_scoreboard.png":        "football stadium scoreboard glowing at night, crowd silhouettes, dramatic lighting, celebration atmosphere, no text no numbers",
    "end_screen.png":              "German football fans celebrating, black red gold scarves, Bundesliga stadium packed, fireworks, joyful atmosphere, wide shot, no text",
}

def load_images_from_csv():
    images = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fn = row["file_name"]
            hint = row["prompt_hint"].strip()
            atype = row["asset_type"]

            if atype == "title_card" or atype == "outro":
                prompt = CARD_PROMPTS.get(fn)
                if not prompt:
                    continue
            elif atype == "question_scene":
                if not hint:
                    continue
                prompt = hint + ", ultra photorealistic, 8k, cinematic, professional sports photography, wide angle"
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
            if d.get("status") == "success" and d.get("output"):
                return d["output"][0]
            if d.get("status") == "error":
                raise Exception(d.get("message", "Fetch error"))
        except Exception as e:
            if i == max_tries - 1:
                raise
    raise Exception("Timed out")

def generate_one(filename, prompt):
    out_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(out_path):
        print(f"  ⏭  skip: {filename}")
        return True

    payload = {
        "key": API_KEY,
        "prompt": prompt,
        "negative_prompt": NEG,
        "width": "1024",
        "height": "576",
        "samples": "1",
        "num_inference_steps": "30",
        "guidance_scale": 7.5,
        "safety_checker": "no",
        "enhance_prompt": "yes",
        "seed": None,
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()

        image_url = None
        if data.get("status") == "success" and data.get("output"):
            image_url = data["output"][0]
        elif data.get("status") == "processing" and data.get("id"):
            print(f"  ⏳ polling... {filename}")
            image_url = poll_fetch(data["id"])
        else:
            raise Exception(data.get("message") or str(data)[:200])

        img_r = requests.get(image_url, timeout=60)
        img_r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(img_r.content)
        print(f"  ✓  {filename}")
        return True

    except Exception as e:
        print(f"  ✗  {filename}: {e}")
        return False

def main():
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: {CSV_FILE} not found. Put it next to this script.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    images = load_images_from_csv()
    total = len(images)
    print(f"Starting generation of {total} images → ./{OUTPUT_DIR}/\n")

    errors = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(generate_one, fn, prompt): fn for fn, prompt in images}
        done = 0
        for future in as_completed(futures):
            fn = futures[future]
            done += 1
            if not future.result():
                errors.append(fn)
            print(f"  [{done}/{total}]")

    print(f"\n{'='*40}")
    print(f"Done: {total - len(errors)}/{total}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("All images generated!")
    print("\nNext step: python ../shared/make_quiz_video.py")

if __name__ == "__main__":
    main()
