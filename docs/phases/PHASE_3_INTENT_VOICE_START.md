# Phase 3 Intent & Voice 起始文档草案

本文档是 Phase 3 的预备起始文档。它不是当前开发阶段的执行指令。

当 Phase 2 Realtime 完成后，Phase 2 收尾 agent 必须根据真实代码状态重写本文档，再交给 Phase 3 agent 使用。

## 1. 阶段目标

Phase 3 的目标是在实时互动稳定后，引入意图编排和更自然的语音合成。

本阶段要让面试官不只是“检测到事件后回复一句话”，而是能根据面试阶段、用户表现、压力程度和面试官目标选择行为。

同时，面试官声音应从浏览器默认电子音升级为更自然、可控、有轻微情绪起伏的语音。

## 2. 前置条件

进入 Phase 3 前，Phase 2 应至少完成：

1. 实时面试房间。
2. 实时 transcript 或接近实时 transcript。
3. 静默追问。
4. 认真度提醒。
5. 兴趣追问或适度打断。
6. WebSocket 或等价实时事件通道。
7. Phase 1 回合式 fallback。
8. 实时房间结束后进入评价报告。

如果这些条件没有满足，应先回到 Phase 2 修复。

## 3. 本阶段关注

1. 意图驱动行为编排器。
2. 面试官行为状态机。
3. 压力强度和追问深度控制。
4. Prompt builder。
5. LLM provider adapter。
6. TTS provider adapter。
7. 面试官语气参数，例如鼓励、追问、提醒、压力测试、收束。

模型调用路径必须保持为：

```text
Browser
  -> SimHire backend
  -> behavior_orchestrator.py / question_agent.py / evaluation_service.py
  -> providers/llm 或 providers/tts
  -> OpenAI-compatible API 或 TTS API
```

真实 provider 至少接收两个核心参数：

1. `base_url`
2. `api_key`

环境变量建议映射为：

```text
LLM_BASE_URL -> base_url
LLM_API_KEY -> api_key
```

前端不得保存模型 key，也不得直接调用模型供应商 API。

## 4. 非目标

Phase 3 不做：

1. 数字人视频。
2. 摄像头表情识别。
3. 口型同步。
4. 企业端、高校端、支付和会员。
5. 大规模数据看板。

## 5. 建议模块方向

后端可能新增：

```text
services/api/app/
  services/
    behavior_orchestrator.py
    prompt_builder.py
    interviewer_policy.py
  providers/
    llm/
      base.py
      mock_provider.py
      openai_provider.py
    tts/
      base.py
      mock_provider.py
      openai_tts_provider.py
  schemas/
    behavior.py
    voice.py
```

前端可能新增：

```text
apps/web/src/
  hooks/
    useAdaptiveVoice.ts
  services/
    voiceApi.ts
  components/interviewer/
    InterviewerVoiceStatus.tsx
    InterviewerIntentBadge.tsx
```

以上只是草案。Phase 3 开始前必须根据 Phase 2 的真实结构重新确认。

如果 Phase 2 没有完成 OpenAI-compatible LLM Provider 基座，Phase 3 的第一个任务必须先实现该 provider，再继续意图编排和情绪化语音。provider 任务至少包括：

1. `LLMProvider` 抽象。
2. `MockLLMProvider` 默认实现。
3. `OpenAICompatibleProvider` 真实实现。
4. `LLM_BASE_URL -> base_url`。
5. `LLM_API_KEY -> api_key`。
6. `QuestionAgent` 或 `BehaviorOrchestrator` 接入 provider。
7. provider 失败时回退或返回可恢复错误。
8. 调试者文档同步真实模型启动方式。

如果 Phase 2 没有完成评价 LLM Provider，Phase 3 收尾前必须决定是否实现它。若实现，必须满足：

1. LLM 只输出结构化诊断片段，后端仍负责组装 `EvaluationReport`。
2. 手动输入回答导致心理线置 0 的规则不能被 LLM 覆盖。
3. provider 失败时可以回退到 deterministic scoring。

如果 Phase 2 没有完成服务端 Realtime Provider 2B，Phase 3 可以继续使用浏览器事件流和浏览器 TTS；不得把服务端 realtime provider 作为意图编排的硬前置。

## 6. Phase 2 收尾 agent 必须补充

Phase 2 完成后，重写本文档时至少补充：

1. Phase 2 最终代码结构。
2. 实时事件契约最终版本。
3. 可复用的状态机和干预策略。
4. 当前 TTS 方案和限制。
5. LLM provider 是否已经实现；如果已实现，说明配置项、调用路径和测试覆盖；如果未实现，把 provider 设为 Phase 3 第一个任务。
6. 评价 LLM Provider 是否已经实现；如果未实现，说明是否进入 Phase 3 范围。
7. 服务端 Realtime Provider 2B 是否已经实现；如果未实现，说明 Phase 3 是否仍使用浏览器事件流。
8. Phase 3 的 subagent 拆分。
9. Phase 3 的验收标准。
10. Phase 3 的回归命令。
