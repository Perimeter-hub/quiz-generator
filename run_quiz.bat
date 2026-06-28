@echo off
title Quiz Generator — Build Video
color 0B
echo.
echo  ========================================
echo   Quiz Generator — Build Video
echo   @QuizBlitzGo
echo  ========================================
echo.

REM Ask which quiz to build
echo  Which quiz do you want to build?
echo.
echo    1. Quiz 1 — 50 States Challenge (EN)
echo    2. Quiz 2 — Guess State by Shape (EN)
echo    3. Quiz 3 — Deutscher Fussball (DE)
echo    4. Quiz 4 — Iconic TV Shows (EN)
echo    5. Quiz 5 — Guess Country by Flag (EN)
echo    6. Quiz 6 — World Capitals (EN)
echo    8. Quiz 8 — Guess Brand by Emoji (EN)
echo   10. Quiz 10 — Guess Sport by Emoji (EN)
echo.
set /p QUIZ_NUM="Enter quiz number: "

set QUIZ_DIR=quiz%QUIZ_NUM%

if not exist %QUIZ_DIR% (
    echo  [ERROR] Folder %QUIZ_DIR% not found!
    pause
    exit /b 1
)

cd %QUIZ_DIR%
echo.
echo  ----------------------------------------
echo  Building %QUIZ_DIR%...
echo.

REM Check images
if not exist images_and_videos (
    echo  [WARN] No images_and_videos folder found
    echo  Run generate_images.py first!
    echo.
    set /p GENERATE="Generate images now? (y/n): "
    if /i "%GENERATE%"=="y" (
        if exist generate_images.py (
            echo  Generating images... (this takes ~20 min)
            python generate_images.py
        ) else if exist generate_shapes.py (
            echo  Generating shapes...
            python generate_shapes.py
        )
    )
)

REM Check music
if not exist music_question.mp3 (
    echo  [INFO] No music files found
    set /p MUSIC="Generate music now? (y/n): "
    if /i "%MUSIC%"=="y" (
        python ..\shared\generate_music.py
    )
)

REM Build video
echo.
echo  Assembling video...
python ..\shared\make_quiz_video.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Video build failed!
    pause
    exit /b 1
)

echo.
echo  ----------------------------------------
set /p INTRO="Add intro card for YouTube thumbnail? (y/n): "
if /i "%INTRO%"=="y" (
    python ..\shared\generate_intro_card.py
)

echo.
echo  ========================================
echo   Done! Your video is ready.
echo  ========================================
echo.
cd ..
pause
