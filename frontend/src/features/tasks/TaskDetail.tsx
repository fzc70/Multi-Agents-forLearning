import { ArrowRight, BookOpen, Route, Sparkles } from "lucide-react";
import { useState } from "react";
import type { LearningResource, LearningTask, PageKey } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { ResourceGenerationModal } from "../../shared/components/ResourceGenerationModal";

type TaskDetailProps = {
  task: LearningTask;
  onPageChange: (page: PageKey) => void;
  onSmartGenerateResource: () => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  isGeneratingResource: boolean;
};

export function TaskDetail({
  task,
  onPageChange,
  onSmartGenerateResource,
  onGenerateSelectedResources,
  isGeneratingResource
}: TaskDetailProps) {
  const [generateOpen, setGenerateOpen] = useState(false);

  return (
    <>
    <div className="surface overflow-hidden">
      <div className="border-b border-line bg-white px-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-muted">当前选中任务</p>
            <h2 className="mt-1 text-xl font-semibold text-ink">{task.title}</h2>
          </div>
          <div className="flex gap-4 text-right text-xs text-muted">
            <span>资料 <strong className="ml-1 text-ink">{task.materialsCount}</strong></span>
            <span>资源 <strong className="ml-1 text-ink">{task.resources.length}</strong></span>
            <span>练习 <strong className="ml-1 text-ink">{task.exerciseCount}</strong></span>
          </div>
        </div>
        <div className="mt-4 h-1.5 rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-emerald-600" style={{ width: `${task.progress}%` }} />
        </div>
      </div>

      <div className="grid gap-5 p-5">
        <section className="rounded-[14px] border border-emerald-100 bg-emerald-50/70 p-5">
          <span className="inline-flex rounded-full bg-white px-2.5 py-1 text-xs font-medium text-emerald-700">下一步建议</span>
          <h3 className="mt-3 text-lg font-semibold text-ink">{task.nextAction}</h3>
          <p className="mt-2 text-sm leading-6 text-muted">{task.reason}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button variant="primary" icon={<ArrowRight size={16} />} onClick={() => onPageChange("chat")}>
              继续学习
            </Button>
            <Button icon={<Route size={16} />} onClick={() => onPageChange("path")}>
              查看路径
            </Button>
            <Button icon={<Sparkles size={16} />} onClick={() => setGenerateOpen(true)}>
              生成资源
            </Button>
          </div>
        </section>

        <section>
          <div className="mb-3 flex items-center gap-2">
            <BookOpen size={17} className="text-emerald-700" />
            <h3 className="section-title">最近路径</h3>
          </div>
          <div className="divide-y divide-line rounded-ui border border-line">
            {task.path.slice(0, 3).map((step) => (
              <div
                key={step.id}
                className={`flex items-center justify-between gap-4 px-4 py-3 ${step.status === "current" ? "bg-emerald-50/60" : ""}`}
              >
                <div>
                  <p className="text-sm font-medium text-ink">{step.title}</p>
                  <p className="mt-1 text-xs text-muted">{step.objective}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-muted">
                  {step.status === "current" ? "当前" : step.status === "done" ? "已完成" : "待学习"}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3 className="section-title">个性化依据</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {task.profileTags.map((tag) => (
              <span key={tag} className="rounded-full border border-line bg-slate-50 px-3 py-1.5 text-xs text-slate-700">
                {tag}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>

    <ResourceGenerationModal
      open={generateOpen}
      onClose={() => setGenerateOpen(false)}
      onSmartGenerate={onSmartGenerateResource}
      onGenerateSelected={onGenerateSelectedResources}
      isGenerating={isGeneratingResource}
    />
    </>
  );
}
