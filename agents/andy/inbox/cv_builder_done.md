# CV Builder — Delivered

CV content extracted from the most recent source (`cv_senior_pm_generic.html` + 2025/2026 archive) and structured into `scratchpad/cv_builder/cv_data.json` with full experience, education, skills, portfolio, and languages fields.
HTML renderer built at `scratchpad/cv_builder/index.html` — fetches JSON via `fetch('./cv_data.json')`, renders a clean A4 layout (Inter font, #00B4D8 accent headers, white background), includes a "Print to PDF" button, and has `@media print` + `@page` styles for clean A4 output.
To use: run `npx serve .` (or `python -m http.server 8080`) inside `scratchpad/cv_builder/`, open `http://localhost:8080`, review, then click "Print to PDF".
