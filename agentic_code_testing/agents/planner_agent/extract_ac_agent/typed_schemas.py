from typing import Optional

from pydantic import BaseModel, Field


class ExtractACAgentState(BaseModel):
    acs: list[str] = Field(default_factory=list, description="List of extracted acceptance criteria string")
    human_accepted: Optional[bool] = Field(default=None, description="Human's decision on the extracted acceptance criteria, set by asking_human")
    human_feedback: Optional[str] = Field(default=None, description="Human's guidance for the next extraction attempt, set by asking_human on rejection")


class HumanReviewDecision(BaseModel):
    accepted: bool
    feedback: Optional[str] = None

