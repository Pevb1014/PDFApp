from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SignatureType = Literal["image", "text", "draw"]


@dataclass(slots=True)
class SignatureRule:
    keyword: str
    signature_type: SignatureType
    value: str | bytes
    display_name: str | None = None
    width: float = 150.0
    height: float = 48.0


@dataclass(slots=True)
class SignaturePlacement:
    page_index: int
    rect: tuple[float, float, float, float]
    signer_index: int
    keyword: str


@dataclass(slots=True)
class PDFSigningPreview:
    pdf_path: str
    placements: list[SignaturePlacement] = field(default_factory=list)


@dataclass(slots=True)
class BatchSigningResult:
    total_documents: int
    processed_documents: int
    total_signatures: int
    output_files: list[str]
    unsigned_files: list[str]
    errors: list[str]
