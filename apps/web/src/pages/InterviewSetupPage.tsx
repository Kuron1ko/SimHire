import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { startInterviewSession } from "../services/interviewApi";
import { InterviewScenario, listScenarios } from "../services/scenarioApi";

export function InterviewSetupPage() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<InterviewScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [questionCount, setQuestionCount] = useState(4);
  const [targetRole, setTargetRole] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedScenario = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenarioId),
    [scenarios, selectedScenarioId],
  );

  useEffect(() => {
    let isMounted = true;

    listScenarios()
      .then((items) => {
        if (!isMounted) {
          return;
        }
        setScenarios(items);
        if (items[0]) {
          setSelectedScenarioId(items[0].id);
          setQuestionCount(items[0].defaultQuestionCount);
        }
      })
      .catch((caught: unknown) => {
        if (isMounted) {
          setError(caught instanceof Error ? caught.message : "场景加载失败");
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  function selectScenario(scenario: InterviewScenario) {
    setSelectedScenarioId(scenario.id);
    setQuestionCount(clampQuestionCount(scenario.defaultQuestionCount));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedScenario || isStarting) {
      return;
    }

    setIsStarting(true);
    setError(null);

    try {
      const trimmedRole = targetRole.trim();
      const safeQuestionCount = clampQuestionCount(questionCount);
      const result = await startInterviewSession({
        scenarioId: selectedScenario.id,
        mode: "voice",
        language: "zh-CN",
        questionCountTarget: safeQuestionCount,
        candidateProfile: trimmedRole
          ? {
              name: null,
              targetRole: trimmedRole,
              background: null,
            }
          : null,
      });

      navigate(`/interview/${result.session.id}`, {
        state: {
          startResult: result,
          scenario: selectedScenario,
          targetRole: trimmedRole || undefined,
        },
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "创建会话失败");
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <main className="page">
      <section className="setup-layout">
        <header className="setup-header">
          <p className="eyebrow">SimHire MVP</p>
          <h1>选择面试场景</h1>
        </header>

        {error && <div className="alert">{error}</div>}

        <form className="setup-grid" onSubmit={handleSubmit}>
          <div className="scenario-list" aria-busy={isLoading}>
            {isLoading ? (
              <div className="empty-state">正在加载场景</div>
            ) : (
              scenarios.map((scenario) => (
                <button
                  className={`scenario-card ${scenario.id === selectedScenarioId ? "is-selected" : ""}`}
                  key={scenario.id}
                  type="button"
                  onClick={() => selectScenario(scenario)}
                >
                  <span className="scenario-card__title">{scenario.name}</span>
                  <span className="scenario-card__description">{scenario.description}</span>
                  <span className="scenario-card__meta">
                    {scenario.defaultQuestionCount} 题 · {difficultyLabel[scenario.difficulty]}
                  </span>
                </button>
              ))
            )}
          </div>

          <aside className="setup-panel">
            <div className="field">
              <label htmlFor="question-count">题数</label>
              <input
                id="question-count"
                max={8}
                min={1}
                type="number"
                value={questionCount}
                onChange={(event) => setQuestionCount(clampQuestionCount(event.target.value))}
              />
            </div>

            <div className="field">
              <label htmlFor="target-role">目标岗位</label>
              <input
                id="target-role"
                placeholder="例如：产品经理实习生"
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
              />
            </div>

            <button className="primary-button" disabled={!selectedScenario || isStarting} type="submit">
              {isStarting ? "创建中" : "开始面试"}
            </button>
          </aside>
        </form>
      </section>
    </main>
  );
}

const difficultyLabel: Record<InterviewScenario["difficulty"], string> = {
  easy: "基础",
  medium: "标准",
  hard: "进阶",
};

function clampQuestionCount(value: string | number): number {
  const numericValue = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(numericValue)) {
    return QUESTION_COUNT_MIN;
  }

  return Math.min(QUESTION_COUNT_MAX, Math.max(QUESTION_COUNT_MIN, Math.trunc(numericValue)));
}

const QUESTION_COUNT_MIN = 1;
const QUESTION_COUNT_MAX = 8;
