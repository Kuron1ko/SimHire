from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas import InterviewScenario


class ScenarioRepository:
    def __init__(self, seed_path: Path | None = None) -> None:
        self._seed_path = seed_path or Path(__file__).resolve().parents[1] / "data" / "seed_scenarios.json"

    async def list_scenarios(self) -> list[InterviewScenario]:
        return list(_load_scenarios(self._seed_path))

    async def get_scenario(self, scenario_id: str) -> InterviewScenario | None:
        for scenario in _load_scenarios(self._seed_path):
            if scenario.id == scenario_id:
                return scenario
        return None


@lru_cache(maxsize=4)
def _load_scenarios(seed_path: Path) -> tuple[InterviewScenario, ...]:
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    return tuple(InterviewScenario.model_validate(item) for item in payload)
