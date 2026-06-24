# 🎬 Quiz Generator

Automated pipeline for generating YouTube quiz MP4 videos.
Each quiz produces ~13 minutes of video with questions, countdowns, and answer reveals.

## Quizzes

| # | Topic | Language | Images | Status |
|---|-------|----------|--------|--------|
| 1 | 50 States Challenge | English 🇺🇸 | Stable Diffusion | ✅ Done |
| 2 | Guess the US State by Shape | English 🇺🇸 | GeoJSON (free) | ✅ Done |
| 3 | Kennst du den deutschen Fußball? | German 🇩🇪 | Stable Diffusion | ✅ Done |

## Setup

```bash
pip install requests moviepy pillow geopandas python-dotenv
cp .env.example .env
# Edit .env and add your API keys
```

## Usage

### Generate images
```bash
cd quiz1/
python generate_images.py

cd quiz2/
python generate_shapes.py   # free, no API needed

cd quiz3/
python generate_images.py
```

### Assemble video (works for all quizzes)
```bash
cd quiz1/   # or quiz2/ or quiz3/
python ../shared/make_quiz_video.py
# Output: quiz_video.mp4
```

## Video structure per question

| Phase | Duration |
|-------|----------|
| Question shown | 5 sec |
| Countdown 6→1 | 6 sec |
| Answer reveal | 4 sec |

**Total per quiz: ~13 minutes**

## Music support

Place these MP3 files in your quiz folder to enable background music:
- `music_question.mp3` — plays during question (volume 40%)
- `music_countdown.mp3` — plays during countdown (volume 60%)
- `music_answer.mp3` — plays during answer reveal (volume 70%)

Generate free tracks at [suno.com](https://suno.com).

## API Keys

| Service | Used for | Get key |
|---------|----------|---------|
| ModelsLab | Image generation | [modelslab.com](https://modelslab.com/dashboard) |
| Poe (optional) | Higher quality images | [poe.com/api_key](https://poe.com/api_key) |

## Adding a new quiz

1. Create folder `quiz4/`
2. Create `batch_generation_queue.csv` with columns:
   `asset_id, asset_type, file_name, question_text, answer, question_number, round_number, prompt_hint`
3. Add image generator script
4. Run `python ../shared/make_quiz_video.py`

## Project structure

```
quiz_generator/
├── .env.example
├── .gitignore
├── README.md
├── shared/
│   └── make_quiz_video.py      ← universal video assembler
├── quiz1/
│   ├── generate_images.py
│   └── batch_generation_queue.csv
├── quiz2/
│   ├── generate_shapes.py
│   └── batch_generation_queue.csv
└── quiz3/
    ├── generate_images.py
    └── batch_generation_queue.csv
```
