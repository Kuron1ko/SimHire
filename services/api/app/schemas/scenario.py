from pydantic import Field

from app.schemas.base import APIModel
from app.schemas.enums import Difficulty, ScenarioCategory


class InterviewScenario(APIModel):
    id: str
    name: str
    description: str
    category: ScenarioCategory
    default_question_count: int = Field(ge=1)
    difficulty: Difficulty
    rubric_id: str
    opening_prompt: str


class ScenariosResponse(APIModel):
    items: list[InterviewScenario]
