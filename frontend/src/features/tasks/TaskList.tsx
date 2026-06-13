import type { LearningTask } from "../../shared/types/task";
import { getPathProgress } from "../../shared/utils/progress";
import { formatDisplayTime } from "../../shared/utils/time";

type TaskListProps = {
  tasks: LearningTask[];
  selectedId: string;
  onSelect: (taskId: string) => void;
};

export function TaskList({ tasks, selectedId, onSelect }: TaskListProps) {
  return (
    <div className="surface overflow-hidden">
      <div className="border-b border-line px-5 py-4">
        <h2 className="section-title">学习任务</h2>
      </div>
      <div className="divide-y divide-line">
        {tasks.map((task) => {
          const active = task.id === selectedId;
          const progress = getPathProgress(task);
          return (
            <button
              key={task.id}
              className={`block w-full px-5 py-4 text-left transition ${
                active ? "bg-emerald-50/70" : "bg-white hover:bg-slate-50"
              }`}
              onClick={() => onSelect(task.id)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="truncate text-[15px] font-semibold text-ink">{task.title}</h3>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-muted">{task.category}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted">{task.nextAction}</p>
                  <p className="mt-2 text-xs text-muted">最近更新：{formatDisplayTime(task.updatedAt)}</p>
                </div>
                <span className="text-sm font-medium text-ink">
                  {progress.completed}/{progress.total}
                </span>
              </div>
              <div className="mt-3 h-1.5 rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-emerald-600" style={{ width: `${progress.percent}%` }} />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
