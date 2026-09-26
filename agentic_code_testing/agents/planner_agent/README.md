The planning pipeline, step by step

Split ACs — a node takes acceptance_criteria (the raw string) and produces a list of discrete AC items, each getting an ac_id (AC-1, AC-2, ...). This can be regex/line-based (numbered/bulleted list → one item per line, same style as _extract_section in parse_text_body.py) or LLM-based if the formatting is inconsistent. Store this as new state, e.g. ac_items: list[str] plus an index/queue.

Loop over ACs one at a time — this is exactly the select_next_field_node / route_after_select pattern in select_node.py. Instead of picking "which field is still empty," the planner's select node picks "which AC hasn't been planned yet," sets something like current_ac_id, and routes to "planning" or "planning_done" conditionally — same conditional-edge shape as the existing parsing_graph.

Generate scenarios for the current AC — the actual "planning" node. For current_ac_id's text, prompt the LLM to produce exactly one happy_path, one-or-more edge_case, and one-or-more negative_case Scenario objects (the model from state.py). The key move: use structured output (llm.with_structured_output(...) against a small wrapper model like list[Scenario] or a ScenariosForAC(scenarios: list[Scenario])) so the LLM is constrained to emit the exact pydantic shape — not free text you'd have to re-parse. story_id/ac_id get stamped onto each returned scenario by code (not trusted from the LLM), since traceability must be exact.

Accumulate — each loop iteration appends its scenarios into Plan.scenarios (a list-reducer channel in the graph state, same idea as the field being written back into state each time in select_next_field_node).

Done — once every AC has been visited, route_after_select returns "planning_done", the graph ends, and the final state's Plan (story_id + full scenario list) is the artifact handed to the downstream Test Code Generator agent.



---

Extractr accpetance critera agent:
Given a user story (read-only, passed via context not state):
- llm tries to write accpetance criteas in a certan format (- a, - b, bullet point style)
- if accpeatnce critea is found from input, then END return the list of accpetance critearia
- if accpectance critera is not found from the input, then it should ask human it accpet this criteria
- if human accept, then END
- if not, then run the agent again
