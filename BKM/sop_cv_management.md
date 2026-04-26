# SOP: CV Management & Application Tracking

**File Path:** `/BKM/sop_cv_management.md`  
**Authority:** Andy (Orchestrator)  
**Agent:** Cole (Copywriter), Silas (DB Architect)  
**Version:** 1.0 — 2026-04-24

---

## Purpose
Every CV version sent and every job application made must be archived. No CV leaves the system without a complete metadata record.

---

## CV Creation Process

1. **Owner drops JD** into `/team_inbox/` with note: "Create CV for [Company] – [Role]"
2. **Andy** assigns task to Cole (copy) and creates a task in `/tasks/active_tasks.json`
3. **Cole** drafts the tailored CV, cross-referencing:
   - `/scratchpad/brief_website_audit.md` for current positioning
   - The JD for keyword alignment
   - Past CV versions for consistency
4. CV draft goes to `/scratchpad/cv_draft_[company]_[date].md`
5. **Jasmin** reviews for accuracy (no false claims)
6. Cole generates the PDF via `scripts/generate_elbit_cv.py` (use as template)
7. **PDF moved to `/owner_inbox/` for approval**
8. Owner approves → file moved to `/output/cv_archive/`
9. Application logged in `cv_archive.db`

---

## CV File Naming Convention

```
Inon_Baasov_CV_[Company]_[YYYY].pdf
```

Example: `Inon_Baasov_CV_Google_2026.pdf`

---

## Application Metadata (Required for Every Application)

| Field | Required | Notes |
|-------|----------|-------|
| Company name | YES | Full legal name |
| Company location | YES | City, Country |
| Job title | YES | Exact title from JD |
| Applied date | YES | ISO format YYYY-MM-DD |
| CV version used | YES | Filename |
| Source | YES | website/linkedin/referral/recruiter/direct |
| Contact person | IF KNOWN | Name + email or LinkedIn |
| Interviewer | WHEN KNOWN | Update after first contact |
| Job URL | YES | Link to original posting |
| Status | YES | sent/screening/interview/offer/rejected/withdrawn/ghosted |
| Notes | YES | Key facts about role and company from JD |

---

## Status Update Protocol

When application status changes:
1. Update `applications.status` in `cv_archive.db`
2. Log any interview details in `interview_log` table
3. Add a note to `/memory/session_log.db` for full timeline

---

## Interview Preparation
When an interview is scheduled:
- Cole drafts 5 tailored answers to likely questions → `/scratchpad/interview_prep_[company].md`
- Owner reviews and practices before the interview
- After the interview, log questions, answers, and feedback in `interview_log`

---

## Website CV Integration
When a recruiter downloads the CV from the website:
- The website should trigger a log entry (future feature — Mack to implement)
- Track: download date, referring page, approximate location (if analytics available)
