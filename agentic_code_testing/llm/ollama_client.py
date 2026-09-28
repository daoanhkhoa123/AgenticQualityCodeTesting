from langchain_ollama import ChatOllama

from agentic_code_testing.llm.key_config import KeyConfig

llm = ChatOllama(
    model=KeyConfig.ollama_model,
    base_url=KeyConfig.ollama_base_url,
    num_ctx=KeyConfig.ollama_num_ctx,
    client_kwargs={"timeout": KeyConfig.ollama_timeout_seconds},
)
