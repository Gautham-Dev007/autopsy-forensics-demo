const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { imageSize } = require("./imgsize");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Evidence",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "141B26", lt1: "FFFFFF", dk2: "1C2A3F", lt2: "EEF1F5",
    accent1: "F2A900", accent2: "D7263D", accent3: "2E8B9A", accent4: "5B6B82",
    accent5: "8FA3BF", accent6: "3C9D5D", hlink: "2E8B9A", folHlink: "5B6B82",
  },
};
const HEX = THEME.colors;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625
  pres.author = "Gautham, Archana";
  pres.title = "Autopsy – Storage Drive Evidence Analysis";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: "TITLE_DARK",
    background: { color: C.text2 },
    objects: [],
    slideNumber: undefined,
  });
  pres.defineSlideMaster({
    title: "SECTION_DARK",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.9, w: 8.8, h: 1.0, fontSize: 36, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 2.95, w: 8.8, h: 0.9, fontSize: 16, color: C.accent5, valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.5, 0.4, 0.5],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.25, w: 9.0, h: 0.7, fontSize: 28, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "Autopsy · Team 1 · 23CIOE09", options: { x: 0.5, y: 5.25, w: 5, h: 0.25, fontSize: 9, color: C.accent4, margin: 0 } } },
    ],
    slideNumber: { x: 9.1, y: 5.25, w: 0.4, h: 0.25, fontSize: 9, color: "5B6B82", align: "right" },
  });

  const imgFit = (slide, path, box, extra = {}) => {
    const { width, height } = imageSize(path);
    let w = box.w, h = (box.w * height) / width;
    if (h > box.h) { h = box.h; w = (box.h * width) / height; }
    const x = box.x + (box.w - w) / 2, y = box.y + (box.h - h) / 2;
    slide.addImage({ path, x, y, w, h, objectName: extra.name || "screenshot",
      shadow: { type: "outer", color: "000000", opacity: 0.25, blur: 4, offset: 2, angle: 90 } });
    return { x, y, w, h };
  };
  const tag = (slide, text, x, y, w, color = C.accent2) => {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.32, fill: { color }, rectRadius: 0.06, line: { color, width: 0 }, objectName: "tag" });
    slide.addText(text, { x, y, w, h: 0.32, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  };
  const bulletList = (slide, items, box, size = 14) => {
    slide.addText(items.map((t, i) => {
      const parts = Array.isArray(t) ? t : [{ text: t }];
      return parts.map((p, j) => ({ text: p.text, options: { bold: !!p.bold, color: p.color || C.text1, bullet: { indent: 14 }, breakLine: j === parts.length - 1 && i < items.length - 1, paraSpaceAfter: 6 } }));
    }).flat(), { ...box, fontSize: size, valign: "top", margin: 0, isTextBox: true, color: C.text1 });
  };

  const ICON = {
    search: await icon(fa.FaSearch, HEX.accent1), trash: await icon(fa.FaTrashRestore, HEX.accent1),
    mask: await icon(fa.FaMask, HEX.accent1), map: await icon(fa.FaMapMarkerAlt, HEX.accent1),
    clock: await icon(fa.FaClock, HEX.accent1), shield: await icon(fa.FaShieldAlt, HEX.accent1),
    gavel: await icon(fa.FaGavel, HEX.background1), building: await icon(fa.FaBuilding, HEX.background1),
    bolt: await icon(fa.FaBolt, HEX.background1), mobile: await icon(fa.FaMobileAlt, HEX.background1),
    camera: await icon(fa.FaCamera, HEX.background1), grad: await icon(fa.FaGraduationCap, HEX.background1),
    usb: await icon(fa.FaUsb, HEX.accent1), windows: await icon(fa.FaWindows, HEX.dk2), linux: await icon(fa.FaLinux, HEX.dk2),
    warn: await icon(fa.FaExclamationTriangle, HEX.accent2),
  };

  // ---------- 1. Title ----------
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
  s.addImage({ path: "img/welcome.png", x: 6.1, y: 1.35, w: 3.4, h: 3.4 * 305 / 475, objectName: "autopsy splash",
    shadow: { type: "outer", color: "000000", opacity: 0.4, blur: 8, offset: 3, angle: 90 } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 0.3, w: 2.3, h: 0.72, fill: { color: C.background1 }, line: { width: 0, color: C.background1 }, rectRadius: 0.06, objectName: "logo card" });
  s.addImage({ path: "img/rit_logo.jpg", x: 0.7, y: 0.37, w: 2.1, h: 2.1 * 656590 / 2383790, objectName: "RIT logo" });
  s.addText("DIGITAL FORENSICS TOOL DEMONSTRATION", { x: 0.6, y: 1.2, w: 5.3, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 2, margin: 0, isTextBox: true });
  s.addText("Autopsy", { x: 0.6, y: 1.55, w: 5.3, h: 0.95, fontSize: 54, bold: true, color: C.background1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addText("Storage Drive Evidence Analysis", { x: 0.6, y: 2.5, w: 5.3, h: 0.5, fontSize: 22, color: C.accent5, margin: 0, isTextBox: true });
  s.addText([
    { text: "Team 1 · Gautham (1MS23EC040) · Archana (1MS24EC400)", options: { breakLine: true } },
    { text: "Introduction to Digital Forensics (23CIOE09) · 27 Oct 2026", options: { breakLine: true } },
    { text: "Faculty: Dr. Rajeshwari S B · Ramaiah Institute of Technology" },
  ], { x: 0.6, y: 3.75, w: 5.4, h: 1.0, fontSize: 12, color: C.background1, margin: 0, paraSpaceAfter: 4, isTextBox: true });
  s.addNotes("Introduce the team and the tool. Autopsy is the first tool in the schedule, so we set the stage: it's the open-source standard for disk and storage-drive forensics. Today we analyse a seized USB pen drive image live.");

  // ---------- 2. What is Autopsy ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
  s.addText("What is Autopsy?", { placeholder: "title" });
  bulletList(s, [
    "Open-source digital forensics platform — a GUI on top of The Sleuth Kit (TSK)",
    "Maintained by Sleuth Kit Labs; created by Brian Carrier",
    "Runs on Windows (MSI), Linux and macOS; written in Java",
    "Reads raw/dd, E01, VHD, VMDK images, physical disks and logical files",
    "File systems: NTFS, FAT, exFAT, ext2/3/4, HFS+, APFS, ISO 9660",
    "Never writes to the evidence — everything lives in a separate case folder",
  ], { x: 0.5, y: 1.15, w: 5.4, h: 3.8 }, 15);
  const stats = [["Free", "open source, Apache 2.0"], ["4.23.1", "latest release (2026)"], ["20+", "built-in ingest modules"]];
  stats.forEach(([big, small], i) => {
    const y = 1.15 + i * 1.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.3, y, w: 3.2, h: 1.1, fill: { color: C.background2 }, line: { color: C.background2, width: 0 }, rectRadius: 0.08, objectName: "stat card" });
    s.addText(big, { x: 6.5, y: y + 0.08, w: 2.9, h: 0.6, fontSize: 30, bold: true, color: C.accent3, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
    s.addText(small, { x: 6.5, y: y + 0.68, w: 2.9, h: 0.32, fontSize: 12, color: C.accent4, margin: 0, isTextBox: true });
  });
  s.addNotes("Key point: Autopsy is the graphical front-end; the heavy lifting of parsing file systems is done by The Sleuth Kit. Because it's open source, results can be independently verified — important in court. Latest version 4.23.1; 4.23.0 (April 2026) added an MCP server for AI-assisted summaries.");

  // ---------- 3. How it works ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
  s.addText("How an Autopsy investigation flows", { placeholder: "title" });
  const flow = [["Case", "folder + database"], ["Data source", "disk image, read-only"], ["Ingest modules", "automatic analysis"], ["Blackboard", "results stored"], ["Review", "tree, timeline, search"], ["Report", "HTML / Excel / KML"]];
  flow.forEach(([t, sub], i) => {
    const x = 0.5 + i * 1.53;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 1.33, h: 1.25, fill: { color: i === 2 ? C.accent1 : C.text2 }, line: { width: 0, color: C.text2 }, rectRadius: 0.08, objectName: "flow step" });
    s.addText(String(i + 1), { x, y: 1.58, w: 1.33, h: 0.35, fontSize: 14, bold: true, color: i === 2 ? C.text2 : C.accent1, align: "center", margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.05, y: 1.92, w: 1.23, h: 0.42, fontSize: 13, bold: true, color: i === 2 ? C.text2 : C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(sub, { x: x + 0.05, y: 2.32, w: 1.23, h: 0.36, fontSize: 10, color: i === 2 ? C.text2 : C.accent5, align: "center", valign: "top", margin: 0, isTextBox: true });
    if (i < flow.length - 1) s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: x + 1.37, y: 2.02, w: 0.12, h: 0.2, rotate: 90, fill: { color: C.accent4 }, line: { width: 0, color: C.accent4 }, objectName: "arrow" });
  });
  s.addText("Ingest modules we use today", { x: 0.5, y: 3.15, w: 9, h: 0.35, fontSize: 15, bold: true, color: C.text2, margin: 0, isTextBox: true });
  const mods = ["File Type Identification", "Extension Mismatch Detector", "Embedded File Extractor", "Picture Analyzer (EXIF)", "Keyword Search", "PhotoRec Carver", "Data Source Integrity"];
  mods.forEach((m, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5 + col * 2.27, y: 3.6 + row * 0.6, w: 2.12, h: 0.46, fill: { color: C.background2 }, line: { width: 0, color: C.background2 }, rectRadius: 0.06, objectName: "module chip" });
    s.addText(m, { x: 0.5 + col * 2.27, y: 3.6 + row * 0.6, w: 2.12, h: 0.46, fontSize: 11, color: C.text2, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("Walk the pipeline: we create a case, add the image read-only, ingest modules run in parallel and post findings to the blackboard, then we review and report. The modules in the chips are exactly the ones we enable in the live demo.");

  // ---------- 4. Applications ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
  s.addText("Where Autopsy is used", { placeholder: "title" });
  const apps = [[ICON.gavel, "Law enforcement", "Seized PCs, drives and memory cards"], [ICON.building, "Corporate / insider threat", "IP theft and data-leak cases"], [ICON.bolt, "Incident response", "Triage of compromised hosts"],
    [ICON.camera, "Media & geolocation", "EXIF, GPS, camera details"], [ICON.mobile, "Mobile artifacts", "Android / iOS extractions"], [ICON.grad, "Education & training", "Free, standard workflow"]];
  apps.forEach(([ic, t, d], i) => {
    const col = i % 3, row = Math.floor(i / 3), x = 0.5 + col * 3.05, y = 1.2 + row * 1.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.85, h: 1.75, fill: { color: C.background2 }, line: { width: 0, color: C.background2 }, rectRadius: 0.08, objectName: "app card" });
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.22, w: 0.62, h: 0.62, fill: { color: C.text2 }, line: { width: 0, color: C.text2 }, objectName: "icon circle" });
    s.addImage({ data: ic, x: x + 0.34, y: y + 0.36, w: 0.34, h: 0.34, objectName: "icon" });
    s.addText(t, { x: x + 0.2, y: y + 0.95, w: 2.5, h: 0.35, fontSize: 14, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.2, y: y + 1.28, w: 2.5, h: 0.35, fontSize: 12, color: C.accent4, margin: 0, isTextBox: true });
  });
  s.addNotes("Our scenario sits in the corporate / insider-threat box: an employee suspected of leaking a confidential design.");

  // ---------- 5. Installation ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
  s.addText("Installing Autopsy", { placeholder: "title" });
  const colInst = (x, ic, head, lines) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.15, w: 4.35, h: 2.75, fill: { color: C.background2 }, line: { width: 0, color: C.background2 }, rectRadius: 0.08, objectName: "install card" });
    s.addImage({ data: ic, x: x + 0.25, y: 1.32, w: 0.4, h: 0.4, objectName: "os icon" });
    s.addText(head, { x: x + 0.8, y: 1.3, w: 3.4, h: 0.45, fontSize: 17, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
    s.addText(lines.map((l, i) => ({ text: l, options: { bullet: { type: "number" }, breakLine: i < lines.length - 1, paraSpaceAfter: 5 } })),
      { x: x + 0.25, y: 1.88, w: 3.9, h: 1.95, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  };
  colInst(0.5, ICON.windows, "Windows (easiest)", ["Download the 64-bit MSI from autopsy.com", "Run as administrator → Install", "Java and Sleuth Kit are bundled", "Launch → Welcome screen → New Case"]);
  colInst(5.15, ICON.linux, "Linux (Ubuntu)", ["Quick: sudo snap install autopsy", "Latest: install Java 21 + Sleuth Kit 4.15", "Run install_application.sh with the ZIP", "Start ~/autopsy/bin/autopsy"]);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.1, w: 9.0, h: 0.95, fill: { color: "FBE9EC" }, line: { width: 0, color: "FBE9EC" }, rectRadius: 0.08, objectName: "gotcha box" });
  s.addImage({ data: ICON.warn, x: 0.7, y: 4.36, w: 0.42, h: 0.42, objectName: "warning icon" });
  s.addText([{ text: "Gotchas we hit on Linux: ", options: { bold: true } }, { text: "4.23.1 needs Java 21 (Java 17 fails with UnsupportedClassVersionError); untick the Windows-only aLEAPP, iLEAPP and YARA modules or ingest won't start." }],
    { x: 1.3, y: 4.15, w: 8.0, h: 0.85, fontSize: 13, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  s.addNotes("On Windows it's a one-click MSI. On Linux the snap is quickest; the official ZIP gives the latest version but needs Java 21 and The Sleuth Kit. Mention the two real issues we ran into while preparing.");

  // ---------- 6. Scenario ----------
  pres.addSection({ title: "Use case" });
  s = pres.addSlide({ masterName: "SECTION_DARK", sectionTitle: "Use case" });
  s.addText("The case: Project Falcon leak", { placeholder: "title" });
  s.addText("A (fictional) employee is suspected of leaking a confidential drone design to a competitor. A USB pen drive was seized and imaged.", { placeholder: "body" });
  s.addImage({ data: ICON.usb, x: 0.6, y: 1.05, w: 0.6, h: 0.6, objectName: "usb icon" });
  s.addText([
    { text: "Evidence: ", options: { bold: true, color: HEX.accent1 } }, { text: "USB_Evidence_RM01.dd · 64 MB · FAT32", options: { breakLine: true } },
    { text: "MD5: ", options: { bold: true, color: HEX.accent1 } }, { text: "bacea5569e56c15fd14d6a4f7023c006" },
  ], { x: 0.6, y: 4.0, w: 8.8, h: 0.75, fontSize: 13, color: C.background1, fontFace: "Courier New", margin: 0, isTextBox: true });
  s.addNotes("Set up the story. Questions to answer: Is Falcon material on the drive, including hidden or deleted files? Who was it going to? When and where did it happen? All names and domains are fictional; .test is a reserved domain.");

  // ---------- 6b. Questions ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Use case" });
  s.addText("Three questions the drive must answer", { placeholder: "title" });
  [["Q1", "What Falcon material is on the drive?", "Including anything deleted, renamed or compressed"],
   ["Q2", "Who was it going to?", "Any contact, address or plan linking it to an outsider"],
   ["Q3", "When and where did it happen?", "Timestamps, photo metadata, sequence of events"]].forEach(([n, t, d], i) => {
    const x = 0.5 + i * 3.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.25, w: 2.85, h: 3.2, fill: { color: C.background2 }, line: { width: 0, color: C.background2 }, rectRadius: 0.08, objectName: "question card" });
    s.addText(n, { x: x + 0.25, y: 1.45, w: 2.4, h: 0.75, fontSize: 40, bold: true, color: C.accent1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: 2.3, w: 2.4, h: 1.0, fontSize: 18, bold: true, color: C.text2, valign: "top", margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.25, y: 3.35, w: 2.4, h: 0.9, fontSize: 13, color: C.accent4, valign: "top", margin: 0, isTextBox: true });
  });
  s.addText("Answers on the last slide.", { x: 0.5, y: 4.65, w: 9, h: 0.35, fontSize: 13, italic: true, color: C.accent4, margin: 0, isTextBox: true });
  s.addNotes("These three questions drive the whole demo. Every finding we show answers one of them; the conclusion slide gives the answers.");

  // ---------- 7. Demo steps ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Use case" });
  s.addText("Live demo: what we will do", { placeholder: "title" });
  const steps = [["Create case", "case number + examiner"], ["Add image", "IST time zone + MD5/SHA-256"], ["Keyword list", "falcon · confidential · transfer"], ["Run ingest", "7 modules, ~30 seconds"], ["Review results", "deleted, mismatch, hits, EXIF"], ["Timeline + report", "sequence of events, HTML"]];
  steps.forEach(([t, d], i) => {
    const col = i % 3, row = Math.floor(i / 3), x = 0.5 + col * 3.05, y = 1.25 + row * 1.2;
    s.addShape(pres.shapes.OVAL, { x, y, w: 0.6, h: 0.6, fill: { color: C.accent1 }, line: { width: 0, color: C.accent1 }, objectName: "step number" });
    s.addText(String(i + 1), { x, y, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: C.text2, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.75, y: y - 0.02, w: 2.2, h: 0.34, fontSize: 15, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.75, y: y + 0.32, w: 2.2, h: 0.32, fontSize: 12, color: C.accent4, margin: 0, isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 3.65, w: 9.0, h: 1.35, fill: { color: C.background2 }, line: { width: 0, color: C.background2 }, rectRadius: 0.08, objectName: "settings box" });
  s.addText([
    { text: "Case: ", options: { bold: true } }, { text: "RIT-DF-2026-01_Falcon_Leak", options: { fontFace: "Courier New", breakLine: true } },
    { text: "Image MD5: ", options: { bold: true } }, { text: "bacea5569e56c15fd14d6a4f7023c006", options: { fontFace: "Courier New", breakLine: true } },
    { text: "Keyword list: ", options: { bold: true } }, { text: "Falcon_Case = falcon, confidential, transfer (substring)", options: { breakLine: true } },
    { text: "E-mail regex: ", options: { bold: true } }, { text: "[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}", options: { fontFace: "Courier New" } },
  ], { x: 0.75, y: 3.72, w: 8.5, h: 1.22, fontSize: 13, color: C.text1, valign: "middle", margin: 0, paraSpaceAfter: 2, isTextBox: true });
  s.addNotes("DEMO SCRIPT: 1) Case → New Case, name RIT-DF-2026-01_Falcon_Leak, number RIT-DF-2026-01, examiners. 2) Add Data Source → Disk Image or VM File → USB_Evidence_RM01.dd, time zone Asia/Calcutta, paste MD5 bacea5569e56c15fd14d6a4f7023c006. 3) Ingest screen → Keyword Search → Global Settings → New List 'Falcon_Case' → New Keywords falcon / confidential / transfer as Substring Match. 4) Tick the modules and Finish. Ingest takes under a minute on this 64 MB image. Backup plan if anything fails live: use the screenshots on the next slides.");

  // ---------- 8-12 findings ----------
  pres.addSection({ title: "Findings" });
  const qChip = (sl, q) => {
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y: 0.38, w: 0.75, h: 0.42, fill: { color: C.accent1 }, line: { width: 0, color: C.accent1 }, rectRadius: 0.06, objectName: "question chip" });
    sl.addText(q, { x: 8.75, y: 0.38, w: 0.75, h: 0.42, fontSize: 14, bold: true, color: C.text2, align: "center", valign: "middle", margin: 0, isTextBox: true });
  };
  // side layout: tall screenshot left, notes right
  const findingSide = (title, q, img, tagText, points, notes, tagColor) => {
    const sl = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
    sl.addText(title, { placeholder: "title" });
    qChip(sl, q);
    imgFit(sl, img, { x: 0.5, y: 1.1, w: 6.1, h: 4.0 });
    tag(sl, tagText, 6.85, 1.15, 2.65, tagColor);
    bulletList(sl, points, { x: 6.85, y: 1.65, w: 2.65, h: 3.4 }, 13);
    sl.addNotes(notes);
    return sl;
  };
  // wide layout: wide screenshot on top, notes in two columns below
  const findingWide = (title, q, img, imgH, tagText, points, notes, tagColor) => {
    const sl = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
    sl.addText(title, { placeholder: "title" });
    qChip(sl, q);
    const r = imgFit(sl, img, { x: 0.5, y: 1.1, w: 9.0, h: imgH });
    const y = r.y + r.h + 0.3;
    tag(sl, tagText, 0.5, y, 2.65, tagColor);
    const half = Math.ceil(points.length / 2);
    bulletList(sl, points.slice(0, half), { x: 3.4, y, w: 2.95, h: 5.05 - y }, 13);
    bulletList(sl, points.slice(half), { x: 6.55, y, w: 2.95, h: 5.05 - y }, 13);
    sl.addNotes(notes);
    return sl;
  };
  findingSide("Deleted files are not gone", "Q1", "img/f_deleted.png", "DELETED · RECOVERED",
    ["Deleted Files lists 2 files marked with a red X", "email_draft.txt: “Attaching the Falcon design and the BOM… transfer the agreed amount”", "Addressed to arjun.k@rivaltech.test", "FAT only marks the entry deleted — data stays until overwritten"],
    "Click File Views → Deleted Files → File System. Select email_draft.txt and show the Text tab. Then select Project_Falcon_Design.pdf — 'CONFIDENTIAL – NEXORA LABS'. PhotoRec also carved a second copy of the PDF under $CarvedFiles.");
  findingWide("A PDF pretending to be music", "Q1", "img/f_mismatch.png", 2.7, "DISGUISED FILE",
    ["track01.mp3 flagged Likely Notable", "Detected MIME type: application/pdf", "Content: Project Falcon – Wiring Schematics", "Type comes from the file signature (%PDF), not the extension"],
    "Analysis Results → Extension Mismatch Detected. Explain file signatures / magic bytes: Autopsy identifies type from content, not the extension. Optional: open the Hex tab to show %PDF at offset 0.", HEX.accent1);
  findingWide("Keyword search connects the dots", "Q2", "img/f_keyword.png", 2.7, "14 KEYWORD HITS",
    ["falcon (9), confidential (3), transfer (2)", "Hits inside the deleted draft, the ZIP, file slack and unallocated space", "todo.txt is the plan: copy → rename → send → delete"],
    "Analysis Results → Keyword Hits → Falcon_Case → falcon. Select todo.txt — the highlighted hit shows the 4-step plan.", HEX.accent3);
  findingWide("A regex finds who it was going to", "Q2", "img/f_regex.png", 1.75, "E-MAIL ADDRESSES",
    ["Pattern: [a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}", "Recipient: arjun.k@rivaltech.test", "Sender: r.mehta.personal@mailbox.test", "Found in todo.txt, the deleted draft and unallocated space"],
    "Toolbar Keyword Search box → Regular Expression → paste the pattern → Search. The built-in Email Addresses list ignores the reserved .test domain, which is why a custom regex is used.", HEX.accent3);
  // EXIF + ZIP
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("Photos and archives tell more", { placeholder: "title" });
  qChip(s, "Q3");
  imgFit(s, "img/f_exif.png", { x: 0.5, y: 1.15, w: 9.0, h: 0.75 }, { name: "exif table" });
  imgFit(s, "img/f_zip.png", { x: 0.5, y: 2.15, w: 5.3, h: 2.9 }, { name: "zip extracted" });
  tag(s, "EXIF + GPS", 6.1, 2.15, 3.4, HEX.accent3);
  bulletList(s, ["Samsung Galaxy S23 photos", "11 Oct 18:02 — whiteboard of the Falcon design (12.97 N, 77.59 E)", "13 Oct 17:30 — café in Indiranagar, hours before the e-mail"], { x: 6.1, y: 2.6, w: 3.4, h: 1.45 }, 12);
  tag(s, "ZIP UNPACKED", 6.1, 4.1, 3.4, HEX.accent4);
  bulletList(s, ["backup_oct.zip → Falcon_BOM.csv: parts, suppliers, costs"], { x: 6.1, y: 4.55, w: 3.4, h: 0.5 }, 12);
  s.addNotes("Analysis Results → EXIF Metadata. Point to date, latitude and longitude. If internet is available, click Geolocation to show both pins on the map. Then Data Sources → Archive → backup_oct.zip to show the extracted CSV.");

  // ---------- Timeline (drawn) ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("Three days, in order", { placeholder: "title" });
  qChip(s, "Q3");
  const days = [["11 Oct", 0.5, 2.0], ["12 Oct", 2.6, 4.6], ["13 Oct", 7.3, 2.2]];
  days.forEach(([d, x, w]) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.72, w, h: 0.36, fill: { color: C.text2 }, line: { width: 0, color: C.text2 }, rectRadius: 0.05, objectName: "day band" });
    s.addText(d, { x, y: 2.72, w, h: 0.36, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  const ev = [
    [1.5, "18:02", "Whiteboard photo of the Falcon design", "up", HEX.accent3],
    [3.0, "21:30", "todo.txt — the plan", "down", HEX.accent4],
    [3.95, "21:40", "Design PDF copied", "up", HEX.accent2],
    [4.9, "21:44", "Schematics saved as track01.mp3", "down", HEX.accent2],
    [5.95, "21:52", "BOM zipped into backup_oct.zip", "up", HEX.accent2],
    [7.85, "17:30", "Café photo, Indiranagar", "down", HEX.accent3],
    [9.0, "22:05", "E-mail draft to the rival", "up", HEX.accent2],
  ];
  ev.forEach(([cx, t, label, side, col]) => {
    const up = side === "up";
    s.addShape(pres.shapes.LINE, { x: cx, y: up ? 1.95 : 3.08, w: 0, h: up ? 0.77 : 0.72, line: { color: col, width: 1.5 }, objectName: "tick" });
    s.addShape(pres.shapes.OVAL, { x: cx - 0.08, y: up ? 1.87 : 3.72, w: 0.16, h: 0.16, fill: { color: col }, line: { width: 0, color: col }, objectName: "event dot" });
    const bx = Math.min(Math.max(cx - 0.75, 0.5), 8.0);
    s.addText([{ text: t, options: { bold: true, color: col, breakLine: true } }, { text: label, options: { color: HEX.dk1 } }],
      { x: bx, y: up ? 1.05 : 3.95, w: 1.5, h: 0.8, fontSize: 11, align: "center", valign: up ? "bottom" : "top", margin: 0, isTextBox: true });
  });
  s.addText("Built from Autopsy’s Timeline (List view, 37 events): file-system times plus EXIF capture times. After this the PDF and e-mail were deleted.",
    { x: 0.5, y: 4.85, w: 9.0, h: 0.35, fontSize: 11, italic: true, color: C.accent4, margin: 0, isTextBox: true });
  s.addNotes("DEMO: Toolbar → Timeline → List view and scroll 11 → 13 Oct, then come back to this slide to tell the story. FAT stores only the access date, which is why access events show 05:30 IST. The 23 Oct entries in Autopsy are the folder entries created when we prepared the image.");

  // ---------- 13. Integrity & report ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("Proving integrity and reporting", { placeholder: "title" });
  imgFit(s, "img/f_integrity.png", { x: 0.5, y: 1.15, w: 4.3, h: 2.3 }, { name: "integrity verified" });
  imgFit(s, "img/report.png", { x: 5.2, y: 1.15, w: 4.3, h: 2.3 }, { name: "html report" });
  s.addImage({ data: ICON.shield, x: 0.5, y: 3.75, w: 0.4, h: 0.4, objectName: "shield" });
  s.addText([{ text: "Hashes verified. ", options: { bold: true } }, { text: "Autopsy recomputed MD5 and SHA-256 — both match the acquisition values, so the evidence is unchanged." }],
    { x: 1.05, y: 3.7, w: 3.75, h: 1.2, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  s.addImage({ data: ICON.search, x: 5.2, y: 3.75, w: 0.4, h: 0.4, objectName: "report icon" });
  s.addText([{ text: "One-click report. ", options: { bold: true } }, { text: "Generate Report → HTML gives the case summary and every result category for the case file." }],
    { x: 5.75, y: 3.7, w: 3.75, h: 1.2, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  s.addNotes("Envelope icon (Ingest Inbox) → 'Integrity of USB_Evidence_RM01.dd verified'. Then Generate Report → HTML Report → All Results → open report.html in the browser.");

  // ---------- 14. Conclusion ----------
  pres.addSection({ title: "Conclusion" });
  s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Conclusion" });
  s.addText("What the drive told us", { x: 0.6, y: 0.4, w: 8.8, h: 0.7, fontSize: 32, bold: true, color: C.background1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  [["Q1", "Falcon design (deleted), wiring schematics (disguised as MP3) and parts list (inside a ZIP)."],
   ["Q2", "arjun.k@rivaltech.test at a rival firm, in return for “the agreed amount”."],
   ["Q3", "11–13 Oct 2026 in Bengaluru; the café photo and the e-mail draft fall on the same evening."]].forEach(([q, a], i) => {
    const y = 1.35 + i * 0.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 0.75, h: 0.6, fill: { color: C.accent1 }, line: { width: 0, color: C.accent1 }, rectRadius: 0.06, objectName: "answer chip" });
    s.addText(q, { x: 0.6, y, w: 0.75, h: 0.6, fontSize: 18, bold: true, color: C.text2, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(a, { x: 1.6, y, w: 7.8, h: 0.6, fontSize: 16, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addImage({ data: ICON.shield, x: 0.75, y: 4.2, w: 0.42, h: 0.42, objectName: "shield" });
  s.addText("Evidence integrity proved with matching MD5 and SHA-256 hashes.", { x: 1.6, y: 4.15, w: 7.8, h: 0.5, fontSize: 15, italic: true, color: C.accent5, valign: "middle", margin: 0, isTextBox: true });
  s.addText("Thank you — questions?", { x: 0.6, y: 4.85, w: 8.8, h: 0.45, fontSize: 20, bold: true, color: C.accent1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addNotes("Answer the three questions from the start of the case. One 64 MB image and under a minute of ingest answered all three while keeping evidence integrity provable. Likely questions: How is deleted data recovered? (FAT directory entry marked 0xE5; clusters not wiped). Can Autopsy recover overwritten data? (No.) Recovery vs carving? (Carving uses file signatures in unallocated space without metadata — PhotoRec.)");

  await pres.writeFile({ fileName: "Autopsy_Demo_Team1.pptx" });
  await applyTheme("Autopsy_Demo_Team1.pptx", THEME);
  console.log("done");
})();
