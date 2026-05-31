# Phase 1 MVP 起始与收尾文档

本文档记录 SimHire Phase 1 MVP 的目标、最终交付状态和可作为后续阶段依赖的稳定基线。

Phase 1 已完成。后续 agent 不应重新拆解本阶段任务，除非操作者明确要求修复 MVP 缺陷。

## 1. 阶段目标

Phase 1 的目标是搭建最小可用平台，形成“模拟、评分、复盘”的闭环。

必须具备：

1. Web 前端界面。
2. 面试场景选择。
3. 创建面试会话。
4. AI 面试官提问。
5. 用户文本或语音回答。
6. 问题播报。
7. 结束面试。
8. 评价报告。

不在 Phase 1 实现：

1. 实时双向语音聊天。
2. 面试官即时打断。
3. 意图编排器。
4. 情绪化语音合成。
5. 数字人视频。
6. 企业端、高校端、会员、支付。

## 2. 当前真实基线

当前代码已经跑通：

1. 场景选择。
2. 创建会话。
3. 文本回答。
4. 浏览器语音转写。
5. 问题语音播报。
6. 短回答追问。
7. 固定题库下一题。
8. 达到题数后结束面试。
9. 生成评价报告。
10. 从完成态进入报告页。

当前实现是 MVP，不是最终产品：

1. 后端使用内存 Repository，服务重启后会话和报告会丢失。
2. 题目生成和评分是确定性 mock。
3. 没有真实 LLM provider。
4. 没有数据库持久化。
5. 语音交互仍是回合式：播报、录音、提交、下一题。
6. 前端没有完整自动化测试。

## 3. 当前项目结构

```text
SimHire/
  12.pptx
  docs/
    AI_INTERVIEW_PLATFORM_DEV_DOC.md
    OPERATOR_GUIDE.md
    archive/
      AI_INTERVIEW_PLATFORM_DEV_DOC_LEGACY.md
    phases/
      PHASE_1_MVP_START.md
      PHASE_2_REALTIME_START.md
      PHASE_3_INTENT_VOICE_START.md
      PHASE_4_VIDEO_SIMULATION_START.md
  scripts/
    export-openapi.ps1
    generate-api-types.ps1
  services/
    api/
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
  apps/
    web/
      src/
        pages/
          InterviewSetupPage.tsx
          InterviewRoomPage.tsx
          EvaluationReportPage.tsx
        components/
          interview/
          evaluation/
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
```

## 4. 稳定 API

Phase 1 提供以下 REST 能力：

1. `GET /api/health`
2. `GET /api/scenarios`
3. `POST /api/interviews/sessions`
4. `POST /api/interviews/sessions/{sessionId}/answers`
5. `POST /api/interviews/sessions/{sessionId}/finish`
6. `GET /api/evaluations/reports/{reportId}`

后端 Pydantic schema 是契约源头。修改 schema 后必须重新生成 OpenAPI 和前端类型。

## 5. 关键规则

### 语音来源与心理线评分

评价系统必须区分回答来源。

规则：

1. 如果任意回答的 `transcriptSource` 是 `manual`，心理线总分和心理线所有维度都置为 0。
2. 报告必须标注存在非语音回答的原因。
3. 如果回答来源是 `browser_stt`，即使缺少完整 `speechMetrics`，也不能直接把心理线置 0，只能做保守估计或提示语音指标不足。

该规则是 Phase 1 收尾时的明确产品规则，后续阶段必须保留，除非操作者明确修改。

### 稳定 fallback

后续阶段即使引入实时能力，也必须保留 Phase 1 回合式面试作为 fallback。

如果浏览器不支持实时语音、WebSocket 失败、麦克风权限缺失或实时 provider 不可用，用户仍应能进入 Phase 1 回合式面试。

## 6. 回归命令

```powershell
.\scripts\generate-api-types.ps1
cd services/api
python -m pytest -q
cd ..\..\apps\web
npm run build
```

历史验证结果：

1. `python -m pytest -q` 曾通过，结果为 `25 passed, 1 warning`。
2. `npm run build` 曾通过。
3. 手动 API 冒烟验证过：创建会话、提交回答、finish、获取报告。
4. 手动输入回答会使心理线置 0，并在报告中出现原因标注。

后续 agent 应重新运行验证命令，不能只引用历史结果。

## 7. 本阶段结论

Phase 1 可以结束。它为 Phase 2 提供了稳定的场景、会话、问答、语音播报、语音转写和评价报告基础。

Phase 2 的核心任务不是重做 MVP，而是在不破坏 MVP 的前提下增加即时性互动。
