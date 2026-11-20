import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DOCX_PATH = r"D:/Downloads/BSR Market Intelligence Requirements.docx"
PDF_DUMP_PATH = r"D:/ReasonaryAI/BSR_Market_Intel - auker/docs/design/_tmp_pdf/full.txt"
DOCX_DUMP_PATH = r"D:/ReasonaryAI/BSR_Market_Intel - auker/docs/design/_tmp_pdf/full_docx.txt"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

with zipfile.ZipFile(DOCX_PATH, "r") as archive:
    root = ET.fromstring(archive.read("word/document.xml"))
paragraphs = []
for paragraph in root.iter(W_NS + "p"):
    parts = []
    for node in paragraph.iter():
        if node.tag == W_NS + "t":
            parts.append(node.text or "")
        elif node.tag == W_NS + "tab":
            parts.append("\t")
        elif node.tag in (W_NS + "br", W_NS + "cr"):
            parts.append("\n")
    text = "".join(parts).strip()
    if text:
        paragraphs.append(text)
docx_text = "\n".join(paragraphs)
pdf_dump = Path(PDF_DUMP_PATH).read_text(encoding="utf-8")
pdf_pages = re.split(r"^=== PAGE \d+ ===\s*$", pdf_dump, flags=re.MULTILINE)[1:]
pdf_text = "\n".join(page.strip() for page in pdf_pages)

def compact(value):
    return re.sub(r"\s+", "", value).replace("●", "")

compact_docx = compact(docx_text)
compact_pdf = compact(pdf_text)
common_prefix = 0
for left, right in zip(compact_docx, compact_pdf):
    if left != right:
        break
    common_prefix += 1
print("DOCX_PARAGRAPHS", len(paragraphs))
print("DOCX_CHARS", len(docx_text))
print("DOCX_DUMP_CHARS", len(Path(DOCX_DUMP_PATH).read_text(encoding="utf-8")))
print("PDF_DUMP_CHARS", len(pdf_dump))
print("PDF_PAGE_MARKERS", len(re.findall(r"^=== PAGE \d+ ===$", pdf_dump, flags=re.MULTILINE)))
print("DOCX_COMPACT_CHARS", len(compact_docx))
print("PDF_COMPACT_CHARS", len(compact_pdf))
print("COMPACT_EQUAL", compact_docx == compact_pdf)
print("COMPACT_COMMON_PREFIX", common_prefix)
print("DOCX_FIRST_200", repr(docx_text[:200]))
print("DOCX_LAST_200", repr(docx_text[-200:]))
print("PDF_FIRST_200", repr(pdf_text[:200]))
print("PDF_LAST_200", repr(pdf_text[-200:]))
