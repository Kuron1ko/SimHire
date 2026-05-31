import type { EvaluationReport } from "../../services/evaluationApi";

type ScoreSummaryProps = {
  report: EvaluationReport;
};

export function ScoreSummary({ report }: ScoreSummaryProps) {
  return (
    <section className="report-summary" aria-label="总评分">
      <div>
        <p className="report-label">总分</p>
        <strong>{Math.round(report.overallScore)}</strong>
        <span>{scoreLevel(report.overallScore)}</span>
      </div>
      <dl>
        <div>
          <dt>能力线</dt>
          <dd>{report.ability.total.toFixed(1)} / 60</dd>
        </div>
        <div>
          <dt>心理线</dt>
          <dd>{report.psychology.total.toFixed(1)} / 40</dd>
        </div>
      </dl>
    </section>
  );
}

function scoreLevel(score: number): string {
  if (score >= 90) {
    return "优秀";
  }
  if (score >= 80) {
    return "良好";
  }
  if (score >= 70) {
    return "可用";
  }
  if (score >= 60) {
    return "待提升";
  }
  return "风险较高";
}
