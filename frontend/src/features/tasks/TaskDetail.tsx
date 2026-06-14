import { BookOpen, Sparkles } from "lucide-react";
import { useState } from "react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { ResourceGenerationModal } from "../../shared/components/ResourceGenerationModal";
import { getPathProgress } from "../../shared/utils/progress";
import { MaterialsPanel } from "../materials/MaterialsPanel";

type TaskDetailProps = {
  task: LearningTask;
  onUploadMaterial: (file: File) => void;
  onSmartGenerateResource: () => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  onStartLearning: () => void;
  isGeneratingResource: boolean;
  isUploadingMaterial: boolean;
};

export function TaskDetail({
  task,
  onUploadMaterial,
  onSmartGenerateResource,
  onGenerateSelectedResources,
  onStartLearning,
  isGeneratingResource,
  isUploadingMaterial
}: TaskDetailProps) {
  const [generateOpen, setGenerateOpen] = useState(false);
  const progress = getPathProgress(task);

  return (
    <>
    <div className="surface overflow-hidden">
      <div className="border-b border-line bg-white px-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-muted">任务详情</p>
            <h2 className="mt-1 text-xl font-semibold text-ink">{task.title}</h2>
          </div>
          <div className="flex gap-4 text-right text-xs text-muted">
            <span>资料 <strong className="ml-1 text-ink">{task.materialsCount}</strong></span>
            <span>资源 <strong className="ml-1 text-ink">{task.resources.length}</strong></span>
            <span>练习 <strong className="ml-1 text-ink">{task.exerciseCount}</strong></span>
          </div>
        </div>
        <div className="mt-4 h-1.5 rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-emerald-600" style={{ width: `${progress.percent}%` }} />
        </div>
      </div>

      <div className="grid gap-5 p-5">
        <section className="rounded-[14px] border border-emerald-100 bg-emerald-50/70 p-5">
          <span className="inline-flex rounded-full bg-white px-2.5 py-1 text-xs font-medium text-emerald-700">建议动作</span>
          <h3 className="mt-3 text-lg font-semibold text-ink">{task.nextAction}</h3>
          <p className="mt-2 text-sm leading-6 text-muted">{task.reason}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button icon={<Sparkles size={16} />} onClick={() => setGenerateOpen(true)}>
              生成资源
            </Button>
            {task.resources.length > 0 ? (
              <Button variant="primary" onClick={onStartLearning}>
                开始学习
              </Button>
            ) : null}
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

        <MaterialsPanel task={task} onUploadMaterial={onUploadMaterial} compact isUploading={isUploadingMaterial} />
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
