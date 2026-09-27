import uvicorn

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agentic_code_testing.agents.planner_agent.agent_executor import PlannerAgentExecutor
from agentic_code_testing.agents.planner_agent.config import ServerConfig

HOST = ServerConfig.planner_agent_host
PORT = ServerConfig.planner_agent_port

if __name__ == "__main__":
    skill = AgentSkill(
        id="plan_scenarios",
        name="Plan Test Scenarios",
        description=(
            "Derives acceptance criteria from a user story and generates test "
            "scenarios (happy path / edge case / negative case) for each, asking "
            "code_reader_agent for codebase context as needed. The request "
            'message must include a data Part {"user_story": <StoryAgentState '
            'JSON>, "output_dir": "<path>", "root_dir": "<path>", "max_acs": '
            "<int, optional>}."
        ),
        input_modes=["application/json"],
        output_modes=["application/json"],
        tags=["planning", "scenarios", "test-design"],
        examples=[
            '{"user_story": {...}, "output_dir": "./scenarios", "root_dir": "./my_project"}'
        ],
    )

    agent_card = AgentCard(
        name="Planner Agent",
        description="Derives acceptance criteria and generates test scenarios for a user story.",
        version="0.1.0",
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
        capabilities=AgentCapabilities(streaming=True, extended_agent_card=False),
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
        agent_executor=PlannerAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host=HOST, port=PORT)
