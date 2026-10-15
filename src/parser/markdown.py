"""Parse CommonMark into escaped HTML understood by fpdf2."""

from html import escape

from markdown_it import MarkdownIt
from markdown_it.token import Token

from ..models import Document


def parse_markdown(source: str) -> Document:
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")

    def code_block(tokens: list[Token], index: int, *_: object) -> str:
        # fpdf2's pre element supplies the monospace font and preserves newlines.
        return f"<pre>{escape(tokens[index].content)}</pre>\n"

    def image(tokens: list[Token], index: int, *_: object) -> str:
        # Local and remote image loading is deliberately not part of this MVP.
        return escape(f"[Image: {tokens[index].content}]")

    parser.renderer.rules["fence"] = code_block
    parser.renderer.rules["code_block"] = code_block
    parser.renderer.rules["image"] = image
    tokens = parser.parse(source)
    title = None
    for index, token in enumerate(tokens[:-1]):
        if token.type == "heading_open" and token.tag == "h1":
            title = tokens[index + 1].content
            break
    return Document(html=parser.renderer.render(tokens, parser.options, {}), title=title)
