import type { components } from "../types/generated/api";
import { apiGet } from "./apiClient";

export type InterviewScenario = components["schemas"]["InterviewScenario"];
type ScenariosResponse = components["schemas"]["ScenariosResponse"];

export async function listScenarios(): Promise<InterviewScenario[]> {
  const response = await apiGet<ScenariosResponse>("/scenarios");
  return response.items;
}
