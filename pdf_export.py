from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# Try to register a monospaced font; fallback to Courier if DejaVuSansMono not found
try:
    pdfmetrics.registerFont(TTFont('DejaVuSansMono', 'DejaVuSansMono.ttf'))
    MONO_FONT = 'DejaVuSansMono'
except Exception:
    MONO_FONT = 'Courier'

MARGIN_X = 15 * mm
MARGIN_Y = 15 * mm
FONT_SIZE = 9
LINE_SPACING = 11  # pts


def write_text_pdf(input_path: str, output_path: str, title: str | None = None):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Header
    if not title:
        title = os.path.basename(input_path)

    def draw_header_footer(page_num: int):
        c.setFont(MONO_FONT, 8)
        c.setFillColorRGB(0, 0, 0)
        # Header line
        c.drawString(MARGIN_X, height - MARGIN_Y + 2, title)
        # Footer with page number
        c.drawRightString(width - MARGIN_X, MARGIN_Y - 5, f"Page {page_num}")
        # Top/bottom rules
        c.line(MARGIN_X, height - MARGIN_Y, width - MARGIN_X, height - MARGIN_Y)
        c.line(MARGIN_X, MARGIN_Y, width - MARGIN_X, MARGIN_Y)

    # Content area
    x = MARGIN_X
    y_start = height - MARGIN_Y - 15
    y = y_start

    c.setFont(MONO_FONT, FONT_SIZE)

    page_num = 1
    draw_header_footer(page_num)

    def new_page():
        nonlocal page_num, y
        c.showPage()
        c.setFont(MONO_FONT, FONT_SIZE)
        page_num += 1
        draw_header_footer(page_num)
        y = y_start

    # Read file and write lines with wrapping if needed
    if not os.path.exists(input_path):
        text = f"[ERROR] File not found: {input_path}\n"
        lines = [text]
    else:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.read().splitlines()

    # Compute approx characters per line based on font metrics (rough wrap)
    # Using Courier width ~ 0.6 * font size per character in points.
    # Derive usable width
    usable_width = (width - 2 * MARGIN_X)
    avg_char_width = 0.6 * FONT_SIZE
    max_chars = max(10, int(usable_width / avg_char_width))

    for raw in lines:
        # Expand tabs for consistency
        line = raw.expandtabs(4)
        # Wrap long lines
        while len(line) > max_chars:
            segment = line[:max_chars]
            # Try to break at last space for better wrap
            brk = segment.rfind(' ')
            if brk >= max(20, int(max_chars * 0.6)):
                segment = line[:brk]
                line = line[brk+1:]
            else:
                line = line[max_chars:]
            c.drawString(x, y, segment)
            y -= LINE_SPACING
            if y < MARGIN_Y + 20:
                new_page()
        # Draw remaining part
        c.drawString(x, y, line)
        y -= LINE_SPACING
        if y < MARGIN_Y + 20:
            new_page()

    c.save()


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    targets = [
        (os.path.join(base, 'app.py'), os.path.join(base, 'app.pdf'), 'app.py'),
        (os.path.join(base, 'Innovation_Brief.md'), os.path.join(base, 'Innovation_Brief.pdf'), 'Innovation_Brief.md'),
        (os.path.join(base, 'README.md'), os.path.join(base, 'README.pdf'), 'README.md'),
        (os.path.join(base, 'requirements.txt'), os.path.join(base, 'requirements.pdf'), 'requirements.txt'),
    ]

    for src, dst, title in targets:
        print(f'Generating {os.path.basename(dst)} from {os.path.basename(src)} ...')
        write_text_pdf(src, dst, title=title)
    print('Done. PDFs generated in project directory.')


if __name__ == '__main__':
    main()
