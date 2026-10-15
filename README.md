# Markdown to PDF

A Python CLI that converts UTF-8 Markdown into professional PDFs using
[markdown-it-py](https://github.com/executablebooks/markdown-it-py),
[fpdf2](https://py-pdf.github.io/fpdf2/), and Pydantic. No LaTeX installation is
required: the default style uses LaTeX-inspired serif typography.

## Install

Python 3.11 or later:

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

For regular use, `python -m pip install .` installs the CLI and bundled styles.
After changing the source layout, reinstall with `python -m pip install -e ".[dev]"`
to refresh the editable package mapping and launchers.

## Use

```sh
md2pdf examples/sample.md
md2pdf notes.md -o output/report.pdf
md2pdf notes.md --style simple
md2pdf notes.md --config config.json --title "Quarterly report" --author "Jane"
md2pdf --list-styles
python -m markdown_to_pdf notes.md
```

From the repository root, you can also use `python -m src examples/sample.md`.
Install the dependencies first using the install command above.

By default, output is written beside the input with a `.pdf` extension. Parent
output folders are created automatically. Existing PDFs are replaced atomically;
the input cannot be used as the output. Errors print to stderr and return exit
code 1; invalid CLI arguments return 2.

## Desktop UI

Launch the Tkinter interface to paste or type Markdown directly and save a PDF:

```sh
md2pdf-ui
# Or:
python -m markdown_to_pdf.ui
```

From the repository root, `python -m src.ui` also launches the UI.

Choose a bundled style or browse to a custom style JSON, optionally set title and
author, then click **Generate PDF…** to choose the destination. The editor stays
responsive during export, and your text stays available if export fails.
The UI loads defaults from `./config.json`; relative style paths use that file's
directory. Changes in the UI apply to that export without modifying the config.
Tkinter is included in standard Windows/macOS Python installs; on Linux it may
need the distribution's `python3-tk` package. After updating an existing install,
run `python -m pip install -e .` again to register `md2pdf-ui`.

## Configuration

The CLI reads `config.json` from the working directory when present. Use
`--config path/to/config.json` to select another file. Missing explicit configs,
unknown fields, and invalid values are errors. CLI options override config values.

```json
{
  "style": "professional",
  "title": null,
  "author": "",
  "page_numbers": true
}
```

`title` controls PDF metadata; when null, it uses the first level-one heading.
Headings are rendered as written, without inserting a second title.

## Styles

Bundled styles live in `src/styles/` and ship with the package:

- `professional`: serif, spacious margins, restrained headings (default).
- `simple`: sans serif, compact margins, blue headings.

To customize, copy a bundled JSON into your own `styles/` folder:

```json
{
  "name": "my-report",
  "font": "Times",
  "font_size": 11,
  "line_height": 1.45,
  "heading_color": "#202020",
  "heading_sizes": [24, 18, 14, 12, 11, 10],
  "page_format": "A4",
  "margins": {"left": 25, "right": 25, "top": 22, "bottom": 22}
}
```

Set `"style": "my-report"` to load `styles/my-report.json` beside your config,
or set `"style": "styles/my-report.json"` directly. Config paths resolve relative
to the config file; `--style ./styles/my-report.json` resolves relative to the
working directory. Named local styles override bundled ones.

Font options are `Times`, `Helvetica`, and `Courier`; page formats are `A4` and
`Letter`. Margins use millimeters, font sizes use points, and line height is a
multiplier. Windows Times New Roman/Arial/Courier New and Linux Liberation fonts
are detected automatically for Unicode text. Without them, PDF core fonts are
used with limited Western character coverage. Unsupported characters produce
an actionable error; fonts must contain glyphs for your document's language.

## Supported Markdown

Headings, paragraphs, bold, italic, inline code, fenced and indented code blocks,
ordered and unordered lists, nested lists, blockquotes, links, horizontal rules,
and pipe tables. Text paginates automatically; page numbers are configurable.

This first version does not typeset LaTeX math, highlight code syntax, or render
raw HTML. Images become `[Image: alt text]` placeholders; no images are fetched.
Complex table layout and extremely long cells are limited by fpdf2's HTML renderer.

## Layout and development

```text
src/
  __init__.py       # Package version
  __main__.py       # Module-based CLI launcher
  cli.py            # Arguments and conversion workflow
  models.py         # Pydantic config, style, document models
  renderer.py       # PDF layout and typography
  conversion.py     # Shared text-to-PDF workflow for CLI and UI
  ui/               # Tkinter Markdown editor and PDF export
  parser/           # Markdown parsing and token rendering
  styles/           # Packaged JSON style definitions
  utils/            # Config loading, font discovery, atomic output
tests/              # End-to-end PDF and error checks
examples/sample.md
config.json
```

```sh
python -m pytest
```

Packaging maps `src/` to the installed `markdown_to_pdf` package, so the existing
`md2pdf`, `md2pdf-ui`, and `python -m markdown_to_pdf` commands keep working.
Run modules with `-m` rather than executing `src/cli.py` or `src/ui/app.py`
directly, so their relative imports resolve correctly.
