import type { TurnFeedback } from "../../services/evaluationApi";

type TurnFeedbackListProps = {
  items: TurnFeedback[];
};

export function TurnFeedbackList({ items }: TurnFeedbackListProps) {
  return (
    <section className="report-section">
      <header className="section-heading">
        <h2>逐题反馈</h2>
      </header>
      <ol className="feedback-list">
        {items.map((item, index) => (
          <li className="feedback-row" key={item.turnId}>
            <div className="feedback-row__top">
              <h3>第 {index + 1} 题</h3>
              <span>{item.score.toFixed(1)} 分</span>
            </div>
            <p>{item.summary}</p>
            <div className="feedback-columns">
              <div>
                <h4>亮点</h4>
                <ul>
                  {(item.highlights ?? ["暂无亮点记录"]).map((highlight) => (
                    <li key={highlight}>{highlight}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>改进</h4>
                <ul>
                  {(item.improvements ?? ["暂无改进记录"]).map((improvement) => (
                    <li key={improvement}>{improvement}</li>
                  ))}
                </ul>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
