from pydantic import BaseModel
from typing import Optional, Literal

from langchain_core.language_models.chat_models import BaseChatModel


class StoryAgentState(BaseModel):
    story_id: int
    file_path: str
    story_body: str

    name: Optional[str]
    description: Optional[str]
    test_description: Optional[str]
    acceptance_criteria: Optional[str]
    techinal_description: Optional[str]

    parsing_field_name: Optional[str]
    
PROCESS_STATE = Literal["parsing", "parsing_done"]
AUTOMATIC_FILL_STORY_STATE = ["name", "description", "test_description", "acceptance_criteria", "techinal_description"]


class StoryAgentContext(BaseModel):
    llm: BaseChatModel
