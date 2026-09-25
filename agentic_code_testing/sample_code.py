from agentic_code_testing.agents.user_story_agent.subgraphs.parsing_graph import parsing_graph

# ASCII in the terminal, no extra deps
parsing_graph.get_graph().print_ascii()

# Mermaid text you can paste into https://mermaid.live or a markdown file
print(parsing_graph.get_graph().draw_mermaid())

# Rendered PNG (uses the mermaid.ink API by default, or pyppeteer/playwright locally)
parsing_graph.get_graph().draw_mermaid_png(output_file_path="parsing_graph.png")
