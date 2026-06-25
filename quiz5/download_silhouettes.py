#!/usr/bin/env python3
"""
Downloads animal silhouette SVGs from PhyloPic (public domain)
and converts them to quiz scene PNGs.

Run from quiz5/ folder:
  python3 download_silhouettes.py
"""

import os, requests, csv, time
from PIL import Image, ImageDraw, ImageFont
import cairosvg
from io import BytesIO

W, H = 1280, 720
OUTPUT_DIR = "images_and_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Animal name → PhyloPic search term
ANIMALS = {
    "Elephant": "Elephas maximus",
    "Giraffe": "Giraffa",
    "Dolphin": "Delphinus",
    "Lion": "Panthera leo",
    "Penguin": "Spheniscus",
    "Kangaroo": "Macropus",
    "Eagle": "Aquila",
    "Shark": "Carcharodon",
    "Gorilla": "Gorilla gorilla",
    "Flamingo": "Phoenicopterus",
    "Cheetah": "Acinonyx jubatus",
    "Crocodile": "Crocodylus",
    "Peacock": "Pavo cristatus",
    "Koala": "Phascolarctos",
    "Octopus": "Octopus",
    "Camel": "Camelus",
    "Panda": "Ailuropoda",
    "Bat": "Chiroptera",
    "Rhinoceros": "Ceratotherium",
    "Toucan": "Ramphastos",
    "Platypus": "Ornithorhynchus",
    "Manta Ray": "Manta birostris",
    "Wolverine": "Gulo gulo",
    "Mandrill": "Mandrillus sphinx",
    "Axolotl": "Ambystoma mexicanum",
    "Tapir": "Tapirus",
    "Okapi": "Okapia johnstoni",
    "Pangolin": "Manis",
    "Narwhal": "Monodon monoceros",
    "Quokka": "Setonix brachyurus",
    "Fossa": "Cryptoprocta ferox",
    "Binturong": "Arctictis binturong",
    "Aardvark": "Orycteropus afer",
    "Saiga Antelope": "Saiga tatarica",
    "Aye-aye": "Daubentonia madagascariensis",
    "Shoebill": "Balaeniceps rex",
    "Sun Bear": "Helarctos malayanus",
    "Gharial": "Gavialis gangeticus",
    "Kinkajou": "Potos flavus",
    "Tarsier": "Tarsius",
    "Gerenuk": "Litocranius walleri",
    "Maned Wolf": "Chrysocyon brachyurus",
    "Blobfish": "Psychrolutes marcidus",
    "Capybara": "Hydrochoerus hydrochaeris",
    "Numbat": "Myrmecobius fasciatus",
    "Irrawaddy Dolphin": "Orcaella brevirostris",
    "Thorny Devil": "Moloch horridus",
    "Hoatzin": "Opisthocomus hoazin",
    "Proboscis Monkey": "Nasalis larvatus",
    "Saola": "Pseudoryx nghetinhensis",
}

BG_COLORS = [
    "#FF6B35","#2196F3","#4CAF50","#FF3D3D","#9C27B0",
    "#FF5722","#00BCD4","#E91E63","#3F51B5","#FF9800",
    "#8BC34A","#F44336","#03A9F4","#E040FB","#009688",
    "#FF7043","#5C6BC0","#66BB6A","#FFA726","#26C6DA",
    "#EF5350","#7E57C2","#26A69A","#D4E157","#EC407A",
    "#42A5F5","#AB47BC","#26C6DA","#8D6E63","#78909C",
    "#FF7043","#5C6BC0","#66BB6A","#FFA726","#26C6DA",
    "#EF5350","#7E57C2","#26A69A","#D4E157","#EC407A",
    "#42A5F5","#AB47BC","#FF8A65","#81C784","#64B5F6",
    "#BA68C8","#4DD0E1","#DCE775","#F06292","#4FC3F7",
]

def load_font(size, bold=False):
    candidates = [
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def get_silhouette_svg(animal_name, search_term):
    """Fetch SVG silhouette from PhyloPic API v2"""
    try:
        # Search for the animal
        url = f"https://api.phylopic.org/images?filter_name={requests.utils.quote(search_term)}&page=0"
        r = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if r.status_code != 200:
            return None
        
        data = r.json()
        items = data.get("_embedded", {}).get("items", [])
        if not items:
            # Try simpler search
            url2 = f"https://api.phylopic.org/images?filter_name={requests.utils.quote(animal_name)}&page=0"
            r2 = requests.get(url2, timeout=15, headers={"Accept": "application/json"})
            if r2.status_code == 200:
                items = r2.json().get("_embedded", {}).get("items", [])
        
        if not items:
            return None
        
        # Get first result's SVG
        item = items[0]
        links = item.get("_links", {})
        
        # Try to get vector SVG
        svg_link = links.get("vectorFile", {}).get("href") or links.get("sourceFile", {}).get("href")
        if not svg_link:
            return None
        
        svg_r = requests.get(svg_link, timeout=15)
        if svg_r.status_code == 200 and b"<svg" in svg_r.content:
            return svg_r.content
    except Exception as e:
        print(f"    PhyloPic error: {e}")
    return None

def svg_to_black_silhouette(svg_bytes, target_w=500, target_h=400):
    """Convert SVG to black silhouette PNG"""
    try:
        # First convert to PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=target_w,
            output_height=target_h,
            background_color="white"
        )
        img = Image.open(BytesIO(png_data)).convert("RGBA")
        
        # Convert to black silhouette
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r,g,b,a = pixels[x,y]
                # If pixel is dark (part of drawing), make it black opaque
                brightness = (r+g+b)/3
                if brightness < 200 and a > 50:
                    pixels[x,y] = (0,0,0,255)
                else:
                    pixels[x,y] = (0,0,0,0)
        return img
    except Exception as e:
        print(f"    SVG convert error: {e}")
        return None

def make_quiz_scene(animal_name, silhouette_img, bg_color, q_num, out_path):
    """Create quiz scene with silhouette on colored background"""
    img = Image.new("RGB", (W,H), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Darker gradient overlay
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for y in range(H):
        alpha = int(60 * (1 - y/H))
        od.line([(0,y),(W,y)], fill=(0,0,0,alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Paste silhouette centered
    if silhouette_img:
        # Scale to fit nicely
        sil = silhouette_img.copy()
        max_w, max_h = 560, 380
        sil.thumbnail((max_w, max_h), Image.LANCZOS)
        sx = W//2 - sil.width//2
        sy = H//2 - sil.height//2 - 20
        img.paste(sil, (sx, sy), sil)
        draw = ImageDraw.Draw(img)
    else:
        # Fallback: big ? mark
        font_q_mark = load_font(300, bold=True)
        draw.text((W//2-90, H//2-180), "?", font=font_q_mark, fill=(255,255,255,80))
    
    # Question number badge
    font_num = load_font(42, bold=True)
    draw.rounded_rectangle([30,20,130,80], radius=25, fill=(0,0,0,120))
    qtext = f"#{q_num}"
    bbox = draw.textbbox((0,0), qtext, font=font_num)
    tw = bbox[2]-bbox[0]
    draw.text((80-tw//2, 30), qtext, font=font_num, fill="#FFFFFF")
    
    # Question text
    font_qt = load_font(58, bold=True)
    question = "What animal is this?"
    bbox = draw.textbbox((0,0), question, font=font_qt)
    tw = bbox[2]-bbox[0]
    qy = 20
    draw.rounded_rectangle([W//2-tw//2-30, qy, W//2+tw//2+30, qy+80], radius=40, fill=(0,0,0,160))
    draw.text((W//2-tw//2, qy+10), question, font=font_qt, fill="#FFFFFF")
    
    # Answer pill at bottom
    font_ans = load_font(72, bold=True)
    bbox = draw.textbbox((0,0), animal_name, font=font_ans)
    tw = bbox[2]-bbox[0]
    ay = H-130
    draw.rounded_rectangle([W//2-tw//2-40, ay, W//2+tw//2+40, ay+95], radius=48, fill="#FFD700")
    draw.text((W//2-tw//2, ay+8), animal_name, font=font_ans, fill="#1a0a3d")
    
    # QUIZ GO badge
    font_badge = load_font(30, bold=True)
    badge = "QUIZ GO!"
    bbox = draw.textbbox((0,0), badge, font=font_badge)
    bw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-bw-60, H-60, W-10, H-10], radius=25, fill=(255,215,0,200))
    draw.text((W-bw-35, H-54), badge, font=font_badge, fill="#1a0a3d")
    
    img.save(out_path)
    return True

def main():
    print("🦁 Animal Silhouette Downloader")
    print("   Source: PhyloPic (public domain SVGs)\n")
    
    animals_list = list(ANIMALS.items())
    
    for idx, (animal_name, search_term) in enumerate(animals_list):
        q_num = idx + 1
        fname = f"scene_q{idx+1:02d}_{animal_name.lower().replace(' ','_').replace('-','_')}.png"
        out_path = os.path.join(OUTPUT_DIR, fname)
        
        if os.path.exists(out_path):
            print(f"  ⏭  skip: {animal_name}"); continue
        
        print(f"  [{q_num:2d}/50] {animal_name}...")
        
        # Download SVG
        svg = get_silhouette_svg(animal_name, search_term)
        
        if svg:
            sil = svg_to_black_silhouette(svg)
            print(f"         ✅ SVG downloaded")
        else:
            print(f"         ⚠️  No SVG found — using placeholder")
            sil = None
        
        bg = BG_COLORS[idx % len(BG_COLORS)]
        make_quiz_scene(animal_name, sil, bg, q_num, out_path)
        
        time.sleep(0.5)  # rate limit
    
    print(f"\n✅ Done! Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
