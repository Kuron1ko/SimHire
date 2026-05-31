# SimHire API

FastAPI scaffold and contract source for the SimHire MVP.

## Run locally

```powershell
cd services/api
python -m pip install -e ".[dev]"
uvicorn app.main:create_app --factory --reload
```

The health endpoint is available at `http://127.0.0.1:8000/api/health`.
