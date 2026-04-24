from __future__ import annotations

import tkinter as tk
import sys
from pathlib import Path

from src.core.config import CONFIG
from src.services.file_service import FileService
from src.services.pdf_service import PDFService
from src.services.viewer_service import ViewerService
from src.ui.main_window import MainWindow


def run() -> None:
    """
    Punto de entrada principal para iniciar la aplicación.
    Configura la ventana de Tkinter y orquesta los servicios.
    """
    if len(sys.argv) >= 3 and sys.argv[1] == "--qt-editor":
        from src.ui.pdf_editor_app import main as qt_editor_main

        sys.argv = ["pdf_editor_app", str(Path(sys.argv[2]).expanduser().resolve())]
        raise SystemExit(qt_editor_main())

    root = tk.Tk()
    root.title(f"{CONFIG.app_name} v{CONFIG.app_version}")
    root.geometry("900x650")
    root.minsize(850, 600)

    file_service = FileService()
    pdf_service = PDFService()
    viewer_service = ViewerService()
    MainWindow(
        root,
        file_service=file_service,
        pdf_service=pdf_service,
        viewer_service=viewer_service,
    )

    root.mainloop()


if __name__ == "__main__":
    run()
