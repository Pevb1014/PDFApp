from __future__ import annotations

from pathlib import Path

import fitz


class PDFEditAdapter:
    """Adaptador de infraestructura para edición de PDFs con PyMuPDF."""

    @staticmethod
    def open_document(path: Path) -> fitz.Document:
        return fitz.open(str(path))

    @staticmethod
    def save_document(document: fitz.Document, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(output_path))
