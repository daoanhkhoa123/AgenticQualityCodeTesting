@echo off
cd /d "%~dp0.."
".venv\Scripts\python.exe" -m agentic_code_testing.agents.code_reader_agent
