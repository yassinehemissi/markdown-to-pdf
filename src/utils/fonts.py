"""Use common system TrueType fonts when available, preserving core-font fallback."""

import os
from pathlib import Path

from fpdf import FPDF


def register_fonts(pdf: FPDF, family: str) -> str:
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    windows_names = {
        "Times": ("times", "timesbd", "timesi", "timesbi"),
        "Helvetica": ("arial", "arialbd", "ariali", "arialbi"),
        "Courier": ("cour", "courbd", "couri", "courbi"),
    }
    liberation = {"Times": "Serif", "Helvetica": "Sans", "Courier": "Mono"}[family]
    candidates = [tuple(windows / f"{name}.ttf" for name in windows_names[family])]
    for directory in ("/usr/share/fonts/truetype/liberation2", "/usr/share/fonts/truetype/liberation"):
        candidates.append(tuple(Path(directory) / f"Liberation{liberation}-{weight}.ttf" for weight in ("Regular", "Bold", "Italic", "BoldItalic")))
    for paths in candidates:
        if all(path.is_file() for path in paths):
            alias = f"Document{family}"
            for emphasis, path in zip(("", "B", "I", "BI"), paths):
                pdf.add_font(alias, emphasis, str(path))
            return alias
    return family
