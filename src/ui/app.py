"""Small paste-to-PDF desktop interface. Tk operations stay on the UI thread."""

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from ..conversion import convert_markdown
from ..models import Config
from ..utils.config import load_config
from ..utils.styles import available_styles


class MarkdownApp:
    def __init__(self, root: tk.Tk, config: Config, style_base: Path) -> None:
        self.root = root
        self.config = config
        self.style_base = style_base
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pdf-export")
        self.pending: Future[Path] | None = None
        self.title = tk.StringVar(root, config.title or "")
        self.author = tk.StringVar(root, config.author)
        self.style = tk.StringVar(root, config.style)
        self.page_numbers = tk.BooleanVar(root, config.page_numbers)
        self.status = tk.StringVar(root, "Paste Markdown below, then choose Generate PDF.")
        root.title("Markdown to PDF")
        root.geometry("820x650")
        root.minsize(600, 450)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)
        ttk.Label(frame, text="Markdown to PDF", font=("TkDefaultFont", 16, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )
        ttk.Label(frame, text="Title (optional)").grid(row=1, column=0, sticky="w", padx=(0, 12))
        ttk.Entry(frame, textvariable=self.title).grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)
        ttk.Label(frame, text="Author").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.author).grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)
        ttk.Label(frame, text="Style").grid(row=3, column=0, sticky="w")
        choices = sorted(set(available_styles() + [self.config.style]))
        ttk.Combobox(frame, textvariable=self.style, values=choices).grid(row=3, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse style…", command=self.browse_style).grid(row=3, column=2, padx=(8, 0))
        ttk.Label(frame, text="Markdown · paste or type here").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(12, 6)
        )
        ttk.Checkbutton(frame, text="Page numbers", variable=self.page_numbers).grid(row=4, column=2, sticky="e")
        self.editor = ScrolledText(frame, wrap="word", undo=True, font=("Courier", 11), padx=10, pady=10)
        self.editor.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.generate_button = ttk.Button(frame, text="Generate PDF…", command=self.generate)
        self.generate_button.grid(row=6, column=2, sticky="e", pady=(12, 0))
        ttk.Label(frame, textvariable=self.status, wraplength=500).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(12, 0), padx=(0, 12)
        )
        self.editor.focus_set()

    def browse_style(self) -> None:
        selected = filedialog.askopenfilename(parent=self.root, title="Choose a JSON style", filetypes=[("JSON styles", "*.json")])
        if selected:
            self.style.set(str(Path(selected).resolve()))

    def generate(self) -> None:
        if self.pending is not None:
            return
        source = self.editor.get("1.0", "end-1c")
        if not source.strip():
            messagebox.showwarning("Markdown required", "Paste or type some Markdown first.", parent=self.root)
            return
        try:
            config = Config.model_validate(self.config.model_dump() | {
                "title": self.title.get().strip() or None,
                "author": self.author.get(),
                "style": self.style.get().strip(),
                "page_numbers": self.page_numbers.get(),
            })
        except ValueError as error:
            messagebox.showerror("Invalid settings", str(error), parent=self.root)
            return
        selected = filedialog.asksaveasfilename(
            parent=self.root, title="Save PDF", defaultextension=".pdf",
            initialfile="document.pdf", filetypes=[("PDF documents", "*.pdf")],
        )
        if not selected:
            return
        self.generate_button.state(["disabled"])
        self.status.set("Generating PDF…")
        self.pending = self.executor.submit(convert_markdown, source, Path(selected), config, self.style_base)
        self.root.after(100, self._check_export)

    def _check_export(self) -> None:
        if self.pending is None:
            return
        if not self.pending.done():
            self.root.after(100, self._check_export)
            return
        try:
            destination = self.pending.result()
        except Exception as error:
            # At the GUI boundary, report worker failures without losing the editor.
            self.status.set("Export failed. Your Markdown is still in the editor.")
            messagebox.showerror("Could not generate PDF", str(error), parent=self.root)
        else:
            self.status.set(f"Saved: {destination}")
        finally:
            self.pending = None
            self.generate_button.state(["!disabled"])

    def close(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    root.withdraw()
    try:
        config, base = load_config()
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load config.json", str(error), parent=root)
        root.destroy()
        return 1
    MarkdownApp(root, config, base)
    root.deiconify()
    root.mainloop()
    return 0
