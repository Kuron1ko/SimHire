from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic.json_schema import models_json_schema

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.schemas import CONTRACT_MODELS


def _contract_components() -> dict[str, Any]:
    _, schema = models_json_schema(
        [(model, "validation") for model in CONTRACT_MODELS],
        ref_template="#/components/schemas/{model}",
    )
    return schema.get("$defs", {})


def _install_custom_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        components = openapi_schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        schemas.update(_contract_components())
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SimHire API",
        version=__version__,
        description="Contract-first API scaffold for the SimHire interview MVP.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api")
    _install_custom_openapi(app)
    return app


app = create_app()
