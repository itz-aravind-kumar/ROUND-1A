# test_extract.py
import fitz
from utils import extract_text_blocks

doc = fitz.open("input/Aravind CV.pdf")  # replace with any PDF you have
blocks = extract_text_blocks(doc)

for b in blocks[:5]:  # just print first 5
    print(b)
