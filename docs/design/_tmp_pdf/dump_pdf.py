import argparse
import sys

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser()
parser.add_argument("--from-page", type=int, default=1)
parser.add_argument("--to-page", type=int, default=46)
args = parser.parse_args()

pdf = pdfplumber.open(r"D:/Downloads/BSR Market Intelligence Requirements.pdf")
try:
    start = max(1, args.from_page)
    end = min(len(pdf.pages), args.to_page)
    for page_number in range(start, end + 1):
        page = pdf.pages[page_number - 1]
        text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
        print(f"=== PAGE {page_number} ===")
        print(text)
finally:
    pdf.close()
