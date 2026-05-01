# CV PDF Conversion — V4 TrainingPM (Elbit Netanya)
**Prepared by:** Cole (Conversion Copywriter)
**Date:** 2026-04-30

---

## File Details

| Field | Value |
|---|---|
| Source PPTX | `owner_inbox\archive\cv_archive\6486_TrainingPM_Elbit_Netanya\v4_Inon_Baasov_CV_TrainingPM.pptx` |
| Output PDF | `owner_inbox\archive\cv_archive\6486_TrainingPM_Elbit_Netanya\v4_Inon_Baasov_CV_TrainingPM.pdf` |
| Method | Microsoft PowerPoint COM automation (Windows) |
| Requirement | PowerPoint must be installed on the machine |

---

## PowerShell Command (Copy and Run As-Is)

```powershell
$pptxPath = "D:\Claude Playground\owner_inbox\archive\cv_archive\6486_TrainingPM_Elbit_Netanya\v4_Inon_Baasov_CV_TrainingPM.pptx"
$pdfPath  = "D:\Claude Playground\owner_inbox\archive\cv_archive\6486_TrainingPM_Elbit_Netanya\v4_Inon_Baasov_CV_TrainingPM.pdf"

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

$presentation = $ppt.Presentations.Open($pptxPath, $false, $false, $true)
$presentation.SaveAs($pdfPath, 32)   # 32 = ppSaveAsPDF
$presentation.Close()
$ppt.Quit()

[System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "PDF saved to: $pdfPath"
```

---

## How to Run This

**Option A — Paste directly into PowerShell:**
Open PowerShell (not CMD), paste the entire block above, press Enter.

**Option B — Ask Yoni or Andy to run it:**
The command is ready to execute. Tell Andy "run the CV PDF conversion for v4 TrainingPM" and share this file.

**Option C — Claude Code terminal:**
The Claude Code terminal is PowerShell-capable. Andy can run this command directly in the Claude Code session.

---

## Caveats and Requirements

1. **The PPTX must be closed in PowerPoint before running this command.**
   If the file is open, PowerPoint may lock it or export a cached version without your latest edits. Save and close before running.

2. **Microsoft PowerPoint must be installed.**
   This uses COM automation — it requires a full PowerPoint installation (Office 365, Office 2019/2021, or Office 2016+). LibreOffice or online converters will not work identically; fonts and layout may shift.

3. **Font fidelity warning.**
   If the PPTX uses custom or downloaded fonts, the PDF will render correctly only if those fonts are installed on the same machine where PowerPoint is running. Verify the output PDF visually before submitting to Elbit.

4. **Run from a path with no special characters.**
   The path `D:\Claude Playground\...` contains a space. The PowerShell command above wraps paths in quotes, which handles this correctly. Do not shorten or modify the path.

5. **SaveAs format code 32 = ppSaveAsPDF.**
   This is the official Microsoft enumeration value. It produces a standard PDF/A-compatible output suitable for email submission and ATS (Applicant Tracking System) ingestion.

6. **The output PDF will appear in the same folder as the source PPTX:**
   `D:\Claude Playground\owner_inbox\archive\cv_archive\6486_TrainingPM_Elbit_Netanya\`

---

## After Conversion

- Open the PDF and check: layout, fonts, alignment, page count
- Confirm the file size is reasonable (typically 300KB–2MB for a single-page CV)
- If anything looks off, re-open the PPTX in PowerPoint, fix, save, close, then re-run the command
- Once approved, this PDF is ready for Elbit submission under task ELBIT-APPLY-001

---

*Cole — Conversion Copywriter | V4 TrainingPM Elbit Netanya | 2026-04-30*
