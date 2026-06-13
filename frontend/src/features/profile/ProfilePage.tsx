import { BadgeCheck, Brain, Clock3, FileSearch } from "lucide-react";
import type { LearningTask } from "../../shared/types/task";
import { formatDisplayTime } from "../../shared/utils/time";

type ProfilePageProps = {
  task: LearningTask;
};

export function ProfilePage({ task }: ProfilePageProps) {
  const profile = task.profile ?? { summary: "画像正在建立中。", dimensions: [], recentEvidences: [] };
  const averageConfidence = Math.round(
    profile.dimensions.length
      ? profile.dimensions.reduce((sum, item) => sum + item.confidence, 0) / profile.dimensions.length
      : 0
  );

  return (
    <div className="space-y-5">
      <header className="rounded-[16px] border border-slate-200 bg-[linear-gradient(135deg,#ffffff,#f3f8f6_52%,#fff8ee)] p-5">
        <div className="flex items-start justify-between gap-5">
          <div>
            <p className="text-xs font-medium text-emerald-700">学习画像</p>
            <h1 className="mt-1 text-2xl font-semibold text-ink">系统如何理解你的学习状态</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{profile.summary}</p>
          </div>
          <div className="rounded-[14px] border border-emerald-100 bg-white/80 px-4 py-3 text-right">
            <p className="text-xs text-muted">画像可信度</p>
            <p className="mt-1 text-2xl font-semibold text-emerald-800">{averageConfidence}%</p>
          </div>
        </div>
      </header>

      <section className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <div className="grid gap-3 md:grid-cols-2">
          {profile.dimensions.map((dimension) => (
            <article key={dimension.id} className="rounded-[16px] border border-slate-200 bg-white p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-muted">{dimension.label}</p>
                  <h2 className="mt-1 text-base font-semibold leading-6 text-ink">{dimension.value}</h2>
                </div>
                <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs text-emerald-700">
                  {dimension.confidence}%
                </span>
              </div>
              <div className="mt-4 rounded-ui bg-slate-50 px-3 py-2">
                <div className="mb-1 flex items-center gap-2 text-xs font-medium text-slate-700">
                  <FileSearch size={14} />
                  更新依据
                </div>
                <p className="text-sm leading-6 text-muted">{dimension.evidence}</p>
              </div>
              <p className="mt-3 text-xs text-muted">最近更新：{formatDisplayTime(dimension.updatedAt)}</p>
            </article>
          ))}
        </div>

        <aside className="space-y-4">
          <div className="rounded-[16px] border border-emerald-100 bg-emerald-50/80 p-5">
            <div className="flex items-center gap-2">
              <Brain size={18} className="text-emerald-700" />
              <h2 className="section-title">随学随新</h2>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-700">
              每次对话、测评、资料上传和资源使用，都会成为更新画像的依据。
            </p>
          </div>

          <div className="rounded-[16px] border border-slate-200 bg-white p-5">
            <div className="flex items-center gap-2">
              <BadgeCheck size={18} className="text-amber-600" />
              <h2 className="section-title">最近依据</h2>
            </div>
            <div className="mt-4 space-y-3">
              {profile.recentEvidences.map((evidence) => (
                <div key={evidence} className="flex gap-3 rounded-ui bg-slate-50 px-3 py-2">
                  <Clock3 size={15} className="mt-0.5 shrink-0 text-slate-400" />
                  <p className="text-sm leading-6 text-slate-700">{evidence}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}
