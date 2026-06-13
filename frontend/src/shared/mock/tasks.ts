import type { LearningTask } from "../types/task";

export const initialTasks: LearningTask[] = [
  {
    id: "writing",
    title: "提升议论文写作能力",
    category: "语文",
    progress: 42,
    updatedAt: "今天 09:20",
    nextAction: "完成一段中心论点训练",
    reason: "最近练习中观点容易分散，先练论点表达比直接写整篇作文更有效。",
    profileTags: ["基础中等", "偏好示例讲解", "薄弱点：论点明确性", "目标：作文提分"],
    materialsCount: 2,
    exerciseCount: 8,
    resources: [
      {
        id: "wr-r1",
        type: "讲解文档",
        title: "议论文中心论点表达模板",
        description: "用 4 个例句说明如何把观点写得集中。"
      },
      {
        id: "wr-r2",
        type: "练习题",
        title: "论点改写小练习",
        description: "把模糊观点改写为可论证观点。"
      }
    ],
    path: [
      {
        id: "wr-s1",
        title: "明确中心论点",
        objective: "能用一句话表达清楚自己的观点。",
        resource: "讲解文档",
        exercise: "改写 3 个模糊论点",
        status: "done"
      },
      {
        id: "wr-s2",
        title: "展开分论点",
        objective: "让每个分论点都服务中心论点。",
        resource: "思维导图",
        exercise: "补全一组分论点",
        status: "current"
      },
      {
        id: "wr-s3",
        title: "完成短段论证",
        objective: "用例证支撑观点，并保持不偏题。",
        resource: "示例讲解",
        exercise: "写一个 180 字论证段",
        status: "todo"
      }
    ],
    assessment: {
      score: 76,
      mastery: "基础稳定，论证展开仍需加强",
      weakPoints: ["论点不够集中", "例证和观点衔接弱"],
      mistakeTypes: ["观点泛化", "段落目标不清"],
      effort: "近 7 天完成 4 次练习",
      nextSuggestion: "先完成一段论证训练，再进入整篇作文。 ",
      tested: true
    },
    messages: [
      {
        id: "wr-m1",
        role: "assistant",
        content: "今天建议先练中心论点表达。我会先给你一个例子，再让你改写一段。"
      },
      {
        id: "wr-m2",
        role: "user",
        content: "我写作文经常写着写着偏题。"
      },
      {
        id: "wr-m3",
        role: "assistant",
        content: "可以先用一句话锁定观点，再检查每个分论点是否服务这个观点。"
      }
    ]
  },
  {
    id: "python",
    title: "掌握 Python 函数与循环",
    category: "编程",
    progress: 58,
    updatedAt: "昨天 21:10",
    nextAction: "完成函数参数与循环组合练习",
    reason: "你已经理解基础语法，下一步适合用小程序巩固函数拆分。",
    profileTags: ["基础入门", "偏好代码示例", "薄弱点：函数返回值", "目标：独立写小程序"],
    materialsCount: 1,
    exerciseCount: 12,
    resources: [
      {
        id: "py-r1",
        type: "代码案例",
        title: "成绩统计小程序",
        description: "用函数和循环完成平均分、最高分统计。"
      },
      {
        id: "py-r2",
        type: "练习题",
        title: "return 与 print 区分练习",
        description: "通过 5 道小题理解函数返回值。"
      }
    ],
    path: [
      {
        id: "py-s1",
        title: "复习循环语法",
        objective: "能使用 for 循环遍历列表。",
        resource: "讲解文档",
        exercise: "列表求和",
        status: "done"
      },
      {
        id: "py-s2",
        title: "理解函数参数",
        objective: "能把重复逻辑拆成函数。",
        resource: "代码案例",
        exercise: "封装统计函数",
        status: "current"
      },
      {
        id: "py-s3",
        title: "完成组合练习",
        objective: "能独立写一个小型统计程序。",
        resource: "综合练习",
        exercise: "成绩统计程序",
        status: "todo"
      }
    ],
    assessment: {
      score: 81,
      mastery: "语法掌握较好，函数设计还需练习",
      weakPoints: ["函数返回值", "循环边界条件"],
      mistakeTypes: ["把 print 当 return", "变量作用域混乱"],
      effort: "近 7 天完成 6 次练习",
      nextSuggestion: "先完成一个小型统计函数，再组合成完整程序。",
      tested: true
    },
    messages: [
      {
        id: "py-m1",
        role: "assistant",
        content: "今天可以用成绩统计例子，把 for 循环和函数放在一起练。"
      }
    ]
  },
  {
    id: "english",
    title: "英语四级阅读训练",
    category: "英语",
    progress: 35,
    updatedAt: "周二 18:40",
    nextAction: "训练题干关键词定位",
    reason: "当前主要问题是读得慢，先提升定位效率更合适。",
    profileTags: ["基础中等", "偏好题型训练", "薄弱点：长难句", "目标：阅读提速"],
    materialsCount: 3,
    exerciseCount: 18,
    resources: [
      {
        id: "en-r1",
        type: "练习题",
        title: "关键词定位训练",
        description: "用 6 道题练习题干定位和同义替换。"
      }
    ],
    path: [
      {
        id: "en-s1",
        title: "识别题干关键词",
        objective: "能快速找出题干中的定位词。",
        resource: "讲解文档",
        exercise: "关键词标注",
        status: "current"
      },
      {
        id: "en-s2",
        title: "定位原文信息",
        objective: "能在原文中找到同义表达。",
        resource: "练习题",
        exercise: "原文定位",
        status: "todo"
      },
      {
        id: "en-s3",
        title: "限时阅读",
        objective: "提高阅读速度和正确率。",
        resource: "阶段测验",
        exercise: "12 分钟阅读",
        status: "todo"
      }
    ],
    assessment: {
      score: 69,
      mastery: "基础可跟上，速度和长难句影响正确率",
      weakPoints: ["定位速度慢", "转折句理解不稳定"],
      mistakeTypes: ["忽略同义替换", "转折后重点误判"],
      effort: "近 7 天完成 3 次阅读训练",
      nextSuggestion: "先做短篇定位训练，再进入限时阅读。",
      tested: true
    },
    messages: []
  },
  {
    id: "math",
    title: "高等数学极限",
    category: "数学",
    progress: 27,
    updatedAt: "周一 10:05",
    nextAction: "整理三类常见极限方法",
    reason: "基础概念刚建立，先掌握方法选择比刷难题更稳。",
    profileTags: ["基础偏弱", "偏好步骤推导", "薄弱点：方法选择", "目标：会做基础题"],
    materialsCount: 1,
    exerciseCount: 6,
    resources: [],
    path: [
      {
        id: "ma-s1",
        title: "理解极限概念",
        objective: "知道极限描述的变化趋势。",
        resource: "讲解文档",
        exercise: "概念判断题",
        status: "done"
      },
      {
        id: "ma-s2",
        title: "掌握等价无穷小",
        objective: "能判断何时可以替换。",
        resource: "例题讲解",
        exercise: "等价替换练习",
        status: "current"
      },
      {
        id: "ma-s3",
        title: "选择解题方法",
        objective: "能区分等价替换和洛必达法则。",
        resource: "题型总结",
        exercise: "方法选择题",
        status: "todo"
      }
    ],
    assessment: {
      score: 62,
      mastery: "概念开始建立，题型选择仍不稳定",
      weakPoints: ["等价替换条件", "题型判断"],
      mistakeTypes: ["条件忽略", "公式套用过早"],
      effort: "近 7 天完成 2 次练习",
      nextSuggestion: "先做方法选择题，再进入综合题。",
      tested: true
    },
    messages: [
      {
        id: "ma-m1",
        role: "assistant",
        content: "今天先不刷难题，建议整理三类常见极限方法的使用条件。"
      }
    ]
  }
];
