import uvicorn

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agentic_code_testing.agents.code_reader_agent.agent_executor import (
    CodeReaderAgentExecutor,
)
from agentic_code_testing.agents.code_reader_agent.config import ServerConfig

HOST = ServerConfig.code_reader_agent_host
PORT = ServerConfig.code_reader_agent_port

if __name__ == "__main__":
    skill = AgentSkill(
        id="read_codebase",
        name="Read Codebase",
        description=(
            "Answers read-only questions about the code in a directory by listing, "
            "searching, and reading files. Never executes or runs code. The request "
            "message must include a text Part with the question and a data Part "
            '{"root_dir": "<path>"} naming the directory to read.'
        ),
        input_modes=["text/plain", "application/json"],
        output_modes=["text/plain"],
        tags=["code", "qa", "read-only"],
        examples=['{"root_dir": "./my_project"} + "What does read_file.py do?"'],
    )

    agent_card = AgentCard(
        name="Code Reader Agent",
        description="Read-only Q&A agent over a directory of code.",
        version="0.1.0",
        default_input_modes=["text/plain", "application/json"],
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
        agent_executor=CodeReaderAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host=HOST, port=PORT)
