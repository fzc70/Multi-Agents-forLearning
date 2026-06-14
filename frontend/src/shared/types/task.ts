export type PageKey = "tasks" | "profile" | "chat" | "resources" | "resource-detail" | "path" | "assessment";

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
  type: "讲解文档" | "练习题" | "思维导图" | "拓展阅读" | "代码案例" | "知识图谱";
  title: string;
  description: string;
  content?: string;
  detail?: Record<string, any>;
  recommendationReason?: string;
  sourceRefs?: SourceRef[];
  createdAt?: string;
};

export type SourceRef = {
  type: string;
  id: string;
  title?: string;
  page?: number;
  chunkId?: string;
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

export type ProfileDimension = {
  id: string;
  label: string;
  value: string;
  confidence: number;
  evidence: string;
  updatedAt: string;
};

export type StudentProfile = {
  summary: string;
  dimensions: ProfileDimension[];
  recentEvidences: string[];
};

export type LearningMaterial = {
  id: string;
  name: string;
  type: "PDF" | "文档" | "网页" | "笔记";
  size: string;
  status: "已解析" | "解析中" | "待处理";
  textLength: number;
  usedFor: string[];
  updatedAt: string;
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
  profile?: StudentProfile;
  materials?: LearningMaterial[];
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
