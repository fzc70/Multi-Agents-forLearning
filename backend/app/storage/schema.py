import sqlite3


SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS learning_tasks (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT '自定义',
  next_action TEXT NOT NULL,
  reason TEXT NOT NULL,
  profile_tags TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profile_dimensions (
  id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  label TEXT NOT NULL,
  value TEXT NOT NULL,
  confidence INTEGER NOT NULL,
  evidence TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(task_id, id),
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS materials (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  size_label TEXT NOT NULL,
  status TEXT NOT NULL,
  text_length INTEGER NOT NULL DEFAULT 0,
  used_for TEXT NOT NULL DEFAULT '[]',
  file_path TEXT,
  text_path TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS material_chunks (
  id TEXT PRIMARY KEY,
  material_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  page INTEGER,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  token_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY(material_id) REFERENCES materials(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL UNIQUE,
  summary TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memory_records (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  type TEXT NOT NULL,
  content TEXT NOT NULL,
  evidence TEXT NOT NULL,
  importance INTEGER NOT NULL DEFAULT 50,
  created_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_resources (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  content TEXT NOT NULL,
  detail_json TEXT NOT NULL DEFAULT '{}',
  recommendation_reason TEXT NOT NULL,
  source_refs TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_steps (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  title TEXT NOT NULL,
  objective TEXT NOT NULL,
  resource TEXT NOT NULL,
  exercise TEXT NOT NULL,
  status TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessment_results (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL UNIQUE,
  score INTEGER NOT NULL,
  mastery TEXT NOT NULL,
  weak_points TEXT NOT NULL DEFAULT '[]',
  mistake_types TEXT NOT NULL DEFAULT '[]',
  effort TEXT NOT NULL,
  next_suggestion TEXT NOT NULL,
  tested INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exercise_attempts (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  resource_title TEXT NOT NULL,
  score INTEGER NOT NULL,
  total_score INTEGER NOT NULL DEFAULT 100,
  detail_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE,
  FOREIGN KEY(resource_id) REFERENCES learning_resources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resource_mastery (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  resource_title TEXT NOT NULL,
  mastery INTEGER NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(task_id, resource_id),
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE,
  FOREIGN KEY(resource_id) REFERENCES learning_resources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_graphs (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  title TEXT NOT NULL,
  nodes TEXT NOT NULL,
  edges TEXT NOT NULL,
  source_stats TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES learning_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workflow_runs (
  id TEXT PRIMARY KEY,
  task_id TEXT,
  workflow_name TEXT NOT NULL,
  status TEXT NOT NULL,
  input_json TEXT NOT NULL,
  output_json TEXT,
  error TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_run_logs (
  id TEXT PRIMARY KEY,
  task_id TEXT,
  workflow_run_id TEXT,
  agent_name TEXT NOT NULL,
  model TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  input_json TEXT NOT NULL,
  output_json TEXT,
  error TEXT,
  latency_ms INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);
"""


def apply_schema(conn: sqlite3.Connection) -> None:
    """创建数据表并执行向后兼容的小型迁移。"""
    conn.executescript(SCHEMA_SQL)
    ensure_column(
        conn, "learning_resources", "detail_json", "TEXT NOT NULL DEFAULT '{}'"
    )


def ensure_column(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> None:
    """在旧数据库缺少字段时补充该字段。"""
    columns = {
        row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
