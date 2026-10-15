# A Professional Markdown Report

This report demonstrates **bold**, *italic*, and `inline code` with a restrained, LaTeX-inspired layout. Typography includes café, naïve, and an em dash — using available system fonts.

## Findings

1. Parse Markdown with markdown-it-py.
2. Validate settings with Pydantic.
3. Generate the PDF with fpdf2.

- Styles are JSON files.
- Layout is separate from parsing.
  - Nested lists work too.

> Clear typography makes technical writing easier to read.

### A small example

```python
from pathlib import Path

def hello(name: str) -> str:
    return f"Hello, {name}!"
```

| Component | Responsibility |
| --- | --- |
| parser/ | Markdown parsing |
| utils/ | Shared helpers |
| styles/ | Typography and page settings |

Read the [Markdown parser documentation](https://markdown-it-py.readthedocs.io/).

---

No LaTeX installation is required.
