import { ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { SpeechPlaybackButton } from "../components/interview/SpeechPlaybackButton";
import { VoiceRecorderButton } from "../components/interview/VoiceRecorderButton";
import { VolumeMeter } from "../components/interview/VolumeMeter";
import { useInterviewSession } from "../hooks/useInterviewSession";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import type { StartSessionResponse } from "../services/interviewApi";
import type { InterviewScenario } from "../services/scenarioApi";

type RoomLocationState = {
  startResult: StartSessionResponse;
  scenario?: InterviewScenario;
  targetRole?: string;
};

export function InterviewRoomPage() {
  const location = useLocation();
  const state = location.state as RoomLocationState | null;
  const {
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
  } = useInterviewSession({ startResult: state?.startResult });
  const [answerText, setAnswerText] = useState("");
  const [isSpeechDraftActive, setIsSpeechDraftActive] = useState(false);
  const [recordingDurationMs, setRecordingDurationMs] = useState<number | null>(null);
  const [hasPlayedQuestion, setHasPlayedQuestion] = useState(false);
  const answerTextareaRef = useRef<HTMLTextAreaElement | null>(null);
  const speechBaseTextRef = useRef("");
  const recordingStartedAtRef = useRef<number | null>(null);
  const hasSpeechAnswerRef = useRef(false);
  const interviewLanguage = session?.language === "en-US" ? "en-US" : "zh-CN";
  const speechRecognition = useSpeechRecognition({ language: interviewLanguage });
  const speechPlayback = useSpeechSynthesis();

  const finishRecording = useCallback(() => {
    if (recordingStartedAtRef.current !== null) {
      setRecordingDurationMs(Math.round(performance.now() - recordingStartedAtRef.current));
      recordingStartedAtRef.current = null;
    }

    dispatchRoomAction({ type: "RECORD_STOP" });
    window.setTimeout(() => answerTextareaRef.current?.focus(), 0);
  }, [dispatchRoomAction]);

  useEffect(() => {
    setAnswerText("");
    setIsSpeechDraftActive(false);
    setRecordingDurationMs(null);
    setHasPlayedQuestion(false);
    speechBaseTextRef.current = "";
    recordingStartedAtRef.current = null;
    hasSpeechAnswerRef.current = false;
    speechRecognition.reset();
    speechPlayback.cancel();
  }, [currentTurn?.id]);

  useEffect(() => {
    const speechText = [speechRecognition.transcript, speechRecognition.interimTranscript].filter(Boolean).join(" ").trim();
    if (!isSpeechDraftActive || !speechText) {
      return;
    }

    const baseText = speechBaseTextRef.current.trim();
    setAnswerText(baseText ? `${baseText}\n${speechText}` : speechText);
    hasSpeechAnswerRef.current = true;
  }, [isSpeechDraftActive, speechRecognition.interimTranscript, speechRecognition.transcript]);

  useEffect(() => {
    if (!speechRecognition.isListening && roomState === "recording") {
      finishRecording();
    }
  }, [finishRecording, roomState, speechRecognition.isListening]);

  useEffect(() => {
    if (!speechPlayback.isSpeaking && roomState === "speaking_question") {
      dispatchRoomAction({ type: "SPEAK_END" });
    }
  }, [dispatchRoomAction, roomState, speechPlayback.isSpeaking]);

  if (!state?.startResult) {
    return (
      <main className="page">
        <section className="room-shell">
          <div className="empty-state">
            <h1>会话信息已失效</h1>
            <p>请返回场景选择页重新开始。</p>
            <Link className="primary-link" to="/">
              返回场景选择
            </Link>
          </div>
        </section>
      </main>
    );
  }

  if (!session) {
    return null;
  }

  async function handleStartRecording() {
    if (!currentTurn || !canRecord || isSubmitting || isFinishing) {
      return;
    }

    if (speechPlayback.isSpeaking) {
      speechPlayback.cancel();
      dispatchRoomAction({ type: "SPEAK_END" });
    }

    speechRecognition.reset();
    speechBaseTextRef.current = answerText;
    recordingStartedAtRef.current = performance.now();
    setRecordingDurationMs(null);
    setIsSpeechDraftActive(true);

    const started = await speechRecognition.start();
    if (started) {
      dispatchRoomAction({ type: "RECORD_START" });
      return;
    }

    recordingStartedAtRef.current = null;
    answerTextareaRef.current?.focus();
  }

  function handleStopRecording() {
    speechRecognition.stop();
  }

  function handlePlayQuestion() {
    if (!currentTurn || !canSpeak || isSubmitting || isFinishing) {
      return;
    }

    const didSpeak = speechPlayback.speak({
      text: currentTurn.question.text,
      lang: interviewLanguage,
      rate: 0.96,
      pitch: 1,
      volume: 1,
    });

    if (didSpeak) {
      setHasPlayedQuestion(true);
      dispatchRoomAction({ type: "SPEAK_START" });
    }
  }

  function handleStopPlayback() {
    speechPlayback.cancel();
    dispatchRoomAction({ type: "SPEAK_END" });
  }

  function handleAnswerChange(event: ChangeEvent<HTMLTextAreaElement>) {
    setAnswerText(event.target.value);
    if (!speechRecognition.isListening) {
      setIsSpeechDraftActive(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (speechRecognition.isListening) {
      return;
    }

    if (speechPlayback.isSpeaking) {
      handleStopPlayback();
    }

    setIsSpeechDraftActive(false);
    await submitAnswer({
      text: answerText,
      transcriptSource: hasSpeechAnswerRef.current ? "browser_stt" : "manual",
      durationMs: recordingDurationMs,
    });
  }

  async function handleFinishSession() {
    if (speechRecognition.isListening) {
      handleStopRecording();
    }

    if (speechPlayback.isSpeaking) {
      handleStopPlayback();
    }

    await finishSession();
  }

  const answeredCount = timeline.filter((turn) => turn.answer).length;
  const isBusy = isSubmitting || isFinishing || roomState === "loading_next_question";

  return (
    <main className="page">
      <section className="room-shell">
        <header className="room-header">
          <div>
            <p className="eyebrow">{state.scenario?.name ?? session.scenarioId}</p>
            <h1>{roomState === "completed" ? "面试已完成" : currentTurn ? `第 ${currentTurn.index} 题` : "可以结束面试"}</h1>
          </div>
          <div className="progress-pill">
            {Math.min(Math.max(session.currentTurnIndex, answeredCount), session.questionCountTarget)}/
            {session.questionCountTarget}
          </div>
        </header>

        {state.targetRole && <p className="target-role">目标岗位：{state.targetRole}</p>}

        {error && <div className="alert">{error}</div>}
        {lastAssistantAck && roomState !== "completed" && <div className="status-strip">{lastAssistantAck}</div>}

        {roomState === "completed" ? (
          <article className="complete-panel">
            <h2>面试已完成，评价报告已生成</h2>
            {finishResult && <p>报告 ID：{finishResult.reportId}</p>}
            <div className="complete-actions">
              {finishResult && (
                <Link className="primary-link" to={`/reports/${finishResult.reportId}`}>
                  查看评价报告
                </Link>
              )}
              <Link className="secondary-link" to="/">
                重新选择场景
              </Link>
            </div>
          </article>
        ) : (
          <div className="room-grid">
            <section className="room-main">
              {currentTurn ? (
                <article className="question-panel">
                  <p className="question-type">{currentTurn.question.type}</p>
                  <h2>{currentTurn.question.text}</h2>
                  <div className="question-toolbar">
                    <SpeechPlaybackButton
                      disabled={
                        speechPlayback.isSpeaking ? false : !canSpeak || isBusy || speechRecognition.isListening
                      }
                      hasPlayed={hasPlayedQuestion}
                      isSpeaking={speechPlayback.isSpeaking}
                      isSupported={speechPlayback.isSupported}
                      onPlay={handlePlayQuestion}
                      onStop={handleStopPlayback}
                    />
                  </div>
                  <div className="signal-row">
                    {(currentTurn.question.expectedSignals ?? []).map((signal) => (
                      <span key={signal}>{signal}</span>
                    ))}
                  </div>
                </article>
              ) : (
                <article className="question-panel">
                  <p className="question-type">finish_available</p>
                  <h2>本次文本问答已达到设定题数。</h2>
                </article>
              )}

              {currentTurn && (
                <form className="answer-panel" onSubmit={handleSubmit}>
                  <label htmlFor="answer">回答</label>
                  <div className="voice-control-row">
                    <VoiceRecorderButton
                      disabled={speechRecognition.isListening ? false : !canRecord || isBusy}
                      error={speechRecognition.error}
                      isListening={speechRecognition.isListening}
                      isSupported={speechRecognition.isSupported}
                      onStart={handleStartRecording}
                      onStop={handleStopRecording}
                    />
                    <VolumeMeter
                      active={speechRecognition.isListening}
                      hasPermission={speechRecognition.hasPermission}
                      level={speechRecognition.volumeLevel}
                    />
                  </div>
                  {speechRecognition.error && <p className="voice-hint">{speechRecognition.error}</p>}
                  <textarea
                    ref={answerTextareaRef}
                    id="answer"
                    placeholder={speechRecognition.isSupported ? "输入你的回答，也可以使用语音转写后编辑" : "输入你的回答"}
                    value={answerText}
                    onChange={handleAnswerChange}
                    disabled={isSubmitting || isFinishing}
                  />
                  <div className="room-actions">
                    <button
                      className="primary-button"
                      disabled={!canSubmit || !answerText.trim() || isSubmitting || speechRecognition.isListening}
                      type="submit"
                    >
                      {isSubmitting ? "提交中" : "提交回答"}
                    </button>
                  </div>
                </form>
              )}

              {finishAvailable && (
                <div className="finish-panel">
                  <button className="primary-button" disabled={!canFinish || isFinishing} onClick={handleFinishSession} type="button">
                    {isFinishing ? "结束中" : "结束面试"}
                  </button>
                </div>
              )}
            </section>

            <aside className="timeline-panel">
              <h2>问答记录</h2>
              <ol className="timeline-list">
                {timeline.map((turn) => (
                  <li className="timeline-item" key={turn.id}>
                    <p className="timeline-index">第 {turn.index} 题</p>
                    <p className="timeline-question">{turn.question.text}</p>
                    <p className={turn.answer ? "timeline-answer" : "timeline-answer is-pending"}>
                      {turn.answer?.text ?? "等待回答"}
                    </p>
                  </li>
                ))}
              </ol>
            </aside>
          </div>
        )}
      </section>
    </main>
  );
}
