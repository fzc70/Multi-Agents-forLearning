import { ArrowLeft, CheckCircle2, Code2, Network, Send } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import type { LearningResource, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";

type ResourceDetailPageProps = {
  task: LearningTask;
  resource: LearningResource;
  onBack: () => void;
  onSubmitExercise: (resource: LearningResource, answers: Record<string, string>) => Promise<any>;
  isSubmitting: boolean;
};

export function ResourceDetailPage({ task, resource, onBack, onSubmitExercise, isSubmitting }: ResourceDetailPageProps) {
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

      {resource.type === "讲解文档" ? <LectureDocument detail={detail} content={resource.content} /> : null}
      {resource.type === "思维导图" ? <GraphResource title="思维导图" detail={detail} /> : null}
      {resource.type === "知识图谱" ? <GraphResource title="知识图谱" detail={detail} /> : null}
      {resource.type === "拓展阅读" ? <ReadingResource detail={detail} /> : null}
      {resource.type === "代码案例" ? <CodePractice detail={detail} /> : null}
    </div>
  );
}

function LectureDocument({ detail, content }: { detail: Record<string, any>; content?: string }) {
  const sections = Array.isArray(detail.sections) ? detail.sections : [];
  return (
    <section className="rounded-[16px] border border-slate-200 bg-white p-6">
      <div className="prose prose-slate max-w-none">
        {sections.length ? (
          sections.map((section: any) => (
            <article key={section.heading} className="mb-7">
              <h2 className="text-xl font-semibold text-ink">{section.heading}</h2>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">{section.body}</p>
            </article>
          ))
        ) : (
          content ? <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{content}</p> : <MissingDetail message="这份讲解文档缺少正文内容，请返回资源库重新生成。" />
        )}
      </div>
      {Array.isArray(detail.checkpoints) ? (
        <div className="mt-4 rounded-ui border border-emerald-100 bg-emerald-50/70 p-4">
          <h3 className="text-sm font-semibold text-ink">学完自检</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {detail.checkpoints.map((item: string) => (
              <span key={item} className="rounded-full bg-white px-3 py-1 text-xs text-emerald-800">{item}</span>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function GraphResource({ title, detail }: { title: string; detail: Record<string, any> }) {
  const nodes = Array.isArray(detail.nodes) ? detail.nodes : [];
  const edges = Array.isArray(detail.edges) ? detail.edges : [];
  return (
    <section className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <div className="rounded-[16px] border border-slate-200 bg-white p-5">
        <h2 className="section-title">{title}</h2>
        <div className="mt-5 flex min-h-[360px] flex-wrap content-start gap-3 rounded-[14px] border border-line bg-slate-50 p-4">
          {nodes.length ? nodes.map((node: any) => (
            <div key={node.id} className="rounded-full border border-emerald-100 bg-white px-4 py-2 text-sm font-medium text-emerald-800">
              {node.label}
            </div>
          )) : <MissingDetail message={`${title}缺少节点，系统需要重新生成结构化图谱。`} />}
        </div>
      </div>
      <aside className="rounded-[16px] border border-slate-200 bg-white p-5">
        <div className="flex items-center gap-2">
          <Network size={18} className="text-emerald-700" />
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
