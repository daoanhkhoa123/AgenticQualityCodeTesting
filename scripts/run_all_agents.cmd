@echo off
cd /d "%~dp0.."
start "user_story_agent" cmd /k scripts\run_user_story_agent.cmd
start "planner_agent" cmd /k scripts\run_planner_agent.cmd
start "codetest_writer_agent" cmd /k scripts\run_codetest_writer_agent.cmd
start "code_reader_agent" cmd /k scripts\run_code_reader_agent.cmd
