#!/bin/bash
# ============================================================
# Quiz Blitz Go — Universal Pipeline Runner
# Usage: ./run_all.sh [quiz5] [quiz6] ...  or just ./run_all.sh for all
# ============================================================

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SHARED="$REPO_DIR/shared"

# Which quizzes to run
if [ "$#" -gt 0 ]; then
    QUIZZES=("$@")
else
    QUIZZES=(quiz5 quiz6 quiz7 quiz8 quiz9 quiz10)
fi

echo "╔══════════════════════════════════════════╗"
echo "║     QUIZ BLITZ GO — Pipeline Runner      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

for QUIZ in "${QUIZZES[@]}"; do
    QUIZ_DIR="$REPO_DIR/$QUIZ"
    
    if [ ! -d "$QUIZ_DIR" ]; then
        echo "⚠  Skipping $QUIZ — folder not found"; continue
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎬 Processing $QUIZ..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    cd "$QUIZ_DIR"
    
    # STEP 1: Generate images
    VIDEO="${QUIZ}.mp4"
    if [ -f "$VIDEO" ]; then
        echo "  ⏭  $VIDEO already exists — skipping image gen"
    else
        # Use local generator (no API) or ModelsLab based on quiz number
        QUIZ_NUM=$(echo "$QUIZ" | grep -o '[0-9]*')
        if [ "$QUIZ_NUM" -ge 5 ]; then
            echo "  🖼  Generating images locally (no API)..."
            python3 "$SHARED/generate_local_images.py"
        else
            echo "  🖼  Generating images via ModelsLab API..."
            python3 generate_images.py
        fi
        
        # STEP 2: Build video
        echo "  🎬 Building video..."
        python3 "$SHARED/make_quiz_video.py"
    fi
    
    if [ -f "$VIDEO" ]; then
        SIZE=$(du -sh "$VIDEO" | cut -f1)
        echo "  ✅ $VIDEO ($SIZE)"
    else
        echo "  ❌ Video not created — check errors above"
    fi
    
    echo ""
    cd "$REPO_DIR"
done

echo "╔══════════════════════════════════════════╗"
echo "║              ALL DONE! 🎉                ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Videos ready in each quiz folder."
