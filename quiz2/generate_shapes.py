#!/usr/bin/env python3
"""Quiz 2: Guess the US State by its Shape — free, no API needed"""
import os, urllib.request, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = "images_and_videos"
W, H = 1280, 720
GEOJSON_URL = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
GEOJSON_PATH = "/tmp/us-states.json"

ROUND_COLORS = {1:(15,20,50),2:(20,15,50),3:(10,35,25),4:(50,20,10),5:(30,25,5)}
STATE_ROUNDS = {
    "Texas":1,"California":1,"Florida":1,"Michigan":1,"Hawaii":1,"Alaska":1,"Louisiana":1,"Oklahoma":1,"Idaho":1,"Maryland":1,
    "Utah":2,"Wyoming":2,"Colorado":2,"Nevada":2,"New Mexico":2,"Minnesota":2,"Virginia":2,"West Virginia":2,"Tennessee":2,"Kentucky":2,
    "Maine":3,"New Hampshire":3,"Vermont":3,"Massachusetts":3,"Connecticut":3,"Rhode Island":3,"North Carolina":3,"South Carolina":3,"Georgia":3,"Alabama":3,
    "Mississippi":4,"Arkansas":4,"Missouri":4,"Iowa":4,"Illinois":4,"Indiana":4,"Ohio":4,"Pennsylvania":4,"New York":4,"New Jersey":4,
    "Delaware":5,"North Dakota":5,"South Dakota":5,"Nebraska":5,"Kansas":5,"Montana":5,"Oregon":5,"Washington":5,"Arizona":5,"Wisconsin":5,
}
FILE_MAP = {
    "Texas":"scene_q01_texas.png","California":"scene_q02_california.png","Florida":"scene_q03_florida.png",
    "Michigan":"scene_q04_michigan.png","Hawaii":"scene_q05_hawaii.png","Alaska":"scene_q06_alaska.png",
    "Louisiana":"scene_q07_louisiana.png","Oklahoma":"scene_q08_oklahoma.png","Idaho":"scene_q09_idaho.png",
    "Maryland":"scene_q10_maryland.png","Utah":"scene_q11_utah.png","Wyoming":"scene_q12_wyoming.png",
    "Colorado":"scene_q13_colorado.png","Nevada":"scene_q14_nevada.png","New Mexico":"scene_q15_new_mexico.png",
    "Minnesota":"scene_q16_minnesota.png","Virginia":"scene_q17_virginia.png","West Virginia":"scene_q18_west_virginia.png",
    "Tennessee":"scene_q19_tennessee.png","Kentucky":"scene_q20_kentucky.png","Maine":"scene_q21_maine.png",
    "New Hampshire":"scene_q22_new_hampshire.png","Vermont":"scene_q23_vermont.png","Massachusetts":"scene_q24_massachusetts.png",
    "Connecticut":"scene_q25_connecticut.png","Rhode Island":"scene_q26_rhode_island.png","North Carolina":"scene_q27_north_carolina.png",
    "South Carolina":"scene_q28_south_carolina.png","Georgia":"scene_q29_georgia.png","Alabama":"scene_q30_alabama.png",
    "Mississippi":"scene_q31_mississippi.png","Arkansas":"scene_q32_arkansas.png","Missouri":"scene_q33_missouri.png",
    "Iowa":"scene_q34_iowa.png","Illinois":"scene_q35_illinois.png","Indiana":"scene_q36_indiana.png",
    "Ohio":"scene_q37_ohio.png","Pennsylvania":"scene_q38_pennsylvania.png","New York":"scene_q39_new_york.png",
    "New Jersey":"scene_q40_new_jersey.png","Delaware":"scene_q41_delaware.png","North Dakota":"scene_q42_north_dakota.png",
    "South Dakota":"scene_q43_south_dakota.png","Nebraska":"scene_q44_nebraska.png","Kansas":"scene_q45_kansas.png",
    "Montana":"scene_q46_montana.png","Oregon":"scene_q47_oregon.png","Washington":"scene_q48_washington.png",
    "Arizona":"scene_q49_arizona.png","Wisconsin":"scene_q50_wisconsin.png",
}

def get_coords(geometry):
    rings = []
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]: rings.append([(c[0],c[1]) for c in ring])
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            largest = max(polygon, key=lambda r: len(r))
            rings.append([(c[0],c[1]) for c in largest])
    return rings

def normalize(rings, pad=120):
    all_pts = [pt for ring in rings for pt in ring]
    xs,ys = [p[0] for p in all_pts],[p[1] for p in all_pts]
    min_x,max_x,min_y,max_y = min(xs),max(xs),min(ys),max(ys)
    scale = min((W-pad*2)/(max_x-min_x or 1),(H-pad*2)/(max_y-min_y or 1))
    cx,cy = (W-scale*(max_x-min_x))/2,(H-scale*(max_y-min_y))/2
    return [[(cx+(x-min_x)*scale, cy+(max_y-y)*scale) for x,y in ring] for ring in rings]

def make_state_image(state, rings, round_num, out_path):
    bg = ROUND_COLORS.get(round_num,(15,20,50))
    arr = np.zeros((H,W,3),dtype=np.uint8); arr[:,:]=bg
    img = Image.fromarray(arr,"RGB")
    draw = ImageDraw.Draw(img)
    gc = tuple(min(255,c+12) for c in bg)
    for x in range(0,W,80): draw.line([(x,0),(x,H)],fill=gc,width=1)
    for y in range(0,H,80): draw.line([(0,y),(W,y)],fill=gc,width=1)
    norm = normalize(rings)
    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for ring in norm:
        if len(ring)>=3: gd.polygon([(int(x),int(y)) for x,y in ring],fill=(120,180,255,60))
    img = Image.alpha_composite(img.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(18))).convert("RGB")
    shape = Image.new("RGBA",(W,H),(0,0,0,0))
    sd = ImageDraw.Draw(shape)
    for ring in norm:
        if len(ring)>=3:
            pts=[(int(x),int(y)) for x,y in ring]
            sd.polygon(pts,fill=(240,245,255,255))
            sd.polygon(pts,outline=(100,160,255,255))
    img = Image.alpha_composite(img.convert("RGBA"),shape).convert("RGB")
    img.save(out_path,"PNG",optimize=True)

def make_card(filename, bg):
    arr=np.zeros((H,W,3),dtype=np.uint8); arr[:,:]=bg
    img=Image.fromarray(arr,"RGB")
    draw=ImageDraw.Draw(img)
    gc=tuple(min(255,c+12) for c in bg)
    for x in range(0,W,80): draw.line([(x,0),(x,H)],fill=gc,width=1)
    for y in range(0,H,80): draw.line([(0,y),(W,y)],fill=gc,width=1)
    draw.ellipse([(W//2-180,H//2-180),(W//2+180,H//2+180)],outline=(200,220,255),width=3)
    img.save(os.path.join(OUTPUT_DIR,filename),"PNG")

def main():
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    if not os.path.exists(GEOJSON_PATH):
        print("Downloading US states GeoJSON...")
        urllib.request.urlretrieve(GEOJSON_URL,GEOJSON_PATH)
    with open(GEOJSON_PATH) as f: geojson=json.load(f)
    state_geom={f["properties"]["name"]:f["geometry"] for f in geojson["features"]}
    total,done,errors=len(FILE_MAP),0,[]
    print(f"Generating {total} state shape images...\n")
    for state,filename in FILE_MAP.items():
        out_path=os.path.join(OUTPUT_DIR,filename)
        if os.path.exists(out_path): print(f"  ⏭  skip: {filename}"); done+=1; continue
        if state not in state_geom: errors.append(state); continue
        try:
            rings=get_coords(state_geom[state])
            make_state_image(state,rings,STATE_ROUNDS.get(state,1),out_path)
            done+=1; print(f"  ✓  [{done}/{total}] {state}")
        except Exception as e: print(f"  ✗  {state}: {e}"); errors.append(state)
    cards=[("opening_title_state_shapes.png",(10,15,45)),("round_01_easy_shapes.png",ROUND_COLORS[1]),
           ("round_02_medium_shapes.png",ROUND_COLORS[2]),("round_03_tricky_shapes.png",ROUND_COLORS[3]),
           ("round_04_harder_shapes.png",ROUND_COLORS[4]),("round_05_final_shapes.png",ROUND_COLORS[5]),
           ("outro_scoreboard.png",(10,30,20)),("end_screen.png",(10,10,40))]
    print("\nGenerating title cards...")
    for fn,color in cards: make_card(fn,color); print(f"  ✓  {fn}")
    print(f"\nDone: {done}/{total}")
    if errors: print(f"Errors: {errors}")
    print("\nNext: python ../shared/make_quiz_video.py")

if __name__=="__main__": main()
