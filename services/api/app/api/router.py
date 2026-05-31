from fastapi import APIRouter

from app.api.routes import evaluations, health, interviews, scenarios

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(scenarios.router)
api_router.include_router(interviews.router)
api_router.include_router(evaluations.router)
