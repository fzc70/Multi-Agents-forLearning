import { CheckCircle2, Circle, Clock, FilePlus2, RotateCcw } from "lucide-react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { getPathProgress } from "../../shared/utils/progress";

type LearningPathPageProps = {
  task: LearningTask;
  onAdjustPath: () => void;
  onGenerateResource: (type?: LearningResource["type"]) => void;
  onStartAssessment: () => void;
  isAdjustingPath: boolean;
  isAssessing: boolean;
  isGeneratingResource: boolean;
};

export function LearningPathPage({
  task,
  onAdjustPath,
  onGenerateResource,
  onStartAssessment,
  isAdjustingPath,
  isAssessing,
  isGeneratingResource
}: LearningPathPageProps) {
  const progress = getPathProgress(task);
  const currentStep = task.path.find((step) => step.status === "current") ?? task.path[0];

  return (
    <div className="space-y-5">
      <header className="flex items-start justify-between gap-4 rounded-[16px] border border-slate-200 bg-[#f7f3ea] p-5">
        <div>
          <p className="text-xs font-medium text-stone-600">路径规划</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink">学习路径</h1>
          <p className="mt-2 text-sm text-muted">
            已完成 {progress.completed}/{progress.total} 个阶段
          </p>
        </div>
        <Button variant="primary" icon={<RotateCcw size={16} />} onClick={onAdjustPath} loading={isAdjustingPath}>
          调整路径
        </Button>
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        {[
          { label: "当前阶段", value: currentStep?.title ?? task.nextAction },
          { label: "练习安排", value: currentStep?.exercise ?? "完成一次小练习" },
          { label: "节奏建议", value: progress.percent >= 70 ? "进入复盘和巩固" : "保持小步推进" }
        ].map((item) => (
          <div key={item.label} className="rounded-[14px] border border-slate-200 bg-white px-4 py-3">
            <p className="text-xs text-muted">{item.label}</p>
            <p className="mt-1 text-sm font-medium text-ink">{item.value}</p>
          </div>
        ))}
      </section>

      {(isAdjustingPath || task.pathAdjustmentNote) ? (
        <section className="rounded-[16px] border border-emerald-100 bg-emerald-50/80 p-4">
          <p className="text-xs font-medium text-emerald-700">最近变化</p>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {isAdjustingPath ? "正在更新下一阶段安排..." : task.pathAdjustmentNote}
          </p>
        </section>
      ) : null}

      <section className="rounded-[18px] border border-slate-200 bg-white p-4">
        <div className="space-y-3">
          {task.path.map((step, index) => {
            const Icon = step.status === "done" ? CheckCircle2 : step.status === "current" ? Clock : Circle;
            return (
              <div key={step.id} className={`grid grid-cols-[48px_1fr] gap-4 rounded-[14px] px-4 py-4 ${step.status === "current" ? "bg-emerald-50/70 ring-1 ring-emerald-100" : "bg-slate-50/70"}`}>
                <div className="flex flex-col items-center">
                  <Icon className={step.status === "current" ? "text-emerald-700" : step.status === "done" ? "text-green-600" : "text-slate-300"} size={22} />
                  {index < task.path.length - 1 ? <div className="mt-3 h-full min-h-12 w-px bg-line" /> : null}
                </div>
                <div>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs text-muted">阶段 {index + 1}</p>
                      <h2 className="mt-1 text-lg font-semibold text-ink">{step.title}</h2>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs text-muted">
                      {step.status === "current" ? "当前阶段" : step.status === "done" ? "已完成" : "待学习"}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted">{step.objective}</p>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-ui border border-line bg-white p-3">
                      <p className="text-xs text-muted">推荐资源</p>
                      <p className="mt-1 text-sm font-medium text-ink">{step.resource}</p>
                    </div>
                    <div className="rounded-ui border border-line bg-white p-3">
                      <p className="text-xs text-muted">练习安排</p>
                      <p className="mt-1 text-sm font-medium text-ink">{step.exercise}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {step.status === "done" ? (
                      <Button>查看复盘</Button>
                    ) : step.status === "current" ? (
                      <>
                        <Button variant="primary" onClick={onStartAssessment} loading={isAssessing}>
                          开始练习
                        </Button>
                        <Button icon={<FilePlus2 size={15} />} onClick={() => onGenerateResource()} loading={isGeneratingResource}>
                          生成配套资源
                        </Button>
                      </>
                    ) : (
                      <Button icon={<FilePlus2 size={15} />} onClick={() => onGenerateResource()} loading={isGeneratingResource}>
                        提前准备资源
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
