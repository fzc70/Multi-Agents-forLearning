import { ChevronDown, Target } from "lucide-react";
import { useState } from "react";
import type { LearningTask, PageKey } from "../types/task";
import { Button } from "./Button";
import { Modal } from "./Modal";
import { getPathProgress } from "../utils/progress";

type TaskContextBarProps = {
  page: Exclude<PageKey, "tasks">;
  task: LearningTask;
  tasks: LearningTask[];
  onTaskChange: (taskId: string) => void;
};

export function TaskContextBar({
  task,
  tasks,
  onTaskChange
}: TaskContextBarProps) {
  const [open, setOpen] = useState(false);
  const progress = getPathProgress(task);

  return (
    <>
      <div className="mb-6 flex items-center justify-between rounded-ui border border-line bg-white px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-ui bg-emerald-50 text-emerald-800">
            <Target size={18} />
          </div>
          <div className="min-w-0">
            <p className="text-xs text-muted">当前任务</p>
            <h2 className="truncate text-sm font-semibold text-ink">{task.title}</h2>
          </div>
          <div className="hidden h-8 w-px bg-line md:block" />
          <div className="hidden items-center gap-2 md:flex">
            <span className="text-xs text-muted">路径进度</span>
            <div className="h-2 w-28 rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-emerald-600" style={{ width: `${progress.percent}%` }} />
            </div>
            <span className="text-xs font-medium text-ink">
              {progress.completed}/{progress.total}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" icon={<ChevronDown size={16} />} onClick={() => setOpen(true)}>
            切换任务
          </Button>
        </div>
      </div>

      <Modal open={open} title="切换学习任务" onClose={() => setOpen(false)}>
        <div className="grid gap-2">
          {tasks.map((item) => {
            const itemProgress = getPathProgress(item);
            return (
            <button
              key={item.id}
              className={`rounded-ui border px-4 py-3 text-left transition ${
                item.id === task.id
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-line bg-white hover:border-slate-300 hover:bg-slate-50"
              }`}
              onClick={() => {
                onTaskChange(item.id);
                setOpen(false);
              }}
            >
              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-ink">{item.title}</span>
                <span className="text-xs text-muted">
                  路径 {itemProgress.completed}/{itemProgress.total}
                </span>
              </div>
              <p className="mt-1 text-sm text-muted">{item.nextAction}</p>
            </button>
            );
          })}
        </div>
      </Modal>
    </>
  );
}
