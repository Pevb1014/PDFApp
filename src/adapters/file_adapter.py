from __future__ import annotations

from pathlib import Path


class FileAdapter:
    """Operaciones de infraestructura sobre rutas y sistema de archivos."""

    @staticmethod
    def validate_readable_files(paths: list[str]) -> list[Path]:
        """
        Verifica que una lista de rutas correspondan a archivos existentes y legibles.
        :param paths: Lista de rutas.
        :return: Lista de objetos Path resueltos.
        :raises FileNotFoundError: Si un archivo no existe.
        :raises ValueError: Si la ruta no es un archivo.
        """
        resolved: list[Path] = []
        for raw in paths:
            path = Path(raw).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"No existe el archivo: {path}")
            if not path.is_file():
                raise ValueError(f"La ruta no es un archivo: {path}")
            resolved.append(path)
        return resolved

    @staticmethod
    def ensure_parent_dir(path: str | Path) -> Path:
        """
        Asegura que el directorio padre de una ruta exista.
        :param path: Ruta objetivo.
        :return: Objeto Path resuelto.
        """
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        return target
