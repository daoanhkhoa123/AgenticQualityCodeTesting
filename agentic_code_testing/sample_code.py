import asyncio
from pathlib import Path

from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.graph import planner_agent_once_ac
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.graph import codetest_writer_once_scenario
from agentic_code_testing.agents.code_reader_agent.agent import create_code_reader_agent
from agentic_code_testing.llm.ollama_client import llm



# # ASCII in the terminal, no extra deps
# planner_agent_once_ac.get_graph().print_ascii()

# # Mermaid text you can paste into https://mermaid.live or a markdown file
# print(planner_agent_once_ac.get_graph().draw_mermaid())

# # Rendered PNG (uses the mermaid.ink API by default, or pyppeteer/playwright locally)
# planner_agent_once_ac.get_graph().draw_mermaid_png(output_file_path="planner_agent_once_ac.png")

# code_reader_agent is built async (create_agent wraps its tools in a ReAct graph
# at call time), so it needs an event loop before .get_graph() is available.
code_reader_agent = asyncio.run(create_code_reader_agent(llm, Path(__file__).parent))

code_reader_agent.get_graph().print_ascii()
print(code_reader_agent.get_graph().draw_mermaid())
code_reader_agent.get_graph().draw_mermaid_png(output_file_path="code_reader_agent.png")
