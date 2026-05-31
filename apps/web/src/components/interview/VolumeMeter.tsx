type VolumeMeterProps = {
  level: number;
  active: boolean;
  hasPermission?: boolean | null;
};

function clampLevel(level: number) {
  if (!Number.isFinite(level)) {
    return 0;
  }

  return Math.min(1, Math.max(0, level));
}

export function VolumeMeter({ level, active, hasPermission = null }: VolumeMeterProps) {
  const normalizedLevel = active ? clampLevel(level) : 0;
  const status = !active ? "安静" : hasPermission === false ? "无麦克风权限" : "录音中";

  return (
    <div className={active ? "volume-meter is-active" : "volume-meter"} aria-label={`麦克风音量：${status}`}>
      <div className="volume-meter__track" aria-hidden="true">
        <span style={{ transform: `scaleX(${normalizedLevel})` }} />
      </div>
      <span className="volume-meter__label">{status}</span>
    </div>
  );
}
