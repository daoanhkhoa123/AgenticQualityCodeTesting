from langchain_groq import ChatGroq

from agentic_code_testing.llm.key_config import KeyConfig

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=KeyConfig.groq_api_key,
)
