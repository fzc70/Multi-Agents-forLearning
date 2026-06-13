import type { ReactNode } from "react";
import type { LearningTask, PageKey } from "../../shared/types/task";
import { AssistantLauncher } from "../../shared/components/AssistantLauncher";
import { TaskContextBar } from "../../shared/components/TaskContextBar";
import { Sidebar } from "./Sidebar";

type AppLayoutProps = {
  page: PageKey;
  task: LearningTask;
  tasks: LearningTask[];
  children: ReactNode;
  onPageChange: (page: PageKey) => void;
  onTaskChange: (taskId: string) => void;
  onContextAction: () => void;
  onAssistantSend: (message: string) => void;
  busyAction: "resource" | "path" | "assessment" | null;
};

export function AppLayout({
  page,
  task,
  tasks,
  children,
  onPageChange,
  onTaskChange,
  onContextAction,
  onAssistantSend,
  busyAction
}: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar page={page} onPageChange={onPageChange} />
      <main className="ml-[88px] px-8 py-7">
        <div className="mx-auto max-w-[1220px]">
          {page !== "tasks" ? (
            <TaskContextBar
              page={page}
              task={task}
              tasks={tasks}
              onTaskChange={onTaskChange}
              onPrimaryAction={onContextAction}
              busyAction={busyAction}
            />
          ) : null}
          {children}
        </div>
      </main>
      <AssistantLauncher task={task} onSend={onAssistantSend} />
    </div>
  );
}
