import type { LearningResource, LearningTask, NewTaskInput, SourceRef } from "../types/task";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

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

  sendMessage(taskId: string, message: string) {
    return request<{ task: LearningTask; reply: { id: string; role: "assistant"; content: string }; grounded: boolean; sourceRefs: SourceRef[] }>("/chat", {
      method: "POST",
      body: JSON.stringify({ taskId, message, useRag: true })
    });
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

  adjustPath(taskId: string, reason?: string) {
    return request<LearningTask>("/learning-path/adjust", {
      method: "POST",
      body: JSON.stringify({ taskId, reason })
    });
  },

  runAssessment(taskId: string) {
    return request<LearningTask>("/assessment/run", {
      method: "POST",
      body: JSON.stringify({ taskId, answers: [{ id: "quick-check", answer: "completed" }] })
    });
  }
};
