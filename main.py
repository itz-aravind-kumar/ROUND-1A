import fitz
import os
import json
from utils import extract_text_blocks, detect_title, detect_headings

INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = extract_text_blocks(doc)
    title = detect_title(doc)
    headings = detect_headings(blocks)

    output_data = {
        "title": title,
        "outline": headings
    }

    filename = os.path.basename(pdf_path).replace(".pdf", ".json")
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Output written to: {output_path}")

if __name__ == "__main__":
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".pdf"):
            process_pdf(os.path.join(INPUT_DIR, file))
