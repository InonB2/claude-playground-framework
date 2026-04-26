"""
Initialize the CV Archive database.
Tracks every CV version sent or used, with full application metadata.
Run: python scripts/init_cv_archive.py
"""
import sqlite3, os
from datetime import datetime

os.makedirs("output/cv_archive", exist_ok=True)
DB = "output/cv_archive/cv_archive.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS cv_versions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT    NOT NULL,
    version_label   TEXT    NOT NULL,
    created_date    TEXT    NOT NULL,
    tailored_for    TEXT,
    job_title       TEXT,
    key_changes     TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cv_id           INTEGER REFERENCES cv_versions(id),
    applied_date    TEXT    NOT NULL,
    company_name    TEXT    NOT NULL,
    company_location TEXT,
    company_website TEXT,
    job_title       TEXT    NOT NULL,
    job_url         TEXT,
    contact_person  TEXT,
    contact_email   TEXT,
    contact_linkedin TEXT,
    interviewer     TEXT,
    interviewer_role TEXT,
    source          TEXT    CHECK(source IN ('website','linkedin','referral','direct','recruiter','other')),
    status          TEXT    CHECK(status IN ('sent','screening','interview','offer','rejected','withdrawn','ghosted')) DEFAULT 'sent',
    notes           TEXT,
    next_action     TEXT,
    next_action_date TEXT,
    attachments     TEXT
);

CREATE TABLE IF NOT EXISTS interview_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER REFERENCES applications(id),
    interview_date  TEXT    NOT NULL,
    interview_type  TEXT    CHECK(interview_type IN ('phone','video','onsite','technical','case','final','other')),
    interviewer     TEXT,
    interviewer_role TEXT,
    duration_min    INTEGER,
    questions_asked TEXT,
    my_answers      TEXT,
    feedback_received TEXT,
    outcome         TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_app_company ON applications(company_name);
CREATE INDEX IF NOT EXISTS idx_app_status  ON applications(status);
CREATE INDEX IF NOT EXISTS idx_app_date    ON applications(applied_date);
"""

conn = sqlite3.connect(DB)
conn.executescript(SCHEMA)

# Seed with the Elbit application
now = datetime.utcnow().date().isoformat()
conn.execute("""
    INSERT INTO cv_versions (filename, version_label, created_date, tailored_for, job_title, key_changes)
    VALUES (?,?,?,?,?,?)
""", (
    "Inon_Baasov_CV_Elbit_2026.pdf",
    "v1.0 — Elbit Systems",
    now,
    "Elbit Systems — Learning Department",
    "Product Manager, Learning Department",
    "Tailored summary for defence learning/training systems; emphasised V&V, regulated environments, Technion background; added Elbit relevance note; reordered skills for EdTech/training focus"
))
cv_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

conn.execute("""
    INSERT INTO applications (cv_id, applied_date, company_name, company_location, job_title,
        contact_person, source, status, notes)
    VALUES (?,?,?,?,?,?,?,?,?)
""", (
    cv_id, now,
    "Elbit Systems",
    "Israel",
    "Product Manager – Learning Department",
    "TBD — to be added when contact is identified",
    "direct",
    "sent",
    "JD in Hebrew. Role in Learning Dept managing TPSS, simulators, emulators, ETL, LMS. Elbit defence & aerospace. Requires EdTech/training tech PM background. BSc+MBA Technion is strong fit."
))

conn.commit()
conn.close()
print(f"CV archive database ready: {DB}")
print("Elbit application seeded.")
