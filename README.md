# Adobe Hackathon Round 1A – Heading Extractor

This solution extracts structured outlines from PDFs using a hybrid rule-based method.

## 🧠 Approach

- Detects title as largest font size on the first page.
- Headings are detected based on font size ≥ 13, bold or all caps.
- Levels (H1, H2, H3) currently treated the same (can be enhanced in Round 1B).

## ⚙️ Tech Stack
- Python (PyMuPDF)
- Docker

## 🐳 Run with Docker

```bash
docker build --platform linux/amd64 -t headingextractor .