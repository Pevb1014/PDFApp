from __future__ import annotations

from pathlib import Path


def ensure_pdf_extension(file_path: str | Path) -> Path:
<<<<<<< HEAD
=======
    """
    Asegura que la ruta termine en .pdf.
    :param file_path: Ruta original.
    :return: Objeto Path con extensión .pdf.
    """
>>>>>>> main
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        return path.with_suffix(".pdf")
    return path


def human_error(exc: Exception) -> str:
<<<<<<< HEAD
=======
    """
    Convierte una excepción en un mensaje de error legible para el usuario.
    :param exc: Excepción capturada.
    :return: Mensaje de error formateado.
    """
>>>>>>> main
    return f"{type(exc).__name__}: {exc}"
