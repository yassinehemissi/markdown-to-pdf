"""Shared conversion workflow for file-based and interactive clients."""

from pathlib import Path

from .models import Config
from .parser import parse_markdown
from .renderer import render_pdf
from .utils.output import write_pdf
from .utils.styles import load_style


def convert_markdown(source: str, destination: Path, config: Config, style_base: Path) -> Path:
    """Generate a PDF directly from Markdown text using validated settings."""
    style = load_style(config.style, style_base)
    document = parse_markdown(source)
    write_pdf(destination, render_pdf(document, config, style))
    return destination
