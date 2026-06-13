import { Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { LearningResource, LearningTask, NewTaskInput, PageKey } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { EmptyState } from "../../shared/components/EmptyState";
import { CreateTaskModal } from "./CreateTaskModal";
import { TaskDetail } from "./TaskDetail";
import { TaskList } from "./TaskList";

type TasksPageProps = {
  tasks: LearningTask[];
  selectedTask: LearningTask;
  onSelectTask: (taskId: string) => void;
  onCreateTask: (input: NewTaskInput) => void;
  onPageChange: (page: PageKey) => void;
  onSmartGenerateResource: () => void;
  onGenerateSelectedResources: (types: LearningResource["type"][]) => void;
  isGeneratingResource: boolean;
};

export function TasksPage({
  tasks,
  selectedTask,
  onSelectTask,
  onCreateTask,
  onPageChange,
  onSmartGenerateResource,
  onGenerateSelectedResources,
  isGeneratingResource
}: TasksPageProps) {
  const [query, setQuery] = useState("");
  const [createOpen, setCreateOpen] = useState(false);

  const filteredTasks = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return tasks;
    return tasks.filter((task) => `${task.title} ${task.category} ${task.nextAction}`.toLowerCase().includes(value));
  }, [query, tasks]);

  return (
    <div>
      <header className="mb-6 rounded-[14px] border border-slate-200 bg-[linear-gradient(135deg,#ffffff,#f1f7f2_52%,#faf6ea)] p-5">
        <div className="flex items-start justify-between gap-5">
          <div>
            <p className="mb-2 text-xs font-medium text-emerald-700">学习任务中心</p>
            <h1 className="text-2xl font-semibold text-ink">我的学习任务</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              每个任务独立维护对话、资源、路径和评估。先选任务，再进入对应学习工作区。
            </p>
          </div>
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setCreateOpen(true)}>
            新建学习任务
          </Button>
        </div>
        <div className="mt-5 flex items-center justify-between gap-4 border-t border-white/80 pt-4">
          <div className="flex gap-6 text-sm">
            <span className="text-muted">任务数 <strong className="ml-1 text-ink">{tasks.length}</strong></span>
            <span className="text-muted">当前任务 <strong className="ml-1 text-ink">{selectedTask.title}</strong></span>
          </div>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={17} />
            <input
              className="focus-ring h-10 w-80 rounded-ui border border-slate-200 bg-white/90 pl-9 pr-3 text-sm"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索任务"
            />
          </div>
        </div>
      </header>

      {tasks.length === 0 ? (
        <EmptyState
          title="还没有学习任务"
          description="先创建第一个学习目标，后续系统会根据对话、资源和练习逐步完善计划。"
          action={<Button variant="primary" onClick={() => setCreateOpen(true)}>新建学习任务</Button>}
        />
      ) : (
        <div className="grid grid-cols-[0.95fr_1.25fr] gap-5">
          <TaskList tasks={filteredTasks} selectedId={selectedTask.id} onSelect={onSelectTask} />
          <TaskDetail
            task={selectedTask}
            onPageChange={onPageChange}
            onSmartGenerateResource={onSmartGenerateResource}
            onGenerateSelectedResources={onGenerateSelectedResources}
            isGeneratingResource={isGeneratingResource}
          />
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
