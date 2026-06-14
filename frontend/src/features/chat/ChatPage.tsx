import { FormEvent, useState } from "react";
import { BookOpen, Send, UserRound } from "lucide-react";
import type { LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";

type ChatPageProps = {
  task: LearningTask;
  onSendMessage: (message: string) => void | Promise<void>;
  isSending: boolean;
};

const prompts = ["讲解一下当前重点", "出一道小题", "帮我复盘错误", "调整今天学习计划"];

export function ChatPage({ task, onSendMessage, isSending }: ChatPageProps) {
  const [text, setText] = useState("");
  const messages = Array.isArray(task.messages) ? task.messages : [];
  const profileTags = Array.isArray(task.profileTags) ? task.profileTags : [];

  function send(value: string) {
    const message = value.trim();
    if (!message) return;
    onSendMessage(message);
    setText("");
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    send(text);
  }

  return (
    <div className="grid grid-cols-[1fr_300px] gap-5">
      <section className="flex min-h-[640px] flex-col overflow-hidden rounded-[16px] border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-line bg-white px-5 py-4">
          <p className="text-xs font-medium text-emerald-700">完整学习对话</p>
          <h1 className="mt-1 text-lg font-semibold text-ink">围绕当前任务深入学习</h1>
          <p className="subtle mt-1">可以直接提问，也可以选择一个学习动作开始。</p>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto bg-[#fbfaf7] p-5">
          <div className="grid gap-2 rounded-[14px] border border-emerald-100 bg-white/90 p-3 sm:grid-cols-2">
            {prompts.map((prompt) => (
              <button
                key={prompt}
                className="rounded-ui border border-line bg-slate-50 px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                onClick={() => send(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          {messages.length === 0 ? (
            <div className="rounded-ui border border-line bg-slate-50 p-5">
              <h3 className="font-semibold text-ink">可以这样开始</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {prompts.map((prompt) => (
                  <button
                    key={prompt}
                    className="rounded-full border border-line bg-white px-3 py-1.5 text-sm text-muted hover:border-emerald-200 hover:text-emerald-800"
                    onClick={() => send(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" ? (
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-ui border border-emerald-100 bg-emerald-50 text-emerald-800">
                    <BookOpen size={16} />
                  </div>
                ) : null}

                <div className={`max-w-[68%] ${message.role === "user" ? "order-1" : ""}`}>
                  <div className={`mb-1 text-xs ${message.role === "user" ? "text-right text-muted" : "text-muted"}`}>
                    {message.role === "user" ? "我" : "学习助手"}
                  </div>
                  <div
                    className={`w-fit whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                      message.role === "user"
                        ? "ml-auto rounded-tr-md bg-emerald-700 text-white"
                        : "rounded-tl-md border border-slate-200 bg-white text-ink"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>

                {message.role === "user" ? (
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-ui bg-emerald-100 text-emerald-800">
                    <UserRound size={16} />
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>

        <form className="border-t border-line bg-white p-4" onSubmit={handleSubmit}>
          <div className="flex gap-2 rounded-[12px] border border-slate-200 bg-slate-50 p-1">
            <input
              className="h-10 flex-1 bg-transparent px-3 text-sm outline-none"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="输入问题，或说出你想怎么学"
            />
            <Button variant="primary" className="h-10" icon={<Send size={16} />} loading={isSending}>
              发送
            </Button>
          </div>
        </form>
      </section>

      <aside className="space-y-4">
        <div className="rounded-[16px] border border-emerald-100 bg-emerald-50/80 p-5">
          <p className="text-xs font-medium text-emerald-700">当前建议</p>
          <h2 className="mt-2 text-base font-semibold text-ink">先做一个小步骤</h2>
          <p className="mt-3 text-sm leading-6 text-slate-700">{task.reason}</p>
        </div>
        <div className="rounded-[16px] border border-slate-200 bg-white p-5">
          <h2 className="section-title">学习依据</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {profileTags.slice(0, 6).map((tag) => (
              <span key={tag} className="rounded-full border border-line bg-slate-50 px-3 py-1.5 text-xs text-slate-700">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
