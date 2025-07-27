import fitz 
from collections import Counter


def extract_text_blocks(doc):
    blocks = []
    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                line_text = ""
                font_size = None
                font_name = None
                if not line["spans"]:
                    continue
                for span in line["spans"]:
                    line_text += span["text"]
                    font_size = span["size"]
                    font_name = span["font"]

                if not line_text.strip():
                    continue

                is_bold = "Bold" in font_name
                is_all_caps = line_text.isupper()
                x0, y0 = line["bbox"][0], line["bbox"][1]

                blocks.append({
                    "text": line_text.strip(),
                    "font_size": font_size,
                    "is_bold": is_bold,
                    "is_all_caps": is_all_caps,
                    "x": x0,
                    "y": y0,
                    "page": page_num + 1
                })
    return blocks

def detect_title(doc):
    first_page_blocks = extract_text_blocks(doc[:1])  # Only first page
    if not first_page_blocks:
        return "Untitled Document"

    # Pick the largest font block (with clean text)
    largest_block = max(first_page_blocks, key=lambda b: b["font_size"])

    return largest_block["text"]

from collections import Counter
import re

def is_line_isolated(current_line, all_lines, min_spacing=5):
    current_y = current_line["y"]
    page = current_line["page"]
    count_nearby = 0

    for line in all_lines:
        if line["page"] != page or line["text"] == current_line["text"]:
            continue
        if abs(line["y"] - current_y) <= min_spacing:
            count_nearby += 1
    return count_nearby == 0


def detect_headings(blocks, title=""):
    font_sizes = sorted({b["font_size"] for b in blocks}, reverse=True)
    size_to_level = {}
    if len(font_sizes) >= 3:
        size_to_level = {
            font_sizes[0]: "H1",
            font_sizes[1]: "H2",
            font_sizes[2]: "H3"
        }

    style_counter = Counter()
    for b in blocks:
        style_key = (b["font_size"], b["is_bold"])
        style_counter[style_key] += 1

    headings = []

    for idx, b in enumerate(blocks):
        text = b["text"].strip()
        words = text.split()
        style_key = (b["font_size"], b["is_bold"])

        # --- Heuristic Filters ---
        if text.lower() == title.lower():
            continue
        if len(words) > 12 or len(text) < 3:
            continue
        if sum(c.isalpha() for c in text) < 3:
            continue  # Too few letters
        if text.replace(".", "").replace(" ", "").isdigit():
            continue
        if style_counter[style_key] > 12 and not b["is_all_caps"] and not b["is_bold"]:
            continue
        if not is_line_isolated(b, blocks) and not b["is_all_caps"] and not b["is_bold"]:
            continue
        if any(char.isdigit() for char in text) and len(words) <= 3 and not b["is_bold"]:
            continue  # Avoids CGPA, TABLE I, RAM, 8 GB etc.
        if len(words) <= 2 and (text.isupper() or text.istitle()) and any(char.isdigit() for char in text):
            continue  # Avoids short, value-like lines
        if len(text) <= 5 and not b["is_bold"] and not b["is_all_caps"]:
            continue  # Avoids short, non-bold lines
        if re.match(r"^[A-Za-z]{1,4}$", text):
            continue  # Avoids single-word, short fields like 'DOB', 'CGPA'
        if text.endswith(":") and len(words) <= 2:
            continue  # Avoids 'CGPA:' etc.
        if re.match(r"^[0-9.]+$", text):
            continue  # Avoids numbers only
        if re.match(r"^[A-Za-z]+ [0-9.]+$", text):
            continue  # Avoids 'CGPA 8.5', 'RAM 8GB'

        # Context: If next line is a value, this is likely a field, not a heading
        if idx + 1 < len(blocks):
            next_text = blocks[idx + 1]["text"].strip()
            if re.match(r"^[0-9.]+$", next_text) or (len(next_text) <= 6 and any(char.isdigit() for char in next_text)):
                if len(words) <= 3:
                    continue

        # --- Heading detection via font layout/styling ---
        is_heading = False
        level = ""

        if b["font_size"] in size_to_level and (b["is_bold"] or b["is_all_caps"]):
            level = size_to_level[b["font_size"]]
            is_heading = True
        elif b["is_all_caps"] and len(words) <= 3 and b["font_size"] >= font_sizes[-1]:
            level = "H2"
            is_heading = True

        # Extra: If line is isolated, bold, and reasonably long, treat as heading
        if not is_heading and is_line_isolated(b, blocks):
            if b["is_bold"] and 3 <= len(words) <= 8 and b["font_size"] >= font_sizes[-1]:
                level = "H3"
                is_heading = True

        if is_heading:
            headings.append({
                "level": level,
                "text": text,
                "page": b["page"]
            })

    return headings
