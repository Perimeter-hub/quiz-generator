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
    ("opening_title_quiz6.png", "Create an original 16:9 quiz-show title card for a world flags quiz. Colorful flags of the world arranged dramatically, bold text GUESS THE FLAG, globe motif, bright saturated colors, no copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EASY FLAGS. Bold clean typography, original design, no copied branding."),
    ("scene_q06_01_usa.png", "Create an original 16:9 quiz graphic. Show a large bold flat illustration of the UNITED STATES FLAG (red and white stripes, blue canton with 50 white stars) centered on dark background. Question: Which country does this flag belong to? Answer card: United States. Bold readable text, original design."),
    ("scene_q06_02_japan.png", "Create an original 16:9 quiz graphic. Show the JAPAN FLAG (white background, single red circle centered) large and bold. Question: Which country? Answer: Japan. Clean minimal design."),
    ("scene_q06_03_canada.png", "Create an original 16:9 quiz graphic. Show the CANADA FLAG (red-white-red vertical bands, red maple leaf center) large and bold. Question: Which country? Answer: Canada."),
    ("scene_q06_04_uk.png", "Create an original 16:9 quiz graphic. Show the UK UNION JACK FLAG (blue background, red and white cross and diagonal cross) large and bold. Question: Which country? Answer: United Kingdom."),
    ("scene_q06_05_brazil.png", "Create an original 16:9 quiz graphic. Show the BRAZIL FLAG (green background, yellow diamond, blue circle with stars and band) large and bold. Question: Which country? Answer: Brazil."),
    ("scene_q06_06_australia.png", "Create an original 16:9 quiz graphic. Show the AUSTRALIA FLAG (blue background, Union Jack top left, Southern Cross stars, Commonwealth star) large and bold. Question: Which country? Answer: Australia."),
    ("scene_q06_07_france.png", "Create an original 16:9 quiz graphic. Show the FRANCE FLAG (blue, white, red vertical bands) large and bold. Question: Which country? Answer: France."),
    ("scene_q06_08_germany.png", "Create an original 16:9 quiz graphic. Show the GERMANY FLAG (black, red, gold horizontal bands) large and bold. Question: Which country? Answer: Germany."),
    ("scene_q06_09_china.png", "Create an original 16:9 quiz graphic. Show the CHINA FLAG (red background, large yellow star with four smaller yellow stars) large and bold. Question: Which country? Answer: China."),
    ("scene_q06_10_india.png", "Create an original 16:9 quiz graphic. Show the INDIA FLAG (saffron, white, green horizontal bands, blue Ashoka Chakra wheel in center) large and bold. Question: Which country? Answer: India."),
    ("round_02_medium.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 2: MEDIUM FLAGS. Bold clean typography, original design, no copied branding."),
    ("scene_q06_11_turkey.png", "Create an original 16:9 quiz graphic. Show the TURKEY FLAG (red background, white crescent moon and white star) large and bold. Question: Which country? Answer: Turkey."),
    ("scene_q06_12_south_korea.png", "Create an original 16:9 quiz graphic. Show the SOUTH KOREA FLAG (white background, red-blue taeguk circle, black trigrams in corners) large and bold. Question: Which country? Answer: South Korea."),
    ("scene_q06_13_mexico.png", "Create an original 16:9 quiz graphic. Show the MEXICO FLAG (green, white, red vertical bands, eagle with snake on cactus coat of arms in center) large and bold. Question: Which country? Answer: Mexico."),
    ("scene_q06_14_switzerland.png", "Create an original 16:9 quiz graphic. Show the SWITZERLAND FLAG (red square background, white plus cross centered) large and bold. Question: Which country? Answer: Switzerland."),
    ("scene_q06_15_south_africa.png", "Create an original 16:9 quiz graphic. Show the SOUTH AFRICA FLAG (horizontal Y-shape design with green, yellow, black, red, white, blue) large and bold. Question: Which country? Answer: South Africa."),
    ("scene_q06_16_norway.png", "Create an original 16:9 quiz graphic. Show the NORWAY FLAG (red background, blue cross outlined in white, offset to left) large and bold. Question: Which country? Answer: Norway."),
    ("scene_q06_17_argentina.png", "Create an original 16:9 quiz graphic. Show the ARGENTINA FLAG (light blue, white, light blue horizontal bands, yellow Sol de Mayo sun in center) large and bold. Question: Which country? Answer: Argentina."),
    ("scene_q06_18_portugal.png", "Create an original 16:9 quiz graphic. Show the PORTUGAL FLAG (green left third, red right two-thirds, armillary sphere and shield coat of arms on border) large and bold. Question: Which country? Answer: Portugal."),
    ("scene_q06_19_new_zealand.png", "Create an original 16:9 quiz graphic. Show the NEW ZEALAND FLAG (blue background, Union Jack top left, four red stars with white borders Southern Cross) large and bold. Question: Which country? Answer: New Zealand."),
    ("scene_q06_20_ukraine.png", "Create an original 16:9 quiz graphic. Show the UKRAINE FLAG (top half blue sky, bottom half golden yellow wheat field) large and bold. Question: Which country? Answer: Ukraine."),
    ("round_03_tricky.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 3: TRICKY FLAGS. Bold clean typography, original design, no copied branding."),
    ("scene_q06_21_nepal.png", "Create an original 16:9 quiz graphic. Show the NEPAL FLAG (unique double-pennant shape, only non-rectangular national flag, crimson red with blue border, white moon and sun symbols) large and bold. Question: Which country? Answer: Nepal."),
    ("scene_q06_22_bhutan.png", "Create an original 16:9 quiz graphic. Show the BHUTAN FLAG (diagonal split orange upper right and yellow-orange lower left, white Thunder Dragon in center) large and bold. Question: Which country? Answer: Bhutan."),
    ("scene_q06_23_cambodia.png", "Create an original 16:9 quiz graphic. Show the CAMBODIA FLAG (blue, wide red center with white Angkor Wat silhouette, blue bands) large and bold. Question: Which country? Answer: Cambodia."),
    ("scene_q06_24_mozambique.png", "Create an original 16:9 quiz graphic. Show the MOZAMBIQUE FLAG (green, black, yellow horizontal bands with red triangle, white star, open book, crossed hoe and AK-47) large and bold. Question: Which country? Answer: Mozambique. Fun fact: only flag with an assault rifle!"),
    ("scene_q06_25_kiribati.png", "Create an original 16:9 quiz graphic. Show the KIRIBATI FLAG (red upper half with yellow rising sun and golden frigate bird in flight, blue and white wavy stripes lower) large and bold. Question: Which country? Answer: Kiribati."),
    ("scene_q06_26_sri_lanka.png", "Create an original 16:9 quiz graphic. Show the SRI LANKA FLAG (maroon background, golden lion holding sword, four Bo leaves, vertical green and saffron stripes) large and bold. Question: Which country? Answer: Sri Lanka."),
    ("scene_q06_27_albania.png", "Create an original 16:9 quiz graphic. Show the ALBANIA FLAG (red background, black double-headed eagle centered) large and bold. Question: Which country? Answer: Albania."),
    ("scene_q06_28_papua_new_guinea.png", "Create an original 16:9 quiz graphic. Show the PAPUA NEW GUINEA FLAG (diagonal split red upper left, black lower right, golden Raggiana Bird of Paradise on red, Southern Cross stars on black) large and bold. Question: Which country? Answer: Papua New Guinea."),
    ("scene_q06_29_trinidad.png", "Create an original 16:9 quiz graphic. Show the TRINIDAD AND TOBAGO FLAG (red background, diagonal black stripe from upper left to lower right with white borders each side) large and bold. Question: Which country? Answer: Trinidad and Tobago."),
    ("scene_q06_30_lesotho.png", "Create an original 16:9 quiz graphic. Show the LESOTHO FLAG (blue, white, green horizontal bands, black Basotho hat in center) large and bold. Question: Which country? Answer: Lesotho."),
    ("outro_quiz6.png", "Create an original 16:9 quiz-show outro scoreboard card. Celebration confetti, score ranges, festive energy. No copied branding."),
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
