import { FileText, Upload } from "lucide-react";
import { useRef } from "react";
import type { LearningMaterial, LearningTask } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";

type MaterialsPanelProps = {
  task: LearningTask;
  onUploadMaterial: (file: File) => void | Promise<void>;
  compact?: boolean;
  isUploading?: boolean;
};

export function MaterialsPanel({ task, onUploadMaterial, compact = false, isUploading = false }: MaterialsPanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const materials = task.materials ?? [];

  function handleFiles(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    onUploadMaterial(file);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <section className={`rounded-[16px] border border-slate-200 bg-white ${compact ? "p-4" : "p-5"}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-sky-700">学习资料</p>
          <h2 className="mt-1 text-lg font-semibold text-ink">任务资料库</h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            上传课程资料后，后续资源生成、答疑和路径规划会优先参考这些内容。
          </p>
        </div>
        <Button icon={<Upload size={16} />} onClick={() => inputRef.current?.click()} loading={isUploading}>
          上传资料
        </Button>
        <input
          ref={inputRef}
          className="hidden"
          type="file"
          accept=".pdf"
          onChange={(event) => handleFiles(event.target.files)}
        />
      </div>

      <div className="mt-4 grid gap-3">
        {materials.length === 0 ? (
          <div className="rounded-ui border border-dashed border-slate-200 bg-slate-50/70 px-3 py-4 text-sm text-muted">
            暂无学习资料。上传 PDF 后，答疑、资源和图谱会优先参考资料内容。
          </div>
        ) : null}
        {materials.slice(0, compact ? 2 : materials.length).map((material: LearningMaterial) => (
          <div key={material.id} className="rounded-ui border border-line bg-slate-50/70 px-3 py-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex min-w-0 gap-3">
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-ui bg-sky-50 text-sky-700">
                  <FileText size={17} />
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{material.name}</p>
                  <p className="mt-1 text-xs text-muted">
                    {material.type} · {material.size} · 文本约 {material.textLength.toLocaleString()} 字
                  </p>
                </div>
              </div>
              <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-1 text-xs text-emerald-700">
                {material.status}
              </span>
            </div>
            {!compact ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {material.usedFor.map((item) => (
                  <span key={item} className="rounded-full bg-white px-2.5 py-1 text-xs text-slate-600">
                    参与{item}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        ))}
      </div>

      {compact && materials.length > 2 ? (
        <p className="mt-3 text-xs text-muted">还有 {materials.length - 2} 份资料，可在资源页查看。</p>
      ) : null}
    </section>
  );
}
