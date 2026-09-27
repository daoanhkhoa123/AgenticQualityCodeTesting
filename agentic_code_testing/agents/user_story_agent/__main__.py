import uvicorn

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agentic_code_testing.agents.user_story_agent.agent_executor import (
    UserStoryAgentExecutor,
)
from agentic_code_testing.agents.user_story_agent.config import ServerConfig

HOST = ServerConfig.user_story_agent_host
PORT = ServerConfig.user_story_agent_port

if __name__ == "__main__":
    skill = AgentSkill(
        id="parse_user_story",
        name="Parse User Story",
        description=(
            "Parses a user story markdown file into structured fields (name, "
            "description, test_description, acceptance_criteria, "
            "techinal_description). The request message must include a data Part "
            '{"file_path": "<path>", "story_id": <int>} naming the story file to '
            "parse."
        ),
        input_modes=["application/json"],
        output_modes=["application/json"],
        tags=["user-story", "parsing"],
        examples=['{"file_path": "./stories/US-1.md", "story_id": 1}'],
    )

    agent_card = AgentCard(
        name="User Story Agent",
        description="Parses user story markdown files into structured StoryAgentState.",
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
        agent_executor=UserStoryAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host=HOST, port=PORT)
