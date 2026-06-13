export type PageKey = "tasks" | "chat" | "resources" | "path" | "assessment";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type LearningStep = {
  id: string;
  title: string;
  objective: string;
  resource: string;
  exercise: string;
  status: "done" | "current" | "todo";
};

export type LearningResource = {
  id: string;
  type: "讲解文档" | "练习题" | "思维导图" | "拓展阅读" | "视频脚本" | "代码案例" | "知识图谱";
  title: string;
  description: string;
};

export type Assessment = {
  score: number;
  mastery: string;
  weakPoints: string[];
  mistakeTypes: string[];
  effort: string;
  nextSuggestion: string;
  tested: boolean;
};

export type LearningTask = {
  id: string;
  title: string;
  category: string;
  progress: number;
  updatedAt: string;
  nextAction: string;
  reason: string;
  profileTags: string[];
  materialsCount: number;
  exerciseCount: number;
  resources: LearningResource[];
  path: LearningStep[];
  assessment: Assessment;
  messages: Message[];
  pathAdjustmentNote?: string;
};

export type NewTaskInput = {
  title: string;
  foundation?: string;
  expectedOutcome?: string;
};
