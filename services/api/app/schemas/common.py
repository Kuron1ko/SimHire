from typing import Literal

from app.schemas.base import APIModel


class HealthResponse(APIModel):
    status: Literal["ok"]
    version: str
