# Autopsy Demo — Team Plan & Presenter Guide

Live version: https://claude.ai/artifact/KtV1Jx3RFZyNDgJkPV52E6

## At a glance

Gautham presents and runs the live demo on his CachyOS laptop; Archana opens the talk, runs a pre-processed backup case on her Windows laptop and owns the report submission.

| Item | Detail |
| --- | --- |
| Demo | Tuesday 27 Oct 2026, Team 1 (first slot) |
| Main laptop | Gautham — CachyOS, Autopsy, live demo + slides |
| Backup laptop | Archana — Windows, same case already processed, slides open |
| Evidence | USB_Evidence_RM01.dd (64 MB), MD5 bacea5569e56c15fd14d6a4f7023c006 |
| Talk length | Planned for 12 min + 3 min Q&A — confirm the slot length with Dr. Rajeshwari |

## Work split before Tuesday

**Gautham (CachyOS, presenter)**

- [ ] Sat — Unzip the evidence image and run the full case once using the demo script; note anything that differs
- [ ] Sat — Untick aLEAPP, iLEAPP and YARA in the ingest screen (Windows-only); confirm ingest finishes
- [ ] Sun — Make Autopsy readable on a projector: start it with `autopsy --fontsize 16` and test at 1920×1080
- [ ] Sun — Rehearse slides 5–16 out loud twice with a timer (target 9 min)
- [ ] Mon — Keep a finished copy of the case as a fallback in case live ingest fails
- [ ] Mon — Test HDMI / USB-C output and screen mirroring on CachyOS

**Archana (Windows, opener + backup)**

- [ ] Sat — Run the same case on Windows so a fully processed case is ready on her laptop
- [ ] Sat — Read the report end to end and fix anything that reads wrong
- [ ] Sun — If faculty wants your own screenshots: retake figures 1–14 on Windows and paste them over the report images
- [ ] Sun — Rehearse slides 1–4 (target 3 min) and the theory answers in the Q&A bank
- [ ] Mon — Export the report to PDF; keep .docx and .pdf ready for submission
- [ ] Mon — Copy the deck, report and evidence zip to a pen drive and her laptop

**Both**

- [ ] Mon evening — Full run-through: slides + live demo + 5 practice questions, timed
- [ ] Mon evening — Agree the hand-over cue (slide 5) and the fallback signal if the demo stalls

## Presentation run-sheet (12 min)

| Slide | Speaker | Time | Key line |
| --- | --- | --- | --- |
| 1 Title | Archana | 0:00–0:30 | "We are Team 1; our tool is Autopsy and our use case is storage drive evidence analysis." |
| 2 What is Autopsy | Archana | 0:30–1:30 | Open-source GUI on The Sleuth Kit; never writes to evidence; v4.23.1. |
| 3 How it flows | Archana | 1:30–2:15 | Case → data source → ingest modules → blackboard → review → report. |
| 4 Where it's used | Archana | 2:15–3:00 | Ours is the corporate insider-threat case. Hand over to Gautham. |
| 5 Installing | Gautham | 3:00–3:40 | Windows = MSI; Linux = snap/AUR or ZIP; Java 21 and Windows-only module gotchas. |
| 6 The case | Gautham | 3:40–4:10 | Seized USB, Project Falcon leak, MD5 shown. |
| 7 Three questions | Gautham | 4:10–4:40 | Q1 what's on it, Q2 who it was going to, Q3 when and where. |
| 8 Demo plan | Gautham | 4:40–5:00 | Switch to Autopsy (Alt+Tab). |
| LIVE DEMO | Gautham | 5:00–10:00 | Follow the demo script. Archana gives 1-minute warnings. |
| 9–14 Findings | Gautham | (backup) | Skip if the demo worked; use instead of the demo if it fails. Slide 14 (drawn timeline) is worth showing either way. |
| 15 Integrity + report | Gautham | 10:00–10:45 | Hashes match → evidence unchanged; one-click HTML report. |
| 16 Conclusion | Archana | 10:45–12:00 | Answer Q1, Q2, Q3 from the slide. "Questions?" |

If the slot is shorter, cut slide 4 and shorten the demo to deleted files, mismatch and keyword hits.

## Live demo script (5 min)

1. **Create the case** — Case → New Case. Name `RIT-DF-2026-01_Falcon_Leak` → Next. Number `RIT-DF-2026-01`, Examiner `Gautham, Archana` → Finish.
   - Say: "The case folder holds everything; the evidence is never modified."
2. **Add the image** — Add Data Source → Next → Disk Image or VM File → Next. Browse to `USB_Evidence_RM01.dd`, time zone Asia/Calcutta, paste MD5 `bacea5569e56c15fd14d6a4f7023c006` → Next.
   - Say: "The acquisition hash lets Autopsy prove the image hasn't changed."
3. **Configure ingest** — Tick Keyword Search → Global Settings → New List `Falcon_Case` → New Keywords: falcon, confidential, transfer → Substring Match → OK → OK. Untick aLEAPP, iLEAPP, YARA → Next → Finish.
   - Say: "Ingest modules run automatically over every file, even deleted ones."
4. **Deleted files** — File Views → Deleted Files → File System → `email_draft.txt` → Text tab.
   - Say: "Deleted on FAT doesn't mean gone — here's the e-mail offering the design for money."
5. **Disguised file** — Analysis Results → Extension Mismatch Detected → `track01.mp3` → Text tab.
   - Say: "The name says MP3, the content says PDF — Falcon wiring schematics."
6. **Keyword hits** — Analysis Results → Keyword Hits → Falcon_Case → falcon → `todo.txt`.
   - Say: "The suspect's own plan: copy, rename, send, delete."
7. **E-mail regex** — Toolbar Keyword Search → Regular Expression → `[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}` → Search.
8. **EXIF + ZIP** — Analysis Results → EXIF Metadata (date and GPS). Then Data Sources → Archive → `backup_oct.zip` → `Falcon_BOM.csv`.
9. **Timeline** — Toolbar Timeline → List. Scroll 11 → 13 Oct.
10. **Integrity** — Envelope icon (Ingest Inbox) → "Integrity … verified". Back to slide 15.

If the tree doesn't show new results after ingest, collapse and re-expand Analysis Results.

## CachyOS setup and fallback plan

| Check | How | If it fails |
| --- | --- | --- |
| Java version | `java -version` should show 21 | `sudo pacman -S jdk21-openjdk`, start Autopsy with `--jdkhome /usr/lib/jvm/java-21-openjdk` |
| Windows-only modules | Untick aLEAPP, iLEAPP, YARA | Ingest refuses to start until unticked |
| Text size on projector | Start with `--fontsize 16` | Use the slide 9–13 screenshots instead |
| Wayland glitches | Java runs under XWayland | Log in to an X11 session for the demo |
| Keyword search won't start | Watch for a "Solr" error when opening the case | Reopen the case; fall back to Archana's laptop |
| Geolocation map | Needs internet for map tiles | Show the EXIF Metadata table instead |

**Fallback ladder (decide in 10 seconds):**

1. Live ingest fails → open the pre-processed case on Gautham's laptop and continue from step 4.
2. Gautham's laptop fails → switch HDMI to Archana's laptop with the same case open.
3. Both fail → present slides 9–15 (real screenshots of this case).

## Q&A bank

| Likely question | Who | Short answer |
| --- | --- | --- |
| How can a deleted file still be read? | Archana | On FAT, deleting only marks the directory entry (first byte 0xE5) and frees the clusters; data stays until overwritten. |
| Deleted-file recovery vs file carving? | Archana | Recovery uses surviving file-system metadata; carving (PhotoRec) finds files in unallocated space by signature — it carved a second copy of the design PDF. |
| How did it know track01.mp3 was a PDF? | Gautham | It reads the file signature (`%PDF` at the start), not the extension. |
| Why hash the image? | Archana | MD5/SHA-256 prove the evidence is unchanged since acquisition — chain of custody. |
| Does Autopsy change the evidence? | Archana | No — the image is read-only; output goes to the case folder. |
| Why didn't the Email Addresses list find the addresses? | Gautham | We used reserved `.test` domains, which its built-in pattern skips; a custom regex found them. |
| Why 05:30 for access times? | Gautham | FAT stores only the access date, so it shows midnight UTC = 05:30 IST. |
| Could timestamps be faked? | Archana | Yes — investigators correlate several sources (EXIF, file system, e-mail). |
| Can Autopsy recover overwritten data? | Archana | No — once clusters are overwritten the content is gone. |
| Autopsy vs FTK Imager? | Gautham | FTK Imager acquires and previews; Autopsy is the full analysis platform. Often used together. |
| What else can Autopsy analyse? | Archana | NTFS/ext4/APFS disks, registry, browser history, Android/iOS extractions, e-mail files. |

## Day-of checklist

- [ ] Gautham: laptop charged + charger, HDMI/USB-C adapter
- [ ] Gautham: Autopsy open at the Welcome screen (`--fontsize 16`), deck in a second window
- [ ] Gautham: `USB_Evidence_RM01.dd` and the fallback case folder on the desktop
- [ ] Gautham: notifications off, Wi-Fi on if possible
- [ ] Archana: Windows laptop with the processed case open, deck open, charged
- [ ] Archana: report PDF ready, pen drive with all files
- [ ] Archana: phone timer for 1-minute warnings
- [ ] Both: arrive 10 minutes early and test the projector
