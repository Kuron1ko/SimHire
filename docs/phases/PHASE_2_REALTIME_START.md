# Phase 2 Realtime 起始文档

本文档是 SimHire 第二阶段“即时性互动”的起始文档。所有负责 Phase 2 的 agent 和 subagent 应先阅读 `docs/AI_INTERVIEW_PLATFORM_DEV_DOC.md`，再阅读本文档。

## 1. 阶段目标

Phase 2 的目标是把 Phase 1 的回合式“一问一答”升级为更像语音聊天的面试互动。

用户体验目标：

1. 用户进入实时面试房间后，可以连续说话，而不是每次都依赖“录音、停止、提交”。
2. 面试官能感知沉默，并主动询问原因、复述问题或给出轻提示。
3. 面试官能识别答非所问、明显乱答或不认真回答，并提醒用户认真作答。
4. 面试官能在用户提到高价值线索时追问，必要时适度打断。
5. 实时能力失败时，仍能回退到 Phase 1 回合式面试。

本阶段先追求“行为上像真人”，不追求“完全真人”。

## 2. 可行性判断

即时性在当前技术条件下可以实现，但应分层实现。

可稳定推进的能力：

1. 浏览器麦克风输入。
2. 浏览器语音识别增量 transcript。
3. Web Audio API 音量与静音检测。
4. WebSocket 实时事件传输。
5. 后端基于事件流触发沉默追问、认真度提醒和兴趣追问。
6. 前端 TTS 播放可被中断或排队。

不应在本阶段承诺的能力：

1. 完全自然的双向抢话。
2. 全场景稳定情绪识别。
3. 完美情绪化语音。
4. 数字人视频、口型和表情同步。

## 3. 当前依赖基线

Phase 2 基于 Phase 1 已完成能力：

1. `GET /api/scenarios`
2. `POST /api/interviews/sessions`
3. `POST /api/interviews/sessions/{sessionId}/answers`
4. `POST /api/interviews/sessions/{sessionId}/finish`
5. `GET /api/evaluations/reports/{reportId}`
6. 前端 `InterviewSetupPage.tsx`
7. 前端 `InterviewRoomPage.tsx`
8. 前端 `EvaluationReportPage.tsx`
9. 浏览器 STT/TTS hooks
10. 确定性 mock 题目与评分

Phase 2 不应破坏以上能力。

## 4. 推荐技术路线

采用“事件驱动 + 分阶段实时化”。

### 2A：浏览器事件流

先不让后端接收原始音频。前端负责语音识别和语音活动检测，然后把结构化事件发给后端。

前端事件来源：

1. `SpeechRecognition` transcript delta。
2. Web Audio API 音量。
3. 静音时长。
4. 说话开始。
5. 说话结束。
6. 当前 TTS 播放状态。

后端根据事件返回面试官事件：

1. 等待。
2. 沉默追问。
3. 认真度提醒。
4. 兴趣追问。
5. 适度打断。
6. 提交当前回答片段为正式 turn。

### 2B：服务端实时 provider

在 2A 稳定后，再接入服务端 ASR/TTS 或 Realtime LLM。

要求：

1. provider 放入 adapter 层。
2. 不把供应商 SDK 调用散落到业务服务。
3. 保持 Phase 2 事件契约稳定。
4. 没有真实 key 时，mock provider 仍可跑通。

## 5. 后端新增结构建议

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

职责说明：

1. `api/routes/realtime.py`：WebSocket 连接、收发事件、错误封装、鉴权占位。
2. `schemas/realtime.py`：实时事件 Pydantic schema。
3. `realtime_interview_service.py`：实时会话状态、当前问题、回答片段和 turn commit。
4. `intervention_policy.py`：沉默追问、乱答提醒、兴趣打断、冷却和频率上限。
5. `realtime_event_bus.py`：阶段内可先用内存队列，后续可替换 Redis pub/sub。
6. `providers/realtime/*`：为后续 Realtime LLM 或服务端 ASR/TTS 预留 adapter。

## 6. 前端新增结构建议

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

职责说明：

1. `RealtimeInterviewRoomPage.tsx`：新的实时房间页面，不把旧 `InterviewRoomPage` 改成复杂大组件。
2. `useRealtimeInterview.ts`：WebSocket 连接、事件收发、重连、错误状态和会话状态。
3. `useRealtimeSpeechRecognition.ts`：浏览器 STT 增量 transcript。
4. `useVoiceActivity.ts`：音量、静音计时、说话开始和说话结束检测。
5. `useRealtimePlayback.ts`：面试官 TTS 队列、播放中断和播放状态。
6. `components/realtime/*`：实时 transcript、音量、干预提示、控制按钮和事件时间线。

## 7. 实时事件契约草案

后端 Pydantic schema 应是最终契约源头。下面是概念草案，实际实现时应转为后端 schema，并同步前端类型。

客户端事件：

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
    }
  | {
      type: "candidate_attention_warning";
      sessionId: string;
      reason: "off_topic" | "nonsense" | "too_short";
      evidenceText?: string;
      at: string;
    };
```

服务端事件：

```ts
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
      type: "interviewer_attention_reminder";
      message: string;
      reason: "off_topic" | "nonsense" | "too_short";
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

## 8. 干预策略规则

### 沉默追问

1. 当前题播报结束后开始计时。
2. `candidate_speech_started` 前静默超过 8 秒，触发一次温和提醒。
3. 已提醒后再静默 12 秒，触发一次更具体的帮助提示。
4. 每题最多触发 2 次沉默追问。

### 认真度提醒

1. 回答过短、明显重复、答非所问或包含无意义内容时，可触发提醒。
2. 提醒语气应保持面试官专业感，不羞辱用户。
3. 每题最多触发 1 次认真度提醒。
4. 提醒后应允许用户继续回答，而不是直接结束题目。

### 兴趣追问与打断

1. transcript 中出现数字结果、项目名、职责、关键技术、业务指标、个人贡献等信号时，进入候选追问状态。
2. 用户至少连续说满 6 秒后，才允许兴趣打断，避免过早抢话。
3. 每轮最多打断 1 次。
4. 打断必须围绕证据、边界、个人贡献或结果验证。

### 节奏保护

1. 面试官 TTS 播放中，不触发新的打断。
2. 面试官刚打断后，应有 1 到 2 秒冷却。
3. 用户恢复说话时，等待态结束。
4. 任何干预事件都必须有频率上限，避免循环触发。

## 9. Subagent 拆分建议

### Agent R0：实时契约和状态设计

负责：

1. `services/api/app/schemas/realtime.py`
2. `apps/web/src/services/realtimeApi.ts`
3. 实时房间状态机文档或类型。

交付：

1. Client/Server realtime event schema。
2. WebSocket 错误结构。
3. 前端事件类型同步策略。
4. 后端契约测试。

### Agent R1：后端 WebSocket 与实时服务

负责：

1. `services/api/app/api/routes/realtime.py`
2. `services/api/app/services/realtime_interview_service.py`
3. `services/api/app/services/realtime_event_bus.py`

交付：

1. WebSocket `/api/realtime/interviews/{sessionId}`。
2. 接收 transcript、silence、speech events。
3. 返回 mock interviewer events。
4. 与现有 `SessionRepository` 共享会话。

### Agent R2：干预策略

负责：

1. `services/api/app/services/intervention_policy.py`
2. `services/api/app/tests/test_intervention_policy.py`

交付：

1. 沉默追问策略。
2. 认真度提醒策略。
3. 兴趣追问和适度打断策略。
4. 冷却、频率上限和确定性测试。

### Agent R3：前端实时房间

负责：

1. `apps/web/src/pages/RealtimeInterviewRoomPage.tsx`
2. `apps/web/src/hooks/useRealtimeInterview.ts`
3. `apps/web/src/hooks/useRealtimeSpeechRecognition.ts`
4. `apps/web/src/hooks/useVoiceActivity.ts`
5. `apps/web/src/hooks/useRealtimePlayback.ts`
6. `apps/web/src/components/realtime/*`

交付：

1. 实时 transcript 展示。
2. 音量和静音计时。
3. 面试官即时提示、追问和打断展示。
4. 回退到现有回合式房间的入口。

### Agent R4：集成验证与文档同步

负责：

1. 后端 realtime flow 测试。
2. 前端 hook 或状态机测试。
3. 手动验收脚本。
4. 浏览器权限和降级路径说明。
5. 为 Phase 3 更新起始文档。

交付：

1. 端到端模拟：题目播报、静默追问、乱答提醒、兴趣打断、继续回答、结束报告。
2. WebSocket 断开时有重连或明确错误提示。
3. 无浏览器语音 API 时仍可使用 Phase 1 回合式文本面试。
4. `docs/phases/PHASE_3_INTENT_VOICE_START.md` 根据真实 Phase 2 结果更新。

## 10. 验收标准

Phase 2 完成时必须满足：

1. 用户可以进入实时面试房间。
2. 用户连续说话时能看到实时 transcript 或接近实时的 transcript 更新。
3. 用户在题目后静默超过阈值，面试官会主动提示。
4. 用户明显乱答或答非所问时，面试官能提醒认真作答。
5. 用户提到重要经历、数字结果或技术线索时，面试官能产生相关追问或打断。
6. 干预不会无限触发，有冷却和每题次数上限。
7. 实时房间可以正常结束，并复用 Phase 1 评价报告链路。
8. Phase 1 回合式面试仍可用。

## 11. 回归命令

每个 Phase 2 agent 完成任务后，至少运行与自己改动相关的命令。阶段集成时必须运行：

```powershell
.\scripts\generate-api-types.ps1
cd services/api
python -m pytest -q
cd ..\..\apps\web
npm run build
```

如果加入前端测试，应同步加入对应命令，例如：

```powershell
cd apps/web
npm test
```

## 12. 给 Phase 2 agent 的通用提示词

```text
你正在实现 SimHire AI 面试平台 Phase 2：即时性互动。请先阅读 docs/AI_INTERVIEW_PLATFORM_DEV_DOC.md，再阅读 docs/phases/PHASE_2_REALTIME_START.md。Phase 1 MVP 已完成，现有回合式面试、浏览器语音输入输出和评价报告链路必须保持可用。你的任务只覆盖当前 subagent 指定范围，不要引入数字人视频、情绪化 TTS、企业端、支付或组织管理。后端 Pydantic schema 是契约源头，前端 generated 类型不能手工改。完成后请说明改动文件、接口变化、验证命令、验证结果和已知限制。
```
