from langchain_ollama import ChatOllama

from agentic_code_testing.llm.key_config import KeyConfig

llm = ChatOllama(
    model=KeyConfig.ollama_model,
    base_url=KeyConfig.ollama_base_url,
)
