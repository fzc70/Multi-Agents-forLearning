import type { LearningResource, LearningTask, NewTaskInput, SourceRef } from "../types/task";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

function toCamelKey(value: string) {
  return value.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase());
}

function camelize<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => camelize(item)) as T;
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [toCamelKey(key), camelize(item)])
    ) as T;
  }
  return value;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: options?.body instanceof FormData
      ? options.headers
      : { "Content-Type": "application/json", ...(options?.headers ?? {}) }
  });

  if (!response.ok) {
    const text = await response.text();
    let message = "请求失败";
    try {
      const data = JSON.parse(text);
      message = data.detail?.message || data.detail || data.message || message;
    } catch {
      message = text || message;
    }
    throw new Error(typeof message === "string" ? message : "请求失败");
  }

  return response.json() as Promise<T>;
}

export const api = {
  listTasks() {
    return request<LearningTask[]>("/tasks");
  },

  createTask(input: NewTaskInput) {
    return request<LearningTask>("/tasks", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  deleteTask(taskId: string) {
    return request<{ ok: boolean }>(`/tasks/${encodeURIComponent(taskId)}`, {
      method: "DELETE"
    });
  },

  sendMessage(taskId: string, message: string) {
    return request<{ task: LearningTask; reply: { id: string; role: "assistant"; content: string }; grounded: boolean; sourceRefs: SourceRef[] }>("/chat", {
      method: "POST",
      body: JSON.stringify({ taskId, message, useRag: true })
    });
  },

  async streamMessage(
    taskId: string,
    message: string,
    handlers: {
      onStatus?: (message: string) => void;
      onDelta: (content: string) => void;
      onDone: (payload: { task: LearningTask }) => void;
    }
  ) {
    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId, message, useRag: true })
      });
      if (!response.ok || !response.body) {
        const text = await response.text();
        throw new Error(text || "对话请求失败");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.trim()) continue;
          let event: any;
          try {
            event = JSON.parse(line);
          } catch {
            continue;
          }
          if (event.type === "status") handlers.onStatus?.(event.message);
          if (event.type === "delta") handlers.onDelta(event.content);
          if (event.type === "done") handlers.onDone({ task: camelize(event.task) });
          if (event.type === "error") throw new Error(event.message);
        }
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "";
      if (message.toLowerCase().includes("network")) {
        throw new Error("对话连接中断，请确认后端正在运行，并稍后重试。");
      }
      throw new Error(message || "对话连接失败，请稍后重试。");
    }
  },

  uploadMaterial(taskId: string, file: File) {
    const form = new FormData();
    form.append("file", file);
    return request<LearningTask>(`/materials/upload?task_id=${encodeURIComponent(taskId)}`, {
      method: "POST",
      body: form
    });
  },

  generateResources(taskId: string, mode: "smart" | "selected", types?: LearningResource["type"][]) {
    return request<{ task: LearningTask; resources: LearningResource[] }>("/resources/generate", {
      method: "POST",
      body: JSON.stringify({ taskId, mode, types })
    });
  },

  attachResourceToPath(taskId: string, resourceId: string) {
    return request<LearningTask>(`/resources/${encodeURIComponent(resourceId)}/attach-to-path`, {
      method: "POST",
      body: JSON.stringify({ taskId })
    });
  },

  getResource(taskId: string, resourceId: string) {
    return request<LearningResource>(`/resources/${encodeURIComponent(resourceId)}?task_id=${encodeURIComponent(taskId)}`);
  },

  submitExercise(taskId: string, resourceId: string, answers: Record<string, string>) {
    return request<{ task: LearningTask; result: any }>(`/resources/${encodeURIComponent(resourceId)}/submit`, {
      method: "POST",
      body: JSON.stringify({ taskId, answers })
    });
  },

  markResourceMastery(taskId: string, resourceId: string, mastery: number, note?: string) {
    return request<LearningTask>(`/resources/${encodeURIComponent(resourceId)}/mastery`, {
      method: "POST",
      body: JSON.stringify({ taskId, mastery, note })
    });
  },

  adjustPath(taskId: string, reason?: string) {
    return request<LearningTask>("/learning-path/adjust", {
      method: "POST",
      body: JSON.stringify({ taskId, reason })
    });
  },

  completePathStep(taskId: string, stepId: string) {
    return request<LearningTask>("/learning-path/complete-step", {
      method: "POST",
      body: JSON.stringify({ taskId, stepId })
    });
  },

  runAssessment(taskId: string) {
    return request<LearningTask>("/assessment/run", {
      method: "POST",
      body: JSON.stringify({ taskId, answers: [{ id: "quick-check", answer: "completed" }] })
    });
  }
};
