"""Builds a small FAT32 USB-drive image with planted evidence for the Autopsy demo.

Scenario (fictional): Nexora Labs suspects employee "R. Mehta" leaked the
confidential "Project Falcon" design to a competitor using a USB pen drive.
"""
import os, subprocess, shutil, zipfile, datetime as dt, hashlib
from PIL import Image, ImageDraw
import piexif
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT, "src")
IMG = os.path.join(OUT, "USB_Evidence_RM01.dd")
shutil.rmtree(SRC, ignore_errors=True)
os.makedirs(SRC)

def ts(s):  # IST string -> epoch
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(
        tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30))).timestamp()

def pdf(path, title, lines):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 18); c.drawString(60, 780, title)
    c.setFont("Helvetica-Bold", 12); c.setFillColorRGB(0.75, 0, 0)
    c.drawString(60, 755, "CONFIDENTIAL - NEXORA LABS INTERNAL USE ONLY")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica", 11)
    y = 720
    for l in lines:
        c.drawString(60, y, l); y -= 18
    c.save()

def photo(path, text, colour, when, lat, lon):
    im = Image.new("RGB", (800, 600), colour)
    d = ImageDraw.Draw(im)
    d.rectangle([40, 40, 760, 560], outline="white", width=6)
    d.text((70, 280), text, fill="white")
    def dms(v):
        v = abs(v); dg = int(v); m = int((v - dg) * 60); s = round(((v - dg) * 60 - m) * 60 * 100)
        return ((dg, 1), (m, 1), (s, 100))
    exif = {"0th": {piexif.ImageIFD.Make: b"Samsung", piexif.ImageIFD.Model: b"Galaxy S23"},
            "Exif": {piexif.ExifIFD.DateTimeOriginal: when.encode()},
            "GPS": {piexif.GPSIFD.GPSLatitudeRef: b"N", piexif.GPSIFD.GPSLatitude: dms(lat),
                    piexif.GPSIFD.GPSLongitudeRef: b"E", piexif.GPSIFD.GPSLongitude: dms(lon)}}
    im.save(path, "JPEG", exif=piexif.dump(exif))

# (relative path, builder, mtime IST)
files = []
os.makedirs(f"{SRC}/Documents"); os.makedirs(f"{SRC}/Photos"); os.makedirs(f"{SRC}/Music")
os.makedirs(f"{SRC}/Personal"); os.makedirs(f"{SRC}/Archive")

open(f"{SRC}/Documents/Meeting_Notes.txt", "w").write(
    "Team sync - 05 Oct 2026\n- Sprint review moved to Thursday\n- Lab inventory pending\n")
files.append(("Documents/Meeting_Notes.txt", "2026-10-05 10:15"))

pdf(f"{SRC}/Documents/Project_Falcon_Design.pdf", "Project Falcon - System Design v2.3",
    ["Drone flight-controller architecture, sensor fusion pipeline,",
     "proprietary motor-control algorithm and supplier list.",
     "Distribution: Core engineering team only."])
files.append(("Documents/Project_Falcon_Design.pdf", "2026-10-12 21:40"))

# PDF disguised as an MP3 (extension mismatch)
pdf(f"{SRC}/Music/track01.mp3", "Project Falcon - Wiring Schematics",
    ["Board rev C pin-out, power rail design, ESC wiring.", "Do not copy or distribute."])
files.append(("Music/track01.mp3", "2026-10-12 21:44"))

photo(f"{SRC}/Photos/IMG_2041.jpg", "Whiteboard - Falcon architecture sketch", (30, 60, 110),
      "2026:10:11 18:02:11", 12.9716, 77.5946)
files.append(("Photos/IMG_2041.jpg", "2026-10-11 18:02"))
photo(f"{SRC}/Photos/IMG_2042.jpg", "Cafe meeting - Indiranagar", (110, 60, 30),
      "2026:10:13 17:30:45", 12.9784, 77.6408)
files.append(("Photos/IMG_2042.jpg", "2026-10-13 17:30"))

open(f"{SRC}/Personal/todo.txt", "w").write(
    "1. Copy Falcon design + schematics to pen drive\n"
    "2. Rename schematics so it looks like music\n"
    "3. Send files to arjun.k@rivaltech.test before Friday\n"
    "4. Delete originals from drive after sending\n")
files.append(("Personal/todo.txt", "2026-10-12 21:30"))

open(f"{SRC}/Personal/email_draft.txt", "w").write(
    "To: arjun.k@rivaltech.test\nFrom: r.mehta.personal@mailbox.test\n"
    "Subject: the files we discussed\n\nArjun,\nAttaching the Falcon design and the BOM as promised.\n"
    "Transfer the agreed amount once received.\n- R\n")
files.append(("Personal/email_draft.txt", "2026-10-13 22:05"))

with open(f"{SRC}/Falcon_BOM.csv", "w") as f:
    f.write("part,supplier,unit_cost_inr\nFC-STM32H7,Elcon Components,1850\n"
            "IMU-ICM42688,Sensetek,640\nESC-45A,Volt Drives,2100\n")
os.utime(f"{SRC}/Falcon_BOM.csv", (ts("2026-10-12 21:50"),) * 2)
with zipfile.ZipFile(f"{SRC}/Archive/backup_oct.zip", "w") as z:
    z.write(f"{SRC}/Falcon_BOM.csv", "Falcon_BOM.csv")
os.remove(f"{SRC}/Falcon_BOM.csv")
files.append(("Archive/backup_oct.zip", "2026-10-12 21:52"))

for rel, t in files:
    os.utime(f"{SRC}/{rel}", (ts(t), ts(t)))

# Build 64 MB FAT32 image
if os.path.exists(IMG): os.remove(IMG)
subprocess.run(["dd", "if=/dev/zero", f"of={IMG}", "bs=1M", "count=64", "status=none"], check=True)
subprocess.run(["mkfs.vfat", "-F", "32", "-n", "RM_USB", "-i", "1A2B3C4D", IMG], check=True,
               stdout=subprocess.DEVNULL)
env = dict(os.environ, MTOOLS_SKIP_CHECK="1")
for d in ["Documents", "Photos", "Music", "Personal", "Archive"]:
    subprocess.run(["mmd", "-i", IMG, f"::/{d}"], check=True, env=env)
for rel, _ in files:
    subprocess.run(["mcopy", "-m", "-i", IMG, f"{SRC}/{rel}", f"::/{rel}"], check=True, env=env)
# Suspect deletes the originals (data stays in unallocated clusters)
for rel in ["Documents/Project_Falcon_Design.pdf", "Personal/email_draft.txt"]:
    subprocess.run(["mdel", "-i", IMG, f"::/{rel}"], check=True, env=env)

h_md5, h_sha = hashlib.md5(), hashlib.sha256()
with open(IMG, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h_md5.update(chunk); h_sha.update(chunk)
print("MD5   ", h_md5.hexdigest()); print("SHA256", h_sha.hexdigest())
