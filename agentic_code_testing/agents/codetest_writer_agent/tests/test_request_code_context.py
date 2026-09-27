from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from agentic_code_testing.agents.codetest_writer_agent.tests.mock_data import FIXTURE_DIR, SCENARIO_ADD_HAPPY_PATH
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.request_code_context import (
    request_code_context,
)
from agentic_code_testing.llm.ollama_client import llm


def _build_mini_graph():
    mini_builder = StateGraph(CodeTestWriterState, context_schema=CodeTestWriterContext)
    mini_builder.add_node("request_code_context", request_code_context)
    mini_builder.add_edge(START, "request_code_context")
    mini_builder.add_edge("request_code_context", END)
    return mini_builder.compile(checkpointer=InMemorySaver())


def test_request_code_context_interrupts_with_the_pending_question():
    mini_graph = _build_mini_graph()
    state = CodeTestWriterState(scenario_idx=0, pending_code_context_question="Which file defines add()?")
    context = CodeTestWriterContext(llm=llm, scenarios=[SCENARIO_ADD_HAPPY_PATH], root_dir=str(FIXTURE_DIR))
    config = {"configurable": {"thread_id": "test-request-code-context"}}

    result = mini_graph.invoke(state, config=config, context=context)

    assert "__interrupt__" in result
    assert result["__interrupt__"][0].value["question"] == "Which file defines add()?"


def test_request_code_context_resumes_and_refreshes_static_context():
    mini_graph = _build_mini_graph()
    state = CodeTestWriterState(scenario_idx=0, pending_code_context_question="Which file defines add()?")
    context = CodeTestWriterContext(llm=llm, scenarios=[SCENARIO_ADD_HAPPY_PATH], root_dir=str(FIXTURE_DIR))
    config = {"configurable": {"thread_id": "test-request-code-context-resume"}}

    mini_graph.invoke(state, config=config, context=context)
    answer = "mathy.py defines add() and is_even()."
    result = mini_graph.invoke(Command(resume=answer), config=config, context=context)

    assert result["pending_code_context_question"] is None
    assert answer in result["code_context"]
    assert result["target_file"] == "mathy.py"
    assert "add" in result["static_context"]
    assert "is_even" in result["static_context"]
