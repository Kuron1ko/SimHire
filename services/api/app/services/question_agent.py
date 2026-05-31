from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.schemas import (
    CandidateProfile,
    InterviewQuestion,
    InterviewScenario,
    InterviewTurn,
    NextAction,
    QuestionIntent,
    QuestionType,
)


@dataclass(frozen=True)
class QuestionDecision:
    next_action: NextAction
    question: InterviewQuestion | None = None
    assistant_ack: str | None = None


class QuestionAgent:
    async def generate_first_question(
        self,
        scenario: InterviewScenario,
        candidate_profile: CandidateProfile | None,
    ) -> InterviewQuestion:
        return InterviewQuestion(
            id=f"q_{uuid4().hex[:12]}",
            text=scenario.opening_prompt,
            type=QuestionType.OPENING,
            intent=QuestionIntent.ASK,
            expected_signals=["表达结构", "经历匹配", "自信程度"],
        )

    async def generate_next_question(
        self,
        scenario: InterviewScenario,
        turns: list[InterviewTurn],
    ) -> QuestionDecision:
        answered_turns = [turn for turn in turns if turn.answer is not None]
        latest_turn = answered_turns[-1] if answered_turns else None

        if latest_turn and _is_short_answer(latest_turn.answer.text):
            return QuestionDecision(
                next_action=NextAction.FOLLOW_UP,
                assistant_ack="我先追问一下，帮助你把刚才的回答展开。",
                question=InterviewQuestion(
                    id=_make_question_id(),
                    text="刚才的回答还比较简略。请补充一个具体例子，说明你的行动、结果和个人贡献。",
                    type=QuestionType.FOLLOW_UP,
                    intent=QuestionIntent.PROBE,
                    expected_signals=["具体案例", "个人贡献", "结果呈现"],
                ),
            )

        question_index = len(turns)
        bank = QUESTION_BANK_BY_SCENARIO.get(scenario.id, DEFAULT_QUESTION_BANK)
        template = bank[(question_index - 1) % len(bank)]
        return QuestionDecision(
            next_action=NextAction.NEXT_QUESTION,
            assistant_ack="好的，我们进入下一题。",
            question=InterviewQuestion(
                id=_make_question_id(),
                text=template.text,
                type=template.type,
                intent=template.intent,
                expected_signals=list(template.expected_signals),
            ),
        )


@dataclass(frozen=True)
class QuestionTemplate:
    text: str
    type: QuestionType
    intent: QuestionIntent
    expected_signals: tuple[str, ...]


DEFAULT_QUESTION_BANK: tuple[QuestionTemplate, ...] = (
    QuestionTemplate(
        text="请分享一次你解决复杂问题的经历，你是如何拆解并推进的？",
        type=QuestionType.BEHAVIORAL,
        intent=QuestionIntent.ASK,
        expected_signals=("问题拆解", "行动路径", "结果复盘"),
    ),
    QuestionTemplate(
        text="如果面试官质疑你的经验不足，你会如何回应？",
        type=QuestionType.PRESSURE,
        intent=QuestionIntent.CHALLENGE,
        expected_signals=("抗压表达", "自我认知", "补足计划"),
    ),
    QuestionTemplate(
        text="请说明你接下来最希望提升的一项能力，以及你的训练计划。",
        type=QuestionType.CLOSING,
        intent=QuestionIntent.SUMMARIZE,
        expected_signals=("目标清晰", "行动计划", "自我驱动"),
    ),
)

QUESTION_BANK_BY_SCENARIO: dict[str, tuple[QuestionTemplate, ...]] = {
    "campus_general": (
        QuestionTemplate(
            text="请介绍一个你最有代表性的项目或实践经历，并说明你的具体贡献。",
            type=QuestionType.BEHAVIORAL,
            intent=QuestionIntent.ASK,
            expected_signals=("STAR 结构", "个人贡献", "结果量化"),
        ),
        QuestionTemplate(
            text="你为什么选择这个目标岗位？请结合自己的经历说明匹配度。",
            type=QuestionType.PROFESSIONAL,
            intent=QuestionIntent.ASK,
            expected_signals=("岗位理解", "经历匹配", "职业动机"),
        ),
        QuestionTemplate(
            text="如果入职后发现工作内容和预期不一致，你会如何处理？",
            type=QuestionType.PRESSURE,
            intent=QuestionIntent.CHALLENGE,
            expected_signals=("应变能力", "沟通策略", "稳定心态"),
        ),
    ),
    "civil_service_structured": (
        QuestionTemplate(
            text="面对一项临时且紧急的组织协调任务，你会如何安排优先级？",
            type=QuestionType.BEHAVIORAL,
            intent=QuestionIntent.ASK,
            expected_signals=("统筹意识", "优先级", "执行步骤"),
        ),
        QuestionTemplate(
            text="如果群众对你的解释并不认可，你会如何继续沟通？",
            type=QuestionType.PRESSURE,
            intent=QuestionIntent.CHALLENGE,
            expected_signals=("情绪稳定", "换位思考", "解决方案"),
        ),
        QuestionTemplate(
            text="请结合岗位要求，谈谈你认为基层服务最重要的能力是什么。",
            type=QuestionType.PROFESSIONAL,
            intent=QuestionIntent.ASK,
            expected_signals=("岗位认知", "服务意识", "价值判断"),
        ),
    ),
    "technical_intern": (
        QuestionTemplate(
            text="请展开说明你项目中的一个技术难点，以及你最终采用的解决方案。",
            type=QuestionType.PROFESSIONAL,
            intent=QuestionIntent.PROBE,
            expected_signals=("技术深度", "方案权衡", "结果验证"),
        ),
        QuestionTemplate(
            text="如果线上出现一个你无法立即定位的问题，你会如何排查？",
            type=QuestionType.PRESSURE,
            intent=QuestionIntent.CHALLENGE,
            expected_signals=("排查路径", "风险控制", "协作意识"),
        ),
        QuestionTemplate(
            text="请介绍一个你最近学习的新技术，并说明它适合解决什么问题。",
            type=QuestionType.PROFESSIONAL,
            intent=QuestionIntent.ASK,
            expected_signals=("学习能力", "应用场景", "技术判断"),
        ),
    ),
    "postgraduate_reexam": (
        QuestionTemplate(
            text="请介绍你最感兴趣的研究方向，以及你目前对它的理解。",
            type=QuestionType.PROFESSIONAL,
            intent=QuestionIntent.ASK,
            expected_signals=("研究兴趣", "专业基础", "学术表达"),
        ),
        QuestionTemplate(
            text="如果复试老师认为你的科研经历不足，你会如何回应？",
            type=QuestionType.PRESSURE,
            intent=QuestionIntent.CHALLENGE,
            expected_signals=("自我认知", "补足计划", "抗压能力"),
        ),
        QuestionTemplate(
            text="请说明你读研期间希望达成的一个具体目标。",
            type=QuestionType.CLOSING,
            intent=QuestionIntent.SUMMARIZE,
            expected_signals=("目标规划", "行动计划", "专业匹配"),
        ),
    ),
}


def _is_short_answer(text: str) -> bool:
    compact = "".join(text.split())
    return len(compact) < 20


def _make_question_id() -> str:
    return f"q_{uuid4().hex[:12]}"
