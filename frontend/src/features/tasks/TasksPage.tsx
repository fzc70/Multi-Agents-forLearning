import { ArrowRight, BookOpen, Plus, Route, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { LearningResource, LearningTask, NewTaskInput, PageKey } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { EmptyState } from "../../shared/components/EmptyState";
import { getPathProgress } from "../../shared/utils/progress";
import { CreateTaskModal } from "./CreateTaskModal";
import { TaskDetail } from "./TaskDetail";
import { TaskList } from "./TaskList";

type TasksPageProps = {
  tasks: LearningTask[];
  selectedTask: LearningTask | null;
  loading: boolean;
  onSelectTask: (taskId: string) => void;
  onCreateTask: (input: NewTaskInput) => void;
  onDeleteTask: (taskId: string) => void;
  onPageChange: (page: PageKey) => void;
  onUploadMaterial: (file: File) => void;
  onSmartGenerateResource: () => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  isGeneratingResource: boolean;
  isUploadingMaterial: boolean;
};

export function TasksPage({
  tasks,
  selectedTask,
  loading,
  onSelectTask,
  onCreateTask,
  onDeleteTask,
  onPageChange,
  onUploadMaterial,
  onSmartGenerateResource,
  onGenerateSelectedResources,
  isGeneratingResource,
  isUploadingMaterial
}: TasksPageProps) {
  const [query, setQuery] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const selectedProgress = selectedTask ? getPathProgress(selectedTask) : { completed: 0, total: 0, percent: 0 };

  const filteredTasks = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return tasks;
    return tasks.filter((task) => `${task.title} ${task.category} ${task.nextAction}`.toLowerCase().includes(value));
  }, [query, tasks]);

  return (
    <div>
      <header className="mb-6 rounded-[16px] border border-slate-200 bg-[linear-gradient(135deg,#ffffff,#f4f8f1_48%,#fff8ed)] p-5">
        <div className="flex items-start justify-between gap-5">
          <div>
            <p className="mb-2 text-xs font-medium text-emerald-700">学习任务</p>
            <h1 className="max-w-3xl text-2xl font-semibold text-ink">
              {selectedTask ? selectedTask.title : "创建一个学习任务，开始个性化学习"}
            </h1>
            {!selectedTask ? (
              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                系统会根据你的对话、资料、资源使用和练习反馈逐步形成学习画像与路径。
              </p>
            ) : null}
            {selectedTask ? (
              <div className="mt-5 flex flex-wrap gap-2">
                <Button variant="primary" icon={<ArrowRight size={16} />} onClick={() => onPageChange("chat")}>
                  继续学习
                </Button>
                {selectedTask.resources.length > 0 ? (
                  <Button icon={<BookOpen size={16} />} onClick={() => onPageChange("resources")}>
                    开始学习
                  </Button>
                ) : null}
                <Button icon={<Route size={16} />} onClick={() => onPageChange("path")}>
                  查看路径
                </Button>
              </div>
            ) : null}
          </div>
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setCreateOpen(true)}>
            新建学习任务
          </Button>
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-4 border-t border-white/80 pt-4">
          <div className="flex flex-wrap gap-4 text-sm">
            <span className="text-muted">当前任务 <strong className="ml-1 text-ink">{selectedTask?.title ?? "未创建"}</strong></span>
            <span className="text-muted">路径 <strong className="ml-1 text-ink">{selectedProgress.completed}/{selectedProgress.total}</strong></span>
            <span className="text-muted">资源 <strong className="ml-1 text-ink">{selectedTask?.resources.length ?? 0}</strong></span>
          </div>
          <div className="relative w-full sm:w-auto">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={17} />
            <input
              className="focus-ring h-10 w-full rounded-ui border border-slate-200 bg-white/90 pl-9 pr-3 text-sm sm:w-80"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索任务"
            />
          </div>
        </div>
      </header>

      {loading ? (
        <EmptyState title="正在连接学习系统" description="正在读取你的学习任务。" />
      ) : tasks.length === 0 ? (
        <EmptyState
          title="还没有学习任务"
          description="先创建第一个学习目标。创建后可以上传资料、对话学习、生成资源并获得路径建议。"
          action={<Button variant="primary" onClick={() => setCreateOpen(true)}>新建学习任务</Button>}
        />
      ) : (
        <div className="grid gap-5 xl:grid-cols-[0.95fr_1.25fr]">
          <TaskList tasks={filteredTasks} selectedId={selectedTask?.id ?? ""} onSelect={onSelectTask} onDelete={onDeleteTask} />
          {selectedTask ? (
            <TaskDetail
              task={selectedTask}
              onUploadMaterial={onUploadMaterial}
              onSmartGenerateResource={onSmartGenerateResource}
              onGenerateSelectedResources={onGenerateSelectedResources}
              onStartLearning={() => onPageChange("resources")}
              isGeneratingResource={isGeneratingResource}
              isUploadingMaterial={isUploadingMaterial}
            />
          ) : null}
        </div>
      )}

      <CreateTaskModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreate={(input) => {
          onCreateTask(input);
          setCreateOpen(false);
        }}
      />
    </div>
  );
}
