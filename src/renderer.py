"""PDF layout and typography; Markdown syntax lives in parser/."""

from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.errors import FPDFUnicodeEncodingException

from .models import Config, Document, Style
from .utils.fonts import register_fonts


class StyledPDF(FPDF):
    def __init__(self, style: Style, page_numbers: bool) -> None:
        super().__init__(format=style.page_format)
        self.page_numbers = page_numbers
        self.body_font = style.font

    def footer(self) -> None:
        if self.page_numbers:
            self.set_y(-12)
            self.set_font(self.body_font, size=9)
            self.set_text_color(110)
            self.cell(0, 5, str(self.page_no()), align="C")


def render_pdf(document: Document, config: Config, style: Style) -> bytearray:
    pdf = StyledPDF(style, config.page_numbers)
    body_font = register_fonts(pdf, style.font)
    code_font = body_font if style.font == "Courier" else register_fonts(pdf, "Courier")
    pdf.body_font = body_font
    margins = style.margins
    pdf.set_margins(margins.left, margins.top, margins.right)
    pdf.set_auto_page_break(auto=True, margin=margins.bottom)
    pdf.set_title(config.title if config.title is not None else document.title or "Untitled")
    pdf.set_author(config.author)
    pdf.set_creator("markdown-to-pdf-cli")
    pdf.add_page()
    pdf.set_font(body_font, size=style.font_size)
    color = tuple(int(style.heading_color[index:index + 2], 16) for index in (1, 3, 5))
    tag_styles = {
        f"h{level}": FontFace(family=body_font, emphasis="B", size_pt=size, color=color)
        for level, size in enumerate(style.heading_sizes, start=1)
    }
    tag_styles["code"] = FontFace(family=code_font, size_pt=style.font_size * 0.9)
    tag_styles["pre"] = FontFace(family=code_font, size_pt=style.font_size * 0.85)
    tag_styles["blockquote"] = FontFace(family=body_font, emphasis="I", color="#505050")
    try:
        html = document.html
        for tag in ("p", "ul", "ol"):
            html = html.replace(f"<{tag}>", f'<{tag} line-height="{style.line_height}">')
        pdf.write_html(html, tag_styles=tag_styles, font_family=body_font, li_prefix_color=color)
        return pdf.output()
    except FPDFUnicodeEncodingException as error:
        raise ValueError("This document needs a Unicode font. Install Times New Roman/Arial/Courier New or Liberation fonts.") from error
