@echo off
cd /d "%~dp0.."
set "STORY_FILE=user_inputs\user_stories\05_leaderboard_no_format.md"
".venv\Scripts\python.exe" scripts\run_pipeline.py "%STORY_FILE%" --root-dir D:/CardGame-main %*
