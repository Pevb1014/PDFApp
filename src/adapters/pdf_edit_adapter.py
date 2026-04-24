from __future__ import annotations

from pathlib import Path

import fitz

from src.core.pdf_security import PDFInvalidPasswordError, PDFPasswordRequiredError


class PDFEditAdapter:
    """Adaptador de infraestructura para edición de PDFs con PyMuPDF."""

    @staticmethod
    def open_document(path: Path, password: str | None = None) -> fitz.Document:
        document = fitz.open(str(path))
        if not document.needs_pass:
            return document

        if not password:
            document.close()
            raise PDFPasswordRequiredError(path)

        if not document.authenticate(password):
            document.close()
            raise PDFInvalidPasswordError(path)
        return document

    @staticmethod
    def save_document(document: fitz.Document, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(output_path))
