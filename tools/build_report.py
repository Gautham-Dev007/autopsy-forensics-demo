"""Fills the RIT report template with the Autopsy demo report.
Usage: python3 build_report.py <unpacked_template_dir> <shots_dir> <out.docx>
"""
import os, re, sys, shutil, subprocess
from xml.sax.saxutils import escape
from PIL import Image

SRC, SHOTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
DOC = f"{WORK}/word/document.xml"
x = open(DOC, encoding="utf-8").read()

HASH_MD5 = os.environ.get("IMG_MD5", "")
HASH_SHA = os.environ.get("IMG_SHA256", "")

# ---------- cover page ----------
x = x.replace("<w:t>&lt;tool_name&gt;’</w:t>", "<w:t>Autopsy’</w:t>")
x = x.replace("<w:t>&lt;Student1-Name&gt;(&lt;USN&gt;)</w:t>", "<w:t>Gautham (1MS23EC040)</w:t>", 1)
x = x.replace("<w:t>&lt;Student2-Name&gt;(&lt;USN&gt;)</w:t>", "<w:t>Archana (1MS24EC400)</w:t>", 1)
# drop the unused third-student line
x = re.sub(r'<w:p w14:paraId="21DB94D1">.*?</w:p>', "", x, count=1, flags=re.S)
assert "&lt;" not in x, "placeholder left on cover"

# ---------- helpers ----------
F = '<w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:cs="Verdana"/>'
BODY_SZ = 20  # 10 pt

def run(t, b=False, i=False, sz=BODY_SZ, color=None, mono=False):
    font = '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>' if mono else F
    rpr = font + ("<w:b/>" if b else "") + ("<w:i/>" if i else "") + \
        (f'<w:color w:val="{color}"/>' if color else "") + f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r>'

def rich(text, **kw):
    """**bold** and `mono` inline markup."""
    out = []
    for part in re.split(r"(\*\*.+?\*\*|`.+?`)", text):
        if not part: continue
        if part.startswith("**"): out.append(run(part[2:-2], b=True, **kw))
        elif part.startswith("`"): out.append(run(part[1:-1], mono=True, sz=18))
        else: out.append(run(part, **kw))
    return "".join(out)

def p(text, jc="both", after=120, keep=False, ind=None, extra=""):
    ppr = f'<w:spacing w:before="0" w:after="{after}" w:line="300" w:lineRule="auto"/>' + (f'<w:ind w:left="{ind}"/>' if ind else "") + f'<w:jc w:val="{jc}"/>'
    if keep: ppr = "<w:keepNext/>" + ppr
    return f"<w:p><w:pPr>{extra}{ppr}</w:pPr>{rich(text) if isinstance(text, str) else text}</w:p>"

def pagebreak():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def h1(t):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:keepNext/><w:spacing w:before="240" w:after="160"/></w:pPr>'
            f'{run(t, b=True, sz=28, color="1F3864")}</w:p>')

def h2(t):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:spacing w:before="200" w:after="100"/></w:pPr>'
            f'{run(t, b=True, sz=22, color="2E2E2E")}</w:p>')

NUM_BULLET = 50
_next_num = [60]
def bullets(items, num=None):
    nid = num or NUM_BULLET
    return "".join(
        f'<w:p><w:pPr><w:pStyle w:val="11"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="{nid}"/></w:numPr>'
        f'<w:spacing w:after="60" w:line="288" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>{rich(it)}</w:p>'
        for it in items)

def steps(items):
    nid = _next_num[0]; _next_num[0] += 1
    NUMS.append(nid)
    return bullets(items, nid)

NUMS = []

def code(lines):
    out = []
    for i, l in enumerate(lines):
        after = 120 if i == len(lines) - 1 else 0
        out.append(f'<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>'
                   f'<w:spacing w:after="{after}" w:line="240" w:lineRule="auto"/><w:ind w:left="360" w:right="360"/></w:pPr>'
                   f'{run(l if l else " ", mono=True, sz=17)}</w:p>')
    return "".join(out)

def table(header, rows, widths):
    total = sum(widths)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    def cell(t, w, head=False, shade=None):
        sh = f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>' if shade else ""
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:before="40" w:after="40" w:line="252" w:lineRule="auto"/></w:pPr>'
                f'{rich(t, sz=18) if not head else run(t, b=True, sz=18, color="FFFFFF")}</w:p></w:tc>')
    trs = ['<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' +
           "".join(cell(h, w, True, "1F3864") for h, w in zip(header, widths)) + "</w:tr>"]
    for k, r in enumerate(rows):
        trs.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>" +
                   "".join(cell(c, w, False, "EEF2F8" if k % 2 else None) for c, w in zip(r, widths)) + "</w:tr>")
    b = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
    borders = "".join(b.format(s) for s in ["top", "left", "bottom", "right", "insideH", "insideV"])
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>' + p("", after=60))

# images
RELS = f"{WORK}/word/_rels/document.xml.rels"
rels = open(RELS, encoding="utf-8").read()
os.makedirs(f"{WORK}/word/media", exist_ok=True)
_img = [100]
FIG = [0]

def figure(fname, caption, explain, placeholder):
    FIG[0] += 1
    n = FIG[0]
    path = os.path.join(SHOTS, fname) if fname else None
    cap = p(f"**Figure {n}:** {caption}", jc="center", after=80)
    if path and os.path.exists(path):
        global rels
        _img[0] += 1
        rid = f"rIdImg{_img[0]}"
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        ext = "jpeg" if ext == "jpg" else ext
        tgt = f"media/shot{_img[0]}.{ext}"
        shutil.copy(path, f"{WORK}/word/{tgt}")
        rels = rels.replace("</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{tgt}"/></Relationships>')
        w, h = Image.open(path).size
        maxw = 6.3 * 914400
        cx = int(maxw); cy = int(maxw * h / w)
        if cy > 4.6 * 914400:
            cy = int(4.6 * 914400); cx = int(cy * w / h)
        did = 100 + _img[0]
        drawing = (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
                   f'<wp:docPr id="{did}" name="Figure {n}" descr="{escape(caption)}"/>'
                   f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                   f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{did}" name="shot{n}"/><pic:cNvPicPr/></pic:nvPicPr>'
                   f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                   f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:ln w="6350"><a:solidFill><a:srgbClr val="A6A6A6"/></a:solidFill></a:ln></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
        body = (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/></w:pPr>{drawing}</w:p>')
    else:
        body = (f'<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
                + "".join(f'<w:{s} w:val="dashed" w:sz="8" w:space="0" w:color="7F7F7F"/>' for s in ["top", "left", "bottom", "right"]) +
                f'</w:tblBorders></w:tblPr><w:tblGrid><w:gridCol w:w="9000"/></w:tblGrid><w:tr><w:trPr><w:trHeight w:val="3200"/></w:trPr>'
                f'<w:tc><w:tcPr><w:tcW w:w="9000" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="F7F7F7"/><w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr>{run("[ Paste screenshot here ]", b=True, color="7F7F7F")}</w:p>'
                f'<w:p><w:pPr><w:ind w:left="400" w:right="400"/><w:jc w:val="center"/></w:pPr>{run(placeholder, i=True, sz=18, color="7F7F7F")}</w:p>'
                f'</w:tc></w:tr></w:tbl>')
    return body + cap + p(f"**Explanation:** {explain}", after=200)

# ---------- content ----------
B = []
B.append(pagebreak())

# 1. Introduction
B.append(h1("1. Tool Introduction"))
B.append(p("**Autopsy** is a free, open-source digital forensics platform that provides a graphical interface to **The Sleuth Kit (TSK)**, the widely used command-line library for analysing disk images and file systems. It was created by Brian Carrier, developed for many years by Basis Technology, and is now maintained by **Sleuth Kit Labs**. Autopsy is written in Java on the NetBeans Rich Client Platform and runs on Windows (fully supported), Linux and macOS."))
B.append(p("Autopsy is designed as an end-to-end investigation environment: an examiner creates a **case**, adds one or more **data sources** (disk images, physical drives or logical files), runs automated **ingest modules** that extract artifacts in the background, and then reviews the results through tree views, a timeline, a geolocation map and keyword search before exporting a report. Because both the code and the underlying TSK library are open source, its results can be independently verified, which matters when findings are presented in court."))
B.append(h2("1.1 Key facts"))
B.append(table(["Attribute", "Details"], [
    ["Developer", "Sleuth Kit Labs (originally Basis Technology); creator Brian Carrier"],
    ["Current version", "4.23.1 (Autopsy 4.23.0 was released in April 2026)"],
    ["License / cost", "Open source (Apache License 2.0); free to use"],
    ["Platforms", "Windows 64-bit (MSI installer); Linux and macOS (ZIP + install script; snap package on Linux)"],
    ["Language / engine", "Java 17 GUI; file-system parsing by The Sleuth Kit (C/C++); Apache Solr for indexed keyword search"],
    ["Evidence formats", "Raw/dd, split raw, E01 (EnCase), VHD, VMDK, local physical drives, logical files and folders"],
    ["File systems", "NTFS, FAT12/16/32, exFAT, ext2/3/4, HFS+, APFS, ISO 9660, UFS, YAFFS2"],
    ["Recent additions", "BitLocker support (4.22.0); MCP server for AI-assisted summaries and Cyber Triage integration (4.23.0)"],
], [2400, 6960]))
B.append(h2("1.2 Core architecture"))
B.append(bullets([
    "**Case:** a folder holding the case database (SQLite for single-user, PostgreSQL for multi-user), logs, exported files and reports.",
    "**Data source:** the evidence added to the case. Autopsy never writes to it; all work is done on a read-only basis.",
    "**Ingest modules:** plug-ins that run automatically over every file and post their findings to a shared database called the **blackboard**. Examples: Hash Lookup, File Type Identification, Extension Mismatch Detector, Embedded File Extractor, Picture Analyzer (EXIF), Keyword Search, Recent Activity, Email Parser, Encryption Detection, PhotoRec Carver and Data Source Integrity.",
    "**Viewers:** the Directory Tree (Data Sources, File Views, Data Artifacts, Analysis Results, Tags), Result Viewer table, Content Viewer (Hex, Text, Application, File Metadata), plus Timeline, Geolocation, Communications and Image Gallery tools.",
    "**Reports:** HTML, Excel, KML, portable case, body file and other formats generated from tagged items and results.",
]))

# 2. Applications
B.append(h1("2. Tool Applications"))
B.append(p("Autopsy is used wherever stored digital data has to be examined in a repeatable, defensible way. Typical applications are:"))
B.append(table(["Application area", "How Autopsy is used"], [
    ["Law-enforcement investigations", "Examining seized computers, hard disks, USB drives and memory cards for documents, images, chats and browser history linked to a crime."],
    ["Corporate / insider-threat cases", "Investigating intellectual-property theft, data leakage and policy violations by employees (the scenario demonstrated in this report)."],
    ["Incident response", "Triaging compromised hosts: locating malware, suspicious executables, persistence entries, logins and recently run programs."],
    ["Deleted-data recovery", "Recovering deleted files from file-system metadata and carving files from unallocated space with the PhotoRec module."],
    ["Timeline reconstruction", "Correlating file-system timestamps, EXIF dates, web history and registry events to establish the sequence of user actions."],
    ["Media and geolocation analysis", "Extracting camera make/model and GPS coordinates from photos and plotting them on the Geolocation map."],
    ["Keyword and PII search", "Indexed searches for names, project terms, e-mail addresses, phone numbers, IP addresses, URLs and credit-card numbers."],
    ["Mobile and cloud artifacts", "Parsing Android (aLEAPP) and iOS (iLEAPP) extractions and app databases for messages, contacts and call logs."],
    ["Education and training", "Teaching forensic methodology because it is free, open source and follows standard investigative workflows."],
], [2800, 6560]))

# 3. Installation
B.append(h1("3. Tool Installation Steps"))
B.append(h2("3.1 System requirements"))
B.append(bullets([
    "64-bit operating system (Windows 10/11 recommended; Ubuntu/Debian or macOS supported).",
    "At least 8 GB RAM (16 GB recommended for large cases), a multi-core CPU and free disk space for the case folder and keyword index.",
    "Java — bundled with the Windows installer. On Linux/macOS install it separately; for Autopsy 4.23.1 use **Java 21** (its bundled Sleuth Kit library is compiled for Java 21, so Java 17 fails at start-up with `UnsupportedClassVersionError`).",
]))
B.append(h2("3.2 Installation on Windows"))
B.append(steps([
    "Open **autopsy.com/download** (or the Autopsy GitHub Releases page) and download the 64-bit MSI installer, e.g. `autopsy-4.23.1-64bit.msi`.",
    "Run the MSI as administrator and accept the licence agreement.",
    "Keep the default install location (`C:\\Program Files\\Autopsy-4.23.1`) and click **Install**; the installer bundles Java and The Sleuth Kit.",
    "Launch **Autopsy** from the Start menu. On first start-up it loads its modules and shows the Welcome screen with **New Case**, **Open Recent Case** and **Open Case**.",
]))
B.append(h2("3.3 Installation on Linux (Ubuntu / Debian)"))
B.append(p("**Option A – snap package (quickest).** A community snap is published in the Snap Store; it may lag one release behind the latest version."))
B.append(code(["sudo snap install autopsy", "autopsy"]))
B.append(p("**Option B – official ZIP with install scripts (latest version).**"))
B.append(steps([
    "Install prerequisites (Java 21, build tools, image-format libraries): run `install_prereqs_ubuntu.sh` from the `linux_macos_install_scripts` folder of the Autopsy ZIP, or install the packages it lists with apt.",
    "Install The Sleuth Kit with Java bindings — either the `sleuthkit-java` .deb from the Sleuth Kit GitHub releases, or build it with `install_tsk_from_src.sh`, using the TSK version that matches Autopsy (4.15.0 for Autopsy 4.23.1).",
    "Download `autopsy-4.23.1.zip` from GitHub Releases and run the application installer, pointing it at Java 21.",
    "Start Autopsy with `~/autopsy/autopsy-4.23.1/bin/autopsy`.",
]))
B.append(code([
    "# 1. prerequisites",
    "sudo apt update && sudo apt install -y openjdk-21-jdk build-essential autoconf \\",
    "     libtool automake git ant libewf-dev libafflib-dev libvhdi-dev libvmdk-dev testdisk",
    "# 2. The Sleuth Kit 4.15.0 with Java bindings",
    "./install_tsk_from_src.sh -p ~/src/sleuthkit -b sleuthkit-4.15.0",
    "# 3. Autopsy",
    "./install_application.sh -z ~/Downloads/autopsy-4.23.1.zip -i ~/autopsy \\",
    "     -j /usr/lib/jvm/java-21-openjdk-amd64",
    "# 4. run",
    "~/autopsy/autopsy-4.23.1/bin/autopsy",
]))
B.append(p("**Linux notes from our own installation:**"))
B.append(bullets([
    "The Android Analyzer (aLEAPP), iOS Analyzer (iLEAPP) and YARA Analyzer modules are Windows-only; untick them in the ingest screen on Linux, otherwise ingest refuses to start.",
    "The Geolocation map downloads map tiles from the internet, so it needs a network connection to display the base map.",
    "Everything used in this demonstration — file-system analysis, deleted-file recovery, keyword search, EXIF, timeline and reports — works on Linux.",
]))
B.append(h2("3.4 Verifying the installation"))
B.append(bullets([
    "The Welcome window opens without errors and **Help → About** shows the expected version.",
    "**Tools → Options → Application** shows the Java runtime and the memory allocated to Autopsy (increase the maximum JVM memory here for large images).",
]))

# 4. Use-case
B.append(h1("4. Use-Case and its Explanation"))
B.append(h2("4.1 Use-case: Storage Drive Evidence Analysis"))
B.append(p("Storage drive evidence analysis is the examination of a forensic image of a storage device — hard disk, SSD, USB pen drive or memory card — to find, recover and interpret files and metadata relevant to an investigation, without altering the original evidence. The examiner verifies the image hash, parses the file system, recovers deleted content, identifies disguised files, extracts metadata, searches for keywords and builds a timeline, then documents everything in a report."))
B.append(h2("4.2 Case scenario (simulated)"))
B.append(p("A (fictional) technology company, Nexora Labs, suspects that an employee, R. Mehta, leaked the confidential design of its drone product “**Project Falcon**” to a competitor. Security staff seized a USB pen drive from the employee’s desk. A bit-for-bit image of the drive was acquired for examination. The investigation must answer:"))
B.append(steps([
    "Does the drive contain Project Falcon material, including files the suspect tried to hide or delete?",
    "Is there evidence of intent to send the material to an outside party, and who is that party?",
    "When did the relevant activity take place, and where were related photos taken?",
]))
B.append(h2("4.3 Evidence item"))
B.append(table(["Field", "Value"], [
    ["Evidence ID", "RM01 — USB pen drive (simulated)"],
    ["Image file", "`USB_Evidence_RM01.dd` (raw / dd format)"],
    ["Size / file system", "64 MB, FAT32, volume label RM_USB, volume serial 1A2B-3C4D"],
    ["MD5", f"`{HASH_MD5}`"],
    ["SHA-256", f"`{HASH_SHA}`"],
    ["Prepared for", "Classroom demonstration; all names, companies and addresses are fictional (.test domains are reserved for testing)"],
], [2200, 7160]))
B.append(h2("4.4 Investigation methodology in Autopsy"))
B.append(table(["Step", "Action in Autopsy", "Purpose"], [
    ["1. Create case", "New Case → case name, base directory, case number and examiner details", "Organises all evidence, results and notes; records the examiner for documentation"],
    ["2. Add data source", "Add Data Source → Disk Image or VM File → select the .dd image, set time zone Asia/Calcutta (IST), enter the acquisition MD5 and SHA-256", "Loads the evidence read-only; the correct time zone gives correct local timestamps"],
    ["3. Keyword list", "Global Settings → Keyword Search → new list “Falcon_Case” with falcon, confidential, transfer (substring match)", "Searches every file — including deleted and extracted ones — for case-specific terms"],
    ["4. Configure ingest", "Enable File Type Identification, Extension Mismatch Detector, Embedded File Extractor, Picture Analyzer, Keyword Search, PhotoRec Carver and Data Source Integrity", "Selects which automated analyses run on every file"],
    ["5. Verify integrity", "Data Source Integrity module recomputes MD5 and SHA-256 and compares them with the stored values", "Proves the image has not changed since acquisition"],
    ["6. Review file system", "Data Sources tree and File Views → Deleted Files", "Shows folders, live files and deleted files with their timestamps"],
    ["7. Review results", "Analysis Results → Extension Mismatch Detected, Keyword Hits, EXIF Metadata; ad-hoc regex search for e-mail addresses; Timeline", "Finds disguised files, keyword evidence, photo metadata, contacts and the sequence of events"],
    ["8. Report", "Generate Report → HTML Report (All Results)", "Produces a shareable report of the evidence"],
], [1700, 4260, 3400]))
B.append(h2("4.5 What was planted on the drive (ground truth)"))
B.append(p("To make the demonstration verifiable, the image was prepared with known content, and each item is found by a different Autopsy feature:"))
B.append(table(["Item on the drive", "State", "Autopsy feature that found it"], [
    ["Documents/Project_Falcon_Design.pdf", "Deleted", "Deleted Files (also carved back by PhotoRec)"],
    ["Personal/email_draft.txt — message to arjun.k@rivaltech.test", "Deleted", "Deleted Files; e-mail regex search"],
    ["Music/track01.mp3 — actually a PDF of Falcon wiring schematics", "Renamed (disguised)", "Extension Mismatch Detector"],
    ["Archive/backup_oct.zip containing Falcon_BOM.csv", "Compressed", "Embedded File Extractor"],
    ["Photos/IMG_2041.jpg, IMG_2042.jpg", "Live, with EXIF + GPS", "Picture Analyzer (EXIF Metadata)"],
    ["Personal/todo.txt — plan to copy, disguise and send the files", "Live", "Keyword Search (Falcon_Case list)"],
    ["Documents/Meeting_Notes.txt", "Live, benign", "Control file — not relevant"],
], [3800, 1700, 3860]))

# 5. Results
B.append(h1("5. Results Screenshots with Explanation"))
B.append(p("The screenshots below were captured while analysing the evidence image in Autopsy 4.23.1. Each shows one stage of the investigation and the evidence it revealed."))

SHOTS_SPEC = [
    ("01_new_case_c.png", "Creating a new case",
     "The case RIT-DF-2026-01_Falcon_Leak is created with a case number, examiner names and a short note on how the evidence was obtained. Autopsy keeps its database, index, exported files and reports in the case folder, so the evidence itself is never modified.",
     "New Case wizard with case number and examiner details."),
    ("02_add_datasource_c.png", "Adding the USB image as a data source",
     "USB_Evidence_RM01.dd is added as a “Disk Image or VM File” with the Asia/Calcutta time zone so all timestamps display in IST. The MD5 and SHA-256 recorded at acquisition are entered so Autopsy can verify the image later.",
     "Add Data Source with path, time zone and hash fields."),
    ("03b_keyword_list_c.png", "Custom keyword list for the case",
     "A keyword list named Falcon_Case is created with the terms falcon, confidential and transfer as substring matches. Substring matching also catches variations such as file names like Falcon_BOM.csv.",
     "Global Keyword Search Settings with the Falcon_Case list."),
    ("03_ingest_modules_c.png", "Selecting ingest modules",
     "The ingest modules are configured and both the built-in Email Addresses list and the custom Falcon_Case list are enabled for Keyword Search. Ingest runs in the background and posts results to the Data Artifacts and Analysis Results sections of the tree.",
     "Configure Ingest screen with Keyword Search lists."),
    ("03c_integrity.png", "Evidence integrity verified",
     "The Data Source Integrity module recalculated both hashes of the image and found them identical to the stored acquisition values (“Result: verified”). This proves the evidence analysed is exactly what was acquired — a key requirement for admissibility.",
     "Ingest Inbox → Data Source Integrity message."),
    ("04_filesystem_tree.png", "File-system view and a recovered deleted document",
     "Expanding the image shows the FAT32 folders (Archive, Documents, Music, Personal, Photos) plus Autopsy’s virtual folders ($CarvedFiles, $Unalloc). In Documents, Project_Falcon_Design.pdf has a red X and is marked Unallocated — it was deleted — yet its full text is still readable in the Text viewer: “CONFIDENTIAL – NEXORA LABS INTERNAL USE ONLY”.",
     "Documents folder with the deleted PDF selected."),
    ("05_deleted_files.png", "Recovered deleted e-mail draft",
     "File Views → Deleted Files → File System lists two deleted files. The recovered email_draft.txt is a message from r.mehta.personal@mailbox.test to arjun.k@rivaltech.test saying the Falcon design and BOM are attached and asking for “the agreed amount” to be transferred. Deleting a file on FAT only marks the directory entry, so the content survives until overwritten.",
     "Deleted Files view with email_draft.txt selected."),
    ("06_extension_mismatch.png", "Disguised file exposed by Extension Mismatch Detector",
     "Music/track01.mp3 is flagged as Likely Notable because its detected MIME type is application/pdf, not audio. The Text viewer reveals it is “Project Falcon – Wiring Schematics” — the suspect renamed it to look like music, exactly as step 2 of their to-do note says.",
     "Extension Mismatch Detected with track01.mp3."),
    ("07_keyword_hits.png", "Keyword hits for “falcon”",
     "The Falcon_Case list produced 14 hits (falcon 9, confidential 3, transfer 2). Hits include todo.txt, the deleted email draft, the BOM inside the ZIP, the disguised track01.mp3, the deleted PDF, its file slack, a fragment in unallocated space, and f0000000_untitled.pdf — a copy of the deleted PDF independently carved by PhotoRec. The highlighted todo.txt sets out the plan: copy, rename, send to arjun.k@rivaltech.test, then delete the originals.",
     "Keyword Hits → Falcon_Case → falcon with todo.txt selected."),
    ("07b_email_regex.png", "E-mail addresses found by regular-expression search",
     "Because the built-in Email Addresses list did not flag addresses on the reserved .test domain, an ad-hoc regular-expression search ([a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}) was run from the Keyword Search toolbar. It found the recipient arjun.k@rivaltech.test and the sender’s personal address in todo.txt, the deleted email draft, its metadata and unallocated space.",
     "Keyword search results for the e-mail regex."),
    ("08_exif_geolocation.png", "Photo metadata (EXIF) with GPS coordinates",
     "The Picture Analyzer extracted camera make and model (Samsung Galaxy S23), capture time and GPS coordinates. IMG_2041 — a whiteboard sketch of the Falcon architecture — was taken on 11 Oct 2026 at 18:02 at 12.9716 N, 77.5946 E (central Bengaluru); IMG_2042 was taken on 13 Oct 2026 at 17:30 at 12.9784 N, 77.6408 E (Indiranagar), hours before the e-mail draft. With internet access the Geolocation tool plots both points on a map.",
     "EXIF Metadata table."),
    ("09_embedded_zip.png", "ZIP archive contents extracted automatically",
     "The Embedded File Extractor opened backup_oct.zip and added Falcon_BOM.csv to the case as a child file. Its contents — part numbers, suppliers and unit costs — are viewable and were included in the keyword search without manually unzipping anything.",
     "backup_oct.zip expanded with Falcon_BOM.csv."),
    ("10_timeline.png", "Timeline (list view) of file-system and EXIF events",
     "The Timeline orders 37 events: whiteboard photo taken (11 Oct 18:02) → todo.txt (12 Oct 21:30), design PDF (21:40), disguised schematics (21:44), BOM and ZIP (21:50–21:52) written to the drive → café photo (13 Oct 17:30) → e-mail draft (13 Oct 22:05). FAT stores only the date for last access, which is why access events show 05:30 IST (midnight UTC); the 23 Oct entries are the folder entries created when the image was prepared.",
     "Timeline → List view."),
    ("11_report.png", "Generated HTML forensic report",
     "Generate Report → HTML Report produced a report with the case summary, examiner, image details and every result category (EXIF Metadata, Extension Mismatch, Keyword Hits and more), ready to attach to the case file.",
     "HTML report open in a browser."),
]
for fname, cap, expl, ph in SHOTS_SPEC:
    B.append(figure(fname, cap, expl, ph))

B.append(h2("5.1 Summary of findings"))
B.append(table(["Question", "Finding", "Supporting evidence"], [
    ["Falcon material on the drive?", "Yes — design PDF (deleted), wiring schematics (disguised as MP3) and BOM (inside ZIP).", "Figures 6, 8, 12"],
    ["Attempt to conceal?", "Yes — originals deleted and schematics renamed with a false extension, as planned in todo.txt.", "Figures 6, 7, 8, 9"],
    ["Intended recipient?", "arjun.k@rivaltech.test, in return for “the agreed amount”.", "Figures 7, 10"],
    ["When and where?", "11–13 Oct 2026 in Bengaluru; a photo places the suspect in Indiranagar on 13 Oct, the evening the e-mail was drafted.", "Figures 11, 13"],
    ["Evidence integrity", "MD5 and SHA-256 recomputed by Autopsy matched the acquisition hashes.", "Figure 5"],
], [2300, 4560, 2500]))
B.append(h2("5.2 Conclusion"))
B.append(p("Autopsy turned a single raw image of a USB drive into a clear, documented account of what was on the drive, what the user tried to hide, and when. Deleted files were recovered from FAT directory entries (and independently carved by PhotoRec), a renamed PDF was exposed by signature analysis, a ZIP was unpacked automatically, EXIF data placed the photos in time and space, and keyword and regex searches linked the material to an external recipient — all while proving evidence integrity through hash verification. The demonstration shows why Autopsy is a practical first-choice tool for storage-drive examinations in both academic and real investigations."))
B.append(h2("5.3 References"))
B.append(bullets([
    "Autopsy official website and downloads — https://www.autopsy.com",
    "Autopsy User Guide — https://sleuthkit.org/autopsy/docs/user-docs/latest/",
    "Autopsy source and Linux/macOS install notes — https://github.com/sleuthkit/autopsy",
    "The Sleuth Kit — https://www.sleuthkit.org/sleuthkit/",
    "B. Carrier, File System Forensic Analysis, Addison-Wesley, 2005.",
]))

body = "".join(B)
# Insert after the last Index item (before sectPr); drop the trailing blank para
x = x.replace('</w:p><w:sectPr>', '</w:p>' + body + '<w:sectPr>', 1)
open(DOC, "w", encoding="utf-8").write(x)
open(RELS, "w", encoding="utf-8").write(rels)

# content types for png
ct_path = f"{WORK}/[Content_Types].xml"
ct = open(ct_path, encoding="utf-8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
open(ct_path, "w", encoding="utf-8").write(ct)

# numbering: bullet abstract + restartable numbered lists
nb = open(f"{WORK}/word/numbering.xml", encoding="utf-8").read()
bullet_abs = ('<w:abstractNum w:abstractNumId="50"><w:multiLevelType w:val="singleLevel"/>'
              '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/>'
              '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr></w:lvl></w:abstractNum>'
              '<w:abstractNum w:abstractNumId="51"><w:multiLevelType w:val="singleLevel"/>'
              '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>'
              '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:b/><w:sz w:val="20"/></w:rPr></w:lvl></w:abstractNum>')
nums = '<w:num w:numId="50"><w:abstractNumId w:val="50"/></w:num>' + "".join(
    f'<w:num w:numId="{n}"><w:abstractNumId w:val="51"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>'
    for n in NUMS)
i = nb.find("<w:num ")
nb = nb[:i] + bullet_abs + nb[i:]
nb = nb.replace("</w:numbering>", nums + "</w:numbering>")
open(f"{WORK}/word/numbering.xml", "w", encoding="utf-8").write(nb)

# heading styles (for Word navigation pane)
st = open(f"{WORK}/word/styles.xml", encoding="utf-8").read()
if 'w:styleId="Heading1"' not in st:
    hs = "".join(
        f'<w:style w:type="paragraph" w:styleId="Heading{k}"><w:name w:val="heading {k}"/><w:basedOn w:val="1"/><w:next w:val="1"/>'
        f'<w:qFormat/><w:pPr><w:keepNext/><w:outlineLvl w:val="{k-1}"/></w:pPr></w:style>' for k in (1, 2))
    st = st.replace("</w:styles>", hs + "</w:styles>")
open(f"{WORK}/word/styles.xml", "w", encoding="utf-8").write(st)

if os.path.exists(OUT): os.remove(OUT)
subprocess.run(f'cd "{WORK}" && zip -qXr "{os.path.abspath(OUT)}" .', shell=True, check=True)
print("written", OUT, "figures:", FIG[0])
