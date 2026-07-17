#!/bin/bash
# Quiz Blitz — One-Command Build Pipeline
# Runs: generate images (if needed) -> assemble video -> intro card -> shorts
# Usage: run from inside a quiz folder:  bash ../shared/build_quiz.sh
set -e

echo "════════════════════════════════════════"
echo "  Quiz Blitz — Full Build Pipeline"
echo "  Folder: $(basename "$PWD")"
echo "════════════════════════════════════════"
echo ""

# Step 1: Generate images if the folder is empty or missing
if [ ! -d "images_and_videos" ] || [ -z "$(ls -A images_and_videos 2>/dev/null)" ]; then
    echo "▶ Step 1/4: Generating images..."
    python3 generate_images.py
    echo ""
else
    echo "▶ Step 1/4: Images already present — skipping generation"
    echo "  (delete images_and_videos/ or specific files to force regeneration)"
    echo ""
fi

# Step 2: Assemble the main video (music auto-copied from quiz1/ if missing)
echo "▶ Step 2/4: Assembling video..."
python3 ../shared/make_quiz_video.py
echo ""

# Step 3: Add intro card (becomes the YouTube thumbnail)
echo "▶ Step 3/4: Adding intro card..."
python3 ../shared/generate_intro_card.py
echo ""

# Step 4: Build the YouTube Short
echo "▶ Step 4/4: Building Short..."
python3 ../shared/make_shorts.py
echo ""

echo "════════════════════════════════════════"
echo "  ✅ ALL DONE!"
echo "════════════════════════════════════════"
FOLDER=$(basename "$PWD")
echo "  Upload these to YouTube:"
echo "    ${FOLDER}_final.mp4   (main video)"
echo "    ${FOLDER}_short.mp4   (Short)"
echo "════════════════════════════════════════"
