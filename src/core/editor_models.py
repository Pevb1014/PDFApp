from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


OverlayKind = Literal[
    "text_edit",
    "text_add",
    "signature_text",
    "signature_image",
    "signature_draw",
]


@dataclass
class OverlayStyle:
    font_family: str = "Helvetica"
    font_size: float = 12.0
    color_rgb: tuple[float, float, float] = (0, 0, 0)


@dataclass
class OverlayItem:
    kind: OverlayKind
    page_index: int
    rect: tuple[float, float, float, float]
    text: str = ""
    image_bytes: bytes | None = None
    image_ext: str = "png"
    style: OverlayStyle = field(default_factory=OverlayStyle)
