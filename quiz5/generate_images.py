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
    ("opening_title_animal_silhouette.png", "Create an original 16:9 bright 2D quiz-show title card. Show dramatic animal silhouettes (lion, elephant, eagle, dolphin) glowing on dark background with spotlight effects. Bold text: GUESS THE ANIMAL! Saturated colors, strong contrast, mobile-readable. No copied branding."),
    ("round_01_easy.png", "Create an original 16:9 bright 2D quiz-show round card reading ROUND 1: EASY. Show bright jungle background, simple animal outline shapes, 10 progress dots. Bold clean typography. No copied identity."),
    ("scene_q01_elephant.png", "Create an original 16:9 quiz-show graphic for Question 1. Show a bold black silhouette of an ELEPHANT (large body, trunk raised, big ears, tusks) on a bright orange-yellow background. Include question text: What animal is this? Include reveal-ready answer card for Elephant. Bold clean typography, mobile-readable, no copied branding."),
    ("scene_q02_giraffe.png", "Create an original 16:9 quiz-show graphic for Question 2. Show a bold black silhouette of a GIRAFFE (very tall, long neck, small horns, long legs) on bright teal background. Question text: What animal is this? Answer card: Giraffe. Mobile-readable bold text, original design."),
    ("scene_q03_dolphin.png", "Create an original 16:9 quiz-show graphic for Question 3. Show a bold black silhouette of a DOLPHIN leaping from waves on bright blue ocean background. Question text: What animal is this? Answer card: Dolphin. Clean bold typography, original quiz-show style."),
    ("scene_q04_lion.png", "Create an original 16:9 quiz-show graphic for Question 4. Show a bold black silhouette of a LION (large mane around head, muscular body, tail with tuft) on golden savanna background. Question: What animal is this? Answer: Lion. Bold readable text."),
    ("scene_q05_penguin.png", "Create an original 16:9 quiz-show graphic for Question 5. Show a bold black silhouette of a PENGUIN (upright, round body, flippers, distinctive beak) on icy blue-white background. Question: What animal is this? Answer: Penguin. Original design, no copied layouts."),
    ("scene_q06_kangaroo.png", "Create an original 16:9 quiz-show graphic for Question 6. Show a bold black silhouette of a KANGAROO (large hind legs, small front paws, long tail, joey visible in pouch) on warm orange outback background. Question: What animal is this? Answer: Kangaroo."),
    ("scene_q07_eagle.png", "Create an original 16:9 quiz-show graphic for Question 7. Show a bold black silhouette of an EAGLE with wings fully spread in flight, on dramatic sky blue-red background. Question: What animal is this? Answer: Eagle. Bold mobile-readable text."),
    ("scene_q08_shark.png", "Create an original 16:9 quiz-show graphic for Question 8. Show a bold black silhouette of a SHARK (streamlined body, large dorsal fin, tail fin, pointed snout) on deep ocean blue background. Question: What animal is this? Answer: Shark."),
    ("scene_q09_gorilla.png", "Create an original 16:9 quiz-show graphic for Question 9. Show a bold black silhouette of a GORILLA (massive shoulders, knuckle-walking posture, large head) on jungle green background. Question: What animal is this? Answer: Gorilla."),
    ("scene_q10_flamingo.png", "Create an original 16:9 quiz-show graphic for Question 10. Show a bold black silhouette of a FLAMINGO standing on one leg, long curved neck, distinctive beak, on pink-purple sunset background. Question: What animal is this? Answer: Flamingo."),
    ("round_02_medium.png", "Create an original 16:9 round card reading ROUND 2: MEDIUM. Forest background, animal silhouette hints, progress dots 11-20. Bold clean text, original design."),
    ("scene_q11_cheetah.png", "Create an original 16:9 quiz-show graphic for Question 11. Bold black silhouette of a CHEETAH (slender body, long legs, small head, mid-sprint pose) on golden grass background. Question: What animal is this? Answer: Cheetah."),
    ("scene_q12_crocodile.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a CROCODILE (long flat body, bumpy ridged back, wide jaw, short legs) on murky green-brown river background. Question: What animal is this? Answer: Crocodile."),
    ("scene_q13_peacock.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a PEACOCK with magnificent fan tail fully spread (large circular fan pattern, crown on head) on purple-teal background. Question: What animal is this? Answer: Peacock."),
    ("scene_q14_koala.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a KOALA clinging to eucalyptus branch (round fluffy ears, compact body, strong claws gripping) on soft green-grey Australian background. Question: What animal is this? Answer: Koala."),
    ("scene_q15_octopus.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an OCTOPUS (round head, eight tentacles curling outward with sucker hints) on deep blue ocean background. Question: What animal is this? Answer: Octopus."),
    ("scene_q16_camel.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a BACTRIAN CAMEL (two humps clearly visible, long neck, knobby knees) on desert sand dune background. Question: What animal is this? Answer: Camel."),
    ("scene_q17_panda.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a GIANT PANDA (round body, distinctive black patches around eyes visible in shape, sitting and holding bamboo) on soft green bamboo forest background. Question: What animal is this? Answer: Panda."),
    ("scene_q18_bat.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a BAT with wings fully spread in flight (membrane wings, pointed ears, upside-down hanging pose) on dark purple night sky background with moon. Question: What animal is this? Answer: Bat."),
    ("scene_q19_rhinoceros.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a RHINOCEROS (massive body, large front horn clearly visible, armored-looking thick skin folds, short legs) on African grassland background. Question: What animal is this? Answer: Rhinoceros."),
    ("scene_q20_toucan.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a TOUCAN (small body, disproportionately enormous long curved beak, perched on branch) on bright tropical green background. Question: What animal is this? Answer: Toucan."),
    ("round_03_tricky.png", "Create an original 16:9 round card reading ROUND 3: TRICKY. Dark mysterious atmosphere, harder animal shape hints, progress dots 21-30. Original bold design."),
    ("scene_q21_platypus.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a PLATYPUS (duck-like flat bill, furry compact body, broad flat tail like beaver, webbed feet) on Australian creek background. Question: What animal is this? Answer: Platypus."),
    ("scene_q22_manta_ray.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a MANTA RAY (very wide flat diamond-wing shape, long thin tail, cephalic fins curled at front) gliding through ocean blue background. Question: What animal is this? Answer: Manta Ray."),
    ("scene_q23_wolverine_animal.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a WOLVERINE ANIMAL (stocky muscular body, low to ground, bushy tail, large paws, fierce posture) on snowy forest background. Question: What animal is this? Answer: Wolverine."),
    ("scene_q24_mandrill.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a MANDRILL (large primate, distinctive elongated muzzle ridge visible in profile, stocky body, short tail) on jungle background. Question: What animal is this? Answer: Mandrill."),
    ("scene_q25_axolotl.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an AXOLOTL (salamander body, distinctive feathery external gill plumes on head, four legs, wide head, long tail) on dark aquatic blue background. Question: What animal is this? Answer: Axolotl."),
    ("scene_q26_tapir.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a TAPIR (stout pig-like body, distinctive short prehensile trunk-snout, rounded back) on South American rainforest background. Question: What animal is this? Answer: Tapir."),
    ("scene_q27_okapi.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an OKAPI (body like a stocky giraffe but shorter neck, distinctively striped hindquarters and legs visible in silhouette shape) on Congo forest background. Question: What animal is this? Answer: Okapi."),
    ("scene_q28_pangolin.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a PANGOLIN (overlapping armor-plate scale texture clearly visible in silhouette, curled into ball or walking with long snout) on dark forest floor background. Question: What animal is this? Answer: Pangolin."),
    ("scene_q29_narwhal.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a NARWHAL (dolphin-like body, single very long spiral tusk protruding from forehead, no dorsal fin, mottled pattern hint) in Arctic ocean blue background. Question: What animal is this? Answer: Narwhal."),
    ("scene_q30_quokka.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a QUOKKA (small round compact marsupial, short rounded ears, stubby tail, distinctive friendly upright sitting posture) on Australian Rottnest Island background. Question: What animal is this? Answer: Quokka."),
    ("round_04_expert.png", "Create an original 16:9 round card reading ROUND 4: EXPERT. Dramatic dark atmosphere, glowing edge animal silhouettes, progress dots 31-40. Original intense quiz-show design."),
    ("scene_q31_fossa.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a FOSSA (cat-like carnivore, slender muscular body, very long thick tail nearly as long as body, pointed muzzle, large rounded ears) on Madagascar forest background. Question: What animal is this? Answer: Fossa."),
    ("scene_q32_binturong.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a BINTURONG (shaggy bear-like body, very long thick prehensile tail curled, low-slung posture, long tufted ears) on Southeast Asian rainforest canopy background. Question: What animal is this? Answer: Binturong."),
    ("scene_q33_aardvark.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an AARDVARK (very long tubular snout, huge rabbit-like upright ears, arched pig-like body, thick tapering tail) on African night savanna background. Question: What animal is this? Answer: Aardvark."),
    ("scene_q34_saiga.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a SAIGA ANTELOPE (distinctive enormously bulbous drooping nose dominating the profile, goat-like horns, stocky body) on Central Asian steppe background. Question: What animal is this? Answer: Saiga Antelope."),
    ("scene_q35_aye_aye.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an AYE-AYE (huge bat-like ears, very elongated skeletal middle finger visible, large eyes in profile, bushy tail, gripping branch) on dark Madagascar night background. Question: What animal is this? Answer: Aye-aye."),
    ("scene_q36_shoebill.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a SHOEBILL (very tall stork-like bird, extraordinarily wide deep shoe-shaped hooked bill dominating profile, standing still) on African swamp background. Question: What animal is this? Answer: Shoebill."),
    ("scene_q37_sun_bear.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a SUN BEAR (smallest bear species, compact body, distinctive pale chest patch shape visible as lighter area, very long tongue hint, large curved claws) on tropical forest background. Question: What animal is this? Answer: Sun Bear."),
    ("scene_q38_gharial.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a GHARIAL (extremely long very thin narrow snout with bulbous ghara tip, crocodilian body but much longer more slender jaws) in river background. Question: What animal is this? Answer: Gharial."),
    ("scene_q39_kinkajou.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a KINKAJOU (honey bear, small round-faced mammal, very long prehensile tail, hanging upside down from branch) on tropical rainforest night background. Question: What animal is this? Answer: Kinkajou."),
    ("scene_q40_tarsier.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a TARSIER (tiny primate, enormous round eyes dominating oversized head, extremely long fingers and toes gripping branch, very long hairless tail) on dark Philippine forest background. Question: What animal is this? Answer: Tarsier."),
    ("round_05_ultimate.png", "Create an original 16:9 round card reading ROUND 5: ULTIMATE CHALLENGE. Epic gold glowing atmosphere, most exotic animal silhouettes, final 10 progress dots 41-50. Original dramatic design."),
    ("scene_q41_gerenuk.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a GERENUK (extremely long giraffe-like neck, very long slender legs, small head, standing completely upright on hind legs reaching up for leaves) on African acacia background. Question: What animal is this? Answer: Gerenuk."),
    ("scene_q42_maned_wolf.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a MANED WOLF (fox-like face, extremely long stilt-like legs, slender body, large upright ears, mane ridge) on South American grassland background. Question: What animal is this? Answer: Maned Wolf."),
    ("scene_q43_blobfish.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a BLOBFISH (gelatinous drooping face, sad expression shape, bulbous droopy nose, soft formless body) on deep ocean dark background. Question: What animal is this? Answer: Blobfish."),
    ("scene_q44_capybara.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a CAPYBARA (world largest rodent, very large square boxy head, barrel-shaped body, semi-aquatic, short legs) half in river water background. Question: What animal is this? Answer: Capybara."),
    ("scene_q45_numbat.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a NUMBAT (small marsupial anteater, distinctive stripe pattern visible as texture in silhouette, long pointed snout, bushy upright tail) on Australian woodland background. Question: What animal is this? Answer: Numbat."),
    ("scene_q46_irrawaddy_dolphin.png", "Create an original 16:9 quiz graphic. Bold black silhouette of an IRRAWADDY DOLPHIN (distinctively round blunt melon head with NO beak at all, short dorsal fin, different from common dolphin) in Southeast Asian river background. Question: What animal is this? Answer: Irrawaddy Dolphin."),
    ("scene_q47_thorny_devil.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a THORNY DEVIL lizard (entire body covered in sharp conical spines visible as spiky outline, distinctive false head hump on neck, small real head, walking posture) on red Australian desert background. Question: What animal is this? Answer: Thorny Devil."),
    ("scene_q48_hoatzin.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a HOATZIN bird (distinctive tall spiky punk-rock crest on head, small face, chunky body, reddish-brown wing hints, perched on branch over Amazonian water) on Amazon rainforest background. Question: What animal is this? Answer: Hoatzin."),
    ("scene_q49_proboscis_monkey.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a PROBOSCIS MONKEY (male, with enormous pendulous drooping nose dominating face profile, pot-belly body, seated in tree) on Borneo mangrove background. Question: What animal is this? Answer: Proboscis Monkey."),
    ("scene_q50_saola.png", "Create an original 16:9 quiz graphic. Bold black silhouette of a SAOLA (critically endangered Asian unicorn, deer-antelope-like body, TWO very long straight parallel horns, distinctive white facial markings visible as shape detail) on misty Vietnamese forest background. Question: What animal is this? Answer: Saola — One of the rarest animals on Earth!"),
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
