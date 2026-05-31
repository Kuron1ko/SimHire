type VoiceRecorderButtonProps = {
  isSupported: boolean;
  isListening: boolean;
  disabled?: boolean;
  error?: string | null;
  onStart: () => void;
  onStop: () => void;
};

export function VoiceRecorderButton({
  isSupported,
  isListening,
  disabled = false,
  error,
  onStart,
  onStop,
}: VoiceRecorderButtonProps) {
  const isDisabled = disabled || !isSupported;
  const label = !isSupported ? "语音识别不可用" : isListening ? "停止录音" : "开始录音";

  return (
    <button
      aria-pressed={isListening}
      className={isListening ? "voice-button is-recording" : "voice-button"}
      disabled={isDisabled}
      onClick={isListening ? onStop : onStart}
      title={error ?? (!isSupported ? "当前浏览器不支持语音识别" : undefined)}
      type="button"
    >
      <span className="voice-dot" aria-hidden="true" />
      {label}
    </button>
  );
}
