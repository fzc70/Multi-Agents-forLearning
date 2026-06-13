export function formatDisplayTime(value: string) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const diffMs = Date.now() - date.getTime();
  if (diffMs >= 0 && diffMs < 60_000) return "刚刚";
  if (diffMs >= 0 && diffMs < 60 * 60_000) return `${Math.floor(diffMs / 60_000)} 分钟前`;
  if (diffMs >= 0 && diffMs < 24 * 60 * 60_000) return `${Math.floor(diffMs / 60 / 60_000)} 小时前`;
  return date.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}
