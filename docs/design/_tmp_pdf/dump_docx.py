import re
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
DOCX_PATH = r"D:/Downloads/BSR Market Intelligence Requirements.docx"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

with zipfile.ZipFile(DOCX_PATH, "r") as archive:
    xml_bytes = archive.read("word/document.xml")

root = ET.fromstring(xml_bytes)
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

print(f"=== DOCX PARAGRAPHS: {len(paragraphs)} ===")
for index, paragraph in enumerate(paragraphs, 1):
    print(f"=== DOC {index} ===")
    print(paragraph)
