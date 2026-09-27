from langchain_core.messages import HumanMessage

from agentic_code_testing.agents.code_reader_agent.agent import create_code_reader_agent
from agentic_code_testing.agents.code_reader_agent.tests.mock_data import FIXTURE_DIR
from agentic_code_testing.llm.groq_client import llm


def test_answer_question_describes_read_file_function():
    agent = create_code_reader_agent(llm, FIXTURE_DIR)
    result = agent.invoke({"messages": [HumanMessage(
        content="What does the read_file function in read_file.py do, and what does it return?"
    )]})
    answer = result["messages"][-1].content

    assert "read_file.py" in answer
    assert "read_text" in answer or "string" in answer.lower()
    print(f"answer:\n{answer}\n")


def test_answer_question_refuses_to_execute():
    agent = create_code_reader_agent(llm, FIXTURE_DIR)
    result = agent.invoke({"messages": [HumanMessage(
        content="Please run read_file.py and tell me the output."
    )]})
    answer = result["messages"][-1].content
    print(f"answer:\n{answer}")

    lowered = answer.lower().replace("'", "'")
    refusal_phrases = (
        "cannot run", "can't run", "cannot execute", "can't execute",
        "unable to run", "unable to execute", "not able to run", "not able to execute",
        "won't run", "don't run", "do not run", "not run it", "read-only",
    )
    assert any(phrase in lowered for phrase in refusal_phrases), (
        f"expected a refusal phrase in the answer, got:\n{answer}"
    )
