from __future__ import annotations

import io
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import fitz

from src.core.signature.models import PDFSigningPreview


class SignaturePreviewWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, previews: list[PDFSigningPreview]) -> None:
        super().__init__(master)
        self.title("Vista previa de zonas detectadas")
        self.geometry("960x640")
        self.result = False
        self._previews = previews
        self._images: list[tk.PhotoImage] = []

        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Revisa las zonas detectadas antes de firmar", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(body)
        body.add(left, weight=1)
        right = ttk.Frame(body)
        body.add(right, weight=3)

        self.listbox = tk.Listbox(left)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.canvas = tk.Canvas(right, bg="#f8f8f8")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        for preview in previews:
            self.listbox.insert(tk.END, f"{Path(preview.pdf_path).name} ({len(preview.placements)} zonas)")

        footer = ttk.Frame(self, padding=10)
        footer.pack(fill=tk.X)
        ttk.Button(footer, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(footer, text="Confirmar y firmar", command=self._confirm).pack(side=tk.RIGHT, padx=8)

        if previews:
            self.listbox.selection_set(0)
            self._render_preview(0)

    def _on_select(self, _event=None) -> None:
        selected = self.listbox.curselection()
        if not selected:
            return
        self._render_preview(selected[0])

    def _render_preview(self, index: int) -> None:
        preview = self._previews[index]
        doc = fitz.open(preview.pdf_path)
        try:
            first_page = doc[0]
            pix = first_page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1), alpha=False)
            image_bytes = pix.tobytes("png")
        finally:
            doc.close()

        image = tk.PhotoImage(data=image_bytes)
        self._images = [image]
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, image=image, anchor=tk.NW)

        scale = 1.1
        colors = ["#f44336", "#2196f3", "#4caf50", "#ff9800", "#9c27b0"]
        for i, placement in enumerate(preview.placements):
            if placement.page_index != 0:
                continue
            x0, y0, x1, y1 = placement.rect
            color = colors[placement.signer_index % len(colors)]
            self.canvas.create_rectangle(
                10 + x0 * scale,
                10 + y0 * scale,
                10 + x1 * scale,
                10 + y1 * scale,
                outline=color,
                width=2,
            )

    def _confirm(self) -> None:
        self.result = True
        self.destroy()
