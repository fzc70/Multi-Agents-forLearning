# 07. 前端模块架构

## 总体原则

- 页面组件只负责展示和交互。
- API 调用集中在 feature 的 `api/` 中。
- 复杂状态封装到 hooks。
- 复杂业务判断交给后端。
- 图谱、画像、路径等可视化组件只消费后端返回的结构化数据。

## 目录结构

```text
frontend/
  src/
    app/
      router.tsx
      layout.tsx
      providers.tsx

    shared/
      api/
        httpClient.ts
      components/
        Button.tsx
        Panel.tsx
        Loading.tsx
      hooks/
      types/
      utils/

    features/
      task/
        pages/TaskPage.tsx
        components/TaskList.tsx
        api/taskApi.ts
        hooks/useTasks.ts

      chat/
        pages/ChatPage.tsx
        components/ChatPanel.tsx
        components/MessageList.tsx
        api/chatApi.ts
        hooks/useChat.ts

      profile/
        pages/ProfilePage.tsx
        components/ProfileRadar.tsx
        components/ProfileDimensionCard.tsx
        components/ProfileEvidenceList.tsx
        api/profileApi.ts

      materials/
        pages/MaterialsPage.tsx
        components/PdfUploader.tsx
        components/MaterialList.tsx
        api/materialApi.ts

      resources/
        pages/ResourcesPage.tsx
        components/ResourceGeneratorPanel.tsx
        components/ResourceCard.tsx
        api/resourceApi.ts

      learning-path/
        pages/LearningPathPage.tsx
        components/LearningPathTimeline.tsx
        components/LearningStepCard.tsx
        api/learningPathApi.ts

      knowledge-graph/
        pages/KnowledgeGraphPage.tsx
        components/GraphCanvas.tsx
        components/GraphStats.tsx
        api/kgApi.ts

      assessment/
        pages/AssessmentPage.tsx
        components/AssessmentReport.tsx
        components/WeakPointList.tsx
        api/assessmentApi.ts

      recommendation/
        components/RecommendationPanel.tsx
        api/recommendationApi.ts
```

## 模块说明

### task

功能：

- 创建任务
- 切换任务
- 查看任务状态

### chat

功能：

- 发送消息
- 显示 AI 回答
- 显示来源引用
- 显示画像更新提示
- 可选 SSE 流式输出

### profile

功能：

- 展示学生画像维度
- 展示画像 evidence
- 展示画像版本

可视化：

```text
雷达图
维度卡片
证据列表
更新时间线
```

### materials

功能：

- 上传 PDF
- 查看解析状态
- 查看页数、切片数

### resources

功能：

- 选择资源类型
- 触发资源生成
- 展示文档、题目、思维导图、阅读、视频脚本、代码案例

### learning-path

功能：

- 展示学习路径时间线
- 展示当前阶段
- 展示推荐资源和练习
- 显示评估节点

### knowledge-graph

功能：

- 触发图谱生成
- 展示节点/边数量
- 使用 `vis-network` 渲染图谱
- 右侧展示关系列表和图谱摘要

### assessment

功能：

- 展示掌握度
- 展示薄弱点
- 展示错因模式
- 展示下一步建议

### recommendation

功能：

- 展示推荐资源
- 展示推荐理由
- 标注匹配画像维度

