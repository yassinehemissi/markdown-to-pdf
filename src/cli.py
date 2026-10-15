"""Command-line entry point."""

import argparse
import sys
from pathlib import Path

from fpdf.errors import FPDFException

from . import __version__
from .conversion import convert_markdown
from .models import Config
from .utils.config import load_config
from .utils.styles import available_styles


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to a styled PDF without LaTeX.")
    parser.add_argument("input", nargs="?", type=Path, help="UTF-8 Markdown file")
    parser.add_argument("-o", "--output", type=Path, help="PDF destination (default: beside input)")
    parser.add_argument("-c", "--config", type=Path, help="JSON config (default: ./config.json if present)")
    parser.add_argument("-s", "--style", help="Bundled style name or custom JSON file")
    parser.add_argument("--title", help="PDF title metadata")
    parser.add_argument("--author", help="PDF author metadata")
    parser.add_argument("--list-styles", action="store_true", help="List bundled styles and exit")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    if args.list_styles:
        print("\n".join(available_styles()))
        return 0
    if args.input is None:
        parser.error("an input Markdown file is required")
    try:
        config, base = load_config(args.config)
        overrides = {key: getattr(args, key) for key in ("style", "title", "author") if getattr(args, key) is not None}
        config = Config.model_validate(config.model_dump() | overrides)
        destination = args.output or args.input.with_suffix(".pdf")
        if args.input.resolve() == destination.resolve():
            raise ValueError("Input and output paths must be different")
        convert_markdown(args.input.read_text(encoding="utf-8-sig"), destination, config, Path.cwd() if args.style else base)
    except (OSError, ValueError, FPDFException) as error:
        print(f"md2pdf: {error}", file=sys.stderr)
        return 1
    print(f"Created {destination}")
    return 0
