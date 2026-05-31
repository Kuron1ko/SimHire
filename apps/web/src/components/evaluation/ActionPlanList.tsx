import type { ActionItem } from "../../services/evaluationApi";

type ActionPlanListProps = {
  items: ActionItem[];
};

export function ActionPlanList({ items }: ActionPlanListProps) {
  return (
    <section className="report-section">
      <header className="section-heading">
        <h2>行动计划</h2>
      </header>
      <ol className="action-list">
        {items.map((item) => (
          <li className="action-row" key={`${item.title}-${item.practiceType}`}>
            <div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
            <span>{priorityLabel[item.priority]}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

const priorityLabel: Record<ActionItem["priority"], string> = {
  high: "高优先级",
  medium: "中优先级",
  low: "低优先级",
};
