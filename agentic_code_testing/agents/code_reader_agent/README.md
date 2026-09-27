# Code Reader Agent

Read-only Q&A agent over a directory of code.

Given a root directory and a user question, the agent explores the directory with
three tools and answers based only on what it reads -- it never executes, runs, or
tests any code.

Tools (all scoped to the given root directory, in `tools/`):

- `list_directory` -- ASCII tree of files/folders (wraps `list_directory_func.print_tree`)
- `read_file` -- reads a single file's text content
- `search_in_files` -- regex search across files, returns `path:line: text` hits

Entry points (`agent.py`):

- `create_code_reader_agent(llm, root_dir)` -- builds the compiled ReAct agent

## Running as an A2A server

`python -m agentic_code_testing.agents.code_reader_agent` starts an
[A2A protocol](https://a2a-protocol.org/) server (default `127.0.0.1:9998`,
override with `CODE_READER_AGENT_HOST`/`CODE_READER_AGENT_PORT`).

- Agent card: `GET /.well-known/agent-card.json`
- JSON-RPC endpoint: `POST /` -- requires an `A2A-Version: 1.0` header, or the
  server treats the request as protocol v0.3 and rejects it

Each `SendMessage` request's `message` must include:

- a **text Part** -- the question
- a **data Part** -- `{"root_dir": "<path>"}`, the directory to read (set per
  request by the caller, same trust boundary as `create_code_reader_agent`'s
  `root_dir` argument)

The agent replies with a single text `Message` containing the answer.

Example:

```bash
curl -X POST http://127.0.0.1:9998/ \
  -H "Content-Type: application/json" \
  -H "A2A-Version: 1.0" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "test-1",
        "role": "ROLE_USER",
        "parts": [
          {"text": "What does the read_file function in read_file.py do?"},
          {"data": {"root_dir": "agentic_code_testing/agents/code_reader_agent"}}
        ]
      }
    }
  }'
```
