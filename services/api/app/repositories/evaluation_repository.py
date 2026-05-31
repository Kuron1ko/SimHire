from __future__ import annotations

from app.schemas import EvaluationReport


class EvaluationRepository:
    def __init__(self) -> None:
        self._reports: dict[str, EvaluationReport] = {}

    async def save_report(self, report: EvaluationReport) -> EvaluationReport:
        self._reports[report.id] = report
        return report

    async def get_report(self, report_id: str) -> EvaluationReport | None:
        return self._reports.get(report_id)
