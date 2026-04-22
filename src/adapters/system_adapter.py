from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


class SystemAdapter:
    """Adapter para integrar acciones del sistema operativo."""

    @staticmethod
    def open_file(path: Path) -> None:
<<<<<<< HEAD
=======
        """
        Abre un archivo utilizando el comando predeterminado del SO.
        :param path: Ruta al archivo.
        """
>>>>>>> main
        system = platform.system()
        if system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
            return
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
            return
        subprocess.run(["xdg-open", str(path)], check=True)
