from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.draft_test import (
    draft_test,
    route_after_draft,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.request_code_context import (
    request_code_context,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.run_drafted_test import (
    run_drafted_test,
    route_after_run,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.classify_failure import (
    classify_failure,
    route_after_classification,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.finalize import finalize

builder = StateGraph(CodeTestWriterState, context_schema=CodeTestWriterContext)

builder.add_node("draft_test", draft_test)
builder.add_node("request_code_context", request_code_context)
builder.add_node("run_drafted_test", run_drafted_test)
builder.add_node("classify_failure", classify_failure)
builder.add_node("finalize", finalize)

builder.add_edge(START, "draft_test")
builder.add_conditional_edges("draft_test",
                              route_after_draft,
                              {"needs_context": "request_code_context",
                               "run_test": "run_drafted_test"})
builder.add_edge("request_code_context", "draft_test")
builder.add_conditional_edges("run_drafted_test",
                              route_after_run,
                              {"finalize": "finalize",
                               "classify_failure": "classify_failure"})
builder.add_conditional_edges("classify_failure",
                              route_after_classification,
                              {"retry_draft": "draft_test",
                               "finalize": "finalize"})
builder.add_edge("finalize", END)

codetest_writer_once_scenario = builder.compile()
