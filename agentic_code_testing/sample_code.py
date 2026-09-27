from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.graph import planner_agent_once_ac
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.graph import codetest_writer_once_scenario
# ASCII in the terminal, no extra deps
planner_agent_once_ac.get_graph().print_ascii()

# Mermaid text you can paste into https://mermaid.live or a markdown file
print(planner_agent_once_ac.get_graph().draw_mermaid())

# Rendered PNG (uses the mermaid.ink API by default, or pyppeteer/playwright locally)
planner_agent_once_ac.get_graph().draw_mermaid_png(output_file_path="planner_agent_once_ac.png")
