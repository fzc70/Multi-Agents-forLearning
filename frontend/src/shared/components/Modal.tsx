import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";
import { Button } from "./Button";

type ModalProps = {
  open: boolean;
  title: string;
  description?: string;
  children: ReactNode;
  onClose: () => void;
};

export function Modal({ open, title, description, children, onClose }: ModalProps) {
  useEffect(() => {
    if (!open) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-slate-600/25 p-5 backdrop-blur-[2px]"
      role="presentation"
      onMouseDown={onClose}
    >
      <div
        className="w-full max-w-lg rounded-ui border border-line bg-white p-5 shadow-soft"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink">{title}</h2>
            {description ? <p className="mt-1 text-sm leading-6 text-muted">{description}</p> : null}
          </div>
          <Button variant="secondary" className="h-9 shrink-0 px-3" onClick={onClose} aria-label="关闭弹窗">
            <X size={18} />
            关闭
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
