import logging

from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from typing import Literal
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext, ScenarioGenResult

logger = logging.getLogger(__name__)


GENERATE_SENARIO_PROMPT = """
    Based on this accepctance criteria
    {ac}

    Relevant code context:
    {code_context}

    Write a senario follow this caterogy: {sen_cat}


    These are the already generated senarios on the same category:
    {gened_sen}

    The reasoning for the generated senarios not covereage:
    {not_covered_reasoning}

    Genreate senario following format.

    Also decide whether this category is already sufficiently covered by the
    already generated senarios above for this acceptance criteria: set
    is_category_covered to true if no further senario is needed, and explain
    your decision in coverage_reasoning. If is_category_covered is true, set
    scenario to null.

    If the code context above is missing or insufficient to write a senario
    grounded in the real implementation, do NOT guess: leave scenario null and
    set code_context_question to a specific question about the codebase you
    need answered first. Otherwise leave code_context_question null.
"""

prompt_template = PromptTemplate.from_template(GENERATE_SENARIO_PROMPT)


def generate_senarios(state: PlannerAgentState, runtime: Runtime[PlannerAgentContext]) -> dict:
    ac = runtime.context.acs[state.ac_idx]
    ac_id = f"AC-{state.ac_idx + 1}"
    llm = runtime.context.llm

    already_generated = [scenario for scenario in state.scenarios if scenario.ac_id == ac_id]
    gened_sen = "\n".join(f"- {scenario.title}" for scenario in already_generated if scenario.category==state.current_category) or "None yet"

    chain = prompt_template | llm.with_structured_output(ScenarioGenResult)

    logger.info("Calling LLM to generate scenario for %s category '%s'", ac_id, state.current_category)
    result = chain.invoke({
        "ac": ac,
        "code_context": state.code_context or "No code context available",
        "sen_cat": state.current_category,
        "gened_sen": gened_sen,
        "not_covered_reasoning": state.coverage_reasoning,
    })
    logger.info("LLM call finished for %s category '%s'", ac_id, state.current_category)

    if not isinstance(result, ScenarioGenResult):
        raise TypeError(f"Expected ScenarioGenResult from structured output, got {type(result)}")

    if result.code_context_question:
        return {"pending_code_context_question": result.code_context_question}

    update = {
        "is_category_covered": result.is_category_covered,
        "coverage_reasoning": result.coverage_reasoning,
        "pending_code_context_question": None,
    }

    if result.scenario is not None:
        scenario = result.scenario.model_copy(update={
            "scenario_id": f"{ac_id}-{state.current_category.replace(' ', '_')}-{state.senarios_idx + 1}",
            "story_id": runtime.context.user_story.story_id,
            "ac_id": ac_id,
            "category": state.current_category,
        })
        update["scenarios"] = state.scenarios + [scenario]
        update["senarios_idx"] = state.senarios_idx + 1

    return update


NEEDS_CONTEXT_ROUTET = Literal["needs_context", "limit_senarios"]
def route_maybe_needs_context(state: PlannerAgentState) -> NEEDS_CONTEXT_ROUTET:
    if state.pending_code_context_question:
        return "needs_context"
    return "limit_senarios"


GENERATE_AGAIN_ROUTET = Literal["generate_again", "category_done"]
def route_maybe_senarios(state: PlannerAgentState) -> GENERATE_AGAIN_ROUTET:
    if not state.is_category_covered:
        return "generate_again"
    return "category_done"
