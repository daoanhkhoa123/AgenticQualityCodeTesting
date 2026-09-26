from agentic_code_testing.agents.planner_agent.graph import planner_agent
# ASCII in the terminal, no extra deps
planner_agent.get_graph().print_ascii()

# Mermaid text you can paste into https://mermaid.live or a markdown file
print(planner_agent.get_graph().draw_mermaid())

# Rendered PNG (uses the mermaid.ink API by default, or pyppeteer/playwright locally)
planner_agent.get_graph().draw_mermaid_png(output_file_path="planner_agent.png")
