import { useMemo, useRef, useState } from "react";
import { AppLayout } from "./layout/AppLayout";
import { initialTasks } from "../shared/mock/tasks";
import type { LearningResource, LearningTask, NewTaskInput, PageKey } from "../shared/types/task";
import { Toast } from "../shared/components/Toast";
import { AssessmentPage } from "../features/assessment/AssessmentPage";
import { ChatPage } from "../features/chat/ChatPage";
import { LearningPathPage } from "../features/learning-path/LearningPathPage";
import { ResourcesPage } from "../features/resources/ResourcesPage";
import { TasksPage } from "../features/tasks/TasksPage";

const resourceDefaults: LearningResource["type"][] = ["讲解文档", "练习题", "思维导图", "拓展阅读"];
type BusyAction = "resource" | "path" | "assessment" | null;

function makeId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 7)}`;
}

function makeAssistantReply(task: LearningTask) {
  return `好的。围绕“${task.title}”，建议先完成“${task.nextAction}”。如果你愿意，我可以继续给你拆成一个 10 分钟内能完成的小练习。`;
}

function createTask(input: NewTaskInput): LearningTask {
  const title = input.title.trim();
  return {
    id: makeId("task"),
    title,
    category: "自定义",
    progress: 0,
    updatedAt: "刚刚",
    nextAction: input.expectedOutcome || "先通过对话明确目标和当前基础",
    reason: input.foundation
      ? `你提到当前基础是“${input.foundation}”，建议先从小目标开始。`
      : "新任务已创建，建议先用几轮对话明确目标、基础和偏好。",
    profileTags: ["新任务", "画像待完善", "资料可选", input.foundation || "基础待了解"],
    materialsCount: 0,
    exerciseCount: 0,
    resources: [],
    path: [
      {
        id: makeId("step"),
        title: "明确学习目标",
        objective: "把目标拆成可执行的小步骤。",
        resource: "对话澄清",
        exercise: "回答 3 个目标问题",
        status: "current"
      },
      {
        id: makeId("step"),
        title: "评估当前基础",
        objective: "了解已经掌握什么、卡在哪里。",
        resource: "小测评",
        exercise: "完成一次基础测评",
        status: "todo"
      },
      {
        id: makeId("step"),
        title: "生成学习资源",
        objective: "围绕当前薄弱点生成资料和练习。",
        resource: "个性化资源",
        exercise: "完成第一组练习",
        status: "todo"
      }
    ],
    assessment: {
      score: 0,
      mastery: "暂未评估",
      weakPoints: [],
      mistakeTypes: [],
      effort: "暂无记录",
      nextSuggestion: "先完成一次小测评，建立初始学习画像。",
      tested: false
    },
    messages: [
      {
        id: makeId("msg"),
        role: "assistant",
        content: `新任务已创建。你可以先告诉我：学习“${title}”的目标、当前基础和希望多久看到效果。`
      }
    ]
  };
}

export default function App() {
  const [page, setPage] = useState<PageKey>("tasks");
  const [tasks, setTasks] = useState<LearningTask[]>(initialTasks);
  const [selectedTaskId, setSelectedTaskId] = useState(initialTasks[0]?.id ?? "");
  const [toast, setToast] = useState("");
  const [busyAction, setBusyAction] = useState<BusyAction>(null);
  const toastTimerRef = useRef<number | null>(null);

  const selectedTask = useMemo(() => {
    return tasks.find((task) => task.id === selectedTaskId) ?? tasks[0];
  }, [selectedTaskId, tasks]);

  function showToast(message: string) {
    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current);
    }
    setToast(message);
    toastTimerRef.current = window.setTimeout(() => setToast(""), 1800);
  }

  function updateTask(taskId: string, updater: (task: LearningTask) => LearningTask) {
    setTasks((current) => current.map((task) => (task.id === taskId ? updater(task) : task)));
  }

  function runBusy(action: Exclude<BusyAction, null>, pendingMessage: string, done: () => void) {
    if (busyAction) {
      showToast("上一个操作还在处理中");
      return;
    }
    setBusyAction(action);
    showToast(pendingMessage);
    window.setTimeout(() => {
      done();
      setBusyAction(null);
    }, 700);
  }

  function handleCreateTask(input: NewTaskInput) {
    const task = createTask(input);
    setTasks((current) => [task, ...current]);
    setSelectedTaskId(task.id);
    showToast("学习任务已创建");
  }

  function handleSendMessage(message: string) {
    if (!selectedTask) return;
    updateTask(selectedTask.id, (task) => ({
      ...task,
      updatedAt: "刚刚",
      messages: [
        ...task.messages,
        { id: makeId("msg"), role: "user", content: message },
        { id: makeId("msg"), role: "assistant", content: makeAssistantReply(task) }
      ]
    }));
    showToast("已发送");
  }

  function handleGenerateResource(type?: LearningResource["type"]) {
    if (!selectedTask) return;
    const resourceType = type ?? resourceDefaults[selectedTask.resources.length % resourceDefaults.length];
    runBusy("resource", "正在生成学习资源...", () => {
      updateTask(selectedTask.id, (task) => ({
        ...task,
        updatedAt: "刚刚",
        resources: [
          {
            id: makeId("res"),
            type: resourceType,
            title: `${task.title} · ${resourceType}`,
            description: `根据当前任务和下一步建议生成，重点服务“${task.nextAction}”。`
          },
          ...task.resources
        ]
      }));
      showToast("已生成 1 个学习资源");
    });
  }

  function handleGenerateSelectedResources(types: LearningResource["type"][]) {
    if (!selectedTask || types.length === 0) return;
    runBusy("resource", "正在生成所选资源...", () => {
      updateTask(selectedTask.id, (task) => ({
        ...task,
        updatedAt: "刚刚",
        resources: [
          ...types.map((type) => ({
            id: makeId("res"),
            type,
            title: `${task.title} · ${type}`,
            description: `由你指定生成，重点服务“${task.nextAction}”。`
          })),
          ...task.resources
        ]
      }));
      showToast(`已生成 ${types.length} 个学习资源`);
    });
  }

  function handleUseResource(resource: LearningResource, action: "path" | "start") {
    if (action === "path") {
      showToast(`已将「${resource.title}」加入学习路径`);
      return;
    }
    showToast(`开始使用「${resource.title}」`);
  }

  function handleAdjustPath() {
    if (!selectedTask) return;
    runBusy("path", "正在调整学习路径...", () => {
      updateTask(selectedTask.id, (task) => ({
        ...task,
        updatedAt: "刚刚",
        path: task.path.map((step, index) => ({
          ...step,
          status: index === 0 ? "done" : index === 1 ? "current" : "todo"
        })),
        nextAction: task.path[1]?.title ? `继续完成：${task.path[1].title}` : task.nextAction,
        pathAdjustmentNote:
          "已根据当前进度、最近练习表现和薄弱点重新确认优先级：保留已完成阶段，将当前阶段聚焦到最影响学习效果的一步。"
      }));
      showToast("学习路径已调整");
    });
  }

  function handleStartAssessment() {
    if (!selectedTask) return;
    runBusy("assessment", "正在分析测评结果...", () => {
      updateTask(selectedTask.id, (task) => ({
        ...task,
        updatedAt: "刚刚",
        progress: Math.min(100, task.progress + 4),
        exerciseCount: task.exerciseCount + 1,
        assessment: {
          ...task.assessment,
          tested: true,
          score: Math.min(100, Math.max(62, task.assessment.score + 3)),
          mastery: task.assessment.mastery === "暂未评估" ? "已完成初始测评，建议继续小步练习" : task.assessment.mastery,
          weakPoints: task.assessment.weakPoints.length ? task.assessment.weakPoints : ["基础概念不够稳定", "方法选择需要练习"],
          mistakeTypes: task.assessment.mistakeTypes.length ? task.assessment.mistakeTypes : ["步骤遗漏", "理解不完整"],
          effort: "刚完成 1 次测评",
          nextSuggestion: `建议继续完成“${task.nextAction}”，再复盘错误原因。`
        }
      }));
      showToast("测评结果已更新");
    });
  }

  function handleContextAction() {
    if (page === "resources") handleGenerateResource();
    if (page === "path") handleAdjustPath();
    if (page === "assessment") handleStartAssessment();
    if (page === "chat") showToast("可以在对话框继续提问");
  }

  if (!selectedTask) {
    return (
      <AppLayout
        page="tasks"
        task={createTask({ title: "新学习任务" })}
        tasks={[]}
        onPageChange={setPage}
        onTaskChange={setSelectedTaskId}
        onContextAction={handleContextAction}
        onAssistantSend={handleSendMessage}
        busyAction={busyAction}
      >
        <TasksPage
          tasks={[]}
          selectedTask={createTask({ title: "新学习任务" })}
          onSelectTask={setSelectedTaskId}
          onCreateTask={handleCreateTask}
          onPageChange={setPage}
          onSmartGenerateResource={() => handleGenerateResource()}
          onGenerateSelectedResources={handleGenerateSelectedResources}
          isGeneratingResource={busyAction === "resource"}
        />
      </AppLayout>
    );
  }

  return (
    <AppLayout
      page={page}
      task={selectedTask}
      tasks={tasks}
      onPageChange={setPage}
      onTaskChange={setSelectedTaskId}
      onContextAction={handleContextAction}
      onAssistantSend={handleSendMessage}
      busyAction={busyAction}
    >
      {page === "tasks" ? (
        <TasksPage
          tasks={tasks}
          selectedTask={selectedTask}
          onSelectTask={setSelectedTaskId}
          onCreateTask={handleCreateTask}
          onPageChange={setPage}
          onSmartGenerateResource={() => handleGenerateResource()}
          onGenerateSelectedResources={handleGenerateSelectedResources}
          isGeneratingResource={busyAction === "resource"}
        />
      ) : null}
      {page === "chat" ? <ChatPage task={selectedTask} onSendMessage={handleSendMessage} /> : null}
      {page === "resources" ? (
        <ResourcesPage
          task={selectedTask}
          onGenerateResource={handleGenerateResource}
          onGenerateSelectedResources={handleGenerateSelectedResources}
          onUseResource={handleUseResource}
          isGeneratingResource={busyAction === "resource"}
        />
      ) : null}
      {page === "path" ? (
        <LearningPathPage
          task={selectedTask}
          onGenerateResource={handleGenerateResource}
          onStartAssessment={handleStartAssessment}
          isAdjustingPath={busyAction === "path"}
          isAssessing={busyAction === "assessment"}
          isGeneratingResource={busyAction === "resource"}
        />
      ) : null}
      {page === "assessment" ? (
        <AssessmentPage
          task={selectedTask}
          onStartAssessment={handleStartAssessment}
          onGenerateResource={handleGenerateResource}
          isAssessing={busyAction === "assessment"}
        />
      ) : null}
      <Toast message={toast} />
    </AppLayout>
  );
}
