import uvicorn

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agentic_code_testing.agents.codetest_writer_agent.agent_executor import (
    CodetestWriterAgentExecutor,
)
from agentic_code_testing.agents.codetest_writer_agent.config import ServerConfig

HOST = ServerConfig.codetest_writer_agent_host
PORT = ServerConfig.codetest_writer_agent_port

if __name__ == "__main__":
    skill = AgentSkill(
        id="write_scenario_tests",
        name="Write Scenario Tests",
        description=(
            "Drafts, runs, and classifies a pytest test per scenario, asking "
            "code_reader_agent for codebase context as needed, and retrying up "
            "to max_attempts times per scenario. The request message must "
            'include a data Part {"scenarios": <list[Scenario] JSON>, '
            '"output_dir": "<path>", "root_dir": "<path>", "max_attempts": '
            "<int, optional>}."
        ),
        input_modes=["application/json"],
        output_modes=["application/json"],
        tags=["testing", "pytest", "codegen"],
        examples=[
            '{"scenarios": [...], "output_dir": "./generated_tests", "root_dir": "./my_project"}'
        ],
    )

    agent_card = AgentCard(
        name="Codetest Writer Agent",
        description="Drafts, runs, and classifies pytest tests for a list of scenarios.",
        version="0.1.0",
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
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
        agent_executor=CodetestWriterAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host=HOST, port=PORT)
