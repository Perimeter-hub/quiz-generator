@echo off
title Quiz Generator — Setup
color 0A
echo.
echo  ========================================
echo   Quiz Generator — Windows Setup
echo   @QuizBlitzGo
echo  ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Please install Python from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)
echo  [OK] Python found
python --version

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found!
    echo  Please install Git from https://git-scm.com
    echo.
    pause
    exit /b 1
)
echo  [OK] Git found

echo.
echo  Installing Python libraries...
echo  ----------------------------------------
pip install requests moviepy pillow python-dotenv --quiet
echo  [OK] Core libraries installed

pip install geopandas shapely --quiet
if errorlevel 1 (
    echo  [WARN] geopandas failed - quiz2 shapes may not work
    echo         Try: pip install geopandas shapely manually
) else (
    echo  [OK] geopandas installed ^(needed for quiz2 state shapes^)
)

echo.
echo  ----------------------------------------
echo  Setting up .env file...
if not exist .env (
    copy .env.example .env >nul
    echo  [OK] Created .env from template
    echo.
    echo  *** IMPORTANT: Edit .env and add your API keys! ***
    echo  Opening .env in Notepad...
    timeout /t 2 >nul
    notepad .env
) else (
    echo  [OK] .env already exists
)

echo.
echo  ----------------------------------------
echo  Verifying setup...
python -c "import requests, moviepy, PIL; print('  [OK] All core libraries working')"
if errorlevel 1 (
    echo  [ERROR] Some libraries failed to import
    pause
    exit /b 1
)

echo.
echo  ========================================
echo   Setup complete!
echo  ========================================
echo.
echo  How to generate a quiz video:
echo.
echo    cd quiz4
echo    python generate_images.py     ^(~20 min^)
echo    python ..\shared\generate_music.py
echo    python ..\shared\make_quiz_video.py
echo.
echo  Output: quiz4.mp4
echo.
echo  Full docs: https://github.com/Perimeter-hub/quiz-generator
echo.
pause
