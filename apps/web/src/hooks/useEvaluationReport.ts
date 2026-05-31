import { useCallback, useEffect, useState } from "react";

import { EvaluationReport, getEvaluationReport } from "../services/evaluationApi";

export function useEvaluationReport(reportId?: string) {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(reportId));
  const [error, setError] = useState<string | null>(null);

  const loadReport = useCallback(async () => {
    if (!reportId) {
      setReport(null);
      setIsLoading(false);
      setError("缺少报告 ID。");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getEvaluationReport(reportId);
      setReport(result);
    } catch (caught) {
      setReport(null);
      setError(caught instanceof Error ? caught.message : "评价报告加载失败");
    } finally {
      setIsLoading(false);
    }
  }, [reportId]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  return {
    report,
    isLoading,
    error,
    reload: loadReport,
  };
}
