type SpeechPlaybackButtonProps = {
  isSupported: boolean;
  isSpeaking: boolean;
  disabled?: boolean;
  hasPlayed?: boolean;
  onPlay: () => void;
  onStop: () => void;
};

export function SpeechPlaybackButton({
  isSupported,
  isSpeaking,
  disabled = false,
  hasPlayed = false,
  onPlay,
  onStop,
}: SpeechPlaybackButtonProps) {
  const isDisabled = disabled || !isSupported;
  const label = !isSupported ? "播放不可用" : isSpeaking ? "停止播放" : hasPlayed ? "重播问题" : "播放问题";

  return (
    <button
      aria-pressed={isSpeaking}
      className={isSpeaking ? "playback-button is-speaking" : "playback-button"}
      disabled={isDisabled}
      onClick={isSpeaking ? onStop : onPlay}
      title={!isSupported ? "当前浏览器不支持语音播报" : undefined}
      type="button"
    >
      <span className="playback-symbol" aria-hidden="true">
        {isSpeaking ? "■" : "▶"}
      </span>
      {label}
    </button>
  );
}
