import sys

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")
pdf = pdfplumber.open(r"D:/Downloads/BSR Market Intelligence Requirements.pdf")
texts = [(page.extract_text(x_tolerance=2, y_tolerance=3) or "") for page in pdf.pages]
print("PAGE_COUNT", len(texts))
print("PAGE_LENGTHS", ",".join(str(len(text)) for text in texts))
print("NEAR_EMPTY", ",".join(str(index + 1) for index, text in enumerate(texts) if len("".join(text.split())) < 20) or "none")
print("TOTAL_CHARS", sum(map(len, texts)))
print("FIRST_200", repr(texts[0][:200] if texts else ""))
print("LAST_200", repr(texts[-1][-200:] if texts else ""))
pdf.close()
