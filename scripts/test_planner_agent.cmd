@echo off
cd /d "%~dp0.."
".venv\Scripts\python.exe" -m pytest agentic_code_testing/agents/planner_agent/tests/test_planner_agent.py -s -v
