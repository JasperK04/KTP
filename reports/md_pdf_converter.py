"""
Markdown to PDF Converter
Converts Markdown files to nicely formatted PDF documents.
Generated with copilot. Claude Sonnet 4.5.
Prompt: i need the #file:system_report_draft.md  converted into a pdf. can you write a python script md_pdf_converter.py that converts mds to pdfs nicely pls
"""

import argparse
import os
import sys
from pathlib import Path

# Setup library paths for macOS BEFORE importing weasyprint
if sys.platform == 'darwin':  # macOS
    try:
        import subprocess
        result = subprocess.run(['brew', '--prefix'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        brew_prefix = result.stdout.strip()
        lib_path = os.path.join(brew_prefix, 'lib')
        current_path = os.environ.get('DYLD_LIBRARY_PATH', '')
        if lib_path not in current_path:
            os.environ['DYLD_LIBRARY_PATH'] = f"{lib_path}:{current_path}"
    except:
        pass

from markdown import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def get_css_styling():
    """Return CSS styling for the PDF output."""
    return """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: string(heading);
        }
        @bottom-center {
            content: counter(page);
        }
    }
    
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }
    
    h1 {
        font-size: 24pt;
        font-weight: bold;
        color: #1a1a1a;
        margin-top: 0;
        margin-bottom: 0.5em;
        page-break-after: avoid;
        string-set: heading content();
    }
    
    h2 {
        font-size: 18pt;
        font-weight: bold;
        color: #2a2a2a;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.3em;
    }
    
    h3 {
        font-size: 14pt;
        font-weight: bold;
        color: #3a3a3a;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }
    
    h4 {
        font-size: 12pt;
        font-weight: bold;
        color: #4a4a4a;
        margin-top: 1em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }
    
    p {
        margin: 0.5em 0;
        text-align: justify;
    }
    
    ul, ol {
        margin: 0.5em 0;
        padding-left: 2em;
    }
    
    li {
        margin: 0.3em 0;
    }
    
    code {
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        color: #d63384;
    }
    
    pre {
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 1em;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 1em 0;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        color: #333;
    }
    
    blockquote {
        border-left: 4px solid #ddd;
        padding-left: 1em;
        margin: 1em 0;
        color: #666;
        font-style: italic;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
        page-break-inside: avoid;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 0.5em;
        text-align: left;
    }
    
    th {
        background-color: #f0f0f0;
        font-weight: bold;
    }
    
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    strong, b {
        font-weight: bold;
    }
    
    em, i {
        font-style: italic;
    }
    
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 2em 0;
    }
    """


def convert_md_to_pdf(input_path: Path, output_path: Path = None):
    """
    Convert a Markdown file to PDF.
    
    Args:
        input_path: Path to the input Markdown file
        output_path: Path to the output PDF file (optional)
    
    Returns:
        Path to the generated PDF file
    """
    # Validate input file
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.suffix.lower() in ['.md', '.markdown']:
        raise ValueError(f"Input file must be a Markdown file (.md or .markdown)")
    
    # Determine output path
    if output_path is None:
        output_path = input_path.with_suffix('.pdf')
    else:
        output_path = Path(output_path)
    
    # Read Markdown content
    print(f"Reading Markdown from: {input_path}")
    md_content = input_path.read_text(encoding='utf-8')
    
    # Convert Markdown to HTML
    print("Converting Markdown to HTML...")
    html_content = markdown(
        md_content,
        extensions=[
            'extra',           # Tables, footnotes, etc.
            'codehilite',      # Syntax highlighting
            'toc',             # Table of contents
            'nl2br',           # Newline to <br>
            'sane_lists',      # Better list handling
        ]
    )
    
    # Wrap HTML with proper structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{input_path.stem}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Create PDF
    print(f"Generating PDF: {output_path}")
    font_config = FontConfiguration()
    html = HTML(string=full_html)
    css = CSS(string=get_css_styling(), font_config=font_config)
    html.write_pdf(output_path, stylesheets=[css], font_config=font_config)
    
    print(f"✓ PDF created successfully: {output_path}")
    return output_path


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to nicely formatted PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md
  %(prog)s input.md -o output.pdf
  %(prog)s document.md --output report.pdf
        """
    )
    
    parser.add_argument(
        'input',
        type=str,
        help='Input Markdown file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output PDF file path (default: same name as input with .pdf extension)'
    )
    
    args = parser.parse_args()
    
    try:
        input_path = Path(args.input)
        output_path = Path(args.output) if args.output else None
        
        convert_md_to_pdf(input_path, output_path)
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
