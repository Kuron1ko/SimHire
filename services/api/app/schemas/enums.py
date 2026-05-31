from enum import StrEnum


class ScenarioCategory(StrEnum):
    CAMPUS = "campus"
    CIVIL_SERVICE = "civil_service"
    POSTGRADUATE = "postgraduate"
    TECHNICAL = "technical"
    GENERAL = "general"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SessionStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewMode(StrEnum):
    TEXT = "text"
    VOICE = "voice"
    MULTIMODAL = "multimodal"


class Language(StrEnum):
    ZH_CN = "zh-CN"
    EN_US = "en-US"


class QuestionType(StrEnum):
    OPENING = "opening"
    BEHAVIORAL = "behavioral"
    PROFESSIONAL = "professional"
    PRESSURE = "pressure"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"


class QuestionIntent(StrEnum):
    ASK = "ask"
    PROBE = "probe"
    CHALLENGE = "challenge"
    ENCOURAGE = "encourage"
    SUMMARIZE = "summarize"


class TranscriptSource(StrEnum):
    MANUAL = "manual"
    BROWSER_STT = "browser_stt"
    SERVER_ASR = "server_asr"


class EmotionLabel(StrEnum):
    CALM = "calm"
    NERVOUS = "nervous"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class NextAction(StrEnum):
    NEXT_QUESTION = "next_question"
    FOLLOW_UP = "follow_up"
    FINISH_AVAILABLE = "finish_available"
    AUTO_FINISH = "auto_finish"


class FinishStatus(StrEnum):
    GENERATED = "generated"


class ActionPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PracticeType(StrEnum):
    STRUCTURE = "structure"
    CONTENT = "content"
    SPEECH = "speech"
    PRESSURE = "pressure"
    MOCK = "mock"


class ErrorCode(StrEnum):
    SCENARIO_NOT_FOUND = "SCENARIO_NOT_FOUND"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    TURN_NOT_FOUND = "TURN_NOT_FOUND"
    INVALID_SESSION_STATE = "INVALID_SESSION_STATE"
    EMPTY_ANSWER = "EMPTY_ANSWER"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    EVALUATION_FAILED = "EVALUATION_FAILED"
    SPEECH_NOT_SUPPORTED = "SPEECH_NOT_SUPPORTED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
