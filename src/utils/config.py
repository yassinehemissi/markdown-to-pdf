from pathlib import Path

from ..models import Config


def load_config(path: Path | None = None) -> tuple[Config, Path]:
    """An explicit config must exist; a missing implicit config uses defaults."""
    candidate = path if path is not None else Path.cwd() / "config.json"
    if path is None and not candidate.exists():
        return Config(), Path.cwd()
    return Config.model_validate_json(candidate.read_text(encoding="utf-8-sig")), candidate.resolve().parent
