from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from src.core.pdf_security import PDFInvalidPasswordError, PDFPasswordRequiredError


class PDFAdapter:
    """Encapsula la librería pypdf para desacoplar la infraestructura."""

    @staticmethod
    def reader(path: Path, password: str | None = None) -> PdfReader:
        reader = PdfReader(str(path))
        if not reader.is_encrypted:
            return reader

        if not password:
            raise PDFPasswordRequiredError(path)

        auth_result = reader.decrypt(password)
        if auth_result == 0:
            raise PDFInvalidPasswordError(path)
        return reader

    @staticmethod
    def writer() -> PdfWriter:
        return PdfWriter()
