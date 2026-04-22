from __future__ import annotations

from pathlib import Path

from src.adapters.file_adapter import FileAdapter


class FileService:
<<<<<<< HEAD
    def __init__(self, file_adapter: FileAdapter | None = None) -> None:
        self._file_adapter = file_adapter or FileAdapter()

    def validate_pdf_inputs(self, paths: list[str]) -> list[Path]:
        files = self._file_adapter.validate_readable_files(paths)
        invalid = [p for p in files if p.suffix.lower() != ".pdf"]
        if invalid:
            raise ValueError(f"Solo se permiten PDF. Inválidos: {', '.join(map(str, invalid))}")
        return files

    def prepare_output_path(self, output_path: str) -> Path:
=======
    """
    Servicio encargado de la validación y preparación de archivos en el sistema.
    """

    def __init__(self, file_adapter: FileAdapter | None = None) -> None:
        """
        Inicializa el servicio de archivos.
        :param file_adapter: Adaptador para interactuar con el sistema de archivos.
        """
        self._file_adapter = file_adapter or FileAdapter()

    def validate_mixed_inputs(self, paths: list[str]) -> list[Path]:
        """
        Valida que las rutas correspondan a archivos PDF o Word (.docx) legibles.
        :param paths: Lista de rutas en formato string.
        :return: Lista de objetos Path validados.
        :raises ValueError: Si algún archivo no es .pdf o .docx.
        """
        files = self._file_adapter.validate_readable_files(paths)
        invalid = [p for p in files if p.suffix.lower() not in (".pdf", ".docx")]
        if invalid:
            raise ValueError(f"Solo se permiten PDF o Word (.docx). Inválidos: {', '.join(map(str, invalid))}")
        return files

    def validate_word_inputs(self, paths: list[str]) -> list[Path]:
        """
        Valida que las rutas proporcionadas correspondan a archivos Word (.docx) legibles.
        :param paths: Lista de rutas en formato string.
        :return: Lista de objetos Path validados.
        :raises ValueError: Si algún archivo no tiene extensión .docx.
        """
        files = self._file_adapter.validate_readable_files(paths)
        invalid = [p for p in files if p.suffix.lower() != ".docx"]
        if invalid:
            raise ValueError(f"Solo se permiten Word (.docx). Inválidos: {', '.join(map(str, invalid))}")
        return files

    def prepare_output_path(self, output_path: str) -> Path:
        """
        Prepara una ruta de salida asegurando que el directorio padre exista.
        :param output_path: Ruta de destino deseada.
        :return: Objeto Path validado.
        """
>>>>>>> main
        return self._file_adapter.ensure_parent_dir(output_path)
