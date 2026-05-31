import type { ScoreItem } from "../../services/evaluationApi";

export type DimensionEntry = {
  id: string;
  label: string;
  item: ScoreItem;
};

type DimensionScoresProps = {
  title: string;
  total: number;
  maxTotal: number;
  entries: DimensionEntry[];
};

export function DimensionScores({ title, total, maxTotal, entries }: DimensionScoresProps) {
  return (
    <section className="report-section">
      <header className="section-heading">
        <h2>{title}</h2>
        <span>
          {total.toFixed(1)} / {maxTotal}
        </span>
      </header>
      <div className="dimension-list">
        {entries.map(({ id, label, item }) => (
          <article className="dimension-row" key={id}>
            <div className="dimension-row__top">
              <h3>{label}</h3>
              <span>
                {item.score.toFixed(1)} / {item.maxScore}
              </span>
            </div>
            <div className="score-track" aria-hidden="true">
              <span style={{ transform: `scaleX(${Math.max(0, Math.min(1, item.score / item.maxScore))})` }} />
            </div>
            <div className="evidence-block">
              <p>证据</p>
              <ul>
                {(item.evidence ?? ["暂无证据"]).map((evidence) => (
                  <li key={evidence}>{evidence}</li>
                ))}
              </ul>
            </div>
            <p className="suggestion-text">建议：{item.suggestion}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
