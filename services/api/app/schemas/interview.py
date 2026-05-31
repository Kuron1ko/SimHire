from datetime import datetime

from pydantic import Field

from app.schemas.base import APIModel
from app.schemas.enums import (
    EmotionLabel,
    FinishStatus,
    InterviewMode,
    Language,
    NextAction,
    QuestionIntent,
    QuestionType,
    SessionStatus,
    TranscriptSource,
)


class CandidateProfile(APIModel):
    name: str | None = None
    target_role: str | None = None
    background: str | None = None


class SpeechMetrics(APIModel):
    speaking_rate_wpm: float | None = Field(default=None, ge=0)
    pause_count: int | None = Field(default=None, ge=0)
    filler_word_count: int | None = Field(default=None, ge=0)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    emotion_label: EmotionLabel | None = None


class CandidateAnswer(APIModel):
    text: str
    transcript_source: TranscriptSource
    audio_url: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    speech_metrics: SpeechMetrics | None = None


class InterviewQuestion(APIModel):
    id: str
    text: str
    type: QuestionType
    intent: QuestionIntent
    expected_signals: list[str] = Field(default_factory=list)


class InterviewSession(APIModel):
    id: str
    scenario_id: str
    status: SessionStatus
    mode: InterviewMode
    language: Language
    question_count_target: int = Field(ge=1)
    current_turn_index: int = Field(ge=0)
    created_at: datetime
    completed_at: datetime | None = None


class InterviewTurn(APIModel):
    id: str
    session_id: str
    index: int = Field(ge=1)
    question: InterviewQuestion
    answer: CandidateAnswer | None = None
    created_at: datetime
    answered_at: datetime | None = None


class StartSessionRequest(APIModel):
    scenario_id: str
    mode: InterviewMode
    language: Language
    question_count_target: int = Field(ge=1)
    candidate_profile: CandidateProfile | None = None


class StartSessionResponse(APIModel):
    session: InterviewSession
    turn: InterviewTurn


class SubmitAnswerRequest(APIModel):
    turn_id: str
    answer: CandidateAnswer


class SubmitAnswerResponse(APIModel):
    next_action: NextAction
    assistant_ack: str | None = None
    next_turn: InterviewTurn | None = None


class FinishSessionResponse(APIModel):
    report_id: str
    status: FinishStatus
