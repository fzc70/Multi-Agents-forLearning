import { useEffect, useMemo, useRef, useState } from "react";
import { AppLayout } from "./layout/AppLayout";
import type { LearningResource, LearningTask, NewTaskInput, PageKey } from "../shared/types/task";
import { Toast } from "../shared/components/Toast";
import { AssessmentPage } from "../features/assessment/AssessmentPage";
import { ChatPage } from "../features/chat/ChatPage";
import { LearningPathPage } from "../features/learning-path/LearningPathPage";
import { ProfilePage } from "../features/profile/ProfilePage";
import { ResourceDetailPage } from "../features/resources/ResourceDetailPage";
import { ResourcesPage } from "../features/resources/ResourcesPage";
import { TasksPage } from "../features/tasks/TasksPage";
import { api } from "../shared/api/client";

type BusyAction = "loading" | "chat" | "upload" | "resource" | "path" | "assessment" | "exercise" | null;
const PAGE_STORAGE_KEY = "learning-app-page";
const TASK_STORAGE_KEY = "learning-app-task";
const RESOURCE_STORAGE_KEY = "learning-app-resource";

function makeTempId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 7)}`;
}

function inferResourceType(value: string): LearningResource["type"] {
  if (value.includes("练习") || value.includes("题") || value.includes("测评")) return "练习题";
  if (value.includes("图谱")) return "知识图谱";
  if (value.includes("导图")) return "思维导图";
  if (value.includes("阅读")) return "拓展阅读";
  if (value.includes("代码") || value.includes("实操")) return "代码案例";
  return "讲解文档";
}

export default function App() {
  const [page, setPageState] = useState<PageKey>(() => (localStorage.getItem(PAGE_STORAGE_KEY) as PageKey) || "tasks");
  const [tasks, setTasks] = useState<LearningTask[]>([]);
  const [selectedTaskId, setSelectedTaskIdState] = useState(() => localStorage.getItem(TASK_STORAGE_KEY) || "");
  const [selectedResourceId, setSelectedResourceIdState] = useState(() => localStorage.getItem(RESOURCE_STORAGE_KEY) || "");
  const [toast, setToast] = useState("");
  const [busyAction, setBusyAction] = useState<BusyAction>("loading");
  const [pathBusyStep, setPathBusyStep] = useState<{ stepId: string; action: "use" | "generate" | "complete" } | null>(null);
  const toastTimerRef = useRef<number | null>(null);

  const selectedTask = useMemo(() => {
    return tasks.find((task) => task.id === selectedTaskId) ?? tasks[0] ?? null;
  }, [selectedTaskId, tasks]);
  const selectedResource = selectedTask?.resources.find((resource) => resource.id === selectedResourceId) ?? null;

  useEffect(() => {
    void loadTasks();
  }, []);

  function setPage(nextPage: PageKey) {
    localStorage.setItem(PAGE_STORAGE_KEY, nextPage);
    setPageState(nextPage);
  }

  function setSelectedTaskId(taskId: string) {
    localStorage.setItem(TASK_STORAGE_KEY, taskId);
    setSelectedTaskIdState(taskId);
  }

  function setSelectedResourceId(resourceId: string) {
    localStorage.setItem(RESOURCE_STORAGE_KEY, resourceId);
    setSelectedResourceIdState(resourceId);
  }

  async function loadTasks() {
    try {
      setBusyAction("loading");
      const nextTasks = await api.listTasks();
      setTasks(nextTasks);
      setSelectedTaskIdState((current) => {
        const next = nextTasks.some((task) => task.id === current) ? current : nextTasks[0]?.id || "";
        if (next) localStorage.setItem(TASK_STORAGE_KEY, next);
        return next;
      });
    } catch (error) {
      showToast(error instanceof Error ? error.message : "后端连接失败");
    } finally {
      setBusyAction(null);
    }
  }

  function showToast(message: string) {
    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current);
    }
    setToast(message);
    toastTimerRef.current = window.setTimeout(() => setToast(""), 2200);
  }

  function replaceTask(task: LearningTask) {
    setTasks((current) => {
      const exists = current.some((item) => item.id === task.id);
      return exists ? current.map((item) => (item.id === task.id ? task : item)) : [task, ...current];
    });
    setSelectedTaskId(task.id);
  }

  function updateTaskLocal(taskId: string, updater: (task: LearningTask) => LearningTask) {
    setTasks((current) => current.map((task) => (task.id === taskId ? updater(task) : task)));
  }

  async function withBusy(action: Exclude<BusyAction, null>, pendingMessage: string, work: () => Promise<void>) {
    if (busyAction) {
      showToast("上一个操作还在处理中");
      return;
    }
    try {
      setBusyAction(action);
      showToast(pendingMessage);
      await work();
    } catch (error) {
      showToast(error instanceof Error ? error.message : "操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleCreateTask(input: NewTaskInput) {
    await withBusy("loading", "正在创建学习任务...", async () => {
      const task = await api.createTask(input);
      replaceTask(task);
      showToast("学习任务已创建");
    });
  }

  async function handleDeleteTask(taskId: string) {
    await withBusy("loading", "正在删除学习任务...", async () => {
      await api.deleteTask(taskId);
      const nextTasks = tasks.filter((task) => task.id !== taskId);
      setTasks(nextTasks);
      const nextSelected = nextTasks[0]?.id || "";
      setSelectedTaskId(nextSelected);
      if (!nextSelected) setPage("tasks");
      showToast("学习任务已删除");
    });
  }

  async function handleSendMessage(message: string) {
    if (!selectedTask) return;
    if (busyAction) {
      showToast("上一个操作还在处理中");
      return;
    }
    const taskId = selectedTask.id;
    const userMessage = { id: makeTempId("user"), role: "user" as const, content: message };
    const assistantId = makeTempId("assistant");
    updateTaskLocal(taskId, (task) => ({
      ...task,
      messages: [...task.messages, userMessage, { id: assistantId, role: "assistant", content: "我正在思考..." }]
    }));
    try {
      setBusyAction("chat");
      let streamed = "";
      await api.streamMessage(taskId, message, {
        onStatus: () => undefined,
        onDelta: (content) => {
          streamed += content;
          updateTaskLocal(taskId, (task) => ({
            ...task,
            messages: task.messages.map((item) => (item.id === assistantId ? { ...item, content: streamed } : item))
          }));
        },
        onDone: ({ task }) => {
          replaceTask(task);
          showToast("已回复");
        }
      });
    } catch (error) {
      updateTaskLocal(taskId, (task) => ({
        ...task,
        messages: task.messages.map((item) =>
          item.id === assistantId ? { ...item, content: error instanceof Error ? error.message : "回复失败，请稍后再试。" } : item
        )
      }));
      showToast(error instanceof Error ? error.message : "回复失败");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleUploadMaterial(file: File) {
    if (!selectedTask) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("当前只支持上传 PDF");
      return;
    }
    await withBusy("upload", "正在解析学习资料...", async () => {
      const task = await api.uploadMaterial(selectedTask.id, file);
      replaceTask(task);
      showToast("学习资料已解析");
    });
  }

  async function handleGenerateResource(type?: LearningResource["type"]) {
    if (!selectedTask) return;
    await withBusy("resource", "正在生成学习资源...", async () => {
      const result = await api.generateResources(selectedTask.id, type ? "selected" : "smart", type ? [type] : undefined);
      replaceTask(result.task);
      if (result.resources[0]) setSelectedResourceId(result.resources[0].id);
      showToast(`已生成 ${result.resources.length} 个学习资源`);
    });
  }

  async function handleGenerateResourceAndOpen(type?: LearningResource["type"], stepId?: string) {
    if (stepId) setPathBusyStep({ stepId, action: "generate" });
    if (!stepId) setPage("resources");
    await handleGenerateResource(type);
    setPage("resources");
    if (stepId) setPathBusyStep(null);
  }

  async function handleGenerateSelectedResources(types: LearningResource["type"][]) {
    if (!selectedTask || types.length === 0) return;
    await withBusy("resource", "正在生成所选资源...", async () => {
      const result = await api.generateResources(selectedTask.id, "selected", types);
      replaceTask(result.task);
      if (result.resources[0]) setSelectedResourceId(result.resources[0].id);
      showToast(`已生成 ${result.resources.length} 个学习资源`);
    });
  }

  async function handleGenerateSelectedResourcesAndOpen(types: LearningResource["type"][]) {
    setPage("resources");
    await handleGenerateSelectedResources(types);
  }

  function handleUseResource(resource: LearningResource, action: "path" | "start") {
    if (!selectedTask) return;
    if (action === "path") {
      void withBusy("path", "正在加入学习路径...", async () => {
        const task = await api.attachResourceToPath(selectedTask.id, resource.id);
        replaceTask(task);
        setPage("path");
        showToast(`已将「${resource.title}」加入当前阶段`);
      });
      return;
    }
    void withBusy("resource", "正在打开资源详情...", async () => {
      const fullResource = await api.getResource(selectedTask.id, resource.id);
      updateTaskLocal(selectedTask.id, (task) => ({
        ...task,
        resources: task.resources.map((item) => (item.id === fullResource.id ? fullResource : item))
      }));
      setSelectedResourceId(fullResource.id);
      setPage("resource-detail");
    });
  }

  async function handleUseRecommendedResource(resourceHint: string, stepId?: string) {
    if (!selectedTask) return;
    if (stepId) setPathBusyStep({ stepId, action: "use" });
    const matched = selectedTask.resources.find((resource) => resource.title === resourceHint || resource.type === resourceHint);
    if (matched) {
      await withBusy("resource", "正在打开推荐资源...", async () => {
        const fullResource = await api.getResource(selectedTask.id, matched.id);
        updateTaskLocal(selectedTask.id, (task) => ({
          ...task,
          resources: task.resources.map((item) => (item.id === fullResource.id ? fullResource : item))
        }));
        setSelectedResourceId(fullResource.id);
        setPage("resource-detail");
      });
      if (stepId) setPathBusyStep(null);
      return;
    }
    const type = inferResourceType(resourceHint);
    await withBusy("resource", "正在生成推荐资源...", async () => {
      const result = await api.generateResources(selectedTask.id, "selected", [type]);
      replaceTask(result.task);
      if (result.resources[0]) {
        setSelectedResourceId(result.resources[0].id);
        setPage("resource-detail");
      }
      showToast("推荐资源已生成");
    });
    if (stepId) setPathBusyStep(null);
  }

  async function handleSubmitExercise(resource: LearningResource, answers: Record<string, string>) {
    if (!selectedTask) return null;
    let resultPayload: any = null;
    await withBusy("exercise", "正在批改练习...", async () => {
      const result = await api.submitExercise(selectedTask.id, resource.id, answers);
      resultPayload = result.result;
      replaceTask(result.task);
      showToast(`练习已完成：${result.result.score} 分`);
    });
    return resultPayload;
  }

  async function handleMarkResourceMastery(resource: LearningResource, mastery: number) {
    if (!selectedTask) return;
    await withBusy("assessment", "正在更新掌握度...", async () => {
      const task = await api.markResourceMastery(selectedTask.id, resource.id, mastery);
      replaceTask(task);
      showToast(`已记录掌握度：${mastery}%`);
    });
  }

  async function handleAdjustPath() {
    if (!selectedTask) return;
    await withBusy("path", "正在调整学习路径...", async () => {
      const task = await api.adjustPath(selectedTask.id, "根据当前学习进度和最近反馈调整");
      replaceTask(task);
      showToast("学习路径已调整");
    });
  }

  async function handleCompleteStep(stepId: string) {
    if (!selectedTask) return;
    setPathBusyStep({ stepId, action: "complete" });
    await withBusy("path", "正在推进学习路径...", async () => {
      const task = await api.completePathStep(selectedTask.id, stepId);
      replaceTask(task);
      showToast("当前阶段已完成");
    });
    setPathBusyStep(null);
  }

  async function handleStartAssessment() {
    if (!selectedTask) return;
    await withBusy("assessment", "正在生成评估结果...", async () => {
      const task = await api.runAssessment(selectedTask.id);
      replaceTask(task);
      showToast("评估结果已更新");
    });
  }

  return (
    <AppLayout
      page={page}
      task={selectedTask}
      tasks={tasks}
      onPageChange={(nextPage) => {
        if (!selectedTask && nextPage !== "tasks") {
          showToast("请先创建学习任务");
          setPage("tasks");
          return;
        }
        setPage(nextPage);
      }}
      onTaskChange={setSelectedTaskId}
      onAssistantSend={handleSendMessage}
    >
      {page === "tasks" ? (
        <TasksPage
          tasks={tasks}
          selectedTask={selectedTask}
          loading={busyAction === "loading"}
          onSelectTask={setSelectedTaskId}
          onCreateTask={handleCreateTask}
          onDeleteTask={handleDeleteTask}
          onPageChange={setPage}
          onUploadMaterial={handleUploadMaterial}
          onSmartGenerateResource={() => handleGenerateResourceAndOpen()}
          onGenerateSelectedResources={handleGenerateSelectedResourcesAndOpen}
          isGeneratingResource={busyAction === "resource"}
          isUploadingMaterial={busyAction === "upload"}
        />
      ) : null}
      {selectedTask && page === "chat" ? (
        <ChatPage task={selectedTask} onSendMessage={handleSendMessage} isSending={busyAction === "chat"} />
      ) : null}
      {selectedTask && page === "profile" ? <ProfilePage task={selectedTask} /> : null}
      {selectedTask && page === "resources" ? (
        <ResourcesPage
          task={selectedTask}
          onUploadMaterial={handleUploadMaterial}
          onGenerateResource={handleGenerateResource}
          onGenerateSelectedResources={handleGenerateSelectedResources}
          onUseResource={handleUseResource}
          isGeneratingResource={busyAction === "resource"}
          isUploadingMaterial={busyAction === "upload"}
        />
      ) : null}
      {selectedTask && selectedResource && page === "resource-detail" ? (
        <ResourceDetailPage
          task={selectedTask}
          resource={selectedResource}
          onBack={() => setPage("resources")}
          onSubmitExercise={handleSubmitExercise}
          onMarkMastery={handleMarkResourceMastery}
          isSubmitting={busyAction === "exercise"}
        />
      ) : null}
      {selectedTask && page === "path" ? (
        <LearningPathPage
          task={selectedTask}
          onAdjustPath={handleAdjustPath}
          onGenerateResource={handleGenerateResourceAndOpen}
          onUseRecommendedResource={handleUseRecommendedResource}
          onStartAssessment={handleStartAssessment}
          onCompleteStep={handleCompleteStep}
          isAdjustingPath={busyAction === "path"}
          isAssessing={busyAction === "assessment"}
          isGeneratingResource={busyAction === "resource"}
          pathBusyStep={pathBusyStep}
        />
      ) : null}
      {selectedTask && page === "assessment" ? (
        <AssessmentPage
          task={selectedTask}
          onStartAssessment={handleStartAssessment}
          onGenerateResource={handleGenerateResourceAndOpen}
          isAssessing={busyAction === "assessment"}
        />
      ) : null}
      <Toast message={toast} />
    </AppLayout>
  );
}
