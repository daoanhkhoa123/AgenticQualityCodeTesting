from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import CodeTestWriterState


def finalize(state: CodeTestWriterState) -> dict:
    run_result = state.run_result
    classification = state.classification

    if state.blocked_reasons:
        status = "blocked"
        notes = "Blocked before running -- drafted test used forbidden pattern(s): " + "; ".join(state.blocked_reasons)
    elif run_result is not None and run_result.returncode == 0:
        status = "passed"
        notes = f"Passed after {state.attempt} attempt(s)."
    elif classification is not None and not classification.is_test_code_bug:
        status = "flagged_source_bug"
        notes = f"Flagged as a likely source bug after {state.attempt} attempt(s): {classification.reasoning}"
    else:
        status = "unresolved"
        reason = classification.reasoning if classification is not None else "test run did not pass"
        notes = f"Unresolved after {state.attempt} attempt(s): {reason}"

    return {"status": status, "notes": notes}
