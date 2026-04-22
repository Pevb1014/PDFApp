from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.services.file_service import FileService
from src.services.pdf_service import PDFService
from src.services.viewer_service import ViewerService
from src.ui.components import create_button
from src.utils.helpers import ensure_pdf_extension, human_error


class MainWindow(ttk.Frame):
<<<<<<< HEAD
=======
    """
    Clase principal de la interfaz gráfica.
    Gestiona la interacción del usuario con los servicios de PDF, archivos y visor.
    """

>>>>>>> main
    def __init__(
        self,
        master: tk.Tk,
        file_service: FileService,
        pdf_service: PDFService,
        viewer_service: ViewerService,
    ) -> None:
<<<<<<< HEAD
        super().__init__(master, padding=12)
=======
        """
        Inicializa la ventana principal y configura los servicios.
        :param master: Ventana raíz de Tkinter.
        :param file_service: Servicio de archivos.
        :param pdf_service: Servicio de procesamiento PDF.
        :param viewer_service: Servicio de visualización.
        """
        super().__init__(master, padding=0)
>>>>>>> main
        self.master = master
        self.file_service = file_service
        self.pdf_service = pdf_service
        self.viewer_service = viewer_service
        self.loaded_files: list[Path] = []
<<<<<<< HEAD
        self.status_var = tk.StringVar(value="Listo")
        self.pdf_info_var = tk.StringVar(value="PDF seleccionado: ninguno")

        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(self)
        btn_row.pack(fill=tk.X, pady=(0, 10))

        create_button(btn_row, "Cargar PDFs", self._load_pdfs).pack(side=tk.LEFT, padx=(0, 6))
        create_button(btn_row, "Unir", self._merge_pdfs).pack(side=tk.LEFT, padx=6)
        create_button(btn_row, "Dividir", self._split_pdf).pack(side=tk.LEFT, padx=6)
        create_button(btn_row, "Extraer contenido", self._extract_content).pack(side=tk.LEFT, padx=6)
        create_button(btn_row, "Visualizar", self._preview_pdf).pack(side=tk.LEFT, padx=6)

        ttk.Label(self, text="PDFs cargados (el orden de esta lista se usa para unir):").pack(anchor=tk.W)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.X, pady=(4, 10))

        self.files_list = tk.Listbox(list_frame, height=8)
        self.files_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.files_list.bind("<<ListboxSelect>>", self._on_file_selection)

        order_controls = ttk.Frame(list_frame)
        order_controls.pack(side=tk.LEFT, padx=(8, 0), anchor=tk.N)
        create_button(order_controls, "Subir ↑", self._move_selected_up).pack(fill=tk.X, pady=(0, 6))
        create_button(order_controls, "Bajar ↓", self._move_selected_down).pack(fill=tk.X)

        ttk.Label(self, textvariable=self.pdf_info_var).pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(self, text="Salida / Texto extraído:").pack(anchor=tk.W)
        self.output_text = scrolledtext.ScrolledText(self, height=12, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _refresh_file_list(self) -> None:
        self.files_list.delete(0, tk.END)
        for index, file_path in enumerate(self.loaded_files, start=1):
            self.files_list.insert(tk.END, f"{index:02d}. {file_path}")

    def _selected_pdf_index(self) -> int | None:
=======
        self.status_var = tk.StringVar(value="Listo para procesar PDFs")
        self.pdf_info_var = tk.StringVar(value="Selecciona un PDF de la lista")

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        """Configura los estilos de TTK para un aspecto moderno."""
        style = ttk.Style()
        style.theme_use("clam")  # Un tema base más moderno y personalizable que el default de Windows

        # Colores
        bg_main = "#f0f2f5"
        bg_sidebar = "#ffffff"
        primary_color = "#1a73e8"
        accent_color = "#34a853"
        text_color = "#202124"

        self.master.configure(bg=bg_main)

        # Estilo de botones
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("Primary.TButton", foreground="white", background=primary_color)
        style.map("Primary.TButton", background=[("active", "#1557b0")])
        
        style.configure("Accent.TButton", foreground="white", background=accent_color)
        style.map("Accent.TButton", background=[("active", "#2d8e47")])

        # Etiquetas
        style.configure("TLabel", background=bg_main, foreground=text_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=primary_color)
        style.configure("Sidebar.TFrame", background=bg_sidebar)
        style.configure("Sidebar.TLabel", background=bg_sidebar, font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        """Construye la disposición de los elementos en la ventana."""
        self.pack(fill=tk.BOTH, expand=True)

        # 1. Cabecera
        header = ttk.Frame(self, padding=(20, 10))
        header.pack(fill=tk.X)
        ttk.Label(header, text="📄 PDF Master Pro", style="Header.TLabel").pack(side=tk.LEFT)
        
        # 2. Área principal con PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 2a. Sidebar (Gestión de archivos)
        sidebar = ttk.Frame(paned, padding=10, style="Sidebar.TFrame")
        paned.add(sidebar, weight=1)

        ttk.Label(sidebar, text="📂 Archivos Cargados", style="Sidebar.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        list_container = ttk.Frame(sidebar, style="Sidebar.TFrame")
        list_container.pack(fill=tk.BOTH, expand=True)

        self.files_list = tk.Listbox(
            list_container, 
            height=15, 
            font=("Segoe UI", 9), 
            borderwidth=1, 
            relief=tk.FLAT,
            selectbackground="#e8f0fe",
            selectforeground="#1a73e8"
        )
        self.files_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.files_list.bind("<<ListboxSelect>>", self._on_file_selection)

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.files_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_list.config(yscrollcommand=scrollbar.set)

        # Controles de gestión de archivos (Subir, Bajar, Quitar, Limpiar)
        file_mgmt_frame = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(0, 5))
        file_mgmt_frame.pack(fill=tk.X)
        file_mgmt_frame.columnconfigure((0, 1), weight=1)

        create_button(file_mgmt_frame, "🔼 Subir", self._move_selected_up).grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=2)
        create_button(file_mgmt_frame, "🔽 Bajar", self._move_selected_down).grid(row=0, column=1, sticky="ew", padx=(2, 0), pady=2)
        create_button(file_mgmt_frame, "❌ Quitar", self._remove_selected_file).grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=2)
        create_button(file_mgmt_frame, "🧹 Limpiar", self._clear_file_list).grid(row=1, column=1, sticky="ew", padx=(2, 0), pady=2)

        # 2b. Área de contenido (Acciones y Consola)
        content_area = ttk.Frame(paned, padding=(15, 0))
        paned.add(content_area, weight=3)

        # Acciones Principales (Organizadas por grupos)
        actions_frame = ttk.LabelFrame(content_area, text="🛠️ Herramientas", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))

        # Fila 1: Gestión y Operaciones PDF
        row1 = ttk.Frame(actions_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        row1.columnconfigure((0, 1, 2, 3), weight=1)
        
        create_button(row1, "📥 Cargar Archivos", self._load_files, style="Primary.TButton").grid(row=0, column=0, sticky="ew", padx=5)
        create_button(row1, "👁️ Visualizar", self._preview_pdf).grid(row=0, column=1, sticky="ew", padx=5)
        create_button(row1, "🔗 Unir", self._merge_pdfs, style="Accent.TButton").grid(row=0, column=2, sticky="ew", padx=5)
        create_button(row1, "✂️ Dividir", self._split_pdf).grid(row=0, column=3, sticky="ew", padx=5)

        # Fila 2: Conversiones
        row2 = ttk.Frame(actions_frame)
        row2.pack(fill=tk.X, pady=(5, 0))
        row2.columnconfigure((0, 1), weight=1)
        
        create_button(row2, "📝 PDF a Word / Extraer", self._extract_content).grid(row=0, column=0, sticky="ew", padx=5)
        create_button(row2, "📘 Word a PDF", self._word_to_pdf).grid(row=0, column=1, sticky="ew", padx=5)

        # Información del PDF seleccionado
        info_frame = ttk.Frame(content_area, padding=(0, 5))
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, textvariable=self.pdf_info_var, font=("Segoe UI", 9, "italic")).pack(side=tk.LEFT)

        # Salida de texto
        output_frame = ttk.LabelFrame(content_area, text="📜 Resultado / Texto Extraído", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            height=10, 
            font=("Consolas", 10), 
            borderwidth=1, 
            relief=tk.FLAT,
            bg="#ffffff"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 3. Barra de estado
        status_bar = ttk.Frame(self, relief=tk.SUNKEN, padding=(10, 2))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_bar, textvariable=self.status_var, font=("Segoe UI", 8)).pack(side=tk.LEFT)

    def _set_status(self, message: str) -> None:
        """Actualiza el mensaje de la barra de estado."""
        self.status_var.set(f"● {message}")

    def _refresh_file_list(self) -> None:
        """Actualiza la lista visual de archivos cargados."""
        self.files_list.delete(0, tk.END)
        for index, file_path in enumerate(self.loaded_files, start=1):
            self.files_list.insert(tk.END, f" {index:02d}. {file_path.name}")

    def _selected_pdf_index(self) -> int | None:
        """Obtiene el índice del PDF seleccionado en la lista."""
>>>>>>> main
        selected = self.files_list.curselection()
        if not selected:
            return None
        return selected[0]

    def _on_file_selection(self, _event=None) -> None:
<<<<<<< HEAD
        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            self.pdf_info_var.set("PDF seleccionado: ninguno")
            return

        input_pdf = self.loaded_files[selected_idx]
        try:
            total_pages = self.pdf_service.get_total_pages(input_pdf)
            self.pdf_info_var.set(f"PDF seleccionado: {input_pdf.name} | Total de páginas: {total_pages}")
        except Exception as exc:
            self.pdf_info_var.set(f"No se pudo leer info: {human_error(exc)}")

    def _move_selected_up(self) -> None:
=======
        """Evento al seleccionar un archivo de la lista."""
        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            self.pdf_info_var.set("Selecciona un PDF de la lista")
            return

        input_file = self.loaded_files[selected_idx]
        if input_file.suffix.lower() == ".docx":
            self.pdf_info_var.set(f"📌 Word: {input_file.name}")
            return

        try:
            total_pages = self.pdf_service.get_total_pages(input_file)
            self.pdf_info_var.set(f"📌 PDF: {input_file.name} | 📖 Páginas: {total_pages}")
        except Exception:
            # Manejar PdfStreamError u otros errores de lectura de metadatos de forma silenciosa
            self.pdf_info_var.set(f"📌 PDF: {input_file.name} | 📖 (Info no disponible)")

    def _move_selected_up(self) -> None:
        """Sube un nivel el archivo seleccionado en la lista."""
>>>>>>> main
        idx = self._selected_pdf_index()
        if idx is None:
            messagebox.showwarning("Orden", "Selecciona un PDF para mover.")
            return
        if idx == 0:
            return

        self.loaded_files[idx - 1], self.loaded_files[idx] = self.loaded_files[idx], self.loaded_files[idx - 1]
        self._refresh_file_list()
        self.files_list.selection_set(idx - 1)
        self._on_file_selection()
<<<<<<< HEAD
        self._set_status("Orden actualizado para unión de PDFs")

    def _move_selected_down(self) -> None:
        idx = self._selected_pdf_index()
        if idx is None:
            messagebox.showwarning("Orden", "Selecciona un PDF para mover.")
=======
        self._set_status("Orden de unión actualizado")

    def _move_selected_down(self) -> None:
        """Baja un nivel el archivo seleccionado en la lista."""
        idx = self._selected_pdf_index()
        if idx is None:
            messagebox.showwarning("Orden", "Selecciona un archivo para mover.")
>>>>>>> main
            return
        if idx == len(self.loaded_files) - 1:
            return

        self.loaded_files[idx + 1], self.loaded_files[idx] = self.loaded_files[idx], self.loaded_files[idx + 1]
        self._refresh_file_list()
        self.files_list.selection_set(idx + 1)
        self._on_file_selection()
<<<<<<< HEAD
        self._set_status("Orden actualizado para unión de PDFs")

    def _load_pdfs(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Selecciona uno o más PDFs",
            filetypes=[("PDF files", "*.pdf")],
=======
        self._set_status("Orden actualizado")

    def _remove_selected_file(self) -> None:
        """Elimina el archivo seleccionado de la lista."""
        idx = self._selected_pdf_index()
        if idx is None:
            messagebox.showwarning("Quitar", "Selecciona un archivo para quitar.")
            return
        
        removed_name = self.loaded_files[idx].name
        del self.loaded_files[idx]
        self._refresh_file_list()
        
        if self.loaded_files:
            new_idx = min(idx, len(self.loaded_files) - 1)
            self.files_list.selection_set(new_idx)
        
        self._on_file_selection()
        self._set_status(f"Archivo '{removed_name}' quitado")

    def _clear_file_list(self) -> None:
        """Limpia todos los archivos de la lista."""
        if not self.loaded_files:
            return
            
        if messagebox.askyesno("Limpiar", "¿Estás seguro de que quieres quitar todos los archivos?"):
            self.loaded_files = []
            self._refresh_file_list()
            self._on_file_selection()
            self._set_status("Lista de archivos vaciada")

    def _load_files(self) -> None:
        """Abre el diálogo para cargar uno o más archivos PDF o Word."""
        selected = filedialog.askopenfilenames(
            title="Selecciona archivos PDF o Word",
            filetypes=[("Archivos permitidos", "*.pdf *.docx"), ("PDF files", "*.pdf"), ("Word files", "*.docx")],
>>>>>>> main
        )
        if not selected:
            return

        try:
<<<<<<< HEAD
            files = self.file_service.validate_pdf_inputs(list(selected))
            self.loaded_files = files
            self._refresh_file_list()
            if self.loaded_files:
                self.files_list.selection_set(0)
                self._on_file_selection()
            self._set_status(
                f"{len(files)} archivo(s) cargado(s). Ajusta el orden con Subir/Bajar antes de unir."
            )
        except Exception as exc:
            messagebox.showerror("Error al cargar archivos", human_error(exc))
            self._set_status("Error al cargar PDFs")

    def _merge_pdfs(self) -> None:
        if len(self.loaded_files) < 2:
            messagebox.showwarning("Unir PDFs", "Carga al menos 2 archivos PDF.")
            return
=======
            files = self.file_service.validate_mixed_inputs(list(selected))
            # Añadimos a los archivos ya cargados en lugar de reemplazarlos
            self.loaded_files.extend(files)
            self._refresh_file_list()
            if self.loaded_files:
                self.files_list.selection_set(len(self.loaded_files) - len(files))
                self._on_file_selection()
            self._set_status(f"{len(files)} archivo(s) añadido(s) correctamente")
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))
            self._set_status("Error al cargar archivos")

    def _merge_pdfs(self) -> None:
        """Une los PDFs de la lista (ignora archivos Word)."""
        pdf_files = [f for f in self.loaded_files if f.suffix.lower() == ".pdf"]
        if len(pdf_files) < 2:
            messagebox.showwarning("Unir", "Carga al menos 2 archivos PDF para unir.")
            return
        
>>>>>>> main
        target = filedialog.asksaveasfilename(
            title="Guardar PDF unido",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not target:
            return

        try:
            output = self.file_service.prepare_output_path(str(ensure_pdf_extension(target)))
<<<<<<< HEAD
            self.pdf_service.merge_pdfs(self.loaded_files, output)
            self._set_status(f"PDF unido guardado en: {output}")
            messagebox.showinfo("Éxito", f"PDF unido guardado en:\n{output}")
        except Exception as exc:
            messagebox.showerror("Error al unir PDFs", human_error(exc))
            self._set_status("Error al unir PDFs")

    def _split_pdf(self) -> None:
        if not self.loaded_files:
            messagebox.showwarning("Dividir PDF", "Carga al menos 1 PDF.")
            return

        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            messagebox.showwarning("Dividir PDF", "Selecciona un PDF de la lista.")
            return

        input_pdf = self.loaded_files[selected_idx]
        split_options = self._ask_split_options(input_pdf)
        if split_options is None:
            return

        output_dir = filedialog.askdirectory(title="Carpeta de salida para división")
=======
            self.pdf_service.merge_pdfs(pdf_files, output)
            self._set_status(f"PDF unido guardado exitosamente")
            messagebox.showinfo("Éxito", f"PDF unido generado en:\n{output.name}")
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))
            self._set_status("Error al unir documentos")

    def _split_pdf(self) -> None:
        """Abre las opciones de división (ignora archivos Word)."""
        if not self.loaded_files:
            messagebox.showwarning("Dividir", "No hay archivos cargados.")
            return

        selected_idx = self._selected_pdf_index()
        
        # Filtrar solo los PDFs para el contexto y proceso
        pdf_files = [f for f in self.loaded_files if f.suffix.lower() == ".pdf"]
        
        if not pdf_files:
            messagebox.showwarning("Dividir", "No hay archivos PDF cargados para esta acción.")
            return

        # Contexto para el diálogo
        if selected_idx is not None:
            input_pdf_context = self.loaded_files[selected_idx]
            if input_pdf_context.suffix.lower() != ".pdf":
                input_pdf_context = pdf_files[0]
        else:
            input_pdf_context = pdf_files[0]

        split_options = self._ask_split_options(input_pdf_context)
        if split_options is None:
            return

        all_files = split_options.get("all_files", False)
        if not all_files and (selected_idx is None or self.loaded_files[selected_idx].suffix.lower() != ".pdf"):
            messagebox.showwarning("Dividir", "Selecciona un archivo PDF de la lista o marca 'Aplicar a todos'.")
            return

        output_dir = filedialog.askdirectory(title="Carpeta de salida")
>>>>>>> main
        if not output_dir:
            return

        try:
            mode = split_options["mode"]
<<<<<<< HEAD
            if mode == "range":
                created = self.pdf_service.split_pdf(
                    input_path=input_pdf,
                    output_dir=Path(output_dir),
                    start_page=split_options["start_page"],
                    end_page=split_options["end_page"],
                )
            elif mode == "parts":
                created = self.pdf_service.split_pdf_by_parts(
                    input_path=input_pdf,
                    output_dir=Path(output_dir),
                    num_parts=split_options["num_parts"],
                )
            else:
                created = self.pdf_service.extract_page_ranges(
                    input_path=input_pdf,
                    output_dir=Path(output_dir),
                    ranges_input=str(split_options["ranges_input"]),
                )

            self._set_status(f"Se generaron {len(created)} archivo(s) en {output_dir}")
            messagebox.showinfo("Éxito", f"Se generaron {len(created)} archivo(s).")
        except Exception as exc:
            messagebox.showerror("Error al dividir PDF", human_error(exc))
            self._set_status("Error al dividir PDF")

    def _extract_content(self) -> None:
        if not self.loaded_files:
            messagebox.showwarning("Extraer contenido", "Carga al menos 1 PDF.")
            return

        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            messagebox.showwarning("Extraer contenido", "Selecciona un PDF de la lista.")
            return

        input_pdf = self.loaded_files[selected_idx]
        mode = self._ask_content_mode()
        if not mode:
            return

        try:
            if mode == "text":
                text = self.pdf_service.extract_text(input_pdf)
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END, text or "[No se encontró texto extraíble]")
                self._set_status(f"Texto extraído de: {input_pdf.name}")

                output_file = filedialog.asksaveasfilename(
                    title="Guardar texto",
                    defaultextension=".txt",
                    initialfile=f"{input_pdf.stem}_texto.txt",
                    filetypes=[("Text files", "*.txt")],
                )
                if output_file:
                    Path(output_file).write_text(text, encoding="utf-8")
                    self._set_status(f"Texto guardado en: {output_file}")

            elif mode == "text_images":
                output_dir = filedialog.askdirectory(title="Carpeta de salida para texto e imágenes")
                if not output_dir:
                    return
                content_dir = Path(output_dir) / f"{input_pdf.stem}_contenido"
                result = self.pdf_service.extract_text_and_images(input_pdf, content_dir)

                text_content = Path(result["text_file"]).read_text(encoding="utf-8")
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END, text_content or "[No se encontró texto extraíble]")
                self._set_status(
                    f"Contenido extraído: texto + {result['image_count']} imagen(es) en {content_dir}"
                )
                messagebox.showinfo(
                    "Extracción completada",
                    f"Texto: {result['text_file']}\nImágenes: {result['images_dir']}\nTotal imágenes: {result['image_count']}",
                )

            elif mode in {"word_quick", "word_advanced"}:
                output_docx = filedialog.asksaveasfilename(
                    title="Guardar Word",
                    defaultextension=".docx",
                    initialfile=f"{input_pdf.stem}.docx",
                    filetypes=[("Word files", "*.docx")],
                )
                if not output_docx:
                    return
                conversion_mode = "advanced" if mode == "word_advanced" else "quick"
                if conversion_mode == "advanced" and not self.pdf_service.is_text_based_pdf(input_pdf):
                    messagebox.showinfo(
                        "PDF posiblemente escaneado",
                        "Este PDF parece no tener capa de texto. La conversión avanzada puede requerir OCR para mejores resultados.",
                    )
                output_path = self.pdf_service.convert_pdf_to_docx(
                    input_pdf, Path(output_docx), mode=conversion_mode
                )
                self._set_status(f"Documento Word generado en: {output_path}")
                messagebox.showinfo("Conversión completada", f"Archivo generado:\n{output_path}")

        except RuntimeError as exc:
            messagebox.showwarning("Dependencia faltante", str(exc))
            self._set_status("Falta dependencia para extracción de imágenes")
        except Exception as exc:
            messagebox.showerror("Error en extracción/conversión", human_error(exc))
            self._set_status("Error en extracción/conversión")

    def _ask_content_mode(self) -> str | None:
        dialog = tk.Toplevel(self)
        dialog.title("Extraer contenido / Convertir")
=======
            files_to_process = pdf_files if all_files else [self.loaded_files[selected_idx]]
            total_created = 0

            for input_pdf in files_to_process:
                if mode == "range":
                    created = self.pdf_service.split_pdf(
                        input_path=input_pdf,
                        output_dir=Path(output_dir),
                        start_page=split_options["start_page"],
                        end_page=split_options["end_page"],
                    )
                elif mode == "parts":
                    created = self.pdf_service.split_pdf_by_parts(
                        input_path=input_pdf,
                        output_dir=Path(output_dir),
                        num_parts=split_options["num_parts"],
                    )
                else:
                    created = self.pdf_service.extract_page_ranges(
                        input_path=input_pdf,
                        output_dir=Path(output_dir),
                        ranges_input=str(split_options["ranges_input"]),
                    )
                total_created += len(created)

            self._set_status(f"Se generaron {total_created} archivo(s)")
            messagebox.showinfo("Éxito", f"División completada: {total_created} archivos creados.")
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))
            self._set_status("Error en la división")

    def _extract_content(self) -> None:
        """Abre el diálogo de extracción de contenido o conversión a Word."""
        if not self.loaded_files:
            messagebox.showwarning("Extraer", "No hay archivos cargados.")
            return

        selected_idx = self._selected_pdf_index()
        options = self._ask_content_mode()
        if not options:
            return
        
        mode = options["mode"]
        all_files = options["all_files"]

        if not all_files and selected_idx is None:
            messagebox.showwarning("Extraer", "Selecciona un PDF o activa 'Aplicar a todos'.")
            return

        try:
            if all_files:
                self._process_batch_extraction(mode)
            else:
                self._process_single_extraction(self.loaded_files[selected_idx], mode)
        except RuntimeError as exc:
            messagebox.showwarning("Dependencia", str(exc))
            self._set_status("Falta Pillow para imágenes")
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))
            self._set_status("Error en el proceso")

    def _process_batch_extraction(self, mode: str) -> None:
        """Procesa todos los PDFs cargados (ignora archivos Word)."""
        pdf_files = [f for f in self.loaded_files if f.suffix.lower() == ".pdf"]
        if not pdf_files:
            messagebox.showwarning("Extraer", "No hay archivos PDF cargados.")
            return

        if mode == "text":
            blocks: list[str] = []
            for pdf in pdf_files:
                text = self.pdf_service.extract_text(pdf)
                blocks.append(f"📄 Documento: {pdf.name}\n{text or '[Sin texto]'}")
            combined = "\n\n" + "="*40 + "\n\n".join(blocks).strip()
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, combined)
            
            output_file = filedialog.asksaveasfilename(
                title="Guardar texto combinado",
                defaultextension=".txt",
                initialfile="textos_combinados.txt",
                filetypes=[("Text files", "*.txt")],
            )
            if output_file:
                Path(output_file).write_text(combined, encoding="utf-8")
                self._set_status(f"Texto guardado en {Path(output_file).name}")
        
        elif mode == "text_images":
            base_dir = filedialog.askdirectory(title="Carpeta de destino para batch")
            if not base_dir: return
            for pdf in pdf_files:
                self.pdf_service.extract_text_and_images(pdf, Path(base_dir) / f"{pdf.stem}_extract")
            messagebox.showinfo("Éxito", "Extracción masiva completada.")
            self._set_status("Batch de imágenes y texto finalizado")
            
        elif mode in {"word_quick", "word_advanced"}:
            output_dir = filedialog.askdirectory(title="Carpeta para archivos Word")
            if not output_dir: return
            conv_mode = "advanced" if mode == "word_advanced" else "quick"
            for pdf in pdf_files:
                self.pdf_service.convert_pdf_to_docx(pdf, Path(output_dir) / f"{pdf.stem}.docx", mode=conv_mode)
            messagebox.showinfo("Éxito", f"Se convirtieron {len(pdf_files)} archivos a Word.")
            self._set_status("Conversión masiva a Word completada")

    def _process_single_extraction(self, input_pdf: Path, mode: str) -> None:
        """Procesa un solo archivo según el modo elegido."""
        if mode == "text":
            text = self.pdf_service.extract_text(input_pdf)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, text or "[Sin texto extraíble]")
            self._set_status(f"Texto extraído de {input_pdf.name}")
            
            output_file = filedialog.asksaveasfilename(
                title="Guardar texto",
                defaultextension=".txt",
                initialfile=f"{input_pdf.stem}.txt",
                filetypes=[("Text files", "*.txt")],
            )
            if output_file:
                Path(output_file).write_text(text, encoding="utf-8")
        
        elif mode == "text_images":
            output_dir = filedialog.askdirectory(title="Carpeta de salida")
            if not output_dir: return
            res = self.pdf_service.extract_text_and_images(input_pdf, Path(output_dir) / f"{input_pdf.stem}_extract")
            messagebox.showinfo("Extracción", f"Finalizado. Imágenes: {res['image_count']}")
            self._set_status("Extracción completada")

        elif mode in {"word_quick", "word_advanced"}:
            output_dir = filedialog.askdirectory(title="Carpeta para Word")
            if not output_dir: return
            conv_mode = "advanced" if mode == "word_advanced" else "quick"
            out_path = self.pdf_service.convert_pdf_to_docx(input_pdf, Path(output_dir) / f"{input_pdf.stem}.docx", mode=conv_mode)
            messagebox.showinfo("Word", f"Archivo generado:\n{out_path.name}")
            self._set_status("Conversión a Word completada")

    def _word_to_pdf(self) -> None:
        """Convierte archivos Word (.docx) cargados a PDF."""
        if not self.loaded_files:
            messagebox.showwarning("Word a PDF", "No hay archivos cargados.")
            return

        selected_idx = self._selected_pdf_index()
        word_files = [f for f in self.loaded_files if f.suffix.lower() == ".docx"]
        
        if not word_files:
            messagebox.showwarning("Word a PDF", "No hay archivos Word (.docx) cargados.")
            return

        # Diálogo para elegir modo (seleccionado o todos)
        mode_options = self._ask_word_to_pdf_mode()
        if not mode_options:
            return
            
        all_files = mode_options.get("all_files", False)
        if not all_files and (selected_idx is None or self.loaded_files[selected_idx].suffix.lower() != ".docx"):
            messagebox.showwarning("Word a PDF", "Selecciona un archivo Word de la lista o marca 'Aplicar a todos'.")
            return

        output_dir = filedialog.askdirectory(title="Selecciona carpeta de salida para los PDFs")
        if not output_dir:
            return

        try:
            files_to_process = word_files if all_files else [self.loaded_files[selected_idx]]
            self._set_status(f"Convirtiendo {len(files_to_process)} archivo(s) Word a PDF...")
            self.master.update_idletasks()

            generated = []
            for docx_path in files_to_process:
                out_path = Path(output_dir) / f"{docx_path.stem}.pdf"
                res = self.pdf_service.convert_docx_to_pdf(docx_path, out_path)
                generated.append(res)
            
            self._set_status(f"Se convirtieron {len(generated)} archivos a PDF")
            messagebox.showinfo("Éxito", f"Se han generado {len(generated)} archivo(s) PDF en:\n{output_dir}")
            
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))
            self._set_status("Error en la conversión Word a PDF")

    def _ask_word_to_pdf_mode(self) -> dict[str, bool] | None:
        """Diálogo simple para elegir entre convertir uno o todos los archivos Word."""
        dialog = tk.Toplevel(self)
        dialog.title("📘 Configurar Word a PDF")
        dialog.grab_set()
        dialog.resizable(False, False)

        all_files_var = tk.BooleanVar(value=False)
        result: dict[str, bool] = {}

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack()

        ttk.Label(main_frame, text="Conversión de Word a PDF", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text="Esta acción solo procesará los archivos .docx cargados.", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Checkbutton(main_frame, text="Aplicar a todos los archivos Word cargados", variable=all_files_var).pack(anchor=tk.W, pady=10)

        btn_frame = ttk.Frame(main_frame, padding=(0, 15, 0, 0))
        btn_frame.pack(fill=tk.X)

        def confirm() -> None:
            result["all_files"] = all_files_var.get()
            dialog.destroy()

        create_button(btn_frame, "✅ Aceptar", confirm, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        create_button(btn_frame, "❌ Cancelar", dialog.destroy).pack(side=tk.RIGHT)

        dialog.wait_window()
        return result if result else None

    def _ask_content_mode(self) -> dict[str, str | bool] | None:
        """Muestra el diálogo para elegir el modo de extracción/conversión."""
        dialog = tk.Toplevel(self)
        dialog.title("Configurar Extracción")
>>>>>>> main
        dialog.grab_set()
        dialog.resizable(False, False)

        mode_var = tk.StringVar(value="text")
<<<<<<< HEAD
        result: dict[str, str] = {}

        ttk.Label(dialog, text="Elige una acción:").grid(row=0, column=0, padx=10, pady=(10, 6), sticky=tk.W)
        ttk.Radiobutton(dialog, text="Extraer solo texto (.txt)", variable=mode_var, value="text").grid(
            row=1, column=0, padx=10, sticky=tk.W
        )
        ttk.Radiobutton(dialog, text="Extraer texto + imágenes", variable=mode_var, value="text_images").grid(
            row=2, column=0, padx=10, sticky=tk.W
        )
        ttk.Radiobutton(dialog, text="Conversión rápida", variable=mode_var, value="word_quick").grid(
            row=3, column=0, padx=10, sticky=tk.W
        )
        ttk.Radiobutton(dialog, text="Conversión avanzada (recomendada)", variable=mode_var, value="word_advanced").grid(
            row=4, column=0, padx=10, sticky=tk.W
        )

        def confirm() -> None:
            result["mode"] = mode_var.get()
            dialog.destroy()

        ttk.Button(dialog, text="Aceptar", command=confirm).grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).grid(row=5, column=0, padx=10, pady=10, sticky=tk.E)

        dialog.wait_window()
        return result.get("mode")

    def _preview_pdf(self) -> None:
        if not self.loaded_files:
            messagebox.showwarning("Visualizar PDF", "Carga al menos 1 PDF.")
            return

        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            messagebox.showwarning("Visualizar PDF", "Selecciona un PDF de la lista.")
=======
        all_files_var = tk.BooleanVar(value=False)
        result: dict[str, str | bool] = {}

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack()

        ttk.Label(main_frame, text="¿Qué deseas hacer?", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        options = [
            ("Solo Texto (.txt)", "text"),
            ("Texto + Imágenes", "text_images"),
            ("Word (Rápido)", "word_quick"),
            ("Word (Avanzado - Recomendado)", "word_advanced")
        ]

        for text, value in options:
            ttk.Radiobutton(main_frame, text=text, variable=mode_var, value=value).pack(anchor=tk.W, pady=2)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Checkbutton(main_frame, text="Aplicar a todos los archivos cargados", variable=all_files_var).pack(anchor=tk.W)

        btn_frame = ttk.Frame(main_frame, padding=(0, 15, 0, 0))
        btn_frame.pack(fill=tk.X)

        def confirm() -> None:
            result["mode"] = mode_var.get()
            result["all_files"] = all_files_var.get()
            dialog.destroy()

        create_button(btn_frame, "✅ Aceptar", confirm, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        create_button(btn_frame, "❌ Cancelar", dialog.destroy).pack(side=tk.RIGHT)

        dialog.wait_window()
        return result if result else None

    def _preview_pdf(self) -> None:
        """Abre el PDF seleccionado en el visor del sistema."""
        selected_idx = self._selected_pdf_index()
        if selected_idx is None:
            messagebox.showwarning("Visualizar", "Selecciona un PDF de la lista.")
>>>>>>> main
            return

        input_pdf = self.loaded_files[selected_idx]
        try:
            self.viewer_service.open_pdf(input_pdf)
<<<<<<< HEAD
            self._set_status(f"Abriendo visor para: {input_pdf.name}")
        except Exception as exc:
            messagebox.showerror("Error al visualizar PDF", human_error(exc))
            self._set_status("Error al visualizar PDF")

    def _ask_split_options(self, input_pdf: Path) -> dict[str, int | str | None] | None:
        total_pages = self.pdf_service.get_total_pages(input_pdf)

        dialog = tk.Toplevel(self)
        dialog.title("Opciones de división")
=======
            self._set_status(f"Visualizando {input_pdf.name}")
        except Exception as exc:
            messagebox.showerror("Error", human_error(exc))

    def _ask_split_options(self, input_pdf: Path) -> dict[str, int | str | None] | None:
        """Muestra el diálogo para configurar la división de un PDF con campos dinámicos."""
        total_pages = self.pdf_service.get_total_pages(input_pdf)
        dialog = tk.Toplevel(self)
        dialog.title("✂️ Configurar División")
>>>>>>> main
        dialog.grab_set()
        dialog.resizable(False, False)

        mode_var = tk.StringVar(value="range")
<<<<<<< HEAD
        result: dict[str, int | str | None] = {}

        ttk.Label(
            dialog,
            text=f"PDF: {input_pdf.name} | Total de páginas: {total_pages}",
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 8), sticky=tk.W)

        ttk.Radiobutton(dialog, text="Dividir por rango", variable=mode_var, value="range", command=lambda: update_mode_fields(mode_var.get())).grid(
            row=1, column=0, columnspan=2, padx=10, sticky=tk.W
        )
        ttk.Label(dialog, text="Inicio (vacío = 1):").grid(row=2, column=0, padx=10, pady=4, sticky=tk.W)
        start_entry = ttk.Entry(dialog)
        start_entry.grid(row=2, column=1, padx=10, pady=4)

        ttk.Label(dialog, text="Fin (vacío = última):").grid(row=3, column=0, padx=10, pady=4, sticky=tk.W)
        end_entry = ttk.Entry(dialog)
        end_entry.grid(row=3, column=1, padx=10, pady=4)

        ttk.Separator(dialog, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        ttk.Radiobutton(dialog, text="Dividir por número de partes", variable=mode_var, value="parts", command=lambda: update_mode_fields(mode_var.get())).grid(
            row=5, column=0, columnspan=2, padx=10, sticky=tk.W
        )
        ttk.Label(dialog, text=f"Partes (1 a {total_pages}):").grid(
            row=6, column=0, padx=10, pady=4, sticky=tk.W
        )
        parts_entry = ttk.Entry(dialog)
        parts_entry.grid(row=6, column=1, padx=10, pady=4)

        ttk.Separator(dialog, orient=tk.HORIZONTAL).grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        ttk.Radiobutton(dialog, text="Extraer rangos", variable=mode_var, value="extract_ranges", command=lambda: update_mode_fields(mode_var.get())).grid(
            row=8, column=0, columnspan=2, padx=10, sticky=tk.W
        )
        ttk.Label(dialog, text="Rangos (ej: 2-14, 16-18, 20-29):").grid(
            row=9, column=0, padx=10, pady=4, sticky=tk.W
        )
        ranges_entry = ttk.Entry(dialog)
        ranges_entry.grid(row=9, column=1, padx=10, pady=4)

        def set_entry_state(entry: ttk.Entry, enabled: bool) -> None:
            state = "normal" if enabled else "disabled"
            entry.configure(state=state)

        def clear_entry(entry: ttk.Entry) -> None:
            entry.configure(state="normal")
            entry.delete(0, tk.END)

        def update_mode_fields(mode: str) -> None:
            is_range = mode == "range"
            is_parts = mode == "parts"
            is_extract = mode == "extract_ranges"

            set_entry_state(start_entry, is_range)
            set_entry_state(end_entry, is_range)
            set_entry_state(parts_entry, is_parts)
            set_entry_state(ranges_entry, is_extract)

            if not is_range:
                clear_entry(start_entry)
                clear_entry(end_entry)
                set_entry_state(start_entry, False)
                set_entry_state(end_entry, False)
            if not is_parts:
                clear_entry(parts_entry)
                set_entry_state(parts_entry, False)
            if not is_extract:
                clear_entry(ranges_entry)
                set_entry_state(ranges_entry, False)

        update_mode_fields(mode_var.get())

        def confirm() -> None:
            try:
                if mode_var.get() == "range":
                    start_raw = start_entry.get().strip()
                    end_raw = end_entry.get().strip()
                    start = int(start_raw) if start_raw else None
                    end = int(end_raw) if end_raw else None
                    result.update({"mode": "range", "start_page": start, "end_page": end})
                elif mode_var.get() == "parts":
                    parts_raw = parts_entry.get().strip()
                    if not parts_raw:
                        raise ValueError("Debes indicar el número de partes.")
                    num_parts = int(parts_raw)
                    if num_parts < 1 or num_parts > total_pages:
                        raise ValueError(f"El número de partes debe estar entre 1 y {total_pages}.")
                    result.update({"mode": "parts", "num_parts": num_parts})
                else:
                    ranges_input = ranges_entry.get().strip()
                    if not ranges_input:
                        raise ValueError("Debes ingresar al menos un rango para extraer.")
                    result.update({"mode": "extract_ranges", "ranges_input": ranges_input})

                dialog.destroy()
            except ValueError as exc:
                messagebox.showwarning("Datos inválidos", str(exc))

        ttk.Button(dialog, text="Aceptar", command=confirm).grid(row=10, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).grid(row=10, column=1, padx=10, pady=10)
=======
        all_files_var = tk.BooleanVar(value=False)
        result: dict[str, int | str | bool | None] = {}

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack()

        ttk.Label(main_frame, text=f"Documento: {input_pdf.name}", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Función para habilitar/deshabilitar campos según el modo
        def update_entries():
            mode = mode_var.get()
            # Modo Rango
            start_ent.configure(state="normal" if mode == "range" else "disabled")
            end_ent.configure(state="normal" if mode == "range" else "disabled")
            # Modo Partes
            parts_ent.configure(state="normal" if mode == "parts" else "disabled")
            # Modo Rangos Múltiples
            multi_ent.configure(state="normal" if mode == "extract_ranges" else "disabled")

        # Modo Rango
        range_frame = ttk.LabelFrame(main_frame, text="1. Por Rango Único", padding=10)
        range_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(range_frame, text="Activar", variable=mode_var, value="range", command=update_entries).pack(anchor=tk.W)
        ttk.Label(range_frame, text="Genera un archivo por cada una de las páginas entre el Inicio y el Fin.", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W)
        
        f1 = ttk.Frame(range_frame)
        f1.pack(fill=tk.X, pady=5)
        ttk.Label(f1, text="Inicio (vacío = 1):").pack(side=tk.LEFT)
        start_ent = ttk.Entry(f1, width=5)
        start_ent.pack(side=tk.LEFT, padx=5)
        ttk.Label(f1, text="Fin (vacío = última):").pack(side=tk.LEFT)
        end_ent = ttk.Entry(f1, width=5)
        end_ent.pack(side=tk.LEFT, padx=5)

        # Modo Partes
        parts_frame = ttk.LabelFrame(main_frame, text="2. Dividir en N Partes", padding=10)
        parts_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(parts_frame, text="Activar", variable=mode_var, value="parts", command=update_entries).pack(anchor=tk.W)
        ttk.Label(parts_frame, text="Divide el PDF en varios archivos de tamaño similar.", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W)
        
        f2 = ttk.Frame(parts_frame)
        f2.pack(fill=tk.X, pady=5)
        ttk.Label(f2, text="Nº de archivos:").pack(side=tk.LEFT)
        parts_ent = ttk.Entry(f2, width=5)
        parts_ent.pack(side=tk.LEFT, padx=5)

        # Modo Rangos Múltiples
        multi_frame = ttk.LabelFrame(main_frame, text="3. Extraer Múltiples Rangos", padding=10)
        multi_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(multi_frame, text="Activar", variable=mode_var, value="extract_ranges", command=update_entries).pack(anchor=tk.W)
        ttk.Label(multi_frame, text="Crea un PDF por cada rango especificado.", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W)
        
        multi_ent = ttk.Entry(multi_frame)
        multi_ent.pack(fill=tk.X, pady=5)
        ttk.Label(multi_frame, text="Ejemplo: 1-3, 5, 10-12 (Obligatorio)", font=("Segoe UI", 8, "italic"), foreground="gray").pack(anchor=tk.W)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(main_frame, text="Aplicar a todos los archivos cargados", variable=all_files_var).pack(anchor=tk.W, pady=(0, 10))

        # Inicializar estados
        update_entries()

        def confirm() -> None:
            try:
                mode = mode_var.get()
                result["all_files"] = all_files_var.get()
                if mode == "range":
                    s_raw = start_ent.get().strip()
                    e_raw = end_ent.get().strip()
                    s = int(s_raw) if s_raw else 1
                    e = int(e_raw) if e_raw else total_pages
                    if s < 1 or e > total_pages or s > e:
                        raise ValueError("Rango inválido.")
                    result.update({"mode": "range", "start_page": s, "end_page": e})
                elif mode == "parts":
                    p_raw = parts_ent.get().strip()
                    if not p_raw: raise ValueError("Ingresa el número de partes.")
                    p = int(p_raw)
                    if p < 1 or p > total_pages: raise ValueError("Número de partes inválido.")
                    result.update({"mode": "parts", "num_parts": p})
                else:
                    m_raw = multi_ent.get().strip()
                    if not m_raw: raise ValueError("Ingresa al menos un rango.")
                    result.update({"mode": "extract_ranges", "ranges_input": m_raw})
                dialog.destroy()
            except ValueError as exc:
                messagebox.showwarning("Valor Inválido", str(exc) if str(exc) else "Revisa los campos.")

        btn_f = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        btn_f.pack(fill=tk.X)
        create_button(btn_f, "✅ Aceptar", confirm, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        create_button(btn_f, "❌ Cancelar", dialog.destroy).pack(side=tk.RIGHT)
>>>>>>> main

        dialog.wait_window()
        return result or None
