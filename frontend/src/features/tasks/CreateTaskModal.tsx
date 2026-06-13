import { FormEvent, useState } from "react";
import type { NewTaskInput } from "../../shared/types/task";
import { Button } from "../../shared/components/Button";
import { Modal } from "../../shared/components/Modal";

type CreateTaskModalProps = {
  open: boolean;
  onClose: () => void;
  onCreate: (input: NewTaskInput) => void;
};

export function CreateTaskModal({ open, onClose, onCreate }: CreateTaskModalProps) {
  const [title, setTitle] = useState("");
  const [foundation, setFoundation] = useState("");
  const [expectedOutcome, setExpectedOutcome] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const value = title.trim();
    if (!value) return;
    onCreate({
      title: value,
      foundation: foundation.trim(),
      expectedOutcome: expectedOutcome.trim()
    });
    setTitle("");
    setFoundation("");
    setExpectedOutcome("");
  }

  return (
    <Modal
      open={open}
      title="新建学习任务"
      description="先写下学习目标即可，其他信息可以在后续对话和练习中逐步完善。"
      onClose={onClose}
    >
      <form className="grid gap-4" onSubmit={handleSubmit}>
        <label className="grid gap-2 text-sm font-medium text-ink">
          学习目标
          <input
            className="focus-ring h-11 rounded-ui border border-line px-3 font-normal"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="例如：学习现代文阅读答题技巧"
            autoFocus
          />
        </label>
        <label className="grid gap-2 text-sm font-medium text-ink">
          当前基础 <span className="font-normal text-muted">可选</span>
          <input
            className="focus-ring h-11 rounded-ui border border-line px-3 font-normal"
            value={foundation}
            onChange={(event) => setFoundation(event.target.value)}
            placeholder="例如：基础一般，容易读不懂题干"
          />
        </label>
        <label className="grid gap-2 text-sm font-medium text-ink">
          希望达到的效果 <span className="font-normal text-muted">可选</span>
          <input
            className="focus-ring h-11 rounded-ui border border-line px-3 font-normal"
            value={expectedOutcome}
            onChange={(event) => setExpectedOutcome(event.target.value)}
            placeholder="例如：两周内提升做题正确率"
          />
        </label>

        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" onClick={onClose}>
            取消
          </Button>
          <Button type="submit" variant="primary" disabled={!title.trim()}>
            创建任务
          </Button>
        </div>
      </form>
    </Modal>
  );
}
