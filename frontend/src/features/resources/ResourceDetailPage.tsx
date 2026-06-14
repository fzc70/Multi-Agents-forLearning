import { AlertTriangle, ArrowLeft, BookOpen, CheckCircle2, Code2, Lightbulb, ListChecks, Network as NetworkIcon, Send } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";

type ResourceDetailPageProps = {
  task: LearningTask;
  resource: LearningResource;
  onBack: () => void;
  onSubmitExercise: (resource: LearningResource, answers: Record<string, string>) => Promise<any>;
  onMarkMastery: (resource: LearningResource, mastery: number) => Promise<void>;
  isSubmitting: boolean;
};

export function ResourceDetailPage({ task, resource, onBack, onSubmitExercise, onMarkMastery, isSubmitting }: ResourceDetailPageProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const detail = resource.detail ?? {};

  async function submit(event: FormEvent) {
    event.preventDefault();
    const nextResult = await onSubmitExercise(resource, answers);
    setResult(nextResult);
  }

  return (
    <div className="space-y-5">
      <header className="rounded-[16px] border border-slate-200 bg-white p-5">
        <Button variant="ghost" icon={<ArrowLeft size={16} />} onClick={onBack}>
          返回资源库
        </Button>
        <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium text-amber-700">{resource.type}</p>
            <h1 className="mt-1 text-2xl font-semibold text-ink">{resource.title}</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{resource.description}</p>
          </div>
          <div className="rounded-ui border border-amber-100 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800">
            {resource.recommendationReason || `围绕当前任务“${task.title}”生成`}
          </div>
        </div>
      </header>

      {resource.type === "练习题" ? (
        <form className="space-y-4" onSubmit={submit}>
          <section className="rounded-[16px] border border-slate-200 bg-white p-5">
            <h2 className="section-title">开始练习</h2>
            <p className="mt-2 text-sm text-muted">{String(detail.instructions ?? "完成题目后提交答案。")}</p>
            <div className="mt-5 space-y-4">
              {Array.isArray(detail.questions) && detail.questions.length > 0 ? detail.questions.map((question: any, index: number) => (
                <article key={question.id ?? index} className="rounded-[14px] border border-line bg-slate-50/70 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-semibold leading-6 text-ink">
                      {index + 1}. {question.stem ?? question.question ?? question.title ?? "练习题"}
                    </h3>
                    <span className="rounded-full bg-white px-2 py-1 text-xs text-muted">{question.difficulty ?? "基础"}</span>
                  </div>
                  {Array.isArray(question.options) && question.options.length > 0 ? (
                    <div className="mt-3 grid gap-2 md:grid-cols-2">
                          {question.options.map((option: string, optionIndex: number) => {
                            const value = String.fromCharCode(65 + optionIndex);
                            const cleanOption = option.replace(/^[A-Da-d][.、\s]+/, "");
                            return (
                          <label key={option} className="flex cursor-pointer gap-2 rounded-ui border border-line bg-white px-3 py-2 text-sm">
                            <input
                              type="radio"
                              name={question.id}
                              value={value}
                              checked={answers[question.id] === value}
                              onChange={() => setAnswers((current) => ({ ...current, [question.id]: value }))}
                            />
                            <span>{value}. {cleanOption}</span>
                          </label>
                        );
                      })}
                    </div>
                  ) : (
                    <textarea
                      className="focus-ring mt-3 min-h-24 w-full rounded-ui border border-line bg-white px-3 py-2 text-sm"
                      value={answers[question.id] ?? ""}
                      onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))}
                      placeholder="写下你的答案"
                    />
                  )}
                </article>
              )) : (
                <MissingDetail message="这份练习题缺少可作答题目，系统会在重新打开或重新生成时补齐。" />
              )}
            </div>
            <div className="mt-5 flex justify-start">
              <Button variant="primary" icon={<Send size={16} />} loading={isSubmitting}>
                提交答案
              </Button>
            </div>
          </section>
          {result ? <ExerciseResult result={result} /> : null}
        </form>
      ) : null}

      {resource.type === "讲解文档" ? <LectureDocument detail={detail} content={resource.content} title={resource.title} /> : null}
      {resource.type === "思维导图" ? <MindmapResource detail={detail} /> : null}
      {resource.type === "知识图谱" ? <GraphResource title="知识图谱" detail={detail} /> : null}
      {resource.type === "拓展阅读" ? <ReadingResource detail={detail} /> : null}
      {resource.type === "代码案例" ? <CodePractice detail={detail} /> : null}
      {resource.type !== "练习题" ? <MasteryFeedback resource={resource} onMarkMastery={onMarkMastery} /> : null}
    </div>
  );
}

function LectureDocument({ detail, content, title }: { detail: Record<string, any>; content?: string; title: string }) {
  const sections = normalizeLectureSections(detail, content, title);
  return (
    <section className="grid gap-5 lg:grid-cols-[240px_1fr]">
      <aside className="h-fit rounded-[16px] border border-slate-200 bg-white p-4">
        <div className="flex items-center gap-2">
          <BookOpen size={18} className="text-emerald-700" />
          <h2 className="section-title">阅读导航</h2>
        </div>
        <div className="mt-4 space-y-2">
          {sections.map((section, index) => (
            <a key={`${section.heading}-${index}`} href={`#lecture-${index}`} className="block rounded-ui px-3 py-2 text-sm text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-800">
              {index + 1}. {section.heading}
            </a>
          ))}
        </div>
        {Array.isArray(detail.key_points) && detail.key_points.length ? (
          <div className="mt-5 border-t border-line pt-4">
            <p className="text-xs font-medium text-muted">关键词</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {detail.key_points.slice(0, 8).map((item: string) => (
                <span key={item} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700">{item}</span>
              ))}
            </div>
          </div>
        ) : null}
      </aside>
      <div className="space-y-4">
        {sections.length ? sections.map((section, index) => (
          <article id={`lecture-${index}`} key={`${section.heading}-${index}`} className="rounded-[16px] border border-slate-200 bg-white p-5">
            <div className="flex items-start gap-3">
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-emerald-50 text-sm font-semibold text-emerald-800">{index + 1}</span>
              <div>
                <h2 className="text-xl font-semibold text-ink">{section.heading}</h2>
                <p className="mt-2 text-sm leading-7 text-slate-700">{section.overview}</p>
              </div>
            </div>
            {section.steps.length ? (
              <div className="mt-4 rounded-ui border border-slate-100 bg-slate-50/70 p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
                  <ListChecks size={16} className="text-emerald-700" />
                  学习步骤
                </div>
                <ol className="space-y-2 pl-1 text-sm leading-6 text-slate-700">
                  {section.steps.map((item, stepIndex) => (
                    <li key={`${item}-${stepIndex}`} className="grid grid-cols-[24px_1fr] gap-2">
                      <span className="mt-0.5 grid h-5 w-5 place-items-center rounded-full bg-white text-xs text-emerald-800">{stepIndex + 1}</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ol>
              </div>
            ) : null}
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <InfoBlock icon={<Lightbulb size={16} />} title="理解要点" items={section.keyPoints} tone="green" />
              <InfoBlock icon={<AlertTriangle size={16} />} title="易错提醒" items={section.warnings} tone="amber" />
            </div>
          </article>
        )) : <MissingDetail message="这份讲解文档缺少正文内容，请返回资源库重新生成。" />}
        {Array.isArray(detail.checkpoints) ? (
          <div className="rounded-[16px] border border-emerald-100 bg-emerald-50/70 p-5">
            <h3 className="text-sm font-semibold text-ink">学完自检</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {detail.checkpoints.map((item: string) => (
                <span key={item} className="rounded-full bg-white px-3 py-1 text-xs text-emerald-800">{item}</span>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function InfoBlock({ icon, title, items, tone }: { icon: ReactNode; title: string; items: string[]; tone: "green" | "amber" }) {
  const color = tone === "green" ? "border-emerald-100 bg-emerald-50/70 text-emerald-800" : "border-amber-100 bg-amber-50/70 text-amber-800";
  return (
    <div className={`rounded-ui border p-4 ${color}`}>
      <div className="flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </div>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
        {items.map((item, index) => <li key={`${item}-${index}`}>• {item}</li>)}
      </ul>
    </div>
  );
}

function normalizeLectureSections(detail: Record<string, any>, content: string | undefined, title: string) {
  const rawSections = Array.isArray(detail.sections) && detail.sections.length
    ? detail.sections
    : splitContentIntoSections(content, title);
  return rawSections.map((section: any, index: number) => {
    const heading = String(section.heading || section.title || `第 ${index + 1} 节`).trim();
    const body = String(section.body || section.content || section.text || "").replace(/\s+/g, " ").trim();
    const sentences = splitSentences(body);
    return {
      heading,
      overview: sentences.slice(0, 2).join(" ") || body || "本节用于建立基本理解。",
      steps: extractStepLike(sentences).slice(0, 5),
      keyPoints: extractKeyPoints(sentences, heading).slice(0, 4),
      warnings: extractWarnings(sentences).slice(0, 3),
    };
  });
}

function splitContentIntoSections(content: string | undefined, title: string) {
  const text = String(content || "").trim();
  if (!text) return [];
  const markdownParts = text.split(/\n(?=##\s+)/).map((part) => part.trim()).filter(Boolean);
  if (markdownParts.length > 1) {
    return markdownParts.map((part) => {
      const lines = part.split(/\n+/);
      return { heading: lines[0].replace(/^##\s*/, "").trim(), body: lines.slice(1).join(" ") };
    });
  }
  const paragraphs = text.split(/\n{2,}/).map((item) => item.trim()).filter(Boolean);
  return paragraphs.map((paragraph, index) => ({
    heading: index === 0 ? title : `补充说明 ${index + 1}`,
    body: paragraph,
  }));
}

function splitSentences(text: string) {
  return text
    .split(/(?<=[。！？；;])\s*/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function extractStepLike(sentences: string[]) {
  const stepWords = ["第一", "第二", "第三", "第四", "步骤", "先", "再", "然后", "最后"];
  const matched = sentences.filter((item) => stepWords.some((word) => item.includes(word)));
  return matched.length ? matched : sentences.slice(1, 5);
}

function extractKeyPoints(sentences: string[], heading: string) {
  const matched = sentences.filter((item) => ["核心", "概念", "关键", "理论", "方法", "例"].some((word) => item.includes(word)));
  return matched.length ? matched : [`理解“${heading}”解决的问题`, "明确适用条件和操作边界", "能用自己的例子复述"];
}

function extractWarnings(sentences: string[]) {
  const matched = sentences.filter((item) => ["易错", "错误", "注意", "不能", "不要", "混淆"].some((word) => item.includes(word)));
  return matched.length ? matched : ["不要只背结论，要能说明条件和步骤", "做题后必须复盘错因，而不是只看答案"];
}

function GraphResource({ title, detail }: { title: string; detail: Record<string, any> }) {
  const nodes = Array.isArray(detail.nodes) ? detail.nodes : [];
  const edges = Array.isArray(detail.edges) ? detail.edges : [];
  return (
    <section className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <div className="rounded-[16px] border border-slate-200 bg-white p-5">
        <h2 className="section-title">{title}</h2>
        {nodes.length ? <VisGraph nodes={nodes} edges={edges} /> : <MissingDetail message={`${title}缺少节点，系统需要重新生成结构化图谱。`} />}
      </div>
      <aside className="rounded-[16px] border border-slate-200 bg-white p-5">
        <div className="flex items-center gap-2">
          <NetworkIcon size={18} className="text-emerald-700" />
          <h3 className="section-title">关系</h3>
        </div>
        <div className="mt-4 space-y-2">
          {edges.length ? edges.map((edge: any, index: number) => {
            const source = nodes.find((node: any) => node.id === edge.source)?.label ?? edge.source;
            const target = nodes.find((node: any) => node.id === edge.target)?.label ?? edge.target;
            return (
              <div key={`${edge.source}-${edge.target}-${index}`} className="rounded-ui bg-slate-50 px-3 py-2 text-sm text-slate-700">
                {source} <span className="text-muted">- {edge.label} -</span> {target}
              </div>
            );
          }) : <MissingDetail message="暂无可展示关系。" />}
        </div>
      </aside>
    </section>
  );
}

function MindmapResource({ detail }: { detail: Record<string, any> }) {
  const nodes = Array.isArray(detail.nodes) ? detail.nodes : [];
  const centerId = String(detail.center_id || nodes.find((node: any) => Number(node.level) === 0)?.id || nodes[0]?.id || "");
  const center = nodes.find((node: any) => String(node.id) === centerId) ?? nodes[0];
  const branches = buildLearningMindmapBranches(nodes, center?.id);

  return (
    <section className="rounded-[16px] border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="section-title">思维导图</h2>
          <p className="mt-2 text-sm text-muted">按“主题、分支、子知识点”组织，用来快速复习知识结构。</p>
        </div>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-800">层级提纲</span>
      </div>
      {nodes.length ? (
        <div className="mt-6 overflow-x-auto rounded-[16px] border border-emerald-100 bg-[#fbfaf7] p-5">
          <div className="min-w-[720px]">
            <div className="mx-auto w-fit rounded-[18px] border border-emerald-200 bg-emerald-700 px-6 py-4 text-center text-base font-semibold text-white shadow-sm">
              {center?.label || detail.center || "中心主题"}
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {branches.map((branch) => (
                <article key={branch.id} className="rounded-[16px] border border-slate-200 bg-white p-4">
                  <div className="flex items-start gap-3">
                    <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500" />
                    <div>
                      <h3 className="font-semibold text-ink">{branch.label}</h3>
                      {branch.relation ? <p className="mt-1 text-xs text-emerald-700">{branch.relation}</p> : null}
                    </div>
                  </div>
                  <div className="mt-3 space-y-2 border-l border-dashed border-emerald-200 pl-4">
                    {branch.children.length ? branch.children.map((child) => (
                      <div key={child.id} className="rounded-ui bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-700">
                        <span className="font-medium text-slate-900">{child.label}</span>
                        {child.relation ? <span className="ml-2 text-xs text-muted">({child.relation})</span> : null}
                      </div>
                    )) : (
                      <div className="rounded-ui bg-slate-50 px-3 py-2 text-sm text-muted">暂无子知识点</div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      ) : <MissingDetail message="思维导图缺少层级节点，请返回资源库重新生成。" />}
    </section>
  );
}

function buildLearningMindmapBranches(nodes: any[], centerId: string) {
  const buckets = [
    { id: "concept", label: "基础概念", relation: "先理解", keywords: ["概念", "定义", "基础", "前置", "知识", "逻辑", "推理"], children: [] as any[] },
    { id: "method", label: "方法步骤", relation: "再掌握", keywords: ["方法", "步骤", "算法", "合一", "归结", "转换", "证明", "规则"], children: [] as any[] },
    { id: "case", label: "典型应用", relation: "用例子验证", keywords: ["例", "题", "应用", "场景", "资源", "练习"], children: [] as any[] },
    { id: "review", label: "易错复盘", relation: "最后复盘", keywords: ["错", "误区", "薄弱", "条件", "限制", "自检"], children: [] as any[] },
  ];
  nodes
    .filter((node) => String(node.id) !== String(centerId))
    .forEach((node) => {
      const label = String(node.label || "");
      const type = String(node.type || "");
      const text = `${label}${type}`;
      const bucket = buckets.find((item) => item.keywords.some((word) => text.includes(word))) ?? buckets[0];
      if (!bucket.children.some((child) => child.label === label)) {
        bucket.children.push({ id: String(node.id), label, relation: type || "知识点" });
      }
    });
  return buckets
    .map((bucket) => ({
      id: bucket.id,
      label: bucket.label,
      relation: bucket.relation,
      children: bucket.children.slice(0, 5),
    }))
    .filter((bucket) => bucket.children.length > 0);
}

function VisGraph({ nodes, edges }: { nodes: any[]; edges: any[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    let destroyed = false;
    let network: any = null;
    void import("vis-network/standalone").then(({ DataSet, Network }) => {
      if (destroyed || !containerRef.current) return;
      const nodeSet = new DataSet(
        nodes.map((node, index) => ({
          id: node.id,
          label: node.label,
          shape: index === 0 ? "box" : "dot",
          color: index === 0
            ? { background: "#047857", border: "#065f46", color: "#ffffff" }
            : { background: "#ecfdf5", border: "#a7f3d0", color: "#064e3b" },
          font: { color: index === 0 ? "#ffffff" : "#0f172a", size: index === 0 ? 17 : 14 },
        }))
      );
      const edgeSet = new DataSet(
        edges.map((edge, index) => ({
          id: `${edge.source}-${edge.target}-${index}`,
          from: edge.source,
          to: edge.target,
          label: edge.label,
          arrows: "to",
          color: { color: "#94a3b8", highlight: "#047857" },
          font: { size: 12, color: "#475569", background: "rgba(255,255,255,0.85)" },
        }))
      );
      network = new Network(
        containerRef.current,
        { nodes: nodeSet, edges: edgeSet },
        {
          interaction: { hover: true, zoomView: true, dragView: true },
          physics: { stabilization: { iterations: 80, fit: true }, barnesHut: { springLength: 120, avoidOverlap: 0.35 } },
          nodes: { borderWidth: 1.5, shadow: false },
          edges: { smooth: { enabled: true, type: "dynamic", roundness: 0.35 } },
        }
      );
      network.once("stabilizationIterationsDone", () => {
        network?.setOptions({ physics: false });
        network?.fit({ animation: false });
      });
    });
    return () => {
      destroyed = true;
      network?.destroy();
    };
  }, [nodes, edges]);

  return <div ref={containerRef} className="mt-5 h-[430px] rounded-[14px] border border-line bg-[#fbfaf7]" />;
}

function ReadingResource({ detail }: { detail: Record<string, any> }) {
  return (
    <section className="rounded-[16px] border border-slate-200 bg-white p-6">
      <h2 className="section-title">拓展阅读安排</h2>
      <p className="mt-3 text-sm leading-7 text-muted">{detail.summary}</p>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {Array.isArray(detail.readings) && detail.readings.length > 0 ? detail.readings.map((item: any) => (
          <article key={item.title} className="rounded-[14px] border border-line bg-slate-50 p-4">
            <h3 className="font-semibold text-ink">{item.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{item.reason}</p>
            <p className="mt-3 text-xs text-amber-700">约 {item.estimated_minutes ?? 8} 分钟</p>
          </article>
        )) : <MissingDetail message="拓展阅读列表为空，请返回资源库重新生成。" />}
      </div>
      {Array.isArray(detail.guiding_questions) ? (
        <div className="mt-5 rounded-ui border border-amber-100 bg-amber-50/70 p-4">
          <h3 className="text-sm font-semibold text-ink">阅读时关注</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {detail.guiding_questions.map((item: string) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      ) : null}
    </section>
  );
}

function MissingDetail({ message }: { message: string }) {
  return (
    <div className="rounded-ui border border-amber-100 bg-amber-50/80 p-4 text-sm leading-6 text-amber-800">
      {message}
    </div>
  );
}

function MasteryFeedback({ resource, onMarkMastery }: { resource: LearningResource; onMarkMastery: (resource: LearningResource, mastery: number) => Promise<void> }) {
  return (
    <section className="rounded-[16px] border border-emerald-100 bg-emerald-50/70 p-5">
      <h2 className="section-title">这份资源掌握得怎么样？</h2>
      <p className="mt-2 text-sm text-muted">你的反馈会更新画像、评估和学习路径。</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {[60, 80, 100].map((value) => (
          <Button key={value} onClick={() => onMarkMastery(resource, value)}>
            掌握 {value}%
          </Button>
        ))}
      </div>
    </section>
  );
}

function CodePractice({ detail }: { detail: Record<string, any> }) {
  return (
    <section className="grid gap-5 lg:grid-cols-[1fr_1fr]">
      <div className="rounded-[16px] border border-slate-200 bg-white p-5">
        <div className="flex items-center gap-2">
          <Code2 size={18} className="text-emerald-700" />
          <h2 className="section-title">实操任务</h2>
        </div>
        <p className="mt-3 text-sm leading-6 text-muted">{detail.scenario}</p>
        <div className="mt-4 space-y-2">
          {(detail.tasks ?? []).map((item: string) => (
            <div key={item} className="flex gap-2 rounded-ui bg-slate-50 px-3 py-2 text-sm">
              <CheckCircle2 size={16} className="mt-0.5 text-emerald-700" />
              {item}
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-[16px] border border-slate-200 bg-white p-5">
        <h2 className="section-title">起始代码</h2>
        <pre className="mt-4 overflow-auto rounded-ui border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-800">
          <code>{detail.starter_code}</code>
        </pre>
        <h3 className="mt-5 text-sm font-semibold text-ink">参考实现</h3>
        <pre className="mt-3 overflow-auto rounded-ui bg-slate-100 p-4 text-sm leading-6 text-slate-800">
          <code>{detail.reference_solution}</code>
        </pre>
      </div>
    </section>
  );
}

function ExerciseResult({ result }: { result: any }) {
  return (
    <section className="rounded-[16px] border border-emerald-100 bg-emerald-50/80 p-5">
      <h2 className="section-title">练习结果：{result.score} 分</h2>
      <p className="mt-2 text-sm text-slate-700">{result.summary}</p>
      <div className="mt-4 space-y-2">
        {(result.items ?? []).map((item: any) => (
          <div key={item.id} className="rounded-ui bg-white px-3 py-2 text-sm leading-6 text-slate-700">
            <strong className={item.correct ? "text-emerald-700" : "text-amber-700"}>{item.correct ? "正确" : "需复盘"}</strong>
            <span className="ml-2">{item.analysis}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
