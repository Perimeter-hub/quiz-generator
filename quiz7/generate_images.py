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
    ("opening_quiz7.png", "Create an original 16:9 quiz-show title card for a movie emoji quiz. Bold popcorn, film reel, movie emojis arranged dramatically. Text: GUESS THE MOVIE! Bright cinematic colors, no copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EASY MOVIES. Bold clean typography, original design."),
    ("scene_q07_01_titanic.png", "Create original 16:9 quiz graphic. Show large bold emojis: ship, iceberg, broken heart (🚢❄️💔) on dark cinematic background. Question: What movie is this? Answer card: Titanic. Bold readable text."),
    ("scene_q07_02_frozen.png", "Create original 16:9 quiz graphic. Large emojis: snowflake, princess, mountain (❄️👸🏔️). Question: What movie? Answer: Frozen."),
    ("scene_q07_03_lion_king.png", "Create original 16:9 quiz graphic. Large emojis: lion, crown, sunrise (🦁👑🌅). Question: What movie? Answer: The Lion King."),
    ("scene_q07_04_jaws.png", "Create original 16:9 quiz graphic. Large emojis: shark, beach, scared face (🦈🏖️😱). Question: What movie? Answer: Jaws."),
    ("scene_q07_05_home_alone.png", "Create original 16:9 quiz graphic. Large emojis: house, scared face, boy (🏠😱👦). Question: What movie? Answer: Home Alone."),
    ("scene_q07_06_toy_story.png", "Create original 16:9 quiz graphic. Large emojis: cowboy, rocket, alien (🤠🚀👾). Question: What movie? Answer: Toy Story."),
    ("scene_q07_07_finding_nemo.png", "Create original 16:9 quiz graphic. Large emojis: tropical fish, waves, magnifying glass (🐠🌊🔍). Question: What movie? Answer: Finding Nemo."),
    ("scene_q07_08_shrek.png", "Create original 16:9 quiz graphic. Large emojis: onion, ogre, heart (🧅👹❤️). Question: What movie? Answer: Shrek."),
    ("scene_q07_09_up.png", "Create original 16:9 quiz graphic. Large emojis: house, balloons, old man (🏠🎈👴). Question: What movie? Answer: Up."),
    ("scene_q07_10_jurassic_park.png", "Create original 16:9 quiz graphic. Large emojis: dinosaur, leaves, scared face (🦕🌿😱). Question: What movie? Answer: Jurassic Park."),
    ("round_02_medium.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 2: MEDIUM MOVIES. Bold clean typography, original design."),
    ("scene_q07_11_forrest_gump.png", "Create original 16:9 quiz graphic. Large emojis: runner, chocolate box, feather (🏃🍫🪶). Question: What movie? Answer: Forrest Gump."),
    ("scene_q07_12_matrix.png", "Create original 16:9 quiz graphic. Large emojis: pill, green circle, sunglasses (💊🟢👓). Question: What movie? Answer: The Matrix."),
    ("scene_q07_13_inception.png", "Create original 16:9 quiz graphic. Large emojis: sleeping, spiral, cityscape (💤🌀🏙️). Question: What movie? Answer: Inception."),
    ("scene_q07_14_grease.png", "Create original 16:9 quiz graphic. Large emojis: microphone, lightning, car (🎤⚡🚗). Question: What movie? Answer: Grease."),
    ("scene_q07_15_top_gun.png", "Create original 16:9 quiz graphic. Large emojis: airplane, sunglasses, fire (✈️🕶️🔥). Question: What movie? Answer: Top Gun."),
    ("scene_q07_16_ghost.png", "Create original 16:9 quiz graphic. Large emojis: ghost, heart, pottery (👻❤️🏺). Question: What movie? Answer: Ghost."),
    ("scene_q07_17_interstellar.png", "Create original 16:9 quiz graphic. Large emojis: rocket, star, galaxy (🚀⭐🌌). Question: What movie? Answer: Interstellar."),
    ("scene_q07_18_beauty_beast.png", "Create original 16:9 quiz graphic. Large emojis: rose, beast monster, books (🌹👹📚). Question: What movie? Answer: Beauty and the Beast."),
    ("scene_q07_19_elf.png", "Create original 16:9 quiz graphic. Large emojis: Christmas tree, elf, spaghetti (🎄🧝🍝). Question: What movie? Answer: Elf."),
    ("scene_q07_20_mean_girls.png", "Create original 16:9 quiz graphic. Large emojis: dancers, nail polish, calendar (👯💅🗓️). Question: What movie? Answer: Mean Girls."),
    ("round_03_hard.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 3: HARD MOVIES. Bold clean typography, original design."),
    ("scene_q07_21_pulp_fiction.png", "Create original 16:9 quiz graphic. Large emojis: briefcase, syringe, dancer (💼💉💃). Question: What movie? Answer: Pulp Fiction."),
    ("scene_q07_22_silence_lambs.png", "Create original 16:9 quiz graphic. Large emojis: zipper mouth, sheep, mask (🤐🐑😷). Question: What movie? Answer: Silence of the Lambs."),
    ("scene_q07_23_shining.png", "Create original 16:9 quiz graphic. Large emojis: axe, hotel, snowflake (🪓🏨❄️). Question: What movie? Answer: The Shining."),
    ("scene_q07_24_cast_away.png", "Create original 16:9 quiz graphic. Large emojis: island, volleyball, silhouette (🏝️🏐👤). Question: What movie? Answer: Cast Away."),
    ("scene_q07_25_goodfellas.png", "Create original 16:9 quiz graphic. Large emojis: pistol, spaghetti, man in suit (🔫🍝🤵). Question: What movie? Answer: Goodfellas."),
    ("outro_quiz7.png", "Create an original 16:9 quiz-show outro celebration scoreboard. Confetti, festive energy, no copied branding."),
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
