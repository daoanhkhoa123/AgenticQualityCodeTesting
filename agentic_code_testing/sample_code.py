from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import extract_ac_graph

# ASCII in the terminal, no extra deps
extract_ac_graph.get_graph().print_ascii()

# Mermaid text you can paste into https://mermaid.live or a markdown file
print(extract_ac_graph.get_graph().draw_mermaid())

# Rendered PNG (uses the mermaid.ink API by default, or pyppeteer/playwright locally)
extract_ac_graph.get_graph().draw_mermaid_png(output_file_path="extract_ac_graph.png")
