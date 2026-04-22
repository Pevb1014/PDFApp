from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


class PDFAdapter:
    """Encapsula la librería pypdf para desacoplar la infraestructura."""

    @staticmethod
    def reader(path: Path) -> PdfReader:
        return PdfReader(str(path))

    @staticmethod
    def writer() -> PdfWriter:
        return PdfWriter()
