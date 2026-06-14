import { BookOpen, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { FormEvent, useState } from "react";
import type { LearningTask } from "../types/task";
import { Button } from "./Button";

type AssistantLauncherProps = {
  task: LearningTask;
  onSend: (message: string) => void;
};

export function AssistantLauncher({ task, onSend }: AssistantLauncherProps) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [showHint, setShowHint] = useState(true);
  const messages = Array.isArray(task.messages) ? task.messages : [];
  const guideQuestions = [
    "解释一下当前页面",
    "我下一步点哪里？",
    "帮我快速生成一个练习"
  ];

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const value = text.trim();
    if (!value) return;
    onSend(value);
    setText("");
  }

  return (
    <>
      <button
        className="fixed bottom-7 right-7 z-30 grid h-14 w-14 place-items-center rounded-2xl border border-emerald-200 bg-white text-emerald-800 shadow-soft transition hover:-translate-y-0.5 hover:bg-emerald-50"
        onClick={() => {
          setOpen(true);
          setShowHint(false);
        }}
        aria-label="打开学习助手"
      >
        <BookOpen size={22} />
        <Sparkles className="absolute right-2 top-2 text-emerald-300" size={13} />
      </button>

      {!open && showHint ? (
        <button
          className="fixed bottom-9 right-24 z-30 rounded-full border border-emerald-100 bg-white px-3 py-2 text-xs text-emerald-800 shadow-soft transition hover:bg-emerald-50"
          onClick={() => {
            setOpen(true);
            setShowHint(false);
          }}
        >
          有问题可以问我
        </button>
      ) : null}

      {open ? (
        <div className="fixed inset-y-0 right-0 z-40 flex w-[440px] flex-col border-l border-slate-200 bg-white shadow-soft">
          <div className="border-b border-line bg-slate-50/80 px-5 py-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-medium text-emerald-700">快速学习助手</p>
                <h2 className="mt-1 text-base font-semibold text-ink">{task.title}</h2>
              </div>
              <Button variant="secondary" className="h-9 px-3" onClick={() => setOpen(false)} aria-label="关闭学习助手">
                <X size={18} />
                关闭
              </Button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-5 py-4">
            <div className="mb-4 rounded-ui border border-emerald-100 bg-emerald-50/70 p-4 text-sm leading-6 text-slate-700">
              <div className="mb-2 flex items-center gap-2 font-medium text-ink">
                <MessageCircle size={17} className="text-emerald-700" />
                这是当前页面的快速助手
              </div>
              适合临时问一句、解释当前页面或快速获得下一步建议。完整学习对话建议进入“对话”页面。
              <div className="mt-3 flex flex-wrap gap-2">
                {guideQuestions.map((prompt) => (
                  <button
                    key={prompt}
                    className="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-800 transition hover:bg-emerald-100"
                    onClick={() => onSend(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              {messages.slice(-5).map((message) => (
                <div
                  key={message.id}
                  className={`max-w-[82%] rounded-ui px-3 py-2 text-sm leading-6 ${
                    message.role === "user"
                      ? "ml-auto bg-emerald-700 text-white"
                      : "border border-line bg-slate-50 text-ink"
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>
          </div>

          <form className="border-t border-line p-4" onSubmit={handleSubmit}>
            <div className="flex gap-2">
              <input
                className="focus-ring h-10 flex-1 rounded-ui border border-line px-3 text-sm"
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="输入你想问的问题..."
              />
              <Button variant="primary" className="w-10 px-0" aria-label="发送">
                <Send size={17} />
              </Button>
            </div>
          </form>
        </div>
      ) : null}
    </>
  );
}
