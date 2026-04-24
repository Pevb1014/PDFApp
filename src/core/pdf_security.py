from __future__ import annotations

from pathlib import Path


class PDFSecurityError(RuntimeError):
    """Error base para problemas de seguridad/cifrado en PDFs."""


class PDFPasswordRequiredError(PDFSecurityError):
    """Se lanza cuando un PDF requiere contraseña y no se proporcionó."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"El PDF '{path.name}' está protegido con contraseña.")
        self.path = path


class PDFInvalidPasswordError(PDFSecurityError):
    """Se lanza cuando la contraseña provista para un PDF es inválida."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"La contraseña ingresada para '{path.name}' es incorrecta.")
        self.path = path
