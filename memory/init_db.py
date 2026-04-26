"""
Initializes the agent framework SQLite database.
Run once: python memory/init_db.py
"""
import sqlite3
from datetime import datetime

DB_PATH = "memory/session_log.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS session_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    agent       TEXT    NOT NULL,
    task_id     TEXT,
    action      TEXT    NOT NULL,
    output_path TEXT,
    next_step   TEXT,
    status      TEXT    CHECK(status IN ('started','completed','blocked','escalated')) DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS decisions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    agent       TEXT    NOT NULL,
    task_id     TEXT,
    decision    TEXT    NOT NULL,
    rationale   TEXT,
    outcome     TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     TEXT    UNIQUE NOT NULL,
    title       TEXT    NOT NULL,
    assigned_to TEXT,
    delegated_by TEXT,
    status      TEXT    CHECK(status IN ('pending','in_progress','blocked','completed')) DEFAULT 'pending',
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_log_agent   ON session_log(agent);
CREATE INDEX IF NOT EXISTS idx_log_task    ON session_log(task_id);
CREATE INDEX IF NOT EXISTS idx_log_status  ON session_log(status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
"""

def init():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO session_log (timestamp, agent, task_id, action, status) VALUES (?, ?, ?, ?, ?)",
        (now, "system", "INIT", "Database initialized — framework v2 deployed.", "completed")
    )
    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")

if __name__ == "__main__":
    init()
