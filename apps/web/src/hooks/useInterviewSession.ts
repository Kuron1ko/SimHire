import { useState } from "react";

import {
  finishInterviewSession,
  FinishSessionResponse,
  StartSessionResponse,
  submitInterviewAnswer,
} from "../services/interviewApi";
import type { components } from "../types/generated/api";
import { useInterviewRoomState } from "./useInterviewRoomState";

export type InterviewSession = components["schemas"]["InterviewSession"];
export type InterviewTurn = components["schemas"]["InterviewTurn"];
export type CandidateAnswer = components["schemas"]["CandidateAnswer"];

type UseInterviewSessionOptions = {
  startResult?: StartSessionResponse | null;
};

type SubmitAnswerInput = {
  text: string;
  transcriptSource?: CandidateAnswer["transcriptSource"];
  durationMs?: number | null;
  speechMetrics?: CandidateAnswer["speechMetrics"];
};

export function useInterviewSession(options: UseInterviewSessionOptions = {}) {
  const [session, setSession] = useState<InterviewSession | null>(() => options.startResult?.session ?? null);
  const [currentTurn, setCurrentTurn] = useState<InterviewTurn | null>(() => options.startResult?.turn ?? null);
  const [timeline, setTimeline] = useState<InterviewTurn[]>(() =>
    options.startResult?.turn ? [options.startResult.turn] : [],
  );
  const [finishAvailable, setFinishAvailable] = useState(false);
  const [lastAssistantAck, setLastAssistantAck] = useState<string | null>(null);
  const [finishResult, setFinishResult] = useState<FinishSessionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { roomState, dispatchRoomAction, isSubmitting, isFinishing, canSubmit: roomCanSubmit, canFinish: roomCanFinish, canRecord, canSpeak } = useInterviewRoomState(
    options.startResult ? "ready_to_answer" : "idle",
  );

  const canSubmit = roomCanSubmit && Boolean(currentTurn) && !finishAvailable;
  const canFinish = roomCanFinish && Boolean(session) && (finishAvailable || currentTurn === null);

  async function submitAnswer(input: SubmitAnswerInput) {
    if (!session || !currentTurn || !canSubmit || isSubmitting) {
      return;
    }

    const text = input.text.trim();
    if (!text) {
      setError("请先输入回答内容。");
      return;
    }

    const answer: CandidateAnswer = {
      text,
      transcriptSource: input.transcriptSource ?? "manual",
      audioUrl: null,
      durationMs: input.durationMs ?? null,
      speechMetrics: input.speechMetrics ?? null,
    };

    setError(null);
    dispatchRoomAction({ type: "SUBMIT_START" });

    try {
      const response = await submitInterviewAnswer(session.id, {
        turnId: currentTurn.id,
        answer,
      });
      const answeredAt = new Date().toISOString();
      const answeredTurn: InterviewTurn = {
        ...currentTurn,
        answer,
        answeredAt,
      };

      setTimeline((previous) => {
        const withAnswer = previous.map((turn) => (turn.id === currentTurn.id ? answeredTurn : turn));
        return response.nextTurn ? [...withAnswer, response.nextTurn] : withAnswer;
      });
      setLastAssistantAck(response.assistantAck);

      if (response.nextTurn) {
        dispatchRoomAction({ type: "NEXT_TURN_READY" });
        setCurrentTurn(response.nextTurn);
        setSession((previous) =>
          previous ? { ...previous, currentTurnIndex: response.nextTurn?.index ?? previous.currentTurnIndex } : previous,
        );
        setFinishAvailable(false);
        dispatchRoomAction({ type: "SESSION_READY" });
        return;
      }

      setCurrentTurn(null);
      setFinishAvailable(true);
      dispatchRoomAction({ type: "FINISH_AVAILABLE" });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "提交回答失败");
      dispatchRoomAction({ type: "FAIL" });
    }
  }

  async function finishSession() {
    if (!session || !canFinish || isFinishing) {
      return;
    }

    setError(null);
    dispatchRoomAction({ type: "FINISH_START" });

    try {
      const result = await finishInterviewSession(session.id);
      setFinishResult(result);
      setSession({
        ...session,
        status: "completed",
        completedAt: new Date().toISOString(),
      });
      setCurrentTurn(null);
      setFinishAvailable(false);
      dispatchRoomAction({ type: "COMPLETE" });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "结束面试失败");
      dispatchRoomAction({ type: "FAIL" });
    }
  }

  function resetSession() {
    setSession(null);
    setCurrentTurn(null);
    setTimeline([]);
    setFinishAvailable(false);
    setLastAssistantAck(null);
    setFinishResult(null);
    setError(null);
    dispatchRoomAction({ type: "RESET" });
  }

  return {
    roomState,
    session,
    currentTurn,
    timeline,
    finishAvailable,
    finishResult,
    lastAssistantAck,
    isSubmitting,
    isFinishing,
    canSubmit,
    canFinish,
    canRecord,
    canSpeak,
    error,
    dispatchRoomAction,
    submitAnswer,
    finishSession,
    resetSession,
  };
}
