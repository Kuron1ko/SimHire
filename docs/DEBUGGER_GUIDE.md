# SimHire 调试者指南

本文档用于快速把项目跑起来，并说明当前 API/AI 配置。本文档由 AI agent 更新；启动方式、端口、环境变量、回归命令或 AI 接入方式变化时，必须同步修改。


## 1. 默认地址

```text
后端 API: http://127.0.0.1:8000/api
前端页面: http://127.0.0.1:5173
前端默认 API: http://127.0.0.1:8000/api
```

建议前端和后端都使用 `127.0.0.1`，不要混用 `localhost` 和 `127.0.0.1`。

## 2. 安装依赖

```powershell
cd D:\simhire\SimHire

cd services\api
python -m pip install -e ".[dev]"

cd ..\..\apps\web
npm install
```

## 3. 启动项目

后端：

```powershell
cd D:\simhire\SimHire\services\api
python -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd D:\simhire\SimHire\apps\web
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api"
npm run dev
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

打开浏览器：

```text
http://127.0.0.1:5173
```

## 4. 当前 API 与 AI 调用路径

前端只调用本项目后端，不直接调用 OpenAI 或其他模型服务。

前端 API 配置在：

```text
apps/web/src/services/apiClient.ts
```

默认值是：

```text
http://127.0.0.1:8000/api
```

后端已经预留 LLM 环境变量，位置在：

```text
services/api/app/core/config.py
```

当前已有：

```text
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=
```

但当前代码还没有真正接入 LLM provider。现在的“AI”逻辑是确定性 mock：

1. `services/api/app/services/question_agent.py`：固定题库、短回答追问。
2. `services/api/app/domain/scoring.py`：规则评分。
3. `services/api/app/services/evaluation_service.py`：组装评价报告。

也就是说，当前只设置 `LLM_API_KEY` 不会调用 OpenAI。

当前真实调用路径是：

```text
Browser
  -> apps/web/src/services/apiClient.ts
  -> FastAPI /api/*
  -> InterviewOrchestrator / EvaluationService
  -> QuestionAgent / DeterministicScoringEngine
  -> mock 题库与规则评分
```

未来接入真实模型后的目标路径是：

```text
Browser
  -> SimHire FastAPI backend
  -> QuestionAgent / BehaviorOrchestrator / EvaluationService
  -> LLMProvider
  -> OpenAI-compatible API(base_url, api_key)
```

## 5. 如果要接入 OpenAI-compatible API

推荐由后端接入，前端不要保存或发送模型 key。

调用外部模型必须有两个核心参数：

1. `base_url`：OpenAI-compatible 服务地址。
2. `api_key`：服务端密钥。

建议环境变量映射：

```text
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=你的 key
LLM_MODEL=gpt-4.1-mini
```

其中 `LLM_BASE_URL` 对应 provider 的 `base_url`，`LLM_API_KEY` 对应 provider 的 `api_key`。如果使用中转或其他 OpenAI-compatible 服务，把 `LLM_BASE_URL` 改成对应地址即可。

建议代码结构：

```text
services/api/app/providers/llm/
  base.py
  mock_provider.py
  openai_provider.py
```

接入原则：

1. `openai_provider.py` 使用 `base_url + api_key + model` 调模型。
2. `QuestionAgent` 先通过 provider 生成首题、追问和下一题。
3. 评价系统先保留规则评分，等提问链路稳定后再接入 LLM。
4. 不要在 `interview_orchestrator.py` 或 `evaluation_service.py` 里直接写供应商 SDK 调用。
5. 没有 key 或 provider 失败时，必须能回退到当前 mock 流程。

## 6. 回归命令

```powershell
cd D:\simhire\SimHire
.\scripts\generate-api-types.ps1

cd services\api
python -m pytest -q

cd ..\..\apps\web
npm run build
```

不要手工修改：

```text
apps/web/src/types/generated/api.ts
```

## 7. 常见问题

`Fail to fetch`：

1. 确认后端正在运行。
2. 确认前端 `VITE_API_BASE_URL` 是 `http://127.0.0.1:8000/api`。
3. 如果 Vite 使用了非 `5173` 端口，后端 `CORS_ORIGINS` 也要包含该前端地址。

临时 CORS 示例：

```powershell
$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:5174"
```

麦克风不可用：

1. 检查浏览器麦克风权限。
2. 检查浏览器是否支持 Web Speech API。
3. 语音不可用时，可以用文本输入完成 MVP 流程。

端口被占用：

```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

换后端端口时，也要同步改前端：

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8010/api"
```
