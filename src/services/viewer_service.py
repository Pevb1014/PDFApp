from __future__ import annotations

from pathlib import Path

from src.adapters.system_adapter import SystemAdapter


class ViewerService:
    """Caso de uso para visualizar archivos PDF con el visor del sistema."""

    def __init__(self, system_adapter: SystemAdapter | None = None) -> None:
<<<<<<< HEAD
        self._system_adapter = system_adapter or SystemAdapter()

    def open_pdf(self, path: Path) -> None:
=======
        """
        Inicializa el servicio del visor.
        :param system_adapter: Adaptador para interactuar con el SO (abrir archivos).
        """
        self._system_adapter = system_adapter or SystemAdapter()

    def open_pdf(self, path: Path) -> None:
        """
        Abre el archivo PDF seleccionado con la aplicación predeterminada del SO.
        :param path: Ruta al archivo PDF.
        :raises FileNotFoundError: Si el archivo no existe.
        :raises ValueError: Si el archivo no es un PDF.
        """
>>>>>>> main
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError("El archivo seleccionado no es un PDF")
        self._system_adapter.open_file(path)
