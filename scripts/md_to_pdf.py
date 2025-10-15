#!/usr/bin/env python3
"""Convert markdown file to PDF with styling."""

import sys
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def convert_md_to_pdf(md_file: str, pdf_file: str):
    """Convert markdown file to styled PDF."""

    # Read markdown content
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML with better list handling
    html_content = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "codehilite", "sane_lists"],  # Better list handling
    )

    # Add CSS styling
    css_style = """
        @page {
            size: letter;
            margin: 0.75in;
        }
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #333;
        }
        h1 {
            color: #1a73e8;
            font-size: 24pt;
            margin-top: 0.5em;
            margin-bottom: 0.3em;
            page-break-after: avoid;
        }
        h2 {
            color: #1a73e8;
            font-size: 18pt;
            margin-top: 1em;
            margin-bottom: 0.3em;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.2em;
            page-break-after: avoid;
        }
        h3 {
            color: #34a853;
            font-size: 14pt;
            margin-top: 0.8em;
            margin-bottom: 0.3em;
            page-break-after: avoid;
        }
        h4 {
            color: #666;
            font-size: 12pt;
            margin-top: 0.6em;
            margin-bottom: 0.2em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }
        th {
            background-color: #1a73e8;
            color: white;
            padding: 8px;
            text-align: left;
            font-weight: bold;
        }
        td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }
        pre {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #1a73e8;
            margin-left: 0;
            padding-left: 1em;
            color: #666;
        }
        hr {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 2em 0;
        }
        ul, ol {
            margin: 0.8em 0;
            padding-left: 2em;
            list-style-position: outside;
        }
        li {
            margin: 0.5em 0;
            line-height: 1.6;
            display: list-item;
            page-break-inside: avoid;
        }
        li p {
            margin: 0.2em 0;
        }
        strong {
            color: #000;
            font-weight: 600;
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
        .page-break {
            page-break-before: always;
        }
    """

    # Wrap HTML with proper structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Cloud Cost Comparison</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF
    HTML(string=full_html).write_pdf(pdf_file, stylesheets=[CSS(string=css_style)])

    print(f"✅ Converted {md_file} → {pdf_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2]

    if not Path(md_file).exists():
        print(f"Error: File not found: {md_file}")
        sys.exit(1)

    convert_md_to_pdf(md_file, pdf_file)
