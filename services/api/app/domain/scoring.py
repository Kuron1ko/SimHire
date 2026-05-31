from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import mean

from app.schemas import (
    AbilityDimensions,
    AbilityEvaluation,
    ActionItem,
    ActionPriority,
    EmotionLabel,
    InterviewTurn,
    PracticeType,
    PsychologyDimensions,
    PsychologyEvaluation,
    QuestionType,
    ScoreItem,
    TranscriptSource,
    TurnFeedback,
)


@dataclass(frozen=True)
class ScoringProfile:
    answered_turns: list[InterviewTurn]
    total_chars: int
    average_chars: float
    short_answer_count: int
    very_short_answer_count: int
    structure_hits: list[str]
    action_hits: list[str]
    result_hits: list[str]
    quantification_count: int
    professional_hits: list[str]
    confidence_hits: list[str]
    uncertainty_hits: list[str]
    filler_text_count: int
    non_voice_answer_count: int
    speech_metric_count: int
    average_pause_count: float | None
    average_filler_word_count: float | None
    average_confidence_score: float | None
    emotion_labels: list[EmotionLabel]

    @property
    def has_speech_metrics(self) -> bool:
        return self.speech_metric_count > 0

    @property
    def has_non_voice_answers(self) -> bool:
        return self.non_voice_answer_count > 0


class DeterministicScoringEngine:
    def build_profile(self, turns: list[InterviewTurn]) -> ScoringProfile:
        answered_turns = [turn for turn in turns if turn.answer is not None]
        texts = [turn.answer.text.strip() for turn in answered_turns if turn.answer is not None]
        joined_text = "\n".join(texts)
        char_counts = [_text_length(text) for text in texts]
        speech_metrics = [turn.answer.speech_metrics for turn in answered_turns if turn.answer and turn.answer.speech_metrics]
        pause_counts = [metric.pause_count for metric in speech_metrics if metric and metric.pause_count is not None]
        filler_counts = [metric.filler_word_count for metric in speech_metrics if metric and metric.filler_word_count is not None]
        confidence_scores = [
            metric.confidence_score for metric in speech_metrics if metric and metric.confidence_score is not None
        ]
        emotion_labels = [metric.emotion_label for metric in speech_metrics if metric and metric.emotion_label is not None]

        return ScoringProfile(
            answered_turns=answered_turns,
            total_chars=sum(char_counts),
            average_chars=mean(char_counts) if char_counts else 0,
            short_answer_count=sum(1 for count in char_counts if count < 35),
            very_short_answer_count=sum(1 for count in char_counts if count < 18),
            structure_hits=_find_unique_hits(joined_text, STRUCTURE_WORDS),
            action_hits=_find_unique_hits(joined_text, ACTION_WORDS),
            result_hits=_find_unique_hits(joined_text, RESULT_WORDS),
            quantification_count=len(QUANTIFICATION_RE.findall(joined_text)),
            professional_hits=_find_unique_hits(joined_text, PROFESSIONAL_WORDS),
            confidence_hits=_find_unique_hits(joined_text, CONFIDENCE_WORDS),
            uncertainty_hits=_find_unique_hits(joined_text, UNCERTAINTY_WORDS),
            filler_text_count=sum(joined_text.count(word) for word in TEXT_FILLER_WORDS),
            non_voice_answer_count=sum(
                1
                for turn in answered_turns
                if turn.answer is not None and turn.answer.transcript_source == TranscriptSource.MANUAL
            ),
            speech_metric_count=len(speech_metrics),
            average_pause_count=mean(pause_counts) if pause_counts else None,
            average_filler_word_count=mean(filler_counts) if filler_counts else None,
            average_confidence_score=mean(confidence_scores) if confidence_scores else None,
            emotion_labels=emotion_labels,
        )

    def evaluate_ability(self, profile: ScoringProfile) -> AbilityEvaluation:
        logical_structure = self._score_logical_structure(profile)
        relevance = self._score_relevance(profile)
        specificity = self._score_specificity(profile)
        professional_depth = self._score_professional_depth(profile)
        communication_clarity = self._score_communication_clarity(profile)

        dimensions = AbilityDimensions(
            logical_structure=logical_structure,
            relevance=relevance,
            specificity=specificity,
            professional_depth=professional_depth,
            communication_clarity=communication_clarity,
        )
        return AbilityEvaluation(
            total=_sum_scores(
                logical_structure,
                relevance,
                specificity,
                professional_depth,
                communication_clarity,
                max_score=60,
            ),
            dimensions=dimensions,
        )

    def evaluate_psychology(self, profile: ScoringProfile) -> PsychologyEvaluation:
        if profile.has_non_voice_answers:
            return _zero_psychology_evaluation(profile.non_voice_answer_count)

        stress_tolerance = self._score_stress_tolerance(profile)
        confidence = self._score_confidence(profile)
        adaptability = self._score_adaptability(profile)
        emotional_stability = self._score_emotional_stability(profile)

        dimensions = PsychologyDimensions(
            stress_tolerance=stress_tolerance,
            confidence=confidence,
            adaptability=adaptability,
            emotional_stability=emotional_stability,
        )
        return PsychologyEvaluation(
            total=_sum_scores(stress_tolerance, confidence, adaptability, emotional_stability, max_score=40),
            dimensions=dimensions,
        )

    def evaluate_turns(self, profile: ScoringProfile) -> list[TurnFeedback]:
        feedback: list[TurnFeedback] = []
        for turn in profile.answered_turns:
            if turn.answer is None:
                continue
            text = turn.answer.text.strip()
            text_length = _text_length(text)
            has_structure = _contains_any(text, STRUCTURE_WORDS)
            has_specifics = bool(QUANTIFICATION_RE.search(text)) or _contains_any(text, RESULT_WORDS)
            has_action = _contains_any(text, ACTION_WORDS)
            score = 48
            score += 18 if text_length >= 60 else 8 if text_length >= 35 else -8
            score += 12 if has_structure else 0
            score += 12 if has_specifics else 0
            score += 8 if has_action else 0
            if turn.question.type in {QuestionType.PRESSURE, QuestionType.FOLLOW_UP} and text_length >= 45:
                score += 6

            highlights = []
            improvements = []
            if has_structure:
                highlights.append("回答中出现结构化表达线索。")
            if has_action:
                highlights.append("能描述自己的行动或推进方式。")
            if has_specifics:
                highlights.append("包含结果、数字或可验证信息。")
            if not highlights:
                highlights.append("已完成当前问题的基础回应。")

            if text_length < 35:
                improvements.append("回答偏短，需要补充背景、行动和结果。")
            if not has_structure:
                improvements.append("建议用“背景-行动-结果-复盘”组织回答。")
            if not has_specifics:
                improvements.append("建议补充数字、结果或个人贡献证据。")
            if not improvements:
                improvements.append("下一步可以压缩铺垫，把亮点前置。")

            feedback.append(
                TurnFeedback(
                    turn_id=turn.id,
                    summary=_turn_summary(text_length, has_structure, has_specifics),
                    score=_clamp(round(score, 1), 0, 100),
                    highlights=highlights,
                    improvements=improvements,
                )
            )

        return feedback

    def build_strengths(self, ability: AbilityEvaluation, psychology: PsychologyEvaluation) -> list[str]:
        strengths: list[str] = []
        if ability.dimensions.logical_structure.score >= 10:
            strengths.append("回答具备较清楚的结构意识，便于面试官跟随。")
        if ability.dimensions.specificity.score >= 10:
            strengths.append("能提供行动、结果或数字化信息，回答可信度较好。")
        if psychology.dimensions.adaptability.score >= 7:
            strengths.append("面对追问或压力题时能保持基本回应节奏。")
        if psychology.dimensions.confidence.score >= 7:
            strengths.append("表达中有一定主动性和自我确认感。")

        return _ensure_count(
            strengths,
            [
                "能够完成连续问答并保留上下文。",
                "回答覆盖了面试问题的基本方向。",
            ],
            minimum=2,
        )

    def build_risks(self, profile: ScoringProfile, ability: AbilityEvaluation, psychology: PsychologyEvaluation) -> list[str]:
        risks: list[str] = []
        if profile.short_answer_count:
            risks.append(f"有 {profile.short_answer_count} 轮回答偏短，可能影响信息完整度。")
        if ability.dimensions.specificity.score < 9:
            risks.append("案例、数据和结果证据不足，容易显得回答偏泛。")
        if ability.dimensions.logical_structure.score < 9:
            risks.append("结构化表达还不稳定，面试官可能难以快速抓住重点。")
        if profile.has_non_voice_answers:
            risks.append(f"检测到 {profile.non_voice_answer_count} 轮非语音回答，心理线按规则置为 0。")
        elif not profile.has_speech_metrics:
            risks.append("本次缺少语音指标，心理线为保守估计。")
        if psychology.dimensions.emotional_stability.score < 7:
            risks.append("停顿、口头禅或不确定表达可能影响稳定感。")

        return _ensure_count(
            risks,
            [
                "需要继续强化逐题复盘，避免只给结论不讲过程。",
                "建议准备更多可迁移的 STAR 案例。",
            ],
            minimum=2,
        )

    def build_action_plan(
        self,
        profile: ScoringProfile,
        ability: AbilityEvaluation,
        psychology: PsychologyEvaluation,
    ) -> list[ActionItem]:
        items: list[ActionItem] = []
        if ability.dimensions.logical_structure.score < 11 or profile.short_answer_count:
            items.append(
                ActionItem(
                    title="重写 3 个 STAR 案例",
                    description="每个案例固定写出背景、任务、行动、结果和复盘，控制在 90 秒内讲完。",
                    priority=ActionPriority.HIGH,
                    practice_type=PracticeType.STRUCTURE,
                )
            )
        if ability.dimensions.specificity.score < 11 or profile.quantification_count < 2:
            items.append(
                ActionItem(
                    title="补齐结果证据",
                    description="为项目、实习或学习经历补充数字、对比、产出物和个人贡献边界。",
                    priority=ActionPriority.HIGH,
                    practice_type=PracticeType.CONTENT,
                )
            )
        if profile.has_non_voice_answers:
            items.append(
                ActionItem(
                    title="使用全语音完成下一次模拟",
                    description="下一次练习请全程使用语音回答，避免手动输入导致心理线无法评分。",
                    priority=ActionPriority.HIGH,
                    practice_type=PracticeType.SPEECH,
                )
            )
        elif not profile.has_speech_metrics or psychology.dimensions.emotional_stability.score < 7:
            items.append(
                ActionItem(
                    title="增加语音复盘",
                    description="下一次练习开启语音输入，记录停顿、口头禅和语速，再对照文本复盘。",
                    priority=ActionPriority.MEDIUM,
                    practice_type=PracticeType.SPEECH,
                )
            )
        if psychology.dimensions.stress_tolerance.score < 7:
            items.append(
                ActionItem(
                    title="训练压力追问",
                    description="针对经验不足、结果不明显、选择动机等问题准备 5 个稳定回应模板。",
                    priority=ActionPriority.MEDIUM,
                    practice_type=PracticeType.PRESSURE,
                )
            )

        items.append(
            ActionItem(
                title="完成一次完整模拟",
                description="用同一场景连续完成 4 轮问答，并在报告中对比本次短板是否改善。",
                priority=ActionPriority.LOW,
                practice_type=PracticeType.MOCK,
            )
        )
        return items[:4] if len(items) >= 3 else _ensure_action_count(items)

    def _score_logical_structure(self, profile: ScoringProfile) -> ScoreItem:
        score = 7.0
        score += 5 if len(profile.structure_hits) >= 3 else 3 if profile.structure_hits else 0
        score += 1.5 if profile.average_chars >= 55 else 0
        score -= 2.2 * profile.short_answer_count
        evidence = [
            _hit_evidence("结构词", profile.structure_hits),
            f"平均回答长度约 {round(profile.average_chars)} 字。",
        ]
        if profile.short_answer_count:
            evidence.append(f"{profile.short_answer_count} 轮回答低于 35 字，结构展开不足。")
        return _score_item(
            score,
            15,
            evidence,
            "继续用 STAR 或“背景-行动-结果-复盘”固定组织每一题。",
        )

    def _score_relevance(self, profile: ScoringProfile) -> ScoreItem:
        score = 5.5
        score += 1.5 if profile.average_chars >= 45 else 0
        score += 1.5 if profile.professional_hits else 0
        score += 1 if profile.action_hits else 0
        score -= 1.5 * profile.very_short_answer_count
        evidence = [
            f"共完成 {len(profile.answered_turns)} 轮有效回答。",
            _hit_evidence("场景/岗位相关词", profile.professional_hits),
        ]
        if profile.very_short_answer_count:
            evidence.append(f"{profile.very_short_answer_count} 轮回答过短，可能没有充分贴合问题。")
        return _score_item(score, 10, evidence, "答题开头先点明问题关键词，再展开经历或观点。")

    def _score_specificity(self, profile: ScoringProfile) -> ScoreItem:
        score = 6.0
        score += min(profile.quantification_count, 3) * 1.6
        score += 2 if profile.result_hits else 0
        score += 2 if profile.action_hits else 0
        score += 1 if profile.total_chars >= 180 else 0
        score -= 2 * profile.short_answer_count
        evidence = [
            f"检测到 {profile.quantification_count} 处数字或量化表达。",
            _hit_evidence("结果词", profile.result_hits),
            _hit_evidence("行动词", profile.action_hits),
        ]
        return _score_item(score, 15, evidence, "每个关键经历至少补充一个数字、产出物或可验证结果。")

    def _score_professional_depth(self, profile: ScoringProfile) -> ScoreItem:
        score = 5.0
        score += min(len(profile.professional_hits), 5) * 0.7
        score += 1.2 if profile.action_hits else 0
        score += 1 if profile.total_chars >= 220 else 0
        score -= 1.2 * profile.short_answer_count
        evidence = [
            _hit_evidence("专业/场景词", profile.professional_hits),
            _hit_evidence("推进动作", profile.action_hits),
        ]
        return _score_item(score, 10, evidence, "把方法、工具、权衡和岗位理解说得更具体。")

    def _score_communication_clarity(self, profile: ScoringProfile) -> ScoreItem:
        score = 6.0
        score += 1.2 if profile.average_chars >= 45 else 0
        score += 1 if profile.structure_hits else 0
        score -= 1.2 * profile.filler_text_count
        score -= 1.8 * profile.very_short_answer_count
        evidence = [
            f"平均回答长度约 {round(profile.average_chars)} 字。",
            _hit_evidence("衔接/结构线索", profile.structure_hits),
        ]
        if profile.filler_text_count:
            evidence.append(f"文本中检测到 {profile.filler_text_count} 个口头填充词。")
        return _score_item(score, 10, evidence, "先给结论，再用短句补充依据，减少口头填充词。")

    def _score_stress_tolerance(self, profile: ScoringProfile) -> ScoreItem:
        pressure_turns = [
            turn
            for turn in profile.answered_turns
            if turn.question.type in {QuestionType.PRESSURE, QuestionType.FOLLOW_UP}
        ]
        score = 6.0
        score += 1.5 if pressure_turns and all(turn.answer and _text_length(turn.answer.text) >= 40 for turn in pressure_turns) else 0
        score += 0.8 if profile.structure_hits else 0
        score -= 1.3 * profile.very_short_answer_count
        if profile.average_pause_count is not None and profile.average_pause_count > 6:
            score -= 1.2
        evidence = [
            f"压力/追问题有效回答 {len(pressure_turns)} 轮。",
            _speech_evidence(profile, "停顿指标"),
        ]
        return _score_item(score, 10, evidence, "遇到质疑时先承认边界，再给补救行动和已有证据。")

    def _score_confidence(self, profile: ScoringProfile) -> ScoreItem:
        score = 6.0
        score += min(len(profile.confidence_hits), 3) * 0.6
        score -= min(len(profile.uncertainty_hits), 3) * 0.8
        if profile.average_confidence_score is not None:
            score = (score * 0.55) + (profile.average_confidence_score * 10 * 0.45)
        if profile.average_filler_word_count is not None and profile.average_filler_word_count > 5:
            score -= 1
        evidence = [
            _hit_evidence("自信表达", profile.confidence_hits),
            _hit_evidence("不确定表达", profile.uncertainty_hits),
            _speech_evidence(profile, "信心指标"),
        ]
        return _score_item(score, 10, evidence, "多使用明确动词说明个人贡献，少用模糊和自我削弱表达。")

    def _score_adaptability(self, profile: ScoringProfile) -> ScoreItem:
        adaptive_turns = [
            turn
            for turn in profile.answered_turns
            if turn.question.type in {QuestionType.FOLLOW_UP, QuestionType.PRESSURE, QuestionType.PROFESSIONAL}
        ]
        score = 6.0
        score += 1.5 if adaptive_turns else 0
        score += 1 if profile.action_hits else 0
        score += 0.8 if profile.result_hits else 0
        score -= 1.4 * profile.very_short_answer_count
        evidence = [
            f"涉及追问、压力或专业展开的回答 {len(adaptive_turns)} 轮。",
            _hit_evidence("调整/行动线索", profile.action_hits),
        ]
        return _score_item(score, 10, evidence, "根据问题类型调整回答重心，追问时优先补充缺失证据。")

    def _score_emotional_stability(self, profile: ScoringProfile) -> ScoreItem:
        score = 6.0
        if profile.average_pause_count is not None:
            score -= 1.2 if profile.average_pause_count > 6 else 0
            score += 0.5 if profile.average_pause_count <= 3 else 0
        if profile.average_filler_word_count is not None:
            score -= 1.2 if profile.average_filler_word_count > 5 else 0
            score += 0.5 if profile.average_filler_word_count <= 2 else 0
        if any(label in {EmotionLabel.NERVOUS, EmotionLabel.UNCERTAIN} for label in profile.emotion_labels):
            score -= 1.1
        if any(label in {EmotionLabel.CALM, EmotionLabel.CONFIDENT} for label in profile.emotion_labels):
            score += 0.8
        if not profile.has_speech_metrics:
            score -= 0.5
        evidence = [
            _speech_evidence(profile, "语音稳定性"),
            _emotion_evidence(profile.emotion_labels),
        ]
        return _score_item(score, 10, evidence, "下一次开启语音练习，重点观察停顿、口头禅和语速变化。")


def calculate_overall_score(ability: AbilityEvaluation, psychology: PsychologyEvaluation) -> float:
    return _clamp(round(ability.total + psychology.total, 1), 0, 100)


def _zero_psychology_evaluation(non_voice_answer_count: int) -> PsychologyEvaluation:
    evidence = [f"检测到 {non_voice_answer_count} 轮回答来自手动输入，未使用语音回答。"]
    suggestion = "请使用语音回答完成整场面试后，再生成心理线评分。"
    zero_item = ScoreItem(score=0, max_score=10, evidence=evidence, suggestion=suggestion)
    return PsychologyEvaluation(
        total=0,
        dimensions=PsychologyDimensions(
            stress_tolerance=zero_item,
            confidence=zero_item,
            adaptability=zero_item,
            emotional_stability=zero_item,
        ),
    )


def _score_item(raw_score: float, max_score: float, evidence: list[str], suggestion: str) -> ScoreItem:
    return ScoreItem(
        score=_clamp(round(raw_score, 1), 0, max_score),
        max_score=max_score,
        evidence=[item for item in evidence if item],
        suggestion=suggestion,
    )


def _sum_scores(*items: ScoreItem, max_score: float) -> float:
    return _clamp(round(sum(item.score for item in items), 1), 0, max_score)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _text_length(text: str) -> int:
    return len("".join(text.split()))


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word.lower() in text.lower() for word in words)


def _find_unique_hits(text: str, words: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [word for word in words if word.lower() in lowered]


def _hit_evidence(label: str, hits: list[str]) -> str:
    if hits:
        return f"{label}：{', '.join(hits[:6])}。"
    return f"未检测到明显{label}。"


def _speech_evidence(profile: ScoringProfile, label: str) -> str:
    if not profile.has_speech_metrics:
        return f"未提供 speechMetrics，{label}采用保守估计。"
    parts = [f"共有 {profile.speech_metric_count} 轮提供语音指标"]
    if profile.average_pause_count is not None:
        parts.append(f"平均停顿 {profile.average_pause_count:.1f} 次")
    if profile.average_filler_word_count is not None:
        parts.append(f"平均口头禅 {profile.average_filler_word_count:.1f} 次")
    if profile.average_confidence_score is not None:
        parts.append(f"平均信心 {profile.average_confidence_score:.2f}")
    return "，".join(parts) + "。"


def _emotion_evidence(labels: list[EmotionLabel]) -> str:
    if not labels:
        return "未提供可用情绪标签。"
    return "情绪标签：" + ", ".join(label.value for label in labels[:4]) + "。"


def _turn_summary(text_length: int, has_structure: bool, has_specifics: bool) -> str:
    if text_length < 35:
        return "回答完成了基础回应，但信息量偏少。"
    if has_structure and has_specifics:
        return "回答结构和证据较完整，适合继续压缩重点。"
    if has_structure:
        return "回答结构较清楚，但还需要补充更具体的结果。"
    if has_specifics:
        return "回答有一定证据，但表达结构还可以更清晰。"
    return "回答方向基本成立，但需要强化结构和证据。"


def _ensure_count(items: list[str], fallbacks: list[str], *, minimum: int) -> list[str]:
    result = list(items)
    for fallback in fallbacks:
        if len(result) >= minimum:
            break
        if fallback not in result:
            result.append(fallback)
    return result


def _ensure_action_count(items: list[ActionItem]) -> list[ActionItem]:
    result = list(items)
    fallbacks = [
        ActionItem(
            title="补充岗位关键词",
            description="把目标岗位要求拆成能力、经历和动机三类，并在回答中主动对应。",
            priority=ActionPriority.MEDIUM,
            practice_type=PracticeType.CONTENT,
        ),
        ActionItem(
            title="做一次限时表达",
            description="每题先用 15 秒列提纲，再用 90 秒完整表达，训练重点排序。",
            priority=ActionPriority.MEDIUM,
            practice_type=PracticeType.STRUCTURE,
        ),
        ActionItem(
            title="复盘一次完整模拟",
            description="完成 3 到 4 轮模拟后，只挑一个最高频问题做二次回答。",
            priority=ActionPriority.LOW,
            practice_type=PracticeType.MOCK,
        ),
    ]
    for item in fallbacks:
        if len(result) >= 3:
            break
        result.append(item)
    return result


STRUCTURE_WORDS = (
    "首先",
    "其次",
    "最后",
    "第一",
    "第二",
    "第三",
    "背景",
    "任务",
    "行动",
    "结果",
    "复盘",
    "总结",
    "STAR",
    "first",
    "second",
    "finally",
)
ACTION_WORDS = (
    "负责",
    "推进",
    "协调",
    "设计",
    "实现",
    "优化",
    "解决",
    "梳理",
    "沟通",
    "落地",
    "完成",
    "主导",
    "参与",
    "分析",
)
RESULT_WORDS = (
    "结果",
    "提升",
    "降低",
    "增长",
    "上线",
    "完成",
    "获得",
    "产出",
    "效率",
    "转化",
    "满意",
    "复盘",
)
PROFESSIONAL_WORDS = (
    "岗位",
    "项目",
    "用户",
    "业务",
    "产品",
    "技术",
    "系统",
    "数据",
    "模型",
    "研究",
    "服务",
    "组织",
    "方法",
    "指标",
)
CONFIDENCE_WORDS = (
    "我负责",
    "我主导",
    "我完成",
    "能够",
    "可以",
    "会",
    "我认为",
    "有把握",
)
UNCERTAINTY_WORDS = (
    "不知道",
    "不会",
    "不确定",
    "可能吧",
    "没什么",
    "还行",
    "随便",
)
TEXT_FILLER_WORDS = ("嗯", "呃", "额", "然后然后", "就是就是")
QUANTIFICATION_RE = re.compile(r"\d+(?:\.\d+)?%?|\b[一二三四五六七八九十百千万]+个?\b")
