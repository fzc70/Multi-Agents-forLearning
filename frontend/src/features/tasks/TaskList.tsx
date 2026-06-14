import { ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import type { LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { getPathProgress } from "../../shared/utils/progress";
import { formatDisplayTime } from "../../shared/utils/time";

type TaskListProps = {
  tasks: LearningTask[];
  selectedId: string;
  onSelect: (taskId: string) => void;
  onDelete: (taskId: string) => void;
};

const PAGE_SIZE = 5;

export function TaskList({ tasks, selectedId, onSelect, onDelete }: TaskListProps) {
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(tasks.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const visibleTasks = useMemo(() => {
    const start = (safePage - 1) * PAGE_SIZE;
    return tasks.slice(start, start + PAGE_SIZE);
  }, [safePage, tasks]);

  return (
    <div className="surface overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
        <h2 className="section-title">学习任务</h2>
        {tasks.length > PAGE_SIZE ? <span className="text-xs text-muted">{safePage}/{totalPages}</span> : null}
      </div>
      <div className="divide-y divide-line">
        {visibleTasks.map((task) => {
          const active = task.id === selectedId;
          const progress = getPathProgress(task);
          return (
            <div
              key={task.id}
              role="button"
              tabIndex={0}
              className={`block w-full px-5 py-4 text-left transition ${
                active ? "bg-emerald-50/70" : "bg-white hover:bg-slate-50"
              }`}
              onClick={() => onSelect(task.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter") onSelect(task.id);
              }}
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
              <div className="mt-3 flex items-center justify-between gap-3">
                <span className="text-xs text-muted">资源 {task.resources.length} · 练习 {task.exerciseCount}</span>
                <button
                  className="rounded-ui border border-transparent px-2 py-1 text-xs text-slate-400 transition hover:border-rose-100 hover:bg-rose-50 hover:text-rose-700"
                  onClick={(event) => {
                    event.stopPropagation();
                    if (window.confirm(`删除学习任务「${task.title}」？`)) onDelete(task.id);
                  }}
                >
                  <Trash2 size={13} className="mr-1 inline" />
                  删除
                </button>
              </div>
              <div className="mt-3 h-1.5 rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-emerald-600" style={{ width: `${progress.percent}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      {tasks.length > PAGE_SIZE ? (
        <div className="flex items-center justify-between border-t border-line bg-slate-50 px-4 py-3">
          <Button className="h-8 px-3" icon={<ChevronLeft size={14} />} disabled={safePage === 1} onClick={() => setPage((current) => Math.max(1, current - 1))}>
            上一页
          </Button>
          <span className="text-xs text-muted">共 {tasks.length} 个任务</span>
          <Button className="h-8 px-3" icon={<ChevronRight size={14} />} disabled={safePage === totalPages} onClick={() => setPage((current) => Math.min(totalPages, current + 1))}>
            下一页
          </Button>
        </div>
      ) : null}
    </div>
  );
}
