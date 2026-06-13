import type { LearningTask } from "../types/task";

export function getPathProgress(task: LearningTask) {
  const total = task.path.length || 1;
  const completed = task.path.filter((step) => step.status === "done").length;
  return {
    completed,
    total,
    percent: Math.round((completed / total) * 100)
  };
}
