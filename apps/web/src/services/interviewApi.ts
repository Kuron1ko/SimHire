import type { components } from "../types/generated/api";
import { apiPost } from "./apiClient";

export type StartSessionRequest = components["schemas"]["StartSessionRequest"];
export type StartSessionResponse = components["schemas"]["StartSessionResponse"];
export type SubmitAnswerRequest = components["schemas"]["SubmitAnswerRequest"];
export type SubmitAnswerResponse = components["schemas"]["SubmitAnswerResponse"];
export type FinishSessionResponse = components["schemas"]["FinishSessionResponse"];

export async function startInterviewSession(request: StartSessionRequest): Promise<StartSessionResponse> {
  return apiPost<StartSessionResponse, StartSessionRequest>("/interviews/sessions", request);
}

export async function submitInterviewAnswer(
  sessionId: string,
  request: SubmitAnswerRequest,
): Promise<SubmitAnswerResponse> {
  return apiPost<SubmitAnswerResponse, SubmitAnswerRequest>(`/interviews/sessions/${sessionId}/answers`, request);
}

export async function finishInterviewSession(sessionId: string): Promise<FinishSessionResponse> {
  return apiPost<FinishSessionResponse, undefined>(`/interviews/sessions/${sessionId}/finish`, undefined);
}
