import logging
from pathlib import Path

from langgraph.runtime import Runtime
from langgraph.types import interrupt

from agentic_code_testing.agents.codetest_writer_agent.utils.static_analysis import (
    extract_file_path_from_answer,
    extract_module_info,
    find_related_test_files,
    render_module_info,
)
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
)

logger = logging.getLogger(__name__)


def request_code_context(state: CodeTestWriterState, runtime: Runtime[CodeTestWriterContext]) -> dict:
    """Suspend the graph and ask whoever is running it (the orchestrator) to answer
    `state.pending_code_context_question`. codetest_writer_agent never calls
    code_reader_agent itself -- this interrupt is the only seam.
    """
    answer = interrupt({"question": state.pending_code_context_question})
    if not isinstance(answer, str):
        answer = str(answer)

    combined = f"{state.code_context}\n\n{answer}" if state.code_context else answer

    root_dir = Path(runtime.context.root_dir).resolve()
    target_file = extract_file_path_from_answer(answer, root_dir) or state.target_file
    static_context = state.static_context

    if target_file is not None and target_file != state.target_file:
        try:
            source = (root_dir / target_file).read_text(encoding="utf-8", errors="replace")
            module_info = extract_module_info(source, target_file)
            static_context = render_module_info(module_info)

            related = find_related_test_files(root_dir, target_file)
            if related:
                names = ", ".join(str(p.relative_to(root_dir)) for p in related)
                static_context += f"\nExisting related test files (reuse their fixtures if relevant): {names}"
        except (OSError, SyntaxError):
            logger.warning("Failed to statically analyze %s; continuing without it", target_file, exc_info=True)

    return {
        "code_context": combined,
        "pending_code_context_question": None,
        "target_file": target_file,
        "static_context": static_context,
    }
