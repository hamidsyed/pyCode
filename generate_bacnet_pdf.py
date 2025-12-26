"""
Simple Markdown -> PDF generator for the BMS BACnet documentation.

This script reads `BMS_BACNET_DOC.md` and writes `BMS_BACNET_DOC.pdf` in the same folder.
It uses `reportlab` to create the PDF. Install with:

    pip install reportlab

Run with Python 3.11 in the project venv:

    python generate_bacnet_pdf.py

Note: This is a basic formatter — it converts markdown headings and paragraphs into
PDF paragraphs and does not render complex markdown features (tables, code blocks)
faithfully. For high-fidelity conversion consider `pandoc` or `weasyprint` workflows.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

INPUT = "BMS_BACNET_DOC.md"
OUTPUT = "BMS_BACNET_DOC.pdf"

styles = getSampleStyleSheet()
# Update existing styles or add custom ones if they don't exist
if 'Heading1' not in styles:
    styles.add(ParagraphStyle(name='Heading1', fontSize=18, leading=22, spaceAfter=12))
else:
    styles['Heading1'].fontSize = 18
    styles['Heading1'].leading = 22
    styles['Heading1'].spaceAfter = 12
    
if 'Heading2' not in styles:
    styles.add(ParagraphStyle(name='Heading2', fontSize=14, leading=18, spaceAfter=10))
else:
    styles['Heading2'].fontSize = 14
    styles['Heading2'].leading = 18
    styles['Heading2'].spaceAfter = 10
    
if 'Heading3' not in styles:
    styles.add(ParagraphStyle(name='Heading3', fontSize=12, leading=14, spaceAfter=8))
else:
    styles['Heading3'].fontSize = 12
    styles['Heading3'].leading = 14
    styles['Heading3'].spaceAfter = 8
    
if 'Code' not in styles:
    styles.add(ParagraphStyle(name='Code', fontName='Courier', fontSize=9, leading=12))


def md_to_flowables(md_text: str):
    flowables = []
    lines = md_text.splitlines()
    buf = []

    def flush_buf_as_paragraph():
        nonlocal buf
        if not buf:
            return
        text = ' '.join(line.strip() for line in buf)
        flowables.append(Paragraph(text, styles['Normal']))
        flowables.append(Spacer(1, 6))
        buf = []

    for line in lines:
        if line.startswith('# '):
            flush_buf_as_paragraph()
            flowables.append(Paragraph(line[2:].strip(), styles['Heading1']))
        elif line.startswith('## '):
            flush_buf_as_paragraph()
            flowables.append(Paragraph(line[3:].strip(), styles['Heading2']))
        elif line.startswith('### '):
            flush_buf_as_paragraph()
            flowables.append(Paragraph(line[4:].strip(), styles['Heading3']))
        elif line.strip() == '':
            flush_buf_as_paragraph()
        elif line.startswith('```'):
            flush_buf_as_paragraph()
            # simple code block capture
            # collect until next ```
            code_lines = []
            continue
        else:
            buf.append(line)
    flush_buf_as_paragraph()
    return flowables


def generate_pdf(input_path=INPUT, output_path=OUTPUT):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md = f.read()
    flowables = md_to_flowables(md)
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    doc.build(flowables)
    print(f"Generated PDF: {output_path}")


if __name__ == '__main__':
    try:
        generate_pdf()
    except Exception as e:
        print('Failed to generate PDF:', e)
        print('Make sure you installed reportlab: pip install reportlab')
