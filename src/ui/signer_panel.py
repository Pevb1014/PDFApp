from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict
from tkinter import filedialog, messagebox, ttk

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
        dialog = _SignerConfigDialog(self)
        self.wait_window(dialog)
        if dialog.result is None:
            return
        keyword, sign_type, value = dialog.result

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


class _SignerConfigDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Agregar firmante")
        self.geometry("460x250")
        self.result: tuple[str, str, str] | None = None

        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Keyword").grid(row=0, column=0, sticky="w", pady=4)
        self.keyword_entry = ttk.Entry(container)
        self.keyword_entry.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(container, text="Tipo de firma").grid(row=1, column=0, sticky="w", pady=4)
        self.type_combo = ttk.Combobox(container, values=["text", "image", "draw"], state="readonly")
        self.type_combo.set("text")
        self.type_combo.grid(row=1, column=1, sticky="ew", pady=4)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        ttk.Label(container, text="Contenido").grid(row=2, column=0, sticky="w", pady=4)
        self.value_entry = ttk.Entry(container)
        self.value_entry.grid(row=2, column=1, sticky="ew", pady=4)

        self.pick_button = ttk.Button(container, text="Seleccionar imagen", command=self._pick_image)
        self.draw_button = ttk.Button(container, text="Dibujar firma", command=self._draw_signature)
        self.draw_data: str | None = None

        container.columnconfigure(1, weight=1)
        footer = ttk.Frame(container)
        footer.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ttk.Button(footer, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(footer, text="Agregar", command=self._save).pack(side=tk.RIGHT, padx=8)
        self._on_type_change()

    def _on_type_change(self, _event=None) -> None:
        for widget in (self.pick_button, self.draw_button):
            widget.grid_forget()

        selected = self.type_combo.get()
        self.value_entry.configure(state=tk.NORMAL)
        self.value_entry.delete(0, tk.END)
        self.draw_data = None
        if selected == "image":
            self.value_entry.configure(state="readonly")
            self.pick_button.grid(row=3, column=1, sticky="w", pady=4)
        elif selected == "draw":
            self.value_entry.configure(state="readonly")
            self.draw_button.grid(row=3, column=1, sticky="w", pady=4)

    def _pick_image(self) -> None:
        image_path = filedialog.askopenfilename(
            title="Selecciona imagen de firma",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if not image_path:
            return
        self.value_entry.configure(state=tk.NORMAL)
        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, image_path)
        self.value_entry.configure(state="readonly")

    def _draw_signature(self) -> None:
        drawer = DrawSignatureDialog(self)
        self.wait_window(drawer)
        if not drawer.result:
            return
        self.draw_data = drawer.result
        self.value_entry.configure(state=tk.NORMAL)
        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, "[Firma dibujada capturada]")
        self.value_entry.configure(state="readonly")

    def _save(self) -> None:
        keyword = self.keyword_entry.get().strip()
        sign_type = self.type_combo.get()
        if not keyword:
            messagebox.showwarning("Firmante", "Debes indicar un keyword.")
            return

        if sign_type == "draw":
            value = self.draw_data
        else:
            value = self.value_entry.get().strip()

        if not value:
            messagebox.showwarning("Firmante", "Debes completar el contenido de firma.")
            return
        self.result = (keyword, sign_type, value)
        self.destroy()
