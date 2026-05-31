import { Link, useParams } from "react-router-dom";

import { ActionPlanList } from "../components/evaluation/ActionPlanList";
import { DimensionEntry, DimensionScores } from "../components/evaluation/DimensionScores";
import { FindingList } from "../components/evaluation/FindingList";
import { ScoreSummary } from "../components/evaluation/ScoreSummary";
import { TurnFeedbackList } from "../components/evaluation/TurnFeedbackList";
import { useEvaluationReport } from "../hooks/useEvaluationReport";
import type { EvaluationReport } from "../services/evaluationApi";

export function EvaluationReportPage() {
  const { reportId } = useParams();
  const { report, isLoading, error, reload } = useEvaluationReport(reportId);

  return (
    <main className="page">
      <section className="report-shell">
        <header className="report-header">
          <div>
            <p className="eyebrow">评价报告</p>
            <h1>面试复盘</h1>
          </div>
          <Link className="secondary-link" to="/">
            返回场景选择
          </Link>
        </header>

        {isLoading && <div className="empty-state">正在生成评价报告</div>}

        {error && (
          <div className="alert report-alert">
            <span>{error}</span>
            <button className="secondary-button" type="button" onClick={() => void reload()}>
              重试
            </button>
          </div>
        )}

        {report && (
          <>
            <ScoreSummary report={report} />
            <div className="report-grid">
              <DimensionScores
                entries={abilityEntries(report)}
                maxTotal={60}
                title="能力线"
                total={report.ability.total}
              />
              <DimensionScores
                entries={psychologyEntries(report)}
                maxTotal={40}
                title="心理线"
                total={report.psychology.total}
              />
            </div>
            <FindingList risks={report.risks} strengths={report.strengths} />
            <TurnFeedbackList items={report.turnFeedback} />
            <ActionPlanList items={report.actionPlan} />
          </>
        )}
      </section>
    </main>
  );
}

function abilityEntries(report: EvaluationReport): DimensionEntry[] {
  const dimensions = report.ability.dimensions;
  return [
    { id: "logicalStructure", label: "逻辑结构", item: dimensions.logicalStructure },
    { id: "relevance", label: "问题相关", item: dimensions.relevance },
    { id: "specificity", label: "案例具体", item: dimensions.specificity },
    { id: "professionalDepth", label: "专业深度", item: dimensions.professionalDepth },
    { id: "communicationClarity", label: "表达清晰", item: dimensions.communicationClarity },
  ];
}

function psychologyEntries(report: EvaluationReport): DimensionEntry[] {
  const dimensions = report.psychology.dimensions;
  return [
    { id: "stressTolerance", label: "抗压能力", item: dimensions.stressTolerance },
    { id: "confidence", label: "信心", item: dimensions.confidence },
    { id: "adaptability", label: "应变能力", item: dimensions.adaptability },
    { id: "emotionalStability", label: "情绪稳定", item: dimensions.emotionalStability },
  ];
}
