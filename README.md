# Quiz Generator — Quiz Business / Quiz Blitz Go

Automated pipeline for generating YouTube quiz MP4 videos.
Each quiz produces ~13 minutes of video with questions, countdowns, answer reveals, music and animated finale.

**Channel:** [@QuizBlitzGo](https://youtube.com/@QuizBlitzGo)
**GitHub:** [Perimeter-hub/quiz-generator](https://github.com/Perimeter-hub/quiz-generator)

## Quizzes

| # | Topic | Language | Type | Status |
|---|-------|----------|------|--------|
| Quiz 1 | 50 States Challenge | English 🇺🇸 | Photo scenes | ✅ Published |
| Quiz 2 | Guess the US State by Shape | English 🇺🇸 | GeoJSON shapes | ✅ Published |
| Quiz 3 | Kennst du den deutschen Fußball? | German 🇩🇪 | Photo scenes | ✅ Ready |
| Quiz 4 | Iconic American TV Shows | English 🇺🇸 | Photo scenes | ✅ Ready |
| Quiz 5 | Guess the Country by Flag | English 🇺🇸 | Flag images | ✅ Ready |
| Quiz 6 | World Capital Cities | English 🇺🇸 | Photo scenes | ✅ Ready |
| Quiz 8 | Guess the Brand by Emoji | English 🇺🇸 | Emoji (CLEAN) | ✅ Ready |
| Quiz 10 | Guess the Sport by Emoji | English 🇺🇸 | Emoji (CLEAN) | ✅ Ready |

## Video features (make_quiz_video.py v2)

- Avatar watermark (@QuizBlitzGo) on every frame — bottom left
- Purple pill channel badge on all title/round cards — bottom center
- Question number badge (purple circle N/50) — top left for photo-scene quizzes
- Countdown timer — top right
- Question text — bottom bar
- Answer reveal — green bar with answer
- Animated fireworks finale (8 sec) replacing outro
- Background music (question / countdown / answer phases)
- Emoji auto-stripped from text bars (no □□□)
- CLEAN_STYLE auto-detected for quiz2, quiz5-10 (text baked into images)

## Setup

```bash
git clone https://github.com/Perimeter-hub/quiz-generator
cd quiz-generator
cp .env.example .env
# Edit .env and add your API keys
pip install requests moviepy pillow geopandas python-dotenv
```

## Workflow for each quiz

### Step 1 — Generate images
```bash
cd quiz1/   # or quiz3, quiz4, quiz5, quiz6, quiz8, quiz10
python generate_images.py    # ~20 min via ModelsLab API

# For quiz2 (state shapes — FREE, no API needed):
cd quiz2/
python generate_shapes.py
```

### Step 2 — Generate music (one time, copy to all quizzes)
```bash
cd quiz1/
python ../shared/generate_music.py
# Copy to other quizzes:
cp music_*.mp3 ../quiz2/ ../quiz3/ ../quiz4/
```

### Step 3 — Assemble video
```bash
cd quiz1/   # run from inside the quiz folder
python ../shared/make_quiz_video.py
# Output: quiz1.mp4
```

### Step 4 — Add intro card (YouTube thumbnail)
```bash
python ../shared/generate_intro_card.py
# Output: quiz1_final.mp4  (with 3-sec intro)
```

## Video structure per question

| Phase | Duration |
|-------|----------|
| Question shown | 5 sec |
| Countdown 6→1 | 6 sec |
| Answer reveal | 4 sec |
| Round/title cards | 4 sec each |
| Animated finale | 8 sec |

**Total per quiz: ~13 minutes**

## Music files

Place in each quiz folder to enable background music:
- `music_question.mp3` — during question (40% volume)
- `music_countdown.mp3` — during countdown (60% volume)  
- `music_answer.mp3` — during answer reveal (70% volume)

Generate free tracks at [suno.com](https://suno.com) or via ElevenLabs API.

## API Keys

| Service | Used for | Get key |
|---------|----------|---------|
| ModelsLab | Image generation (quiz1,3,4,5,6,8,10) | [modelslab.com](https://modelslab.com/dashboard) |
| ElevenLabs | Music generation | [elevenlabs.io](https://elevenlabs.io) |

## Channel strategy

Separate YouTube channels per language for maximum algorithm targeting:
- **Quiz Blitz Go** (@QuizBlitzGo) — English, US audience
- **Quiz Blitz DE** — German, DE/AT/CH audience (high CPM)
- **Quiz Blitz ES** — Spanish, Latin America + Spain
- **Quiz Blitz PT** — Portuguese, Brazil

## Project structure

```
quiz-generator/
├── .env.example
├── .gitignore
├── README.md
├── shared/
│   ├── make_quiz_video.py       ← universal video assembler v2
│   ├── generate_music.py        ← ElevenLabs music generator
│   ├── generate_intro_card.py   ← YouTube thumbnail intro card
│   ├── generate_thumbnails.py   ← static PNG thumbnails
│   └── channel_avatar.png       ← @QuizBlitzGo avatar
├── quiz1/  quiz2/  quiz3/  quiz4/
├── quiz5/  quiz6/  quiz8/  quiz10/
│   ├── generate_images.py  (or generate_shapes.py for quiz2)
│   └── batch_generation_queue.csv
└── Quiz Generator widget (multilingual, viral topic research)
```
