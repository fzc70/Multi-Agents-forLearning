type ToastProps = {
  message: string;
};

export function Toast({ message }: ToastProps) {
  if (!message) return null;

  return (
    <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-ui border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-900 shadow-soft">
      {message}
    </div>
  );
}
