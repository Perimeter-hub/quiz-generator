#!/usr/bin/env python3
"""
Quiz 2: Guess the US State by Shape — VIRAL EDITION
Bright gradients per round, glowing state silhouettes, energetic design.
Uses real US states GeoJSON. No geopandas needed.
Run from quiz2/ folder: python3 generate_shapes.py
"""

import os, json, ssl, urllib.request, csv, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = "images_and_videos"
W, H = 1280, 720
GEOJSON_URL = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
GEOJSON_PATH = "/tmp/us-states.json"

# Vibrant gradient themes per round (bg1, bg2, accent, glow)
ROUND_THEMES = {
    1: {"bg1": (20, 30, 90),   "bg2": (70, 25, 130),  "accent": "#00E5FF", "glow": (0, 200, 255)},
    2: {"bg1": (90, 20, 90),   "bg2": (140, 30, 80),  "accent": "#FF4D9D", "glow": (255, 80, 160)},
    3: {"bg1": (100, 40, 15),  "bg2": (150, 70, 20),  "accent": "#FFB300", "glow": (255, 180, 0)},
    4: {"bg1": (15, 70, 75),   "bg2": (20, 110, 95),  "accent": "#1DE9B6", "glow": (30, 230, 180)},
    5: {"bg1": (55, 20, 100),  "bg2": (100, 35, 140), "accent": "#B388FF", "glow": (180, 140, 255)},
}

def load_font(size, bold=True):
    for p in ["/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def hex_to_rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def download_geojson():
    if os.path.exists(GEOJSON_PATH):
        print("  ✓ GeoJSON cached")
    else:
        print("  Downloading US states GeoJSON...")
        ctx = ssl.create_default_context()
        ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        with urllib.request.urlopen(GEOJSON_URL, context=ctx) as r:
            data=r.read()
        with open(GEOJSON_PATH,'wb') as f: f.write(data)
        print("  ✓ Downloaded")
    with open(GEOJSON_PATH) as f:
        return json.load(f)

def get_coords(geometry):
    rings=[]
    if geometry["type"]=="Polygon":
        for ring in geometry["coordinates"]:
            rings.append([(c[0],c[1]) for c in ring])
    elif geometry["type"]=="MultiPolygon":
        for polygon in geometry["coordinates"]:
            for ring in polygon:
                rings.append([(c[0],c[1]) for c in ring])
    return rings

def normalize(rings, pad=120):
    allpts=[p for r in rings for p in r]
    if not allpts: return rings
    xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
    minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys)
    scale=min((W-pad*2)/(maxx-minx or 1),(H-pad*2-120)/(maxy-miny or 1))
    cx=(W-scale*(maxx-minx))/2
    cy=(H-scale*(maxy-miny))/2+20
    return [[(cx+(x-minx)*scale, cy+(maxy-y)*scale) for x,y in ring] for ring in rings]

def vertical_gradient(c1,c2):
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=(int(c1[0]*(1-t)+c2[0]*t),int(c1[1]*(1-t)+c2[1]*t),int(c1[2]*(1-t)+c2[2]*t)))
    return img

def add_glow_circles(img, glow_rgb):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for cx,cy,r in [(150,160,200),(W-170,200,170),(W-160,H-150,210),(180,H-170,160)]:
        od.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(*glow_rgb,20))
    ov=ov.filter(ImageFilter.GaussianBlur(45))
    return Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")

def rounded_pill(draw,cx,cy,text,font,fill,tcol,px=45,py=20):
    bbox=draw.textbbox((0,0),text,font=font); tw,th=bbox[2]-bbox[0],bbox[3]-bbox[1]
    x1,y1,x2,y2=cx-tw//2-px,cy-th//2-py,cx+tw//2+px,cy+th//2+py
    r=(y2-y1)//2
    draw.rounded_rectangle([x1+4,y1+5,x2+4,y2+5],radius=r,fill=(0,0,0,90))
    draw.rounded_rectangle([x1,y1,x2,y2],radius=r,fill=fill)
    draw.text((cx-tw//2,cy-th//2-bbox[1]),text,font=font,fill=tcol)

def make_state_scene(state, rings, q_num, theme, out_path):
    glow_rgb=theme["glow"]; accent=theme["accent"]
    img=vertical_gradient(theme["bg1"],theme["bg2"])
    img=add_glow_circles(img,glow_rgb)
    draw=ImageDraw.Draw(img,"RGBA")

    norm=normalize(rings)

    # Glow behind state shape
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    for ring in norm:
        if len(ring)>2: gd.polygon(ring,fill=(*glow_rgb,90))
    glow=glow.filter(ImageFilter.GaussianBlur(22))
    img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB")
    draw=ImageDraw.Draw(img,"RGBA")

    # Main white shape with accent outline
    for ring in norm:
        if len(ring)>2:
            draw.polygon(ring,fill=(245,248,255))
    for ring in norm:
        if len(ring)>2:
            draw.line(ring+[ring[0]],fill=hex_to_rgb(accent),width=4,joint="curve")

    # Question label top
    font_q=load_font(46,bold=True)
    rounded_pill(draw,W//2,72,"Which state is this?",font_q,(0,0,0,150),"#FFFFFF")

    # Number circle
    font_num=load_font(40,bold=True)
    draw.ellipse([35,35,105,105],fill=accent)
    nb=draw.textbbox((0,0),str(q_num),font=font_num); nw,nh=nb[2]-nb[0],nb[3]-nb[1]
    draw.text((70-nw//2,70-nh//2-nb[1]),str(q_num),font=font_num,fill="#1a0a2e")

    # QUIZ GO badge
    font_b=load_font(30,bold=True); btxt="QUIZ GO!"
    bb=draw.textbbox((0,0),btxt,font=font_b); bw=bb[2]-bb[0]
    draw.rounded_rectangle([W-bw-75,H-65,W-25,H-15],radius=25,fill=accent)
    draw.text((W-bw-50,H-58),btxt,font=font_b,fill="#1a0a2e")

    img.save(out_path)

def make_title_card(text, theme, out_path):
    img=vertical_gradient(theme["bg1"],theme["bg2"])
    img=add_glow_circles(img,theme["glow"])
    draw=ImageDraw.Draw(img,"RGBA")
    font=load_font(82,bold=True)
    words=text.split()
    if len(text)>16 and len(words)>1:
        mid=(len(words)+1)//2
        lines=[" ".join(words[:mid])," ".join(words[mid:])]
    else: lines=[text]
    cy=H//2
    for i,line in enumerate(lines):
        y=cy-(len(lines)-1)*65+i*130
        rounded_pill(draw,W//2,y,line,font,theme["accent"],"#1a0a2e",px=50,py=25)
    font_b=load_font(38,bold=True); btxt="QUIZ ⚡ GO!"
    bb=draw.textbbox((0,0),btxt,font=font_b); bw=bb[2]-bb[0]
    draw.rounded_rectangle([W//2-bw//2-30,H-95,W//2+bw//2+30,H-25],radius=35,fill="#FFD700")
    draw.text((W//2-bw//2,H-87),btxt,font=font_b,fill="#1a0a2e")
    img.save(out_path)

def main():
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    print("🗺️  Quiz 2: Guess the US State by Shape — VIRAL EDITION\n")

    with open("batch_generation_queue.csv",newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))

    print("Loading US states GeoJSON...")
    geo=download_geojson()
    lookup={}
    for feat in geo["features"]:
        name=feat.get("properties",{}).get("name","")
        if name: lookup[name]=feat["geometry"]
    print(f"  ✓ {len(lookup)} states loaded\n")

    # assign rounds by question number (10 per round)
    for row in rows:
        fname=row.get("file_name","").strip()
        if not fname: continue
        out=os.path.join(OUTPUT_DIR,fname)
        atype=row.get("asset_type","").strip()
        qnum=row.get("question_number","").strip()

        rnd=1
        if qnum and qnum.isdigit():
            rnd=min(5,(int(qnum)-1)//10+1)
        theme=ROUND_THEMES[rnd]

        if atype=="title_card":
            text=row.get("question_text","").strip()
            # round cards: detect round number
            m=re.search(r"ROUND\s*(\d+)",text,re.IGNORECASE)
            if m: theme=ROUND_THEMES[min(5,int(m.group(1)))]
            make_title_card(text,theme,out)
            print(f"  ✅ {fname}")
        else:
            state=row.get("answer","").strip().strip('"')
            geom=lookup.get(state)
            if not geom:
                for k,v in lookup.items():
                    if state.lower() in k.lower():
                        geom=v; break
            if not geom:
                print(f"  ⚠️  not found: {state}"); continue
            rings=get_coords(geom)
            make_state_scene(state,rings,qnum,theme,out)
            print(f"  ✅ [{qnum}] {state}")

    print(f"\n✅ Done! Viral state shapes in {OUTPUT_DIR}/")

if __name__=="__main__":
    main()
