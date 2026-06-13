import { Inbox } from "lucide-react";
import type { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
  tone?: "neutral" | "warm" | "green";
};

const toneClass = {
  neutral: "bg-slate-50 text-slate-500",
  warm: "bg-amber-50 text-amber-700",
  green: "bg-emerald-50 text-emerald-700"
};

export function EmptyState({ title, description, action, tone = "neutral" }: EmptyStateProps) {
  return (
    <div className="surface flex min-h-[220px] flex-col items-center justify-center px-8 py-10 text-center">
      <div className={`mb-4 grid h-11 w-11 place-items-center rounded-ui border border-line ${toneClass[tone]}`}>
        <Inbox size={20} />
      </div>
      <h3 className="text-base font-semibold text-ink">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
