import { Activity, AlertTriangle, CheckCircle2, TrendingUp } from "lucide-react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { EmptyState } from "../../shared/components/EmptyState";

type AssessmentPageProps = {
  task: LearningTask;
  onStartAssessment: () => void;
  onGenerateResource: (type?: LearningResource["type"]) => void;
  isAssessing: boolean;
};

export function AssessmentPage({ task, onStartAssessment, onGenerateResource, isAssessing }: AssessmentPageProps) {
  const score = task.assessment.score;

  if (!task.assessment.tested) {
    return (
      <EmptyState
        title="还没有评估结果"
        description="完成一次小测评后，这里会展示掌握度、薄弱点和下一步建议。"
        action={<Button variant="primary" onClick={onStartAssessment} loading={isAssessing}>开始第一次测评</Button>}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex items-start justify-between gap-4 rounded-[16px] border border-slate-200 bg-white p-5">
        <div>
          <p className="text-xs font-medium text-rose-700">学习反馈</p>
          <h1 className="text-2xl font-semibold text-ink">学习评估</h1>
          <p className="mt-2 text-sm text-muted">根据练习、对话和学习投入生成的阶段性反馈。</p>
        </div>
        <Button variant="primary" onClick={onStartAssessment} loading={isAssessing}>开始测评</Button>
      </header>

      <section className="grid grid-cols-[320px_1fr] gap-5">
        <div className="rounded-[18px] border border-slate-200 bg-[radial-gradient(circle_at_top,#fff7ed,#ffffff_58%)] p-5">
          <p className="text-sm text-muted">当前掌握度</p>
          <div
            className="mt-5 grid h-44 w-44 place-items-center rounded-full p-2 shadow-sm"
            style={{ background: `conic-gradient(#d97706 ${score * 3.6}deg, #f1f5f9 0deg)` }}
            aria-label={`当前掌握度 ${score} 分`}
          >
            <div className="grid h-full w-full place-items-center rounded-full bg-white">
              <div className="text-center">
                <strong className="text-6xl font-semibold text-ink">{score}</strong>
                <span className="pb-2 text-sm text-muted">/ 100</span>
                <p className="mt-1 text-xs text-muted">掌握度</p>
              </div>
            </div>
          </div>
          <p className="mt-4 text-sm leading-6 text-muted">{task.assessment.mastery}</p>
        </div>

        <div className="grid gap-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-[14px] border border-slate-200 bg-white p-4">
              <Activity className="text-emerald-700" size={19} />
              <p className="mt-3 text-xs text-muted">学习投入</p>
              <p className="mt-1 text-sm font-medium text-ink">{task.assessment.effort}</p>
            </div>
            <div className="rounded-[14px] border border-amber-100 bg-amber-50/60 p-4">
              <AlertTriangle className="text-amber-600" size={19} />
              <p className="mt-3 text-xs text-muted">主要薄弱点</p>
              <p className="mt-1 text-sm font-medium text-ink">{task.assessment.weakPoints[0]}</p>
            </div>
            <div className="rounded-[14px] border border-green-100 bg-green-50/60 p-4">
              <TrendingUp className="text-green-600" size={19} />
              <p className="mt-3 text-xs text-muted">下一步</p>
              <p className="mt-1 text-sm font-medium text-ink">{task.nextAction}</p>
            </div>
          </div>

          <div className="rounded-[16px] border border-slate-200 bg-white p-5">
            <div className="mb-4 flex items-center gap-2">
              <CheckCircle2 className="text-green-600" size={18} />
              <h2 className="section-title">下一步建议</h2>
            </div>
            <p className="text-sm leading-6 text-muted">{task.assessment.nextSuggestion}</p>
            <div className="mt-5 grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-semibold text-ink">薄弱点</h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  {task.assessment.weakPoints.map((item) => (
                    <button
                      key={item}
                      className="rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-700 transition hover:bg-amber-100"
                      onClick={() => onGenerateResource("练习题")}
                    >
                      {item} · 生成练习
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-ink">易错类型</h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  {task.assessment.mistakeTypes.map((item) => (
                    <button
                      key={item}
                      className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-800"
                      onClick={() => onGenerateResource("讲解文档")}
                    >
                      {item} · 查看讲解
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
