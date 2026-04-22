from __future__ import annotations

import tkinter as tk

from src.core.config import CONFIG
from src.services.file_service import FileService
from src.services.pdf_service import PDFService
from src.services.viewer_service import ViewerService
from src.ui.main_window import MainWindow


def run() -> None:
<<<<<<< HEAD
    root = tk.Tk()
    root.title(f"{CONFIG.app_name} v{CONFIG.app_version}")
    root.geometry("880x620")
=======
    """
    Punto de entrada principal para iniciar la aplicación.
    Configura la ventana de Tkinter y orquesta los servicios.
    """
    root = tk.Tk()
    root.title(f"{CONFIG.app_name} v{CONFIG.app_version}")
    root.geometry("900x650")
    root.minsize(850, 600)
>>>>>>> main

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
