# Autopsy — Storage Drive Evidence Analysis

Digital forensics tool demonstration for **Introduction to Digital Forensics (23CIOE09)**, Department of CSE (AI & ML) and CSE (Cyber Security), Ramaiah Institute of Technology.

| | |
| --- | --- |
| Team | 1 — Gautham (1MS23EC040), Archana (1MS24EC400) |
| Tool | [Autopsy](https://www.autopsy.com) 4.23.1 |
| Use case | Storage Drive Evidence Analysis |
| Demo date | 27 October 2026 |
| Faculty | Dr. Rajeshwari S B |

## The case

A fictional employee is suspected of leaking the confidential **Project Falcon** drone design to a competitor. A USB pen drive was seized and imaged (`USB_Evidence_RM01.dd`, 64 MB, FAT32). Analysis in Autopsy shows:

- **Deleted files recovered** — the design PDF and an e-mail draft offering it for money
- **Disguised file exposed** — a PDF renamed to `track01.mp3` (Extension Mismatch Detector)
- **ZIP unpacked automatically** — `Falcon_BOM.csv` inside `backup_oct.zip`
- **Keyword and regex hits** — the suspect's plan in `todo.txt` and the recipient `arjun.k@rivaltech.test`
- **EXIF + GPS** — two photos placed in Bengaluru on 11 and 13 Oct 2026
- **Timeline** — the 11–13 Oct sequence of events
- **Integrity verified** — MD5 and SHA-256 match the acquisition hashes

All names, companies and addresses are fictional; `.test` is a reserved domain.

## Repository contents

| Path | What it is |
| --- | --- |
| `report/` | Demonstration report (RIT template) as `.docx` and `.pdf` |
| `slides/` | 16-slide presentation with speaker notes and demo script |
| `evidence/USB_Evidence_RM01.zip` | The evidence disk image used in the demo |
| `screenshots/` | 14 screenshots from the Autopsy analysis, in report order |
| `docs/presenter_guide.md` | Work split, run-sheet, live demo script, fallback plan, Q&A bank |
| `tools/` | Scripts that generated the evidence image, report and slides |

## Evidence hashes

```
File:    USB_Evidence_RM01.dd (inside evidence/USB_Evidence_RM01.zip)
MD5:     bacea5569e56c15fd14d6a4f7023c006
SHA-256: 24083aa3ae08dbe10d585d3ea9280c43fe2c4ddf379b339711c92c36c937f107
```

Verify after unzipping: `md5sum USB_Evidence_RM01.dd` (Linux) or `Get-FileHash -Algorithm MD5 USB_Evidence_RM01.dd` (Windows PowerShell).

## Reproducing the analysis

1. Install Autopsy (Windows MSI, or on Linux the official ZIP with **Java 21**).
2. Case → New Case → `RIT-DF-2026-01_Falcon_Leak`.
3. Add Data Source → Disk Image or VM File → `USB_Evidence_RM01.dd`, time zone Asia/Calcutta, enter the MD5 above.
4. Keyword Search → Global Settings → new list `Falcon_Case` with `falcon`, `confidential`, `transfer` (substring match).
5. On Linux, untick the Windows-only aLEAPP, iLEAPP and YARA modules; run ingest.
6. Review Deleted Files, Extension Mismatch, Keyword Hits, EXIF Metadata and Timeline; for e-mails run a regex search: `[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}`.

To rebuild the evidence image from scratch (Linux, needs `mtools`, `dosfstools`, Pillow, piexif, reportlab): `python3 tools/make_evidence.py`.

## References

- Autopsy — https://www.autopsy.com
- Autopsy User Guide — https://sleuthkit.org/autopsy/docs/user-docs/latest/
- The Sleuth Kit — https://www.sleuthkit.org/sleuthkit/
