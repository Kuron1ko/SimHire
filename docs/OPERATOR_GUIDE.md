# SimHire 操作者指南

本文档给项目操作者阅读。它说明如何使用 agent 推进 SimHire 项目。

重要规则：本文档由操作者维护。AI agent 默认不应该读取、引用或修改本文档。只有当操作者在当前对话中明确要求 AI 访问或修改它时，AI 才能操作。

## 1. 项目一句话说明

SimHire 是一个 AI 面试训练平台，目标是从最小可用 Web 面试系统，逐步演进到接近真人线上面试的语音和视频模拟体验。

## 2. 阶段

项目分为四个阶段：

1. MVP：搭建最小平台。
2. Realtime：让互动像聊天，而不是一问一答。
3. Intent & Voice：引入意图编排和更自然的语音合成。
4. Video Simulation：探索视频合成，模拟线上面试。

当前建议位置：Phase 1 MVP 已完成，下一步进入 Phase 2 Realtime。

以后如果阶段推进，请由操作者手动更新这一行，不要让 AI 自动更新本文档。

## 3. 怎么让 agent 工作

每次给 agent 派任务时，建议这样做：

1. 告诉 agent 当前阶段。
2. 要求 agent 先读 `docs/AI_INTERVIEW_PLATFORM_DEV_DOC.md`。
3. 要求 agent 再读当前阶段起始文档，例如 `docs/phases/PHASE_2_REALTIME_START.md`。
4. 明确这次只做哪个 subagent 任务。
5. 要求 agent 完成后说明改动文件、验证命令、验证结果和已知限制。
6. 完成一个阶段后，要求agent写下一个阶段的开始文档

Phase 2 的任务可以按 R0、R1、R2、R3、R4 依次派发，具体见 `docs/phases/PHASE_2_REALTIME_START.md`。

## 4. 操作者如何更新阶段位置

当一个大阶段完成时，操作者应检查：

1. 当前阶段验收标准是否满足。
2. 回归命令是否通过。
3. 负责收尾的 agent 是否已经更新下一个阶段起始文档。
4. 是否仍保留旧阶段 fallback。

确认后，操作者可以手动更新本文档中的“当前建议位置”。

## 5. 给新 agent 的通用开场

可以把下面这段放到任务开头：

```text
你正在参与 SimHire AI 面试平台开发。请先阅读 docs/AI_INTERVIEW_PLATFORM_DEV_DOC.md，再阅读本次任务指定的阶段起始文档。不要读取或修改 docs/OPERATOR_GUIDE.md，除非我在当前对话中明确要求。请只完成本次任务范围，完成后说明改动文件、验证命令、验证结果和已知限制。
```
