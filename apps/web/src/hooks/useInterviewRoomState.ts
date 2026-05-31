import { useMemo, useReducer } from "react";

export type InterviewRoomState =
  | "idle"
  | "speaking_question"
  | "ready_to_answer"
  | "recording"
  | "reviewing_transcript"
  | "submitting_answer"
  | "loading_next_question"
  | "finishing"
  | "completed"
  | "error";

export type InterviewRoomAction =
  | { type: "SESSION_READY" }
  | { type: "SPEAK_START" }
  | { type: "SPEAK_END" }
  | { type: "RECORD_START" }
  | { type: "RECORD_STOP" }
  | { type: "SUBMIT_START" }
  | { type: "NEXT_TURN_READY" }
  | { type: "FINISH_AVAILABLE" }
  | { type: "FINISH_START" }
  | { type: "COMPLETE" }
  | { type: "FAIL" }
  | { type: "RESET" };

export function roomStateReducer(state: InterviewRoomState, action: InterviewRoomAction): InterviewRoomState {
  if (action.type === "RESET") {
    return "idle";
  }

  const nextState = transitions[state]?.[action.type];
  return nextState ?? state;
}

export function useInterviewRoomState(initialState: InterviewRoomState = "idle") {
  const [roomState, dispatch] = useReducer(roomStateReducer, initialState);
  const permissions = useMemo(
    () => ({
      canSubmit:
        roomState === "ready_to_answer" ||
        roomState === "speaking_question" ||
        roomState === "recording" ||
        roomState === "reviewing_transcript" ||
        roomState === "error",
      canFinish: roomState === "ready_to_answer" || roomState === "error",
      canRecord:
        roomState === "ready_to_answer" ||
        roomState === "speaking_question" ||
        roomState === "reviewing_transcript" ||
        roomState === "error",
      canSpeak: roomState === "ready_to_answer" || roomState === "reviewing_transcript" || roomState === "error",
      isSubmitting: roomState === "submitting_answer" || roomState === "loading_next_question",
      isFinishing: roomState === "finishing",
    }),
    [roomState],
  );

  return {
    roomState,
    dispatchRoomAction: dispatch,
    ...permissions,
  };
}

const transitions: Record<InterviewRoomState, Partial<Record<InterviewRoomAction["type"], InterviewRoomState>>> = {
  idle: {
    SESSION_READY: "ready_to_answer",
    FAIL: "error",
  },
  ready_to_answer: {
    SPEAK_START: "speaking_question",
    RECORD_START: "recording",
    SUBMIT_START: "submitting_answer",
    FINISH_START: "finishing",
    COMPLETE: "completed",
    FAIL: "error",
  },
  speaking_question: {
    SPEAK_END: "ready_to_answer",
    RECORD_START: "recording",
    SUBMIT_START: "submitting_answer",
    FINISH_START: "finishing",
    FAIL: "error",
  },
  recording: {
    RECORD_STOP: "reviewing_transcript",
    FAIL: "error",
  },
  reviewing_transcript: {
    SPEAK_START: "speaking_question",
    RECORD_START: "recording",
    SUBMIT_START: "submitting_answer",
    FINISH_START: "finishing",
    COMPLETE: "completed",
    FAIL: "error",
  },
  submitting_answer: {
    NEXT_TURN_READY: "loading_next_question",
    FINISH_AVAILABLE: "ready_to_answer",
    FAIL: "error",
  },
  loading_next_question: {
    SESSION_READY: "ready_to_answer",
    FAIL: "error",
  },
  finishing: {
    COMPLETE: "completed",
    FAIL: "error",
  },
  completed: {
    RESET: "idle",
  },
  error: {
    SESSION_READY: "ready_to_answer",
    SPEAK_START: "speaking_question",
    RECORD_START: "recording",
    SUBMIT_START: "submitting_answer",
    FINISH_START: "finishing",
    RESET: "idle",
  },
};
