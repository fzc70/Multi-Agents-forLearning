import { FileText, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { EmptyState } from "../../shared/components/EmptyState";
import { ResourceGenerationModal } from "../../shared/components/ResourceGenerationModal";

type ResourcesPageProps = {
  task: LearningTask;
  onGenerateResource: (type?: LearningResource["type"]) => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  onUseResource: (resource: LearningResource, action: "path" | "start") => void;
  isGeneratingResource: boolean;
};

const resourceTypes: Array<LearningResource["type"] | "全部"> = [
  "全部",
  "讲解文档",
  "练习题",
  "思维导图",
  "拓展阅读",
  "视频脚本",
  "代码案例",
  "知识图谱"
];

export function ResourcesPage({
  task,
  onGenerateResource,
  onGenerateSelectedResources,
  onUseResource,
  isGeneratingResource
}: ResourcesPageProps) {
  const [type, setType] = useState<(typeof resourceTypes)[number]>("全部");
  const [generateOpen, setGenerateOpen] = useState(false);
  const [selectedResourceId, setSelectedResourceId] = useState(task.resources[0]?.id ?? "");

  const resources = useMemo(() => {
    if (type === "全部") return task.resources;
    return task.resources.filter((resource) => resource.type === type);
  }, [task.resources, type]);

  const selectedResource = useMemo(() => {
    return resources.find((resource) => resource.id === selectedResourceId) ?? resources[0];
  }, [resources, selectedResourceId]);

  return (
    <div className="space-y-5">
      <header className="rounded-[16px] border border-slate-200 bg-white p-5">
        <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-amber-700">资源库</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink">学习资源</h1>
          <p className="mt-2 text-sm text-muted">按资源类型筛选，也可以从当前任务直接生成新的学习材料。</p>
        </div>
          <Button
            variant="primary"
            icon={<Sparkles size={16} />}
            loading={isGeneratingResource}
            onClick={() => {
              if (type === "全部") {
                setGenerateOpen(true);
                return;
              }
              onGenerateResource(type);
            }}
          >
            生成资源
          </Button>
        </div>
        <div className="mt-5 flex flex-wrap gap-2 border-t border-line pt-4">
          {resourceTypes.map((item) => (
            <button
              key={item}
              className={`rounded-full px-3 py-1.5 text-sm transition ${
                type === item
                  ? "bg-amber-100 text-amber-900 ring-1 ring-amber-200"
                  : "border border-slate-200 bg-slate-50 text-muted hover:border-amber-200 hover:bg-amber-50 hover:text-amber-800"
              }`}
              onClick={() => setType(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </header>

      {resources.length === 0 ? (
        <EmptyState
          title="还没有该类型资源"
          description="可以基于当前任务生成一份资源，后续会根据你的学习表现继续调整。"
          action={
            <Button
              variant="primary"
              loading={isGeneratingResource}
              onClick={() => {
                if (type === "全部") {
                  setGenerateOpen(true);
                  return;
                }
                onGenerateResource(type);
              }}
            >
              生成资源
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-[1fr_360px] gap-4">
          <div className="grid gap-3">
            {resources.map((resource) => {
              const active = selectedResource?.id === resource.id;
              return (
                <button
                  key={resource.id}
                  className={`rounded-[14px] border bg-white p-4 text-left transition ${
                    active ? "border-amber-300 ring-2 ring-amber-100" : "border-slate-200 hover:border-amber-200"
                  }`}
                  onClick={() => setSelectedResourceId(resource.id)}
                >
                  <div className="flex items-start justify-between gap-6">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-ink">{resource.title}</h3>
                        <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700">{resource.type}</span>
                      </div>
                      <p className="mt-2 text-sm text-muted">{resource.description}</p>
                    </div>
                    <span className="text-xs text-amber-700">{active ? "正在预览" : "查看"}</span>
                  </div>
                </button>
              );
            })}
          </div>

          <aside className="sticky top-6 h-fit rounded-[16px] border border-slate-200 bg-[#fffdf8] p-5">
            {selectedResource ? (
              <>
                <div className="mb-4 grid h-10 w-10 place-items-center rounded-ui bg-amber-100 text-amber-800">
                  <FileText size={19} />
                </div>
                <p className="text-xs font-medium text-amber-700">{selectedResource.type}</p>
                <h2 className="mt-2 text-lg font-semibold leading-7 text-ink">{selectedResource.title}</h2>
                <p className="mt-3 text-sm leading-6 text-muted">{selectedResource.description}</p>

                <div className="my-5 h-px bg-slate-200" />

                <h3 className="text-sm font-semibold text-ink">内容预览</h3>
                <div className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                  <p>1. 先围绕当前任务拆出一个最小学习目标。</p>
                  <p>2. 用示例或练习降低理解成本。</p>
                  <p>3. 最后给出一个可复盘的小任务。</p>
                </div>

                <div className="mt-5 flex gap-2">
                  <Button onClick={() => onUseResource(selectedResource, "path")}>加入路径</Button>
                  <Button variant="primary" onClick={() => onUseResource(selectedResource, "start")}>
                    开始使用
                  </Button>
                </div>
              </>
            ) : null}
          </aside>
        </div>
      )}

      <ResourceGenerationModal
        open={generateOpen}
        onClose={() => setGenerateOpen(false)}
        smartDescription="系统根据当前任务和筛选条件自动选择最合适的一类资源。"
        onSmartGenerate={() => onGenerateResource(type === "全部" ? undefined : type)}
        onGenerateSelected={onGenerateSelectedResources}
        isGenerating={isGeneratingResource}
      />
    </div>
  );
}
