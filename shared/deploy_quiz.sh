#!/bin/bash
# Quiz Blitz — One-Command Deploy
# Downloads quiz files + shared scripts from GitHub, builds video+intro+short,
# then uploads both to YouTube. Run from the quiz-generator/ ROOT folder.
#
# Usage:  bash shared/deploy_quiz.sh quiz18
#
set -e

if [ -z "$1" ]; then
    echo "Usage: bash shared/deploy_quiz.sh <quizN>"
    echo "Example: bash shared/deploy_quiz.sh quiz18"
    exit 1
fi

QUIZ="$1"
REPO="https://raw.githubusercontent.com/Perimeter-hub/quiz-generator/main"
TS=$(date +%s)

echo "════════════════════════════════════════"
echo "  Quiz Blitz — One-Command Deploy"
echo "  Target: $QUIZ"
echo "════════════════════════════════════════"
echo ""

echo "▶ Step 1/6: Downloading quiz files from GitHub..."
mkdir -p "$QUIZ"
for f in batch_generation_queue.csv generate_images.py metadata.json; do
    curl -sL "${REPO}/${QUIZ}/${f}?nocache=${TS}" -o "${QUIZ}/${f}"
done
echo "  ✓ CSV, generator, metadata downloaded"
echo ""

echo "▶ Step 2/6: Downloading latest shared scripts..."
for f in make_quiz_video.py generate_intro_card.py make_shorts.py build_quiz.sh upload_to_youtube.py; do
    curl -sL "${REPO}/shared/${f}?nocache=${TS}" -o "shared/${f}"
done
chmod +x shared/build_quiz.sh
echo "  ✓ All scripts updated"
echo ""

cd "$QUIZ"

echo "▶ Step 3/6: Generating images (skips if already present)..."
if [ ! -d "images_and_videos" ] || [ -z "$(ls -A images_and_videos 2>/dev/null)" ]; then
    python3 generate_images.py
else
    echo "  Images already present — skipping"
fi
echo ""

echo "▶ Step 4/6: Assembling video (music auto-copied from quiz1/)..."
python3 ../shared/make_quiz_video.py
echo ""

echo "▶ Step 5/6: Adding intro card + building Short..."
python3 ../shared/generate_intro_card.py
python3 ../shared/make_shorts.py
echo ""

echo "▶ Step 6/6: Uploading to YouTube..."
if [ ! -f "../shared/client_secret.json" ]; then
    echo "  ⚠  client_secret.json not found — skipping upload."
    echo "  Files are ready locally: ${QUIZ}_final.mp4, ${QUIZ}_short.mp4"
    echo "  Set up YouTube API credentials, then run:"
    echo "    cd $QUIZ && python3 ../shared/upload_to_youtube.py"
else
    python3 ../shared/upload_to_youtube.py
    echo ""
    echo "  Uploading Short..."
    python3 ../shared/upload_to_youtube.py --short
fi

echo ""
echo "════════════════════════════════════════"
echo "  ✅ DEPLOY COMPLETE — $QUIZ"
echo "════════════════════════════════════════"
echo "  Remember to manually:"
echo "    - Pin the comment in YouTube Studio"
echo "    - Link the Short to the main video (Add similar video)"
echo "════════════════════════════════════════"
