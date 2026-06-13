import type { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="surface flex min-h-[220px] flex-col items-center justify-center px-8 py-10 text-center">
      <div className="mb-4 h-10 w-10 rounded-ui border border-line bg-slate-50" />
      <h3 className="text-base font-semibold text-ink">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
