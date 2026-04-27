from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict
from tkinter import filedialog, messagebox, simpledialog, ttk

from src.core.signature.models import SignatureRule


class DrawSignatureDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Firma dibujada")
        self.geometry("460x220")
        self.result: str | None = None
        self._strokes: list[list[tuple[float, float]]] = []
        self._active_stroke: list[tuple[float, float]] = []

        self.canvas = tk.Canvas(self, bg="white", width=430, height=150)
        self.canvas.pack(padx=10, pady=8, fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self._start_stroke)
        self.canvas.bind("<B1-Motion>", self._draw_stroke)
        self.canvas.bind("<ButtonRelease-1>", self._end_stroke)

        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(buttons, text="Limpiar", command=self._clear).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Guardar", command=self._save).pack(side=tk.RIGHT)

    def _start_stroke(self, event: tk.Event) -> None:
        self._active_stroke = [(event.x, event.y)]

    def _draw_stroke(self, event: tk.Event) -> None:
        if not self._active_stroke:
            return
        x0, y0 = self._active_stroke[-1]
        self.canvas.create_line(x0, y0, event.x, event.y, fill="black", width=3, capstyle=tk.ROUND, smooth=True)
        self._active_stroke.append((event.x, event.y))

    def _end_stroke(self, _event: tk.Event) -> None:
        if len(self._active_stroke) > 1:
            self._strokes.append(self._active_stroke)
        self._active_stroke = []

    def _clear(self) -> None:
        self._strokes.clear()
        self._active_stroke = []
        self.canvas.delete("all")

    def _save(self) -> None:
        if not self._strokes:
            messagebox.showwarning("Firma", "Dibuja una firma antes de guardar.")
            return
        self.result = json.dumps(self._strokes)
        self.destroy()


class SignerPanel(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Configuración de firmantes")
        self.geometry("760x420")
        self.result: list[SignatureRule] | None = None
        self._rules: list[SignatureRule] = []

        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Define reglas de firma por palabra clave", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        controls = ttk.Frame(self, padding=(10, 0, 10, 10))
        controls.pack(fill=tk.X)
        ttk.Button(controls, text="➕ Add Signer", command=self._add_signer).pack(side=tk.LEFT)
        ttk.Button(controls, text="❌ Eliminar seleccionado", command=self._remove_selected).pack(side=tk.LEFT, padx=8)

        self.tree = ttk.Treeview(self, columns=("keyword", "type", "value"), show="headings")
        self.tree.heading("keyword", text="Keyword")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("value", text="Contenido")
        self.tree.column("keyword", width=180)
        self.tree.column("type", width=120)
        self.tree.column("value", width=420)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        footer = ttk.Frame(self, padding=10)
        footer.pack(fill=tk.X)
        ttk.Button(footer, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(footer, text="Continuar", command=self._submit).pack(side=tk.RIGHT, padx=8)

    def _add_signer(self) -> None:
        keyword = simpledialog.askstring("Keyword", "Palabra clave para detectar zona de firma:", parent=self)
        if not keyword:
            return

        sign_type = simpledialog.askstring(
            "Tipo de firma",
            "Tipo (image/text/draw):",
            parent=self,
            initialvalue="text",
        )
        if sign_type not in {"image", "text", "draw"}:
            messagebox.showwarning("Firmante", "Tipo inválido. Usa: image, text o draw.")
            return

        if sign_type == "image":
            image_path = filedialog.askopenfilename(
                title="Selecciona imagen de firma",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")],
            )
            if not image_path:
                return
            value: str = image_path
        elif sign_type == "text":
            text_value = simpledialog.askstring("Texto de firma", "Texto a insertar:", parent=self, initialvalue=keyword)
            if not text_value:
                return
            value = text_value
        else:
            drawer = DrawSignatureDialog(self)
            self.wait_window(drawer)
            if not drawer.result:
                return
            value = drawer.result

        rule = SignatureRule(keyword=keyword.strip(), signature_type=sign_type, value=value)
        self._rules.append(rule)
        value_preview = str(value)
        if len(value_preview) > 80:
            value_preview = f"{value_preview[:77]}..."
        self.tree.insert("", tk.END, values=(rule.keyword, rule.signature_type, value_preview))

    def _remove_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        self.tree.delete(selected[0])
        self._rules.pop(idx)

    def _submit(self) -> None:
        if not self._rules:
            messagebox.showwarning("Firmantes", "Agrega al menos una regla de firma.")
            return
        self.result = self._rules
        self.destroy()

    def export_rules_payload(self) -> list[dict[str, str]]:
        return [asdict(rule) for rule in self._rules]
