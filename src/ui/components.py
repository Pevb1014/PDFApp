from __future__ import annotations

import tkinter as tk
from tkinter import ttk


<<<<<<< HEAD
def create_button(parent: tk.Widget, text: str, command) -> ttk.Button:
    return ttk.Button(parent, text=text, command=command)


def create_labeled_entry(parent: tk.Widget, label: str) -> tuple[ttk.Frame, ttk.Entry]:
=======
def create_button(parent: tk.Widget, text: str, command, style: str = "TButton") -> ttk.Button:
    """Crea un botón estilizado para la interfaz."""
    return ttk.Button(parent, text=text, command=command, style=style)


def create_labeled_entry(parent: tk.Widget, label: str) -> tuple[ttk.Frame, ttk.Entry]:
    """Crea un campo de entrada con una etiqueta al lado."""
>>>>>>> main
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 8))
    entry = ttk.Entry(frame)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    return frame, entry
