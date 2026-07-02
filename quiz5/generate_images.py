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
NEG = "text, letters, words, writing, typography, watermark, logo, signature, caption, subtitle, title, label, sign, banner, blurry, low quality, distorted, ugly, cartoon, anime, painting, drawing"

IMAGES = [
    ("opening_title_animal_silhouette.png", "Create an original 16:9 bright 2D quiz-show title card. Show dramatic animal silhouettes (lion, elephant, eagle, dolphin) glowing on dark background with spotlight effects. Bold text: GUESS THE ANIMAL! Saturated colors, strong contrast, mobile-readable. No copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EASY. Show bright jungle background, simple animal outline shapes, 10 progress dots. Bold clean typography. No copied identity."),
    ("scene_q01_elephant.png", "wildlife photography, Elephant, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q02_giraffe.png", "wildlife photography, Giraffe, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q03_dolphin.png", "wildlife photography, Dolphin, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q04_lion.png", "wildlife photography, Lion, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q05_penguin.png", "wildlife photography, Penguin, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q06_kangaroo.png", "wildlife photography, Kangaroo, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q07_eagle.png", "wildlife photography, Eagle, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q08_shark.png", "wildlife photography, Shark, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q09_gorilla.png", "wildlife photography, Gorilla, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q10_flamingo.png", "wildlife photography, Flamingo, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("round_02_medium.png", "Create an original 16:9 round card reading ROUND 2: MEDIUM. Forest background, animal silhouette hints, progress dots 11-20. Bold clean text, original design."),
    ("scene_q11_cheetah.png", "wildlife photography, Cheetah, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q12_crocodile.png", "wildlife photography, Crocodile, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q13_peacock.png", "wildlife photography, Peacock, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q14_koala.png", "wildlife photography, Koala, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q15_octopus.png", "wildlife photography, Octopus, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q16_camel.png", "wildlife photography, Camel, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q17_panda.png", "wildlife photography, Panda, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q18_bat.png", "wildlife photography, Bat, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q19_rhinoceros.png", "wildlife photography, Rhinoceros, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q20_toucan.png", "wildlife photography, Toucan, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("round_03_tricky.png", "Create an original 16:9 round card reading ROUND 3: TRICKY. Dark mysterious atmosphere, harder animal shape hints, progress dots 21-30. Original bold design."),
    ("scene_q21_platypus.png", "wildlife photography, Platypus, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q22_manta_ray.png", "wildlife photography, Manta Ray, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q23_wolverine_animal.png", "wildlife photography, Wolverine, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q24_mandrill.png", "wildlife photography, Mandrill, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q25_axolotl.png", "wildlife photography, Axolotl, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q26_tapir.png", "wildlife photography, Tapir, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q27_okapi.png", "wildlife photography, Okapi, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q28_pangolin.png", "wildlife photography, Pangolin, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q29_narwhal.png", "wildlife photography, Narwhal, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q30_quokka.png", "wildlife photography, Quokka, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("round_04_expert.png", "Create an original 16:9 round card reading ROUND 4: EXPERT. Dramatic dark atmosphere, glowing edge animal silhouettes, progress dots 31-40. Original intense quiz-show design."),
    ("scene_q31_fossa.png", "wildlife photography, Fossa, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q32_binturong.png", "wildlife photography, Binturong, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q33_aardvark.png", "wildlife photography, Aardvark, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q34_saiga.png", "wildlife photography, Saiga Antelope, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q35_aye_aye.png", "wildlife photography, Aye-aye, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q36_shoebill.png", "wildlife photography, Shoebill, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q37_sun_bear.png", "wildlife photography, Sun Bear, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q38_gharial.png", "wildlife photography, Gharial, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q39_kinkajou.png", "wildlife photography, Kinkajou, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q40_tarsier.png", "wildlife photography, Tarsier, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("round_05_ultimate.png", "Create an original 16:9 round card reading ROUND 5: ULTIMATE CHALLENGE. Epic gold glowing atmosphere, most exotic animal silhouettes, final 10 progress dots 41-50. Original dramatic design."),
    ("scene_q41_gerenuk.png", "wildlife photography, Gerenuk, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q42_maned_wolf.png", "wildlife photography, Maned Wolf, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q43_blobfish.png", "wildlife photography, Blobfish, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q44_capybara.png", "wildlife photography, Capybara, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q45_numbat.png", "wildlife photography, Numbat, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q46_irrawaddy_dolphin.png", "wildlife photography, Irrawaddy Dolphin, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q47_thorny_devil.png", "wildlife photography, Thorny Devil, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q48_hoatzin.png", "wildlife photography, Hoatzin, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q49_proboscis_monkey.png", "wildlife photography, Proboscis Monkey, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("scene_q50_saola.png", "wildlife photography, Saola, dramatic studio lighting, isolated on solid colored background, full body shot, ultra realistic, 8k"),
    ("outro_scoreboard.png", "Create an original 16:9 quiz-show outro card. Show a glowing scoreboard with score ranges, celebration confetti, collage of animal silhouettes from the quiz. Text: How many did you get right? Bold clean design, festive energy. No copied branding."),
    ("end_screen_animals.png", "Create an original 16:9 end screen for Quiz Blitz Go channel. Show subscribe button prompt, bell notification icon, animal silhouettes background, text: Subscribe for more quizzes every day! Bold readable design, channel branding energy."),
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
