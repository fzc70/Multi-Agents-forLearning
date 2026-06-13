import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
  icon?: ReactNode;
  loading?: boolean;
};

export function Button({
  variant = "secondary",
  icon,
  loading = false,
  children,
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const variants = {
    primary: "border-emerald-700 bg-emerald-700 text-white hover:bg-emerald-800",
    secondary: "border-line bg-white text-ink hover:border-emerald-200 hover:bg-emerald-50/60",
    ghost: "border-transparent bg-transparent text-muted hover:bg-slate-100 hover:text-ink"
  };

  return (
    <button
      className={`inline-flex h-10 items-center justify-center gap-2 rounded-ui border px-4 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="animate-spin" size={16} /> : icon}
      {children}
    </button>
  );
}
