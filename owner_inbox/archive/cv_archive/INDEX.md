# CV Archive Index

> All CV versions and job applications are tracked here.  
> Database: [`cv_archive.db`](cv_archive.db) | Last updated: 2026-04-24

## CV Versions

| File | Version | Date | Tailored For |
|------|---------|------|-------------|
| `Inon_Baasov_CV_Elbit_2026.pdf` | v1.0 — Elbit Systems | 2026-04-24 | Product Manager, Learning Dept — Elbit Systems |
| `Inon_Baasov_CV_SeniorPM.pdf` | v2.0 — Generic Senior PM | 2026-05-01 | General / Multi-role (AI, SaaS, Enterprise) |

## Applications Log

| Date | Company | Role | Contact | Status |
|------|---------|------|---------|--------|
| 2026-04-24 | Elbit Systems | Product Manager – Learning Dept | TBD | Sent |

## How to Add a New Application
1. Generate/duplicate a CV using `scripts/generate_elbit_cv.py` as a template.
2. Run `python scripts/init_cv_archive.py` to create DB (first time only).
3. Insert into `cv_versions` and `applications` tables via:
   ```bash
   python scripts/log_application.py
   ```
4. Update this index.

## CV Metadata to Always Record
- Contact person (name, email, LinkedIn)
- Interviewer (if different from contact)
- Company location & website
- Job URL
- Source (website / LinkedIn / referral / recruiter)
- Any attached documents (cover letter, portfolio link, etc.)
