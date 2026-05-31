import type { components } from "../types/generated/api";
import { apiGet } from "./apiClient";

export type EvaluationReport = components["schemas"]["EvaluationReport"];
export type ScoreItem = components["schemas"]["ScoreItem"];
export type TurnFeedback = components["schemas"]["TurnFeedback"];
export type ActionItem = components["schemas"]["ActionItem"];

export async function getEvaluationReport(reportId: string): Promise<EvaluationReport> {
  return apiGet<EvaluationReport>(`/evaluations/reports/${encodeURIComponent(reportId)}`);
}
