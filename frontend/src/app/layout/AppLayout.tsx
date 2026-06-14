import type { ReactNode } from "react";
import type { LearningTask, PageKey } from "../../shared/types/task";
import { AssistantLauncher } from "../../shared/components/AssistantLauncher";
import { TaskContextBar } from "../../shared/components/TaskContextBar";
import { Sidebar } from "./Sidebar";

type AppLayoutProps = {
  page: PageKey;
  task: LearningTask | null;
  tasks: LearningTask[];
  children: ReactNode;
  onPageChange: (page: PageKey) => void;
  onTaskChange: (taskId: string) => void;
  onAssistantSend: (message: string) => void;
};

export function AppLayout({
  page,
  task,
  tasks,
  children,
  onPageChange,
  onTaskChange,
  onAssistantSend
}: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar page={page} onPageChange={onPageChange} />
      <main className="ml-[88px] px-8 pb-28 pt-7">
        <div className="mx-auto max-w-[1220px]">
          {page !== "tasks" && task ? (
            <TaskContextBar
              page={page}
              task={task}
              tasks={tasks}
              onTaskChange={onTaskChange}
            />
          ) : null}
          {children}
        </div>
      </main>
      {task ? <AssistantLauncher task={task} onSend={onAssistantSend} /> : null}
    </div>
  );
}
