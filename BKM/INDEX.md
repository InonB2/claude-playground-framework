# BKM Index — Standard Operating Procedures

> Business Knowledge Management: centralized procedural library.  
> All agents must check this index before executing complex tasks.  
> Last updated: 2026-04-27

| SOP Name                 | File                       | Applies To          | Summary                                              |
|--------------------------|----------------------------|---------------------|------------------------------------------------------|
| Core Onboarding          | `sop_onboarding.md`        | All Agents          | Chain of command, scratchpad rule, state logging     |
| Skills Usage             | `../skills/sop_skills.md`  | All Agents          | How to create, register, and use skills              |
| Web Security Audit       | `sop_web_security.md`      | Maya                | OWASP checklist, severity levels, findings format    |
| Web Design & Visual      | `sop_web_design.md`        | Lena                | Design audit, brief structure, visual QA protocol    |
| Web Development          | `sop_web_development.md`   | Rex                 | Code standards, deployment gate, Base44 notes        |
| CV Management            | `sop_cv_management.md`     | Cole, Silas         | CV creation, application tracking, archive protocol  |
| Session Logging          | `sop_session_logging.md`   | All Agents          | Mandatory end-of-session summary format and protocol |
| Writing Style Influences | `writing_style.md`         | Sage, Cole          | Voice references, LinkedIn post rules, writing principles |

## SOP Naming Convention
`sop_[domain]_[topic].md` — e.g. `sop_web_security.md`, `sop_db_migrations.md`

## Adding a New SOP
1. Create the SOP file in `/BKM/` following the naming convention.
2. Add a row to this index.
3. Notify Andy in `/memory/session_log.db` that a new procedure is available.
4. Update any agent files that should reference this SOP in their Startup Protocol.
