import { FileText, Sparkles } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { EmptyState } from "../../shared/components/EmptyState";
import { ResourceGenerationModal } from "../../shared/components/ResourceGenerationModal";
import { RESOURCE_FILTERS, RESOURCE_TYPE_REASONS } from "../../shared/constants/resources";
import { formatDisplayTime } from "../../shared/utils/time";
import { MaterialsPanel } from "../materials/MaterialsPanel";

type ResourcesPageProps = {
  task: LearningTask;
  onUploadMaterial: (file: File) => void;
  onGenerateResource: (type?: LearningResource["type"]) => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  onUseResource: (resource: LearningResource, action: "path" | "start") => void;
  isGeneratingResource: boolean;
  isUploadingMaterial: boolean;
};

function getRecommendationReason(task: LearningTask, resource: LearningResource) {
  const weakPoint = task.assessment.weakPoints[0] || task.nextAction;
  return `推荐原因：当前重点是“${weakPoint}”，${RESOURCE_TYPE_REASONS[resource.type]}`;
}

export function ResourcesPage({
  task,
  onUploadMaterial,
  onGenerateResource,
  onGenerateSelectedResources,
  onUseResource,
  isGeneratingResource,
  isUploadingMaterial
}: ResourcesPageProps) {
  const [type, setType] = useState<(typeof RESOURCE_FILTERS)[number]>("全部");
  const [generateOpen, setGenerateOpen] = useState(false);
  const [selectedResourceId, setSelectedResourceId] = useState(task.resources[0]?.id ?? "");
  const resourceCountRef = useRef(task.resources.length);

  const resources = useMemo(() => {
    if (type === "全部") return task.resources;
    return task.resources.filter((resource) => resource.type === type);
  }, [task.resources, type]);

  const selectedResource = useMemo(() => {
    return resources.find((resource) => resource.id === selectedResourceId) ?? resources[0];
  }, [resources, selectedResourceId]);

  useEffect(() => {
    if (task.resources.length > resourceCountRef.current) {
      setSelectedResourceId(task.resources[0]?.id ?? "");
    }
    resourceCountRef.current = task.resources.length;
  }, [task.resources]);

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
          {RESOURCE_FILTERS.map((item) => (
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

      <MaterialsPanel task={task} onUploadMaterial={onUploadMaterial} isUploading={isUploadingMaterial} />

      {resources.length === 0 ? (
        <EmptyState
          title="还没有该类型资源"
          description="可以基于当前任务生成一份资源，后续会根据你的学习表现继续调整。"
          tone="warm"
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
        <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
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
                      <p className="mt-2 text-xs leading-5 text-amber-700">{getRecommendationReason(task, resource)}</p>
                      <p className="mt-1 text-xs text-muted">创建时间：{formatDisplayTime(resource.createdAt)}</p>
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
                {selectedResource.id === task.resources[0]?.id ? (
                  <span className="mb-3 inline-flex rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                    最新资源
                  </span>
                ) : null}
                <div className="mb-4 grid h-10 w-10 place-items-center rounded-ui bg-amber-100 text-amber-800">
                  <FileText size={19} />
                </div>
                <p className="text-xs font-medium text-amber-700">{selectedResource.type}</p>
                <h2 className="mt-2 text-lg font-semibold leading-7 text-ink">{selectedResource.title}</h2>
                <p className="mt-3 text-sm leading-6 text-muted">{selectedResource.description}</p>
                <p className="mt-2 text-xs text-muted">创建时间：{formatDisplayTime(selectedResource.createdAt)}</p>
                <div className="mt-4 rounded-ui border border-amber-100 bg-white p-3 text-sm leading-6 text-amber-800">
                  {getRecommendationReason(task, selectedResource)}
                </div>

                <div className="my-5 h-px bg-slate-200" />

                <h3 className="text-sm font-semibold text-ink">内容预览</h3>
                <div className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                  {(selectedResource.content || selectedResource.description)
                    .split(/\n+/)
                    .filter(Boolean)
                    .slice(0, 6)
                    .map((line) => (
                      <p key={line}>{line.replace(/^#+\s*/, "")}</p>
                    ))}
                </div>

                <div className="mt-5 flex gap-2">
                  <Button onClick={() => onUseResource(selectedResource, "path")}>加入路径</Button>
                  <Button variant="primary" onClick={() => onUseResource(selectedResource, "start")}>
                    进入详情
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
