import asyncio

from langchain_core.messages import HumanMessage

from agentic_code_testing.agents.code_reader_agent.agent import create_code_reader_agent
from agentic_code_testing.agents.code_reader_agent.tests.mock_data import FIXTURE_DIR
from agentic_code_testing.llm.ollama_client import llm


async def _ask(question: str) -> str:
    agent = await create_code_reader_agent(llm, FIXTURE_DIR)
    result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


def test_answer_question_describes_read_file_function():
    answer = asyncio.run(_ask(
        "What does the read_file function in read_file.py do, and what does it return?"
    ))

    assert "read_file.py" in answer
    assert "read_text" in answer or "string" in answer.lower()
    print(f"answer:\n{answer}\n")


def test_answer_question_refuses_to_execute():
    answer = asyncio.run(_ask("Please run read_file.py and tell me the output."))
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
