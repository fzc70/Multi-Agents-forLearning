import { Check, Sparkles } from "lucide-react";
import { useState } from "react";
import type { LearningResource } from "../types/task";
import { Button } from "./Button";
import { Modal } from "./Modal";

type ResourceGenerationModalProps = {
  open: boolean;
  onClose: () => void;
  smartDescription?: string;
  onSmartGenerate: () => void;
  onGenerateSelected: (types: LearningResource["type"][]) => void;
  isGenerating?: boolean;
};

const resourceTypes: LearningResource["type"][] = [
  "讲解文档",
  "练习题",
  "思维导图",
  "拓展阅读",
  "视频脚本",
  "代码案例",
  "知识图谱"
];

export function ResourceGenerationModal({
  open,
  onClose,
  smartDescription = "系统根据当前任务、下一步建议和学习画像，自动选择最合适的一类资源。",
  onSmartGenerate,
  onGenerateSelected,
  isGenerating = false
}: ResourceGenerationModalProps) {
  const [mode, setMode] = useState<"choice" | "custom">("choice");
  const [selectedTypes, setSelectedTypes] = useState<LearningResource["type"][]>(["讲解文档", "练习题"]);

  function close() {
    setMode("choice");
    onClose();
  }

  function toggleType(type: LearningResource["type"]) {
    setSelectedTypes((current) =>
      current.includes(type) ? current.filter((item) => item !== type) : [...current, type]
    );
  }

  return (
    <Modal
      open={open}
      title={mode === "choice" ? "生成学习资源" : "选择要生成的资源"}
      description={mode === "choice" ? "可以让系统自动生成，也可以自己选择需要的资源类型。" : "选择完成后，会一次性生成所选资源。"}
      onClose={close}
    >
      {mode === "choice" ? (
        <div className="grid gap-3">
          <button
            className="rounded-ui border border-emerald-200 bg-emerald-50/70 p-4 text-left transition hover:bg-emerald-50"
            disabled={isGenerating}
            aria-label="智能生成"
            onClick={() => {
              onSmartGenerate();
              close();
            }}
          >
            <div className="flex items-center gap-2 font-semibold text-ink">
              <Sparkles size={18} className="text-emerald-700" />
              智能生成
            </div>
            <p className="mt-2 text-sm leading-6 text-muted">{smartDescription}</p>
          </button>

          <button
            className="rounded-ui border border-line bg-white p-4 text-left transition hover:border-emerald-200 hover:bg-slate-50"
            disabled={isGenerating}
            aria-label="自选类型"
            onClick={() => setMode("custom")}
          >
            <div className="flex items-center gap-2 font-semibold text-ink">
              <Check size={18} className="text-slate-600" />
              自选类型
            </div>
            <p className="mt-2 text-sm leading-6 text-muted">
              手动选择讲解文档、练习题、思维导图等一种或多种资源。
            </p>
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3">
            {resourceTypes.map((type) => {
              const active = selectedTypes.includes(type);
              return (
                <button
                  key={type}
                  className={`flex items-center justify-between rounded-ui border px-4 py-3 text-left text-sm transition ${
                    active
                      ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                      : "border-line bg-white text-ink hover:bg-slate-50"
                  }`}
                  onClick={() => toggleType(type)}
                >
                  {type}
                  {active ? <Check size={16} /> : null}
                </button>
              );
            })}
          </div>
          <div className="mt-5 flex justify-end gap-2">
            <Button onClick={() => setMode("choice")}>返回</Button>
            <Button
              variant="primary"
              disabled={selectedTypes.length === 0}
              loading={isGenerating}
              onClick={() => {
                onGenerateSelected(selectedTypes);
                close();
              }}
            >
              生成所选资源
            </Button>
          </div>
        </>
      )}
    </Modal>
  );
}
