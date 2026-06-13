import { BarChart3, BookOpen, Compass, FolderOpen, GraduationCap, MessageCircle, Sparkles } from "lucide-react";
import type { PageKey } from "../../shared/types/task";

type SidebarProps = {
  page: PageKey;
  onPageChange: (page: PageKey) => void;
};

const items: Array<{ key: PageKey; label: string; icon: typeof BookOpen }> = [
  { key: "tasks", label: "任务", icon: Compass },
  { key: "chat", label: "对话", icon: MessageCircle },
  { key: "resources", label: "资源", icon: FolderOpen },
  { key: "path", label: "路径", icon: BookOpen },
  { key: "assessment", label: "评估", icon: BarChart3 }
];

export function Sidebar({ page, onPageChange }: SidebarProps) {
  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex w-[88px] flex-col items-center border-r border-slate-200 bg-white/90 px-3 py-5 backdrop-blur">
      <div
        className="relative mb-8 grid h-11 w-11 place-items-center rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 shadow-sm"
        title="个性化学习助手"
        aria-label="个性化学习助手"
      >
        <GraduationCap size={22} strokeWidth={2.1} />
        <Sparkles className="absolute right-1.5 top-1.5 text-emerald-300" size={11} strokeWidth={2.3} />
      </div>

      <nav className="flex w-full flex-col gap-2">
        {items.map((item) => {
          const Icon = item.icon;
          const active = item.key === page;
          return (
            <button
              key={item.key}
              className={`flex flex-col items-center gap-1 rounded-ui px-2 py-3 text-xs transition ${
                active ? "bg-emerald-50 text-emerald-800" : "text-muted hover:bg-slate-50 hover:text-ink"
              }`}
              onClick={() => onPageChange(item.key)}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
