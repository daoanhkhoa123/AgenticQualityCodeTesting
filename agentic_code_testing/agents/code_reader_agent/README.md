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
- `answer_question(question, root_dir, llm=None)` -- single-shot convenience call,
  defaults to the shared Groq `llm`
