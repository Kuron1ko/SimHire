from datetime import datetime

from pydantic import Field

from app.schemas.base import APIModel
from app.schemas.enums import ActionPriority, PracticeType


class ScoreItem(APIModel):
    score: float = Field(ge=0)
    max_score: float = Field(gt=0)
    evidence: list[str] = Field(default_factory=list)
    suggestion: str


class AbilityDimensions(APIModel):
    logical_structure: ScoreItem
    relevance: ScoreItem
    specificity: ScoreItem
    professional_depth: ScoreItem
    communication_clarity: ScoreItem


class AbilityEvaluation(APIModel):
    total: float = Field(ge=0, le=60)
    dimensions: AbilityDimensions


class PsychologyDimensions(APIModel):
    stress_tolerance: ScoreItem
    confidence: ScoreItem
    adaptability: ScoreItem
    emotional_stability: ScoreItem


class PsychologyEvaluation(APIModel):
    total: float = Field(ge=0, le=40)
    dimensions: PsychologyDimensions


class TurnFeedback(APIModel):
    turn_id: str
    summary: str
    score: float = Field(ge=0)
    highlights: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class ActionItem(APIModel):
    title: str
    description: str
    priority: ActionPriority
    practice_type: PracticeType


class EvaluationReport(APIModel):
    id: str
    session_id: str
    overall_score: float = Field(ge=0, le=100)
    ability: AbilityEvaluation
    psychology: PsychologyEvaluation
    turn_feedback: list[TurnFeedback]
    strengths: list[str]
    risks: list[str]
    action_plan: list[ActionItem]
    generated_at: datetime
