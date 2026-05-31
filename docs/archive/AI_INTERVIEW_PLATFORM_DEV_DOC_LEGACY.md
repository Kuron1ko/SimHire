# AI 面试模拟平台开发文档

来源材料：`12.pptx`

目标读者：后续负责具体实现的 subagent、项目负责人、测试与集成 agent。

## 1. 项目定位

本项目来自 PPT 中的“AI 面试模拟系统”设想，面向在校学生、求职新人和需要高频面试训练的人群。平台要解决三个核心问题：

1. 线下面试训练资源有限、流程繁琐、成本高。
2. 题库和面经社区只有单向阅读，缺少真实互动。
3. 现有 AI 面试多停留在文字或语音互动，真实感、评价维度和复盘能力不足。

长期目标是一个多模态 AI 面试训练平台，支持视频、语音、文字输入，提供沉浸式模拟、个性化评价和系统化复盘。

第一阶段只实现 MVP：

1. 一个可用的 Web 前端界面。
2. 语音输入：用户可以说出回答，前端转写成文本。
3. 语音输出：AI 面试官的问题可以播报。
4. 面试流程：创建会话，AI 提问，用户回答，AI 追问或进入下一题。
5. 评价系统：面试结束后输出能力线和心理线评价报告。

第一阶段不实现但要预留接口：

1. 视频输入、表情识别、姿态识别。
2. 多智能体并行评估。
3. 意图驱动行为编排器。
4. 简历解析与岗位匹配。
5. 高校端、企业端、会员和支付。
6. 面试复盘视频时间线。

## 2. MVP 产品闭环

MVP 要形成“模拟、评分、复盘”的最小闭环。

用户路径：

1. 进入首页或练习页。
2. 选择面试场景，例如通用校招面试、公考结构化面试、研究生复试、技术岗面试。
3. 点击开始面试。
4. AI 面试官播报第一题，同时页面显示题目文本。
5. 用户点击录音按钮，用语音回答。前端完成语音识别，允许用户编辑识别结果。
6. 用户提交回答。
7. 后端记录问答，并生成下一题、追问或结束建议。
8. 完成 3 到 5 轮问答后，用户点击结束，或者系统达到题数后自动结束。
9. 后端生成评价报告，页面展示总分、分项分、问题诊断、改进建议和推荐练习方向。

MVP 成功标准：

1. 不依赖视频能力也能完整跑完一次面试。
2. 浏览器中可以完成语音输入和语音播报。
3. 没有真实 LLM Key 时，可以用 mock provider 跑通流程。
4. Agent F 完成后，有真实 LLM Key 时可以切换到真实提问和真实评价。
5. 所有核心数据结构稳定，后续 agent 可以基于接口扩展。

当前 A-E 基线状态：

1. 已跑通场景选择、创建会话、文本/语音回答、追问/下一题、结束面试、评价报告页。
2. 后端使用内存 Repository 和确定性 mock 题目/评分，尚未接入真实 LLM provider 和数据库持久化。
3. 前端已完成 Vite/React 页面、浏览器 STT/TTS、报告展示；尚未加入前端自动化测试。
4. 当前整体回归以 OpenAPI 类型生成、后端 pytest、前端 build 和 API 冒烟为准；真实浏览器语音点击验收需要可用浏览器实例。

## 3. 推荐技术栈

第一阶段推荐 Web 优先，不先做桌面端。PPT 提到 PC 端软件，后续可以用 Electron 或 Tauri 包装 Web 版本。

前端：

1. React + TypeScript + Vite。
2. React Router 管理页面。
3. Zustand 或 React Context 只管理跨页面轻量状态；面试房间内部使用显式有限状态机，避免录音、播报、提交互相抢状态。
4. Web Speech API 实现 MVP 语音识别和语音合成，MediaStream API 实现麦克风音量反馈。
5. fetch 封装 API client。
6. `openapi-typescript` 或同类工具从后端 OpenAPI 自动生成前端类型。

后端：

1. Python FastAPI。
2. Pydantic 定义请求、响应和内部领域模型。
3. 当前 MVP 使用内存 Repository 跑通闭环；SQLite 是下一阶段持久化目标，Repository 层预留 PostgreSQL 替换空间。
4. LLM Provider Adapter 隔离模型厂商。
5. REST API 完成第一阶段交互，WebSocket 仅预留。

开发协作：

1. 后端 Pydantic schema 是前后端契约的唯一数据源。FastAPI 自动生成 OpenAPI，前端类型由 OpenAPI 自动生成，不手写重复 TS 类型。
2. 第一阶段直接把 OpenAPI 类型生成到 `apps/web/src/types/generated/api.ts`，暂不引入 `packages/shared`，避免生成产物有两份。
3. subagent 采用“契约优先 + 垂直业务闭环”为主的协作方式：先由契约 agent 固定公共模型，再按场景、问答、语音、评价等闭环派发。
4. 公共 schema、API path、评分维度、面试房间状态机不能私自改名，改动需要同步本文档和生成产物。

## 4. 仓库结构

当前 MVP 使用以下项目结构。不要为了未来能力提前创建空文件；第 13 章扩展模块需要实现时再新增对应文件。

```text
SimHire/
  12.pptx
  .gitignore
  docs/
    AI_INTERVIEW_PLATFORM_DEV_DOC.md
  reply.txt
  apps/
    web/
      package.json
      package-lock.json
      index.html
      vite.config.ts
      tsconfig.json
      src/
        main.tsx
        App.tsx
        routes.tsx
        pages/
          InterviewSetupPage.tsx
          InterviewRoomPage.tsx
          EvaluationReportPage.tsx
        components/
          interview/
            VoiceRecorderButton.tsx
            SpeechPlaybackButton.tsx
            VolumeMeter.tsx
          evaluation/
            ScoreSummary.tsx
            DimensionScores.tsx
            FindingList.tsx
            TurnFeedbackList.tsx
            ActionPlanList.tsx
        hooks/
          useInterviewSession.ts
          useInterviewRoomState.ts
          useSpeechRecognition.ts
          useSpeechSynthesis.ts
          useEvaluationReport.ts
        services/
          apiClient.ts
          interviewApi.ts
          scenarioApi.ts
          evaluationApi.ts
        types/
          generated/
            api.ts
        styles/
          globals.css
  services/
    api/
      pyproject.toml
      README.md
      app/
        main.py
        dependencies.py
        export_openapi.py
        core/
          config.py
          errors.py
        api/
          router.py
          routes/
            health.py
            scenarios.py
            interviews.py
            evaluations.py
        schemas/
          scenario.py
          interview.py
          evaluation.py
          error.py
          common.py
          base.py
          enums.py
        domain/
          scoring.py
        services/
          interview_orchestrator.py
          question_agent.py
          evaluation_service.py
        repositories/
          session_repository.py
          scenario_repository.py
          evaluation_repository.py
        data/
          seed_scenarios.json
        tests/
          test_contracts.py
          test_agent_b_flow.py
          test_agent_c_flow.py
          test_evaluation_service.py
  scripts/
    export-openapi.ps1
    generate-api-types.ps1
```

说明：

1. `apps/web` 只负责浏览器界面、录音交互、TTS 播放和 API 调用。
2. `services/api` 负责面试流程、评分、统一错误和内存数据仓库；真实 LLM 和数据库持久化在后续阶段接入。
3. `services/api/app/schemas` 中的 Pydantic 模型是契约源头；FastAPI 生成 OpenAPI，前端类型从 OpenAPI 自动生成。
4. `services/api/app/dependencies.py` 持有当前内存仓库和服务实例，保证 interview 与 evaluation 使用同一个 `SessionRepository`。
5. 真实 LLM provider、prompt builder、行为编排器、服务端语音等扩展不要放进 MVP 主目录；需要实现时按第 13 章新增文件。

## 5. 核心领域模型

本节描述领域对象和字段语义。代码片段是概念示意，最终接口契约必须以 `services/api/app/schemas` 中的 Pydantic 模型和自动生成的 OpenAPI 为准；前端不要复制这些片段手写 DTO。

### 5.1 Scenario

面试场景。由种子数据提供，后续可后台管理。

```ts
export type InterviewScenario = {
  id: string;
  name: string;
  description: string;
  category: "campus" | "civil_service" | "postgraduate" | "technical" | "general";
  defaultQuestionCount: number;
  difficulty: "easy" | "medium" | "hard";
  rubricId: string;
  openingPrompt: string;
};
```

### 5.2 InterviewSession

一次面试会话。

```ts
export type InterviewSession = {
  id: string;
  scenarioId: string;
  status: "created" | "in_progress" | "completed" | "cancelled";
  mode: "text" | "voice" | "multimodal";
  language: "zh-CN" | "en-US";
  questionCountTarget: number;
  currentTurnIndex: number;
  createdAt: string;
  completedAt?: string;
};
```

### 5.3 InterviewTurn

一轮问答。

```ts
export type InterviewTurn = {
  id: string;
  sessionId: string;
  index: number;
  question: InterviewQuestion;
  answer?: CandidateAnswer;
  createdAt: string;
  answeredAt?: string;
};
```

```ts
export type InterviewQuestion = {
  id: string;
  text: string;
  type: "opening" | "behavioral" | "professional" | "pressure" | "follow_up" | "closing";
  intent: "ask" | "probe" | "challenge" | "encourage" | "summarize";
  expectedSignals: string[];
};
```

```ts
export type CandidateAnswer = {
  text: string;
  transcriptSource: "manual" | "browser_stt" | "server_asr";
  audioUrl?: string;
  durationMs?: number;
  speechMetrics?: SpeechMetrics;
};
```

### 5.4 SpeechMetrics

MVP 可只填充部分字段，先保留结构。

```ts
export type SpeechMetrics = {
  speakingRateWpm?: number;
  pauseCount?: number;
  fillerWordCount?: number;
  confidenceScore?: number;
  emotionLabel?: "calm" | "nervous" | "confident" | "uncertain" | "unknown";
};
```

### 5.5 EvaluationReport

评价体系遵循 PPT 中的“能力线 + 心理线”。

```ts
export type EvaluationReport = {
  id: string;
  sessionId: string;
  overallScore: number;
  ability: AbilityEvaluation;
  psychology: PsychologyEvaluation;
  turnFeedback: TurnFeedback[];
  strengths: string[];
  risks: string[];
  actionPlan: ActionItem[];
  generatedAt: string;
};
```

```ts
export type AbilityEvaluation = {
  total: number;
  dimensions: {
    logicalStructure: ScoreItem;
    relevance: ScoreItem;
    specificity: ScoreItem;
    professionalDepth: ScoreItem;
    communicationClarity: ScoreItem;
  };
};
```

```ts
export type PsychologyEvaluation = {
  total: number;
  dimensions: {
    stressTolerance: ScoreItem;
    confidence: ScoreItem;
    adaptability: ScoreItem;
    emotionalStability: ScoreItem;
  };
};
```

```ts
export type ScoreItem = {
  score: number;
  maxScore: number;
  evidence: string[];
  suggestion: string;
};
```

```ts
export type TurnFeedback = {
  turnId: string;
  summary: string;
  score: number;
  highlights: string[];
  improvements: string[];
};
```

```ts
export type ActionItem = {
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  practiceType: "structure" | "content" | "speech" | "pressure" | "mock";
};
```

## 6. API 契约

MVP 使用 REST。后续实时语音、视频同步和行为编排再引入 WebSocket。

契约生成规则：

1. `services/api/app/schemas` 中的 Pydantic 模型是唯一人工维护的接口模型。
2. FastAPI 暴露 `/openapi.json`。
3. 前端通过 `openapi-typescript http://127.0.0.1:8000/openapi.json -o apps/web/src/types/generated/api.ts` 生成类型。
4. `apps/web/src/types/ui.ts` 只能写 UI 状态类型和前端派生类型，不能复制后端 DTO。
5. 任何接口字段变更必须先改 Pydantic，再重新生成 OpenAPI 和 TS 类型。

### 6.1 Health

```http
GET /api/health
```

响应：

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### 6.2 获取面试场景

```http
GET /api/scenarios
```

响应：

```json
{
  "items": [
    {
      "id": "campus_general",
      "name": "通用校招面试",
      "description": "适合应届生综合素质训练",
      "category": "campus",
      "defaultQuestionCount": 4,
      "difficulty": "medium",
      "rubricId": "default_v1",
      "openingPrompt": "请先做一个 1 分钟自我介绍。"
    }
  ]
}
```

### 6.3 创建面试会话

```http
POST /api/interviews/sessions
```

请求：

```json
{
  "scenarioId": "campus_general",
  "mode": "voice",
  "language": "zh-CN",
  "questionCountTarget": 4,
  "candidateProfile": {
    "name": "可选",
    "targetRole": "产品经理实习生",
    "background": "可选的简历摘要"
  }
}
```

响应：

```json
{
  "session": {
    "id": "session_123",
    "scenarioId": "campus_general",
    "status": "in_progress",
    "mode": "voice",
    "language": "zh-CN",
    "questionCountTarget": 4,
    "currentTurnIndex": 1,
    "createdAt": "2026-05-30T00:00:00Z"
  },
  "turn": {
    "id": "turn_1",
    "sessionId": "session_123",
    "index": 1,
    "question": {
      "id": "q_1",
      "text": "请先做一个 1 分钟自我介绍。",
      "type": "opening",
      "intent": "ask",
      "expectedSignals": ["表达结构", "经历匹配", "自信程度"]
    },
    "createdAt": "2026-05-30T00:00:00Z"
  }
}
```

### 6.4 提交回答并获取下一步

```http
POST /api/interviews/sessions/{sessionId}/answers
```

请求：

```json
{
  "turnId": "turn_1",
  "answer": {
    "text": "老师您好，我是...",
    "transcriptSource": "browser_stt",
    "durationMs": 52000,
    "speechMetrics": {
      "speakingRateWpm": 180,
      "pauseCount": 4,
      "fillerWordCount": 3,
      "emotionLabel": "nervous"
    }
  }
}
```

响应：

```json
{
  "nextAction": "next_question",
  "assistantAck": "好的，我会继续追问你的项目贡献。",
  "nextTurn": {
    "id": "turn_2",
    "sessionId": "session_123",
    "index": 2,
    "question": {
      "id": "q_2",
      "text": "你刚才提到项目经历，请具体说明你在其中承担的角色和结果。",
      "type": "follow_up",
      "intent": "probe",
      "expectedSignals": ["STAR 结构", "结果量化", "个人贡献"]
    },
    "createdAt": "2026-05-30T00:01:00Z"
  }
}
```

`nextAction` 取值：

1. `next_question`：继续下一题。
2. `follow_up`：追问。
3. `finish_available`：已经满足结束条件，可结束。
4. `auto_finish`：系统自动结束并生成报告。

### 6.5 结束面试并生成报告

```http
POST /api/interviews/sessions/{sessionId}/finish
```

响应：

```json
{
  "reportId": "report_123",
  "status": "generated"
}
```

### 6.6 获取报告

```http
GET /api/evaluations/reports/{reportId}
```

响应：完整 `EvaluationReport`。

### 6.7 语音与实时能力边界

MVP 使用浏览器 Web Speech API 和 `speechSynthesis`，不提供服务端 ASR/TTS 和 WebSocket 实时事件接口。服务端语音、实时字幕、视频同步和行为编排事件统一放到第 13 章扩展模块。

## 7. 后端模块设计

### 7.1 app/main.py

职责：

1. 创建 FastAPI app。
2. 注册 CORS。
3. 注册 `/api` router。
4. 注册异常处理。

建议接口：

```py
def create_app() -> FastAPI:
    ...
```

### 7.2 core/config.py

职责：

1. 从环境变量读取配置。
2. 提供模型供应商开关。
3. MVP 默认 `LLM_PROVIDER=mock`，避免没有 Key 时无法开发。

关键配置：

```text
APP_ENV=local
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./simhire.db
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=
```

### 7.3 repositories

Repository 层不要写业务规则，只负责数据存取。

`SessionRepository`：

```py
class SessionRepository:
    async def create_session(self, session: InterviewSession) -> InterviewSession: ...
    async def get_session(self, session_id: str) -> InterviewSession | None: ...
    async def update_session(self, session: InterviewSession) -> InterviewSession: ...
    async def list_turns(self, session_id: str) -> list[InterviewTurn]: ...
    async def append_turn(self, turn: InterviewTurn) -> InterviewTurn: ...
    async def save_answer(self, session_id: str, turn_id: str, answer: CandidateAnswer) -> InterviewTurn: ...
```

`ScenarioRepository`：

```py
class ScenarioRepository:
    async def list_scenarios(self) -> list[InterviewScenario]: ...
    async def get_scenario(self, scenario_id: str) -> InterviewScenario | None: ...
```

`EvaluationRepository`：

```py
class EvaluationRepository:
    async def save_report(self, report: EvaluationReport) -> EvaluationReport: ...
    async def get_report(self, report_id: str) -> EvaluationReport | None: ...
```

### 7.4 interview_orchestrator.py

面试流程的总控服务。前端所有核心流程都应通过它间接完成。

```py
class InterviewOrchestrator:
    async def start_session(self, command: StartSessionCommand) -> StartSessionResult:
        ...

    async def submit_answer(self, command: SubmitAnswerCommand) -> SubmitAnswerResult:
        ...

    async def finish_session(self, session_id: str) -> FinishSessionResult:
        ...
```

职责：

1. 创建会话。
2. 调用 `QuestionAgent` 生成首题或下一题。
3. 保存用户回答。
4. 判断是否达到结束条件。
5. 调用 `EvaluationService` 生成报告。

禁止：

1. 不直接拼接大段 prompt，prompt 交给 `PromptBuilder`。
2. 不直接调用具体模型 SDK，模型调用交给 provider。

### 7.5 question_agent.py

生成面试问题、追问和结束语。

```py
class QuestionAgent:
    async def generate_first_question(
        self,
        scenario: InterviewScenario,
        candidate_profile: CandidateProfile | None,
    ) -> InterviewQuestion:
        ...

    async def generate_next_question(
        self,
        context: InterviewContext,
    ) -> QuestionDecision:
        ...
```

`QuestionDecision`：

```py
class QuestionDecision(BaseModel):
    next_action: Literal["next_question", "follow_up", "finish_available", "auto_finish"]
    question: InterviewQuestion | None = None
    assistant_ack: str | None = None
```

MVP 策略：

1. `mock_provider` 按场景从固定题库取题。
2. 真实 LLM 模式根据场景、历史问答和目标题数生成下一题。
3. 如果上一题回答太短，优先生成追问。

### 7.6 evaluation_service.py

生成并读取评价报告。当前 MVP 的外部入口是 `get_report(report_id)`：`finish` 接口只返回 `reportId`，前端进入报告页后再调用 `GET /api/evaluations/reports/{reportId}`。服务端解析 `report_{sessionId}`，校验会话已完成且回答数量足够，然后生成并缓存报告。

```py
class EvaluationService:
    async def get_report(self, report_id: str) -> EvaluationReport:
        ...

    def _evaluate_ability(self, profile: ScoringProfile) -> AbilityEvaluation:
        ...

    def _evaluate_psychology(self, profile: ScoringProfile) -> PsychologyEvaluation:
        ...

    def _evaluate_turns(self, profile: ScoringProfile) -> list[TurnFeedback]:
        ...

    def _build_action_plan(
        self,
        profile: ScoringProfile,
        ability: AbilityEvaluation,
        psychology: PsychologyEvaluation,
    ) -> list[ActionItem]:
        ...
```

实现策略：

1. `get_report` 是当前对外稳定入口；后续接入真实 LLM 时也不要让 LLM 一次性输出完整大报告。
2. 把评价拆成能力线、心理线、逐题反馈、行动计划四个步骤，能并发的步骤可以并发执行。
3. 每个步骤输出较小的结构化对象，再由业务代码组装成最终 `EvaluationReport`。
4. 支持严格 schema 输出能力的 LLM provider 应优先使用模型原生结构化输出；不支持时才使用 prompt JSON、Pydantic 校验、一次重试和 fallback。
5. 当前 `DeterministicScoringEngine` 是 mock 评分路径；后续 provider 也必须按同样的拆分接口返回数据，保证前端和测试不依赖真实模型。

评分原则：

1. 能力线 60 分：逻辑结构、相关性、具体性、专业深度、表达清晰度。
2. 心理线 40 分：抗压、信心、应变、情绪稳定。
3. 每个分项必须有证据和建议，证据来自用户回答文本或语音指标。
4. 报告不能只有泛泛建议，至少给 3 条可执行练习计划。
5. 最终报告的总分由后端根据能力线和心理线计算，不完全信任模型自报总分。

MVP fallback 规则：

1. 回答字数太短，相关性和具体性扣分。
2. 包含数字、结果、行动词时，具体性加分。
3. 使用“首先、其次、最后、背景、行动、结果”等结构词时，逻辑结构加分。
4. `pauseCount`、`fillerWordCount` 偏高时，信心和情绪稳定扣分。
5. 只要存在 `transcriptSource="manual"` 的非语音回答，心理线总分和全部心理分项直接置为 0，并在证据、风险和行动计划中标注原因。
6. 全部回答都来自 `browser_stt` 或 `server_asr` 时，即使暂时没有细粒度 `speechMetrics`，心理线仍可基于文本和可用语音元数据保守估计，并标注“语音指标不足”。

### 7.7 后续 prompt_builder.py

后续接入真实 LLM provider 时再创建。它用于集中管理 prompt，防止 prompt 分散在业务代码里。

```py
class PromptBuilder:
    def build_question_prompt(self, context: InterviewContext) -> str: ...
    def build_evaluation_prompt(self, context: EvaluationContext) -> str: ...
```

要求：

1. 所有 prompt 输出都要求结构化数据，优先走 provider 原生 strict schema 或 JSON schema 能力。
2. prompt 中明确评分 rubric、输出 schema 名称和证据引用要求。
3. LLM 输出必须经过 Pydantic 校验。
4. 校验失败时最多重试一次，再走 fallback。
5. 不同评价步骤使用独立 prompt，避免一个 prompt 同时要求输出过深的嵌套 JSON。

### 7.8 后续 behavior_orchestrator.py

后续实现 PPT 中“意图驱动行为编排器”时再创建，当前 MVP 不创建该文件。

未来最小接口可以只输出基础语音参数：

```py
class BehaviorOrchestrator:
    def plan_speech_style(self, intent: str) -> SpeechStyle:
        ...
```

示例：

```json
{
  "intent": "encourage",
  "speechStyle": {
    "rate": 0.95,
    "pitch": 1.05,
    "volume": 1.0
  },
  "facialExpression": null,
  "gesture": null
}
```

后续扩展：

1. 把 `intent` 转成语速、语调、音量。
2. 联动数字人表情强度、停顿、点头、追问语气。
3. 与视频生成或实时 avatar 系统对接。

### 7.9 后续 providers/llm

后续 Agent F 接入真实 LLM 时再创建 `services/api/app/providers/llm`。当前 MVP 使用 `question_agent.py` 和 `DeterministicScoringEngine` 提供确定性 mock 行为，不创建 provider 空目录。

`base.py`：

```py
class LLMProvider(Protocol):
    supports_strict_schema: bool

    async def generate_json(self, prompt: str, schema_name: str) -> dict:
        ...

    async def generate_structured(
        self,
        prompt: str,
        schema_name: str,
        json_schema: dict,
    ) -> dict:
        ...

    async def generate_text(self, prompt: str) -> str:
        ...
```

`mock_provider.py`：

1. 不调用外部 API。
2. 返回固定但合理的问题和报告。
3. 用于前端和流程联调。

`openai_provider.py`：

1. 通过环境变量读取 Key 和模型名。
2. 不在代码中硬编码 Key。
3. 出错时抛出统一业务异常。
4. 如果模型支持严格结构化输出，`generate_structured` 必须使用模型原生 schema 约束；否则退回 `generate_json` 加校验。

## 8. 前端模块设计

### 8.1 页面

`InterviewSetupPage.tsx`

职责：

1. 拉取 `/api/scenarios`。
2. 展示场景卡片。
3. 配置题数、目标岗位、是否启用语音。
4. 调用创建会话 API。

`InterviewRoomPage.tsx`

职责：

1. 展示当前问题。
2. 播报 AI 问题。
3. 录音识别回答。
4. 允许编辑转写文本。
5. 提交回答，展示下一题或结束入口。
6. 展示简短阶段反馈。

`EvaluationReportPage.tsx`

职责：

1. 展示总分。
2. 展示能力线和心理线。
3. 展示逐题反馈。
4. 展示下一步训练建议。

### 8.2 hooks

`useInterviewSession.ts`

```ts
export function useInterviewSession() {
  return {
    roomState,
    session,
    currentTurn,
    timeline,
    finishAvailable,
    finishResult,
    lastAssistantAck,
    isSubmitting,
    isFinishing,
    canSpeak,
    canRecord,
    canSubmit,
    canFinish,
    error,
    dispatchRoomAction,
    submitAnswer,
    finishSession,
    resetSession,
  };
}
```

`roomState` 必须来自有限状态机，而不是由多个 boolean 临时拼接。

```ts
export type InterviewRoomState =
  | "idle"
  | "speaking_question"
  | "ready_to_answer"
  | "recording"
  | "reviewing_transcript"
  | "submitting_answer"
  | "loading_next_question"
  | "finishing"
  | "completed"
  | "error";
```

状态规则：

1. `recording` 状态禁止重复开始录音。
2. `submitting_answer` 和 `loading_next_question` 状态禁止录音、重播和二次提交。
3. 进入 `recording` 前必须停止当前 TTS 播报。
4. 进入 `submitting_answer` 前必须停止录音和 TTS。
5. 语音识别结束后进入 `reviewing_transcript`，允许用户编辑文本再提交。
6. 状态切换由 `useInterviewRoomState.ts` 的 reducer 管理，UI 组件只根据 `canRecord`、`canSpeak`、`canSubmit` 渲染可用操作。

`useInterviewRoomState.ts`

```ts
export type InterviewRoomAction =
  | { type: "SESSION_READY" }
  | { type: "SPEAK_START" }
  | { type: "SPEAK_END" }
  | { type: "RECORD_START" }
  | { type: "RECORD_STOP" }
  | { type: "SUBMIT_START" }
  | { type: "NEXT_TURN_READY" }
  | { type: "FINISH_AVAILABLE" }
  | { type: "FINISH_START" }
  | { type: "COMPLETE" }
  | { type: "FAIL" }
  | { type: "RESET" };
```

实现要求：

1. 非法状态跳转要被忽略或返回明确错误，不能让 UI 进入半录音半提交状态。
2. reducer 单元测试必须覆盖“提交中点击录音”“播报中开始录音”“录音中提交”这几类冲突。

`startSession`：

```ts
type StartSessionInput = {
  scenarioId: string;
  mode: "text" | "voice";
  language: "zh-CN" | "en-US";
  questionCountTarget: number;
  candidateProfile?: {
    name?: string;
    targetRole?: string;
    background?: string;
  };
};
```

`submitAnswer`：

```ts
type SubmitAnswerInput = {
  turnId: string;
  text: string;
  transcriptSource: "manual" | "browser_stt" | "server_asr";
  durationMs?: number;
  speechMetrics?: SpeechMetrics;
};
```

`useSpeechRecognition.ts`

```ts
export function useSpeechRecognition(options: {
  language: "zh-CN" | "en-US";
  continuous?: boolean;
}) {
  return {
    isSupported,
    isListening,
    hasPermission,
    volumeLevel,
    transcript,
    interimTranscript,
    error,
    start,
    stop,
    reset,
  };
}
```

实现要求：

1. 使用浏览器 `SpeechRecognition` 或 `webkitSpeechRecognition`。
2. 不支持时返回 `isSupported=false`，页面自动切换到文本输入。
3. 识别中实时更新草稿。
4. 使用 `navigator.mediaDevices.getUserMedia` 和 Web Audio API 计算 `volumeLevel`，供 `VolumeMeter` 展示麦克风音量。
5. 停止后把最终文本写入回答框，并让回答输入框自动聚焦，方便用户修正识别错误。
6. 识别卡住或报错时保留已有 transcript，允许用户直接手动接管。

`useSpeechSynthesis.ts`

```ts
export function useSpeechSynthesis() {
  return {
    isSupported,
    isSpeaking,
    speak,
    cancel,
  };
}
```

`speak`：

```ts
type SpeakInput = {
  text: string;
  lang: "zh-CN" | "en-US";
  rate?: number;
  pitch?: number;
  volume?: number;
};
```

实现要求：

1. 使用浏览器 `speechSynthesis`。
2. 问题加载后可以自动播报，但页面必须提供停止按钮。
3. 用户提交回答时停止当前播报。

`useEvaluationReport.ts`

```ts
export function useEvaluationReport(reportId?: string) {
  return {
    report,
    isLoading,
    error,
    reload,
  };
}
```

### 8.3 UI 组件

`VoiceRecorderButton.tsx`

Props：

```ts
type VoiceRecorderButtonProps = {
  isSupported: boolean;
  isListening: boolean;
  disabled?: boolean;
  error?: string | null;
  onStart: () => void;
  onStop: () => void;
};
```

`SpeechPlaybackButton.tsx`

Props：

```ts
type SpeechPlaybackButtonProps = {
  isSupported: boolean;
  isSpeaking: boolean;
  disabled?: boolean;
  hasPlayed?: boolean;
  onPlay: () => void;
  onStop: () => void;
};
```

`VolumeMeter.tsx`

Props：

```ts
type VolumeMeterProps = {
  level: number;
  active: boolean;
  hasPermission?: boolean | null;
};
```

实现要求：

1. `level` 范围归一到 `0-1`。
2. 录音中必须持续显示音量变化，让用户知道麦克风正在工作。
3. 没有麦克风权限或浏览器不支持时，显示安静的禁用态，不阻塞文本输入。

`ScoreSummary.tsx`

展示总分、能力线分数、心理线分数。

`DimensionScores.tsx`

展示能力线或心理线的分项分、证据和建议。

`FindingList.tsx`

展示优势和风险。

`TurnFeedbackList.tsx`

展示逐题总结、亮点和改进建议。

`ActionPlanList.tsx`

展示后续练习计划和优先级。

## 9. 评分体系

总分 100 分。

能力线 60 分：

1. 逻辑结构 15 分：回答是否有开头、展开、总结，是否能按 STAR 或总分总表达。
2. 相关性 10 分：是否回答了问题，是否贴合岗位或场景。
3. 具体性 15 分：是否有案例、数据、结果、个人贡献。
4. 专业深度 10 分：是否体现专业知识、方法论或行业理解。
5. 表达清晰度 10 分：句子是否清楚，重点是否突出。

心理线 40 分：

1. 抗压能力 10 分：被追问或质疑时是否能稳定回应。
2. 信心 10 分：表达是否坚定，是否频繁自我否定。
3. 应变能力 10 分：是否能根据问题变化调整回答。
4. 情绪稳定 10 分：语速、停顿、口头禅和情绪词是否可控。

心理线前置规则：

1. 如果任意回答的 `transcriptSource` 为 `manual`，说明该轮没有使用语音回答，心理线不具备评分基础。
2. 此时 `psychology.total = 0`，四个心理分项 `score = 0`，但能力线仍按文本正常评分。
3. 报告必须在心理线证据、风险和行动计划中明确标注“存在非语音/手动输入回答，心理线置 0”。
4. `browser_stt` 属于语音回答来源；缺少 `speechMetrics` 时只能标注语音指标不足，不能直接把心理线置 0。

报告必须输出：

1. 总分和等级。
2. 能力线分项分与证据。
3. 心理线分项分与证据。
4. 至少 2 条优势。
5. 至少 2 条风险。
6. 至少 3 条可执行练习计划。
7. 逐题反馈。

等级建议：

```text
90-100 优秀：表达成熟，可进入高强度模拟
80-89 良好：框架基本稳定，需要加强亮点
70-79 可用：能完成回答，但结构和细节不足
60-69 待提升：回答偏泛，需要先训练基础表达
0-59 风险较高：建议从自我介绍和 STAR 表达开始
```

## 10. 种子场景

`services/api/app/data/seed_scenarios.json` 至少包含：

```json
[
  {
    "id": "campus_general",
    "name": "通用校招面试",
    "description": "适合应届生综合素质训练，覆盖自我介绍、项目经历、职业动机和压力追问。",
    "category": "campus",
    "defaultQuestionCount": 4,
    "difficulty": "medium",
    "rubricId": "default_v1",
    "openingPrompt": "请先做一个 1 分钟自我介绍。"
  },
  {
    "id": "civil_service_structured",
    "name": "公考结构化面试",
    "description": "训练综合分析、组织协调、应急应变和人际沟通。",
    "category": "civil_service",
    "defaultQuestionCount": 3,
    "difficulty": "medium",
    "rubricId": "civil_service_v1",
    "openingPrompt": "请谈谈你对青年就业压力的看法。"
  },
  {
    "id": "technical_intern",
    "name": "技术岗实习面试",
    "description": "适合技术实习岗位，关注项目深度、基础知识和问题拆解能力。",
    "category": "technical",
    "defaultQuestionCount": 4,
    "difficulty": "medium",
    "rubricId": "technical_v1",
    "openingPrompt": "请介绍一个你最熟悉的技术项目。"
  },
  {
    "id": "postgraduate_reexam",
    "name": "研究生复试",
    "description": "训练学术动机、专业基础、科研潜力和英文问答。",
    "category": "postgraduate",
    "defaultQuestionCount": 4,
    "difficulty": "medium",
    "rubricId": "postgraduate_v1",
    "openingPrompt": "请介绍你的本科背景和报考本专业的原因。"
  }
]
```

## 11. 开发里程碑

### Milestone 0：契约和脚手架

目标：

1. 建立上述目录。
2. 前后端能启动。
3. `/api/health` 可访问。
4. `GET /api/scenarios` 返回种子数据。
5. 前端能显示场景列表。

验收：

1. `apps/web` 本地启动不报错。
2. `services/api` 本地启动不报错。
3. 前端页面能连接后端。

### Milestone 1：面试流程 MVP

目标：

1. 创建面试会话。
2. 显示 AI 问题。
3. 用户文本提交回答。
4. 后端返回下一题。
5. 达到题数后可结束。

验收：

1. 使用 mock provider 可以完成 3 轮问答。
2. 刷新页面前，前端 timeline 状态正确。
3. API 返回错误时页面有错误提示。

### Milestone 2：语音输入输出

目标：

1. 浏览器语音识别写入回答框。
2. 浏览器语音合成播报问题。
3. 不支持 Web Speech API 时自动降级文本模式。
4. 录音时显示麦克风音量反馈。
5. 停止录音后自动进入 transcript 编辑状态。

验收：

1. Chrome 或 Edge 中可录音转写。
2. 问题可播放、停止、重播。
3. 用户提交回答时不会继续播报旧问题。
4. 用户能看到音量变化，知道系统正在收音。
5. 识别不完整时，用户可以直接编辑回答框再提交。

### Milestone 3：评价报告

目标：

1. 后端生成 `EvaluationReport`。
2. 前端展示总分、能力线、心理线、逐题反馈、行动计划。
3. mock provider 能产出符合 schema 的报告；真实 LLM provider 在 Agent F 阶段接入。

验收：

1. 报告结构稳定。
2. 没有空白分项。
3. 至少 3 条行动建议。

### Milestone 4：扩展接口留桩

目标：

1. 在第 13 章文档化后续多模态、服务端语音、复盘时间线等扩展入口。
2. 确认扩展设计不要求 MVP 创建空文件。
3. 真正实现行为编排、服务端语音、视频识别时，再新增对应模块。

验收：

1. 文档留桩不影响 MVP 目录精简。
2. 后续 agent 能按第 13 章新增真实 ASR/TTS、视频识别或复盘能力。

## 12. Subagent 任务包

后续可以按以下任务交给不同 subagent。每个 subagent 必须先读本文档，再读自己负责目录。

任务切分采用混合策略：

1. 先由契约 agent 固定公共模型、OpenAPI 生成链路和项目脚手架。
2. 业务功能尽量按垂直闭环切分，让每个 agent 能独立跑通一个用户路径。
3. LLM provider、评分 rubric、面试房间状态机这类共享能力必须有明确 owner，避免多个 agent 各写一套。
4. 任何 feature agent 如果需要改公共 schema，必须先更新 Pydantic、重新生成 OpenAPI/TS 类型，并在交付说明中标出破坏性影响。

### Agent A：契约与脚手架守门

负责目录：

1. `services/api/app/schemas`
2. `services/api/app/main.py`
3. `services/api/app/api/router.py`
4. `apps/web/src/types/generated`
5. `scripts`

交付：

1. FastAPI 基础应用和 `/api/health`。
2. Pydantic schema，覆盖 Scenario、Session、Turn、Answer、EvaluationReport、Error。
3. OpenAPI 生成脚本。
4. 前端 TS 类型生成脚本和生成产物。

注意：

1. Pydantic 是契约唯一数据源，不手写第二套 TS DTO。
2. 不实现复杂业务逻辑。
3. 不引入未讨论的新评分维度。
4. 后续 agent 合并前必须以 Agent A 的 schema 为准。

### Agent B：场景选择与会话创建闭环

负责目录：

1. `services/api/app/api/routes/scenarios.py`
2. `services/api/app/api/routes/interviews.py`
3. `services/api/app/repositories/scenario_repository.py`
4. `services/api/app/repositories/session_repository.py`
5. `services/api/app/data/seed_scenarios.json`
6. `apps/web/src/pages/InterviewSetupPage.tsx`
7. `apps/web/src/services/scenarioApi.ts`
8. `apps/web/src/services/interviewApi.ts`

交付：

1. `GET /api/scenarios`。
2. `POST /api/interviews/sessions`。
3. 场景选择页。
4. 创建会话后进入面试房间。
5. 对应后端测试和前端基本渲染测试。

注意：

1. 这个 agent 不负责完整问答流，只保证用户能选场景并拿到第一题。
2. 创建会话必须使用 mock provider 生成首题，不能依赖真实 LLM Key。

### Agent C：面试问答核心闭环

负责目录：

1. `services/api/app/services/interview_orchestrator.py`
2. `services/api/app/services/question_agent.py`
3. `services/api/app/api/routes/interviews.py`
4. `services/api/app/repositories/session_repository.py`
5. `apps/web/src/pages/InterviewRoomPage.tsx`
6. `apps/web/src/hooks/useInterviewSession.ts`
7. `apps/web/src/hooks/useInterviewRoomState.ts`

交付：

1. `POST /api/interviews/sessions/{sessionId}/answers`。
2. `POST /api/interviews/sessions/{sessionId}/finish` 的基础流程。
3. 面试房间有限状态机。
4. 文本回答、下一题、追问、结束入口。
5. 使用 mock provider 完成 3 轮问答的集成测试。

注意：

1. `interview_orchestrator.py` 是业务状态判断中心。
2. 面试房间 UI 必须用状态机控制可操作按钮。
3. 提交中不能录音、重播或二次提交。

### Agent D：语音输入输出闭环

负责目录：

1. `apps/web/src/hooks/useSpeechRecognition.ts`
2. `apps/web/src/hooks/useSpeechSynthesis.ts`
3. `apps/web/src/components/interview/VoiceRecorderButton.tsx`
4. `apps/web/src/components/interview/SpeechPlaybackButton.tsx`
5. `apps/web/src/components/interview/VolumeMeter.tsx`

交付：

1. 浏览器语音转文字。
2. 问题语音播报。
3. 麦克风音量可视化。
4. 不支持语音 API 时降级文本模式。
5. 停止录音后自动聚焦回答框，允许用户编辑 transcript。

注意：

1. 不能阻塞文本输入。
2. 录音状态和音量反馈必须明显。
3. Web Speech API 和 MediaStream API 在测试中都需要 mock。

### Agent E：评价系统闭环

负责目录：

1. `services/api/app/services/evaluation_service.py`
2. `services/api/app/domain/scoring.py`
3. `services/api/app/api/routes/evaluations.py`
4. `services/api/app/repositories/evaluation_repository.py`
5. `services/api/app/dependencies.py`
6. `apps/web/src/pages/EvaluationReportPage.tsx`
7. `apps/web/src/components/evaluation`
8. `apps/web/src/hooks/useEvaluationReport.ts`
9. `apps/web/src/services/evaluationApi.ts`
10. `services/api/app/tests/test_evaluation_service.py`

交付：

1. `GET /api/evaluations/reports/{reportId}`。
2. 能力线和心理线评分。
3. 逐题反馈。
4. 行动计划。
5. 评价报告页。
6. mock 评价路径和真实 provider 接入点。
7. interview 和 evaluation 共享同一个 `SessionRepository`，确保完成会话后能读取 turns 生成报告。

注意：

1. 不要让 LLM 一次性生成完整大报告。
2. 能力线、心理线、逐题反馈、行动计划分步生成，后端组装 `EvaluationReport`。
3. 报告必须引用证据。
4. 分数必须由后端校验并落在合法范围。
5. 前端不要只展示分数，要展示证据和建议。

### Agent F：LLM Provider 与 Prompt Owner

负责目录：

1. `services/api/app/providers/llm`
2. `services/api/app/services/prompt_builder.py`

交付：

1. `LLMProvider` 协议。
2. `mock_provider.py`。
3. `openai_provider.py` 或其他真实 provider。
4. 严格结构化输出能力检测与 fallback。
5. 问题生成和评价生成 prompt。

注意：

1. 不能把 API Key 写进代码。
2. 所有模型输出必须经过 Pydantic 校验。
3. provider 失败时不能破坏 mock 流程。
4. 修改 prompt 输出结构时必须同步 schema 和测试。

### Agent G：测试与集成

负责目录：

1. `services/api/app/tests`
2. `apps/web/src/**/*.test.tsx`
3. `scripts`

交付：

1. 后端核心流程测试。
2. 评价服务测试。
3. 前端状态机和 hook 测试。
4. Web Speech API、MediaStream API mock。
5. 一键启动脚本。
6. 端到端手动验收清单。

注意：

1. 测试优先覆盖 session flow、room state reducer 和 report schema。
2. 生成类型脚本必须纳入验证。
3. 集成 agent 不重写业务逻辑，只修复联调问题。

## 13. 扩展模块接口

本章只定义后续扩展的接入边界。第一阶段不要在主目录中创建这些文件，除非某个扩展被明确派发给 subagent 实现。

### 13.1 多模态视频分析

未来新增：

```text
services/api/app/services/video_analysis_service.py
services/api/app/services/expression_analysis_service.py
services/api/app/services/posture_analysis_service.py
services/api/app/providers/vision/
apps/web/src/hooks/useCameraCapture.ts
apps/web/src/components/interview/CameraPreview.tsx
```

预期输出：

```ts
type VisualMetrics = {
  eyeContactScore?: number;
  postureScore?: number;
  expressionLabel?: "neutral" | "smiling" | "tense" | "distracted" | "unknown";
  frameSampleUrls?: string[];
};
```

接入点：

1. `CandidateAnswer` 增加 `visualMetrics`。
2. `EvaluationService` 将视觉指标纳入心理线。
3. `BehaviorOrchestrator` 可根据用户状态调整追问语气。

### 13.2 简历解析与岗位匹配

未来新增：

```text
services/api/app/api/routes/resumes.py
services/api/app/api/routes/jobs.py
services/api/app/services/resume_parser.py
services/api/app/services/job_matcher.py
apps/web/src/pages/ResumeUploadPage.tsx
```

核心接口：

```http
POST /api/resumes/parse
POST /api/jobs/match
```

用途：

1. 根据简历生成个性化问题。
2. 根据目标岗位调整评分 rubric。
3. 在复盘中给出简历优化建议。

### 13.3 多智能体并行评估

未来新增：

```text
services/api/app/services/agents/
  base.py
  questioning_agent.py
  ability_evaluator_agent.py
  psychology_evaluator_agent.py
  review_summarizer_agent.py
```

思路：

1. 提问 agent 只负责上下文和追问。
2. 能力评估 agent 只评分专业表达。
3. 表现评估 agent 只评分语音、情绪、抗压。
4. 总结 agent 合并报告，解决冲突。

MVP 的 `EvaluationService` 要保持接口稳定，未来内部替换成多 agent 并行，不影响 API。

### 13.4 高校端和企业端

未来新增：

```text
apps/admin/
services/api/app/api/routes/admin.py
services/api/app/domain/organization.py
```

能力：

1. 学校批量创建训练任务。
2. 班级或学院维度查看训练数据。
3. 企业创建岗位测评。
4. 输出候选人画像和岗位匹配度。

第一阶段不要实现，只在数据库设计中避免把 session 绑定死到单一用户。

### 13.5 会员与商业化

未来新增：

```text
services/api/app/api/routes/billing.py
services/api/app/domain/subscription.py
```

能力：

1. 免费次数限制。
2. 会员训练次数。
3. 简历优化增值服务。
4. 高校和企业 SaaS 订阅。

第一阶段不要实现，只预留 `user_id` 和 `organization_id` 字段。

### 13.6 面试复盘视频时间线

未来新增：

```text
services/api/app/api/routes/review.py
services/api/app/services/review_timeline_service.py
services/api/app/repositories/review_repository.py
services/api/app/domain/review.py
apps/web/src/pages/InterviewReviewPage.tsx
apps/web/src/components/review/VideoReviewTimeline.tsx
apps/web/src/components/review/TimelineMarkerList.tsx
apps/web/src/components/review/ReviewPlaybackControls.tsx
apps/web/src/hooks/useReviewTimeline.ts
apps/web/src/services/reviewApi.ts
```

核心接口：

```http
GET /api/interviews/sessions/{sessionId}/review
GET /api/interviews/sessions/{sessionId}/review/timeline
```

预期输出：

```ts
type ReviewTimeline = {
  sessionId: string;
  videoUrl?: string;
  audioUrl?: string;
  markers: ReviewMarker[];
};

type ReviewMarker = {
  id: string;
  turnId?: string;
  timestampMs: number;
  type: "question" | "answer" | "pause" | "filler_word" | "emotion_shift" | "score_drop" | "highlight";
  title: string;
  description: string;
  severity: "info" | "warning" | "positive";
};
```

用途：

1. 把面试视频、音频、转写文本和评价证据对齐到同一时间轴。
2. 在复盘页定位“停顿过长”“口头禅密集”“回答亮点”“追问失分点”等片段。
3. 为后续视频分析、表情识别和姿态识别提供可回放的证据入口。

第一阶段不要实现真实视频录制和时间线生成，只保留接口、类型和页面入口设计。

### 13.7 服务端语音与实时事件

未来新增：

```text
services/api/app/api/routes/speech.py
services/api/app/services/speech_service.py
services/api/app/schemas/speech.py
services/api/app/providers/speech/
  base.py
  server_asr_provider.py
  server_tts_provider.py
```

核心接口：

```http
POST /api/speech/transcriptions
POST /api/speech/synthesis
WS /api/ws/interviews/sessions/{sessionId}/events
```

预留事件：

```ts
type InterviewEvent =
  | { type: "partial_transcript"; text: string; isFinal: boolean }
  | { type: "assistant_speaking"; text: string; audioUrl?: string }
  | { type: "behavior_intent"; intent: string; payload: Record<string, unknown> }
  | { type: "evaluation_delta"; payload: Partial<EvaluationReport> };
```

第一阶段使用浏览器语音能力，不创建这些服务端文件。

## 14. UI 设计原则

面试训练平台应当像一个稳定、可信、低干扰的工作工具。

原则：

1. 第一屏直接进入练习，不做大篇幅营销页。
2. 视觉风格安静、清晰、专业，避免过度装饰。
3. 面试房间页重点是问题、回答输入、录音状态和进度。
4. 不用大段说明文字教用户如何操作，交互本身要清楚。
5. 录音、播放、停止、提交要有明确按钮状态。
6. 评价报告要可扫描，分数、证据、建议分层展示。
7. 移动端可用，但 MVP 主要保证桌面浏览器体验。

建议页面布局：

```text
InterviewRoomPage
  Top: 场景名 / 进度 / 结束按钮
  Main Left: 当前问题 + 播放控制 + 回答输入
  Main Right: 历史对话 timeline + 阶段反馈
  Bottom: 录音按钮 / 提交按钮 / 状态提示
```

## 15. 错误处理

统一错误结构：

```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "面试会话不存在",
    "details": {}
  }
}
```

常见错误码：

```text
SCENARIO_NOT_FOUND
SESSION_NOT_FOUND
TURN_NOT_FOUND
INVALID_SESSION_STATE
EMPTY_ANSWER
LLM_PROVIDER_ERROR
EVALUATION_FAILED
SPEECH_NOT_SUPPORTED
RATE_LIMITED
INTERNAL_ERROR
```

前端要求：

1. 用户回答为空时不提交。
2. 后端失败时保留用户回答草稿。
3. LLM 失败时提示稍后重试，不能清空 timeline。
4. 语音不支持时自动降级到手动输入。

## 16. 数据持久化建议

当前 MVP 使用内存 Repository，方便多个 subagent 在没有数据库迁移的情况下快速联调。下一阶段如果接入 SQLite，可以按以下表结构落地：

```text
scenarios
  id
  name
  description
  category
  default_question_count
  difficulty
  rubric_id
  opening_prompt

interview_sessions
  id
  scenario_id
  status
  mode
  language
  question_count_target
  current_turn_index
  candidate_profile_json
  user_id nullable
  organization_id nullable
  created_at
  completed_at nullable

interview_turns
  id
  session_id
  turn_index
  question_id
  question_text
  question_type
  question_intent
  expected_signals_json
  answer_text nullable
  transcript_source nullable
  answer_duration_ms nullable
  speech_metrics_json nullable
  question_extra_json nullable
  answer_extra_json nullable
  created_at
  answered_at nullable

evaluation_reports
  id
  session_id
  report_json
  overall_score
  created_at
```

MVP 不要求复杂关系建模，优先保证流程稳定。高频查询、评分和排错会用到的字段先展开成列，例如 `question_text`、`answer_text`、`answer_duration_ms`、`transcript_source`。语速、停顿、口头禅、情绪等语音指标先统一放入 `speech_metrics_json`，避免同一数据双写；等后续确实需要统计查询时再拆列。

字段展开原则：

1. 会出现在列表、筛选、评分规则或测试断言里的字段，优先独立成列。
2. 供应商相关、未来多模态相关、结构不稳定的字段，优先放 JSON。
3. Repository 对外仍返回领域模型，不让 API route 直接感知数据库字段拆分。

## 17. 本地运行建议

后端：

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd apps/web
npm install
npm run dev
```

生成前端契约类型：

```powershell
.\scripts\generate-api-types.ps1
```

该脚本会先从 `services/api/app/export_openapi.py` 导出 `services/api/openapi.json`，再生成 `apps/web/src/types/generated/api.ts`，不需要先启动后端服务。

环境变量：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

后端 `.env`：

```text
APP_ENV=local
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./simhire.db
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=
```

## 18. 测试策略

后端测试：

1. `test_contracts.py`：核心 schema、OpenAPI paths、camelCase 序列化。
2. `test_agent_b_flow.py`：场景列表和创建会话。
3. `test_agent_c_flow.py`：提交回答、追问、达到题数、结束会话和错误状态。
4. `test_evaluation_service.py`：完成后生成报告、缓存幂等、未完成 409、缺失报告 404、评分项证据。
5. 后续 Agent G 可补 `test_llm_provider.py` 和前端测试；当前 MVP 尚未接入真实 LLM provider。

前端测试：

当前前端只有 `npm run build` 类型和构建验证，还没有自动化测试。Agent G 补测试时优先覆盖：

1. `useInterviewSession` 可以处理 start、submit、finish。
2. `useInterviewRoomState` 覆盖合法状态流和非法操作拦截。
3. `useSpeechRecognition` 在不支持 API 时正确降级。
4. `VolumeMeter` 能根据 `volumeLevel` 渲染录音反馈。
5. `InterviewRoomPage` 在 loading、error、normal、recording、submitting 状态都能渲染。
6. `EvaluationReportPage` 对空字段有兜底展示。
7. OpenAPI 生成的前端类型不允许手工修改，生成脚本要在验证流程中跑通。

当前整体回归命令：

```powershell
.\scripts\generate-api-types.ps1
cd services/api
python -m pytest -q
cd ..\..\apps\web
npm run build
```

手动验收脚本：

1. 启动后端和前端。
2. 打开前端。
3. 选择“通用校招面试”。
4. 开始面试。
5. 播放第一题。
6. 用语音回答，也可以手动编辑文本。
7. 提交 3 到 4 轮。
8. 结束面试。
9. 查看评价报告。

## 19. 开发约束

为了让多个 subagent 能稳定协作，必须遵守以下约束：

1. 任何 agent 不得随意修改公共类型字段名。
2. 任何 agent 不得删除 mock provider。
3. 前端不能直接调用模型 API。
4. 后端不能把供应商 SDK 调用散落在业务服务里。
5. 评价报告必须符合 `EvaluationReport` schema。
6. MVP 中视频、数字人、支付、组织管理都只留接口，不抢先实现。
7. 新增依赖要写清原因，并优先选择成熟、轻量、维护活跃的库。
8. 出现 schema 冲突时，以 `services/api/app/schemas` 的 Pydantic 模型为准，再重新生成 OpenAPI 和前端类型。
9. `apps/web/src/types/generated` 是生成产物，不能手工改字段。
10. 面试房间状态机、评分维度和错误码属于公共契约，改动必须同步测试。

## 20. 第一阶段 MVP 收尾状态

第一阶段到当前节点可以结束。已完成内容：

1. 契约和脚手架：FastAPI、Pydantic schema、统一错误结构、OpenAPI 导出和前端类型生成。
2. 场景和会话：`GET /api/scenarios`、`POST /api/interviews/sessions`、场景选择页和会话创建。
3. 面试问答：文本回答、浏览器语音转写、问题播报、追问、下一题、达到题数后结束。
4. 评价报告：`GET /api/evaluations/reports/{reportId}`、能力线、心理线、逐题反馈、风险、优势和行动计划。
5. 评分收尾规则：只要存在手动输入回答，心理线置 0 并在报告中标注；全语音转写但缺少语音细指标时，只做保守估计。
6. 文档同步：当前目录结构、回归命令、已完成范围和后续边界已经同步到本文档。

当前 MVP 仍然不是最终产品，它有几个明确限制：

1. 后端仍使用内存 Repository，刷新服务会丢失会话和报告。
2. 题目生成和评分是确定性 mock，没有真实 LLM provider。
3. 浏览器语音能力是回合式的：播报一题、录音回答、提交，再进入下一题。
4. 没有实时双向语音、流式 ASR、面试官即时打断、沉默追问和行为编排。
5. 前端还没有自动化测试；当前主要依靠后端 pytest、前端 build 和手动浏览器验收。

第一阶段最终回归命令：

```powershell
.\scripts\generate-api-types.ps1
cd services/api
python -m pytest -q
cd ..\..\apps\web
npm run build
```

第一阶段手动验收路径：

1. 打开前端。
2. 选择面试场景和题数。
3. 开始面试。
4. 使用语音回答或手动输入回答。
5. 提交到达到题数。
6. 结束面试。
7. 查看评价报告。
8. 如果使用过手动输入，确认心理线为 0 且报告有原因标注。

## 21. 第二阶段目标：即时性语音聊天

第二阶段目标是把当前“回合式语音问答”升级为“更像真实面试的即时语音聊天”。它不是简单地增加一个按钮，而是引入事件流、实时状态、行为策略和可打断的面试官。

### 21.1 产品目标

第二阶段先实现三个高价值即时场景：

1. 沉默追问：面试者长时间不作答时，面试官主动询问原因，例如“你可以先讲思路，也可以告诉我需要我复述问题吗？”
2. 兴趣打断：面试者提到高价值线索时，面试官可以适度打断或插入追问，例如“你刚才提到 20% 提升，这里我想追问一下你具体做了什么。”
3. 连续语音节奏：用户不再强依赖“录音、停止、提交”三步，而是在一个实时房间内说话、停顿、被追问、继续回答。

第二阶段不立刻做：

1. 数字人视频。
2. 摄像头表情识别。
3. 企业端、高校端、支付和会员。
4. 完整服务端音频存储和大规模检索。

### 21.2 技术路线

推荐采用“事件驱动 + 分阶段实时化”的路线。

阶段 2A 先做浏览器 STT 事件流：

1. 前端继续使用浏览器 `SpeechRecognition` 获取实时 transcript。
2. 前端用 Web Audio API 做音量、静音、说话开始和说话结束检测。
3. 前端通过 WebSocket 把 transcript 增量、静音事件、音量摘要和用户状态发送给后端。
4. 后端不接收原始音频，只接收结构化实时事件。
5. 后端根据事件策略返回面试官事件，例如 `interviewer_probe`、`interviewer_interrupt`、`interviewer_wait`。

阶段 2B 再接入服务端 ASR/TTS 或 Realtime LLM：

1. 服务端可以接收音频片段或流式音频。
2. ASR、LLM、TTS provider 都放入 adapter 层。
3. 仍保持同一套实时事件协议，避免前端和业务逻辑被供应商绑定。

### 21.3 新增后端结构建议

```text
services/api/app/
  api/routes/
    realtime.py
  schemas/
    realtime.py
  services/
    realtime_interview_service.py
    intervention_policy.py
    realtime_event_bus.py
  providers/
    realtime/
      base.py
      mock_provider.py
      openai_realtime_provider.py
  tests/
    test_realtime_contracts.py
    test_intervention_policy.py
    test_realtime_flow.py
```

说明：

1. `realtime.py` 只负责 WebSocket 连接、鉴权占位、收发事件和错误封装。
2. `schemas/realtime.py` 定义实时事件契约，仍然由 Pydantic 作为唯一源头。
3. `realtime_interview_service.py` 管理实时会话、当前问题、用户发言片段和面试官事件。
4. `intervention_policy.py` 负责沉默追问、兴趣打断、追问冷却、打断频率上限。
5. `realtime_event_bus.py` 在第二阶段可以是内存队列，后续可替换 Redis pub/sub。
6. `providers/realtime` 第二阶段先放 mock provider；真实 provider 在 2B 接入。

### 21.4 新增前端结构建议

```text
apps/web/src/
  pages/
    RealtimeInterviewRoomPage.tsx
  hooks/
    useRealtimeInterview.ts
    useRealtimeSpeechRecognition.ts
    useVoiceActivity.ts
    useRealtimePlayback.ts
  services/
    realtimeApi.ts
  components/realtime/
    RealtimeTranscript.tsx
    LiveVoiceMeter.tsx
    InterviewerIntervention.tsx
    RealtimeControls.tsx
    ConversationEventTimeline.tsx
```

说明：

1. `RealtimeInterviewRoomPage.tsx` 是第二阶段新房间，不要直接把现有 `InterviewRoomPage` 改成复杂大组件。
2. `useRealtimeInterview.ts` 管 WebSocket 连接、事件收发、重连和会话状态。
3. `useRealtimeSpeechRecognition.ts` 管浏览器 STT 增量 transcript。
4. `useVoiceActivity.ts` 管音量、静音计时、是否正在说话。
5. `InterviewerIntervention.tsx` 展示面试官即时追问、打断和等待提示。
6. 现有回合式房间保留，作为稳定 fallback。

### 21.5 实时事件契约草案

```ts
type RealtimeClientEvent =
  | {
      type: "candidate_speech_started";
      sessionId: string;
      at: string;
    }
  | {
      type: "candidate_transcript_delta";
      sessionId: string;
      text: string;
      isFinal: boolean;
      at: string;
    }
  | {
      type: "candidate_silence";
      sessionId: string;
      silenceMs: number;
      at: string;
    }
  | {
      type: "candidate_speech_ended";
      sessionId: string;
      finalText: string;
      durationMs: number;
      at: string;
    };

type RealtimeServerEvent =
  | {
      type: "interviewer_wait";
      message: string;
      at: string;
    }
  | {
      type: "interviewer_probe";
      message: string;
      reason: "silence" | "unclear_answer" | "missing_evidence";
      at: string;
    }
  | {
      type: "interviewer_interrupt";
      message: string;
      reason: "interesting_signal" | "need_clarification";
      at: string;
    }
  | {
      type: "turn_committed";
      turnId: string;
      answerText: string;
      at: string;
    }
  | {
      type: "error";
      message: string;
      retryable: boolean;
      at: string;
    };
```

后续实现时，以上类型要转为 Pydantic schema，再由 OpenAPI 或专门生成脚本同步到前端。

### 21.6 干预策略规则

沉默追问：

1. 当前题播报结束后开始计时。
2. `candidate_speech_started` 前静默超过 8 秒，发出一次温和提醒。
3. 已经提醒后再静默 12 秒，发出更具体的帮助提示。
4. 每题最多触发 2 次沉默追问。

兴趣打断：

1. transcript delta 中出现数字、结果、职责、项目名、专业关键词时，进入候选打断状态。
2. 同一轮回答中至少等待用户连续说满 6 秒，避免过早打断。
3. 每轮最多打断 1 次。
4. 打断内容必须围绕证据、边界、个人贡献或结果验证，不能泛泛评价。

节奏保护：

1. 面试官打断后要暂停候选人 transcript 提交 1 到 2 秒，避免事件重入。
2. 面试官正在 TTS 播放时，不触发新的打断。
3. 用户点击“继续说”或开始说话时，面试官等待状态结束。

### 21.7 第二阶段 subagent 拆分建议

Agent R0：实时契约和状态设计

负责：

1. `services/api/app/schemas/realtime.py`
2. `apps/web/src/services/realtimeApi.ts`
3. 实时房间状态机文档和类型。

交付：

1. Client/Server realtime event schema。
2. WebSocket 错误结构。
3. 前端事件类型生成或手动桥接策略。
4. 后端契约测试。

Agent R1：后端 WebSocket 与实时服务

负责：

1. `services/api/app/api/routes/realtime.py`
2. `services/api/app/services/realtime_interview_service.py`
3. `services/api/app/services/realtime_event_bus.py`

交付：

1. WebSocket `/api/realtime/interviews/{sessionId}`。
2. 接收 transcript/silence/speech events。
3. 返回 mock interviewer events。
4. 与现有 `SessionRepository` 共享会话。

Agent R2：干预策略

负责：

1. `services/api/app/services/intervention_policy.py`
2. `services/api/app/tests/test_intervention_policy.py`

交付：

1. 沉默追问策略。
2. 兴趣打断策略。
3. 冷却、频率上限和状态保护。
4. 确定性测试。

Agent R3：前端实时房间

负责：

1. `apps/web/src/pages/RealtimeInterviewRoomPage.tsx`
2. `apps/web/src/hooks/useRealtimeInterview.ts`
3. `apps/web/src/hooks/useRealtimeSpeechRecognition.ts`
4. `apps/web/src/hooks/useVoiceActivity.ts`
5. `apps/web/src/components/realtime/*`

交付：

1. 实时 transcript 展示。
2. 音量和静音计时。
3. 面试官即时提示和打断展示。
4. 可回退到现有回合式房间。

Agent R4：集成验证

负责：

1. 后端 realtime flow 测试。
2. 前端 hook/状态机测试。
3. 手动验收脚本。
4. 浏览器权限和降级路径说明。

交付：

1. 无浏览器语音 API 时仍可使用回合式文本面试。
2. WebSocket 断开时有重连或明确错误提示。
3. 端到端模拟：题目播报、静默追问、兴趣打断、继续回答、结束报告。

### 21.8 下一阶段验收标准

1. 用户进入实时面试房间后，可以连续说话并看到实时 transcript。
2. 用户在题目后静默超过阈值，面试官会主动询问缘由或提供帮助。
3. 用户提到数字化结果或重要经历时，面试官可以产生一次相关追问/打断。
4. 干预事件不会无限触发，必须有冷却和每题次数上限。
5. 实时房间可以正常结束并复用第一阶段评价报告链路。
6. 不支持实时能力时，用户可以回退到第一阶段的稳定回合式面试。

## 22. 暂不进入第二阶段范围的能力

以下功能继续延后：

1. 数字人视频生成。
2. 摄像头表情识别。
3. 企业 ATS 集成。
4. 支付和会员。
5. 复杂权限系统。
6. 自动简历美化。
7. 大规模数据看板。

这些能力仍然依赖稳定的实时语音、会话、评价和持久化基础。

## 23. 给下一个阶段 agent 的通用提示词

可以把下面这段放在下一阶段每个 subagent 任务开头：

```text
你正在实现 SimHire AI 面试模拟平台第二阶段：即时性语音聊天。请先阅读 docs/AI_INTERVIEW_PLATFORM_DEV_DOC.md，尤其是第 20 和第 21 章。第一阶段 MVP 已经完成，现有回合式面试、语音输入输出和评价报告链路必须保持可用；任何实时能力都要能回退到现有稳定流程。后端 Pydantic schema 仍是契约唯一数据源，前端类型必须从契约生成或由明确的实时事件类型同步，不要手工改 generated 类型。你只负责当前任务指定范围，不要引入数字人、摄像头、支付、组织管理等非本阶段能力。完成后请说明改动文件、运行方式、验证结果和已知限制。
```

## 24. 当前文档结论

第一阶段 MVP 已经完成，可以作为下一阶段的稳定底座。它证明了：

1. 用户可以从场景选择进入面试。
2. 用户可以用文本或浏览器语音完成回答。
3. 后端能稳定处理问题、回答、追问、结束和报告。
4. 评价系统能输出能力线和心理线，并按语音来源处理心理线评分。
5. 后续即时性能力有明确接口、状态和任务拆分方向。

下一阶段的核心不是继续堆页面，而是把“等待用户提交”的回合式体验升级为“能听、能等、能追问、能适度打断”的实时面试体验。
