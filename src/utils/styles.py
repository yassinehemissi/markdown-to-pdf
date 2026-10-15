from importlib.resources import files
from pathlib import Path

from .. import styles as bundled_styles
from ..models import Style


def available_styles() -> list[str]:
    return sorted(item.name.removesuffix(".json") for item in files(bundled_styles).iterdir() if item.name.endswith(".json"))


def load_style(name: str, base: Path) -> Style:
    """Resolve custom JSON relative to config, then named local/bundled styles."""
    candidate = Path(name)
    if candidate.suffix.lower() == ".json":
        path = candidate if candidate.is_absolute() else base / candidate
        return Style.model_validate_json(path.read_text(encoding="utf-8-sig"))
    if candidate.name != name:
        raise ValueError("Style must be a name or a path ending in .json")
    local = base / "styles" / f"{name}.json"
    if local.is_file():
        return Style.model_validate_json(local.read_text(encoding="utf-8-sig"))
    bundled = files(bundled_styles).joinpath(f"{name}.json")
    if not bundled.is_file():
        raise ValueError(f"Unknown style {name!r}. Available: {', '.join(available_styles())}")
    return Style.model_validate_json(bundled.read_text(encoding="utf-8"))
