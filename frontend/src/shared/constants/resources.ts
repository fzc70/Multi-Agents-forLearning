import type { LearningResource } from "../types/task";

export const RESOURCE_TYPES: LearningResource["type"][] = [
  "讲解文档",
  "练习题",
  "思维导图",
  "拓展阅读",
  "代码案例",
  "知识图谱"
];

export const RESOURCE_FILTERS: Array<LearningResource["type"] | "全部"> = ["全部", ...RESOURCE_TYPES];

export const DEFAULT_SELECTED_RESOURCE_TYPES: LearningResource["type"][] = ["讲解文档", "练习题"];

export const RESOURCE_TYPE_REASONS: Record<LearningResource["type"], string> = {
  讲解文档: "适合先把概念、条件和方法讲清楚。",
  练习题: "适合马上验证是否真的掌握。",
  思维导图: "适合按层级整理学习脉络。",
  拓展阅读: "适合补充背景和迁移理解。",
  代码案例: "适合通过实操建立手感。",
  知识图谱: "适合查看概念之间的语义关系。"
};

export function inferResourceType(value: string): LearningResource["type"] {
  if (value.includes("练习") || value.includes("题") || value.includes("测评")) return "练习题";
  if (value.includes("图谱")) return "知识图谱";
  if (value.includes("导图")) return "思维导图";
  if (value.includes("阅读")) return "拓展阅读";
  if (value.includes("代码") || value.includes("实操")) return "代码案例";
  return "讲解文档";
}
