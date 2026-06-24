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
    ("opening_title_50_state_challenge.png", "dramatic American patriotic quiz show stage, giant glowing red white blue star burst, USA flags, spotlights, dark studio, confetti falling, cinematic wide shot"),
    ("round_01_warm_up.png", "warm cozy quiz show TV studio stage, bright yellow orange lighting, glowing USA map outline on screen, neon colors, game show atmosphere"),
    ("scene_q01_grand_canyon_arizona.png", "Grand Canyon Arizona, dramatic layered red rock formations, Colorado River far below, golden hour sunlight, wide cinematic aerial view"),
    ("scene_q02_california_capital.png", "Sacramento California state capitol building golden dome, palm trees, sunny blue sky, wide angle architecture photography"),
    ("scene_q03_mount_rushmore_south_dakota.png", "Mount Rushmore South Dakota, four presidents carved in granite, Black Hills pine forest, blue sky white clouds"),
    ("scene_q04_sunshine_state_florida.png", "Florida Miami South Beach, turquoise ocean, white sand beach, palm trees, bright sunshine, tropical paradise aerial"),
    ("scene_q05_las_vegas_nevada.png", "Las Vegas Nevada Strip at night, neon casino signs, bright lights, Welcome to Las Vegas sign, desert city skyline"),
    ("scene_q06_texas_capital_austin.png", "Austin Texas state capitol building, Congress Avenue boulevard, modern city skyline, sunny day"),
    ("scene_q07_statue_liberty_new_york.png", "Statue of Liberty New York Harbor, torch raised, Manhattan skyline, blue sky, aerial photography"),
    ("scene_q08_nashville_tennessee.png", "Nashville Tennessee Broadway honky-tonk street at night, neon signs, guitar shops, country music city, vibrant nightlife"),
    ("scene_q09_yellowstone_wyoming.png", "Yellowstone Wyoming Old Faithful geyser erupting, steam column against blue sky, bison in meadow, national park"),
    ("scene_q10_wisconsin_cheese_packers.png", "Wisconsin Green Bay Packers Lambeau Field football stadium aerial view, green gold colors, dairy farm rolling hills"),
    ("round_02_getting_sharper.png", "colorful pencils sunburst pattern from above, red blue yellow pencils sharp tips, patriotic colors, clean studio"),
    ("scene_q11_denver_colorado.png", "Denver Colorado skyline with snow-capped Rocky Mountains, Mile High City, modern skyscrapers, clear blue sky"),
    ("scene_q12_space_needle_washington.png", "Seattle Space Needle Washington state, futuristic tower against Mount Rainier, Puget Sound, Pacific Northwest skyline"),
    ("scene_q13_new_orleans_louisiana.png", "New Orleans Louisiana French Quarter, colorful Creole architecture, wrought iron balconies, jazz musicians, festive atmosphere"),
    ("scene_q14_peach_state_georgia.png", "Georgia peach orchard, ripe juicy peaches on tree, Atlanta skyline in distance, warm golden light"),
    ("scene_q15_boston_massachusetts.png", "Boston Massachusetts skyline, Charles River sailboats, Faneuil Hall, colonial and modern architecture, autumn foliage"),
    ("scene_q16_indianapolis_500_indiana.png", "Indianapolis Motor Speedway, Indy 500 race cars on oval track, packed grandstands, checkered flag, motion blur"),
    ("scene_q17_gateway_arch_missouri.png", "Gateway Arch St Louis Missouri, stainless steel arch against blue sky, Mississippi River below, city skyline"),
    ("scene_q18_portland_crater_lake_oregon.png", "Crater Lake Oregon, deepest blue volcanic caldera, Wizard Island, perfectly still reflection, dense pine forest rim"),
    ("scene_q19_phoenix_arizona.png", "Phoenix Arizona desert cityscape at sunset, saguaro cactus silhouettes, modern skyscrapers, orange purple sky"),
    ("scene_q20_detroit_great_lakes_michigan.png", "Detroit Michigan Renaissance Center skyline, Great Lakes aerial view, automotive city, dramatic clouds"),
    ("round_03_state_expert_mode.png", "USA map flat lay overhead, fifty states different pastel colors, dark dramatic background, glowing state borders"),
    ("scene_q21_acadia_maine.png", "Acadia National Park Maine, rocky pink granite Atlantic coastline, crashing waves, autumn foliage, rugged seascape"),
    ("scene_q22_montpelier_vermont.png", "Montpelier Vermont statehouse golden dome, maple trees peak fall foliage, Green Mountains background, New England"),
    ("scene_q23_land_enchantment_new_mexico.png", "New Mexico adobe pueblo village, Sandia Mountains pink sunset, turquoise sky, Native American Southwest"),
    ("scene_q24_bourbon_mardi_gras_louisiana.png", "New Orleans Mardi Gras parade, colorful festive floats, beads, masked revelers, Bourbon Street celebration"),
    ("scene_q25_des_moines_iowa.png", "Des Moines Iowa state capitol golden dome, endless cornfields horizon, Iowa State Fair ferris wheel, Midwest heartland"),
    ("scene_q26_badlands_black_hills_south_dakota.png", "South Dakota Badlands dramatic eroded landscape, sharp spires and buttes, golden hour light, stark barren beauty"),
    ("scene_q27_boise_idaho.png", "Boise Idaho skyline, state capitol, Snake River valley, rolling foothills, high desert western landscape"),
    ("scene_q28_horse_bluegrass_kentucky.png", "Kentucky bluegrass horse country, thoroughbred horses galloping, white wooden fencing, rolling hills, Churchill Downs"),
    ("scene_q29_raleigh_north_carolina.png", "Raleigh North Carolina Research Triangle skyline, dogwood trees blooming, state capitol, modern tech hub"),
    ("scene_q30_ozarks_hot_springs_arkansas.png", "Arkansas Ozark Mountains autumn colors, Hot Springs Bathhouse Row Victorian spa street, natural thermal steam"),
    ("round_04_harder_clues.png", "dark dramatic quiz show stage, deep blue purple lighting, glowing question mark symbols floating, fog machine, intense spotlights"),
    ("scene_q31_harrisburg_pennsylvania.png", "Harrisburg Pennsylvania state capitol ornate dome, Susquehanna River reflection, historic bridges, keystone state"),
    ("scene_q32_ocean_state_rhode_island.png", "Newport Rhode Island cliff walk, Breakers mansion, Atlantic Ocean, sailing yachts harbor, New England coastal beauty"),
    ("scene_q33_fargo_north_dakota.png", "North Dakota Great Plains flat landscape, golden wheat fields horizon, Theodore Roosevelt Badlands buttes, big sky"),
    ("scene_q34_topeka_kansas.png", "Topeka Kansas state capitol, bright sunflower fields foreground, Flint Hills prairie, wide open sky, great plains"),
    ("scene_q35_everglades_florida.png", "Florida Everglades, airboat in sawgrass prairie, alligator on bank, mangrove wetlands, subtropical wilderness"),
    ("scene_q36_charleston_lowcountry_south_carolina.png", "Charleston South Carolina Rainbow Row colorful pastel homes, church steeple, harbor at golden sunset, antebellum architecture"),
    ("scene_q37_juneau_alaska.png", "Juneau Alaska, Mendenhall Glacier blue ice, Inside Passage fjord mountains, floatplane harbor, snow-capped peaks"),
    ("scene_q38_omaha_nebraska.png", "Omaha Nebraska skyline Missouri River, golden cornfields Great Plains, Union Pacific railroad bridge, Midwest city"),
    ("scene_q39_santa_fe_new_mexico.png", "Santa Fe New Mexico Palace of the Governors plaza, adobe architecture, Sangre de Cristo Mountains, turquoise art market"),
    ("scene_q40_green_mountains_vermont.png", "Vermont Green Mountains Stowe ski resort, peak autumn foliage red orange yellow, covered bridge, maple syrup farm"),
    ("round_05_final_challenge.png", "golden trophy on pedestal center stage, confetti explosion red white blue, dramatic spotlights, fireworks burst, celebration finale"),
    ("scene_q41_frankfort_kentucky.png", "Frankfort Kentucky state capitol, Kentucky River gorge historic bridge, bourbon barrel rickhouse, bluegrass hills autumn"),
    ("scene_q42_first_state_delaware.png", "Delaware First State Dover capitol, Delaware River colonial heritage, historic district, East Coast autumn"),
    ("scene_q43_burlington_lake_champlain_vermont.png", "Burlington Vermont Lake Champlain waterfront, Adirondack Mountains across lake sunset, Green Mountains backdrop"),
    ("scene_q44_carson_city_nevada.png", "Carson City Nevada state capitol, Sierra Nevada mountains, historic silver mining town, Nevada desert landscape"),
    ("scene_q45_mobile_gulf_coast_alabama.png", "Mobile Alabama Gulf Coast, USS Alabama battleship memorial, white sand beaches, Southern azalea blossoms, port city"),
    ("scene_q46_helena_montana.png", "Helena Montana state capitol, Big Sky Country enormous sky, Rocky Mountains dramatic backdrop, Glacier National Park"),
    ("scene_q47_cheyenne_wyoming.png", "Cheyenne Wyoming state capitol, Frontier Days rodeo cowboys on horses, high plains western landscape, mountains"),
    ("scene_q48_white_mountains_new_hampshire.png", "New Hampshire White Mountains, Mount Washington summit, Presidential Range autumn foliage, covered bridge, granite state"),
    ("scene_q49_olympia_washington.png", "Olympia Washington state capitol dome, Puget Sound waterfront, Olympic Mountains snow-capped, evergreen forests"),
    ("scene_q50_mountain_state_west_virginia.png", "West Virginia New River Gorge arch bridge, spectacular autumn Appalachian foliage, whitewater rafting below"),
    ("outro_scoreboard.png", "game show scoreboard glowing golden tiles grid, celebration studio lights, confetti falling, victory atmosphere, dark background"),
    ("end_screen.png", "USA map illuminated glowing lights all fifty states, fireworks red white blue gold, dark night, patriotic celebration aerial view"),
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
