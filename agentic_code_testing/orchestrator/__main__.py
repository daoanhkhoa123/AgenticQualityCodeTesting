import uvicorn

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agentic_code_testing.orchestrator.agent_executor import OrchestratorAgentExecutor
from agentic_code_testing.orchestrator.config import ServerConfig

HOST = ServerConfig.orchestrator_host
PORT = ServerConfig.orchestrator_port

if __name__ == "__main__":
    skill = AgentSkill(
        id="run_pipeline",
        name="Run Code-Test Pipeline",
        description=(
            "Runs the full user_story_agent -> planner_agent -> "
            "codetest_writer_agent pipeline for a story. Not implemented yet -- "
            "currently always reports that back rather than producing results. "
            'The request message must include a data Part {"file_path": '
            '"<path>", "story_id": <int>, "output_dir": "<path>", "root_dir": '
            '"<path>"}.'
        ),
        input_modes=["application/json"],
        output_modes=["text/plain"],
        tags=["orchestrator", "pipeline"],
        examples=[
            '{"file_path": "./stories/US-1.md", "story_id": 1, '
            '"output_dir": "./out", "root_dir": "./my_project"}'
        ],
    )

    agent_card = AgentCard(
        name="Orchestrator Agent",
        description="Coordinates user_story_agent, planner_agent, and codetest_writer_agent.",
        version="0.1.0",
        default_input_modes=["application/json"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=False, extended_agent_card=False),
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC",
                url=f"http://{HOST}:{PORT}",
                protocol_version="1.0",
            )
        ],
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=OrchestratorAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host=HOST, port=PORT)
