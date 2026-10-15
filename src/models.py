"""Validated configuration shared by the CLI, parser, and renderer."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

FontSize = Annotated[float, Field(ge=6, le=72)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Margins(Model):
    left: float = Field(default=25, ge=5, le=60)
    right: float = Field(default=25, ge=5, le=60)
    top: float = Field(default=22, ge=5, le=60)
    bottom: float = Field(default=22, ge=10, le=60)


class Style(Model):
    name: str
    description: str = ""
    font: Literal["Times", "Helvetica", "Courier"] = "Times"
    font_size: float = Field(default=11, ge=6, le=24)
    line_height: float = Field(default=1.4, ge=1, le=3)
    heading_color: str = Field(default="#202020", pattern=r"^#[0-9a-fA-F]{6}$")
    heading_sizes: tuple[FontSize, FontSize, FontSize, FontSize, FontSize, FontSize] = (24, 18, 14, 12, 11, 10)
    page_format: Literal["A4", "Letter"] = "A4"
    margins: Margins = Field(default_factory=Margins)


class Config(Model):
    style: str = Field(default="professional", min_length=1)
    title: str | None = None
    author: str = ""
    page_numbers: bool = True


class Document(Model):
    html: str
    title: str | None = None
