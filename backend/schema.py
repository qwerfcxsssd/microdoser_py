SCHEMA_VERSION = 1

SCHEMA_V1_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS llm_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  language TEXT NOT NULL,
  model TEXT NOT NULL,
  user_text TEXT NOT NULL,
  response_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ok',
  error_text TEXT
);

CREATE INDEX IF NOT EXISTS idx_llm_runs_created_at
ON llm_runs(created_at);

CREATE TABLE IF NOT EXISTS medicines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  form TEXT,
  strength_mg INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(name, form, strength_mg)
);

CREATE INDEX IF NOT EXISTS idx_medicines_name
ON medicines(name);

CREATE TABLE IF NOT EXISTS intake_plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  medicine_id INTEGER,
  medicine_name_text TEXT NOT NULL,
  dose_mg INTEGER,
  max_per_day_mg INTEGER,
  instructions TEXT,
  start_date TEXT,
  end_date TEXT,
  times_json TEXT,
  frequency_hours INTEGER,
  source_llm_run_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE SET NULL,
  FOREIGN KEY (source_llm_run_id) REFERENCES llm_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_intake_plans_start_date
ON intake_plans(start_date);

CREATE TABLE IF NOT EXISTS calendar_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  start_local TEXT NOT NULL,
  end_local TEXT,
  recurrence_json TEXT,
  reminders_json TEXT,
  notes TEXT,

  intake_plan_id INTEGER,
  source_llm_run_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY (intake_plan_id) REFERENCES intake_plans(id) ON DELETE SET NULL,
  FOREIGN KEY (source_llm_run_id) REFERENCES llm_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_calendar_events_start
ON calendar_events(start_local);

CREATE TABLE IF NOT EXISTS diary_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_date TEXT NOT NULL,
  text TEXT NOT NULL,
  source_llm_run_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY (source_llm_run_id) REFERENCES llm_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_diary_entries_date
ON diary_entries(entry_date);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  source_llm_run_id INTEGER,

  FOREIGN KEY (source_llm_run_id) REFERENCES llm_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notes_updated
ON notes(updated_at);
"""
