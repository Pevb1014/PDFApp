from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QBuffer, QByteArray, QPoint, Qt
from PyQt6.QtGui import QAction, QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFontComboBox,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.core.editor_models import OverlayItem, OverlayStyle
from src.services.pdf_editor_service import PDFEditorService


class DrawSignatureDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Dibujar firma")
        self.setMinimumSize(420, 220)
        self.canvas = SignatureCanvas()
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        actions = QHBoxLayout()
        ok_btn = QPushButton("Usar firma")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        actions.addStretch()
        actions.addWidget(cancel_btn)
        actions.addWidget(ok_btn)
        layout.addStretch()
        layout.addLayout(actions)

    def signature_png(self) -> bytes:
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        self.canvas.image.save(buffer, "PNG")
        buffer.close()
        return bytes(ba)


class SignatureCanvas(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(400, 160)
        self.image = QImage(400, 160, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.white)
        self._last: QPoint | None = None

    def mousePressEvent(self, event):  # type: ignore[override]
        self._last = event.position().toPoint()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self._last is None:
            return
        current = event.position().toPoint()
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(self._last, current)
        painter.end()
        self._last = current
        self.update()

    def paintEvent(self, event):  # type: ignore[override]
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)


class OverlayTextItem(QGraphicsTextItem):
    def __init__(self, overlay: OverlayItem, zoom: float, on_move, on_edit, on_resize) -> None:
        super().__init__(overlay.text)
        self.overlay = overlay
        self.zoom = zoom
        self.on_move = on_move
        self.on_edit = on_edit
        self.on_resize = on_resize
        self.setTextWidth((overlay.rect[2] - overlay.rect[0]) * zoom)
        self.setPos(overlay.rect[0] * zoom, overlay.rect[1] * zoom)
        self.setDefaultTextColor(QColor.fromRgbF(*overlay.style.color_rgb))
        font = QFont(overlay.style.font_family, int(overlay.style.font_size))
        self.setFont(font)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        super().mouseReleaseEvent(event)
        x = self.pos().x() / self.zoom
        y = self.pos().y() / self.zoom
        w = (self.overlay.rect[2] - self.overlay.rect[0])
        h = (self.overlay.rect[3] - self.overlay.rect[1])
        self.on_move(self.overlay.uid, (x, y, x + w, y + h))

    def mouseDoubleClickEvent(self, event):  # type: ignore[override]
        super().mouseDoubleClickEvent(event)
        self.on_edit(self.overlay.uid, self.overlay.text)

    def resize_by_factor(self, factor: float) -> None:
        x1, y1, x2, y2 = self.overlay.rect
        new_w = max(60.0, (x2 - x1) * factor)
        new_h = max(24.0, (y2 - y1) * factor)
        self.setTextWidth(new_w * self.zoom)
        self.overlay.rect = (x1, y1, x1 + new_w, y1 + new_h)
        self.on_resize(self.overlay.uid, self.overlay.rect)

    def apply_style(self, style: OverlayStyle) -> None:
        self.overlay.style = style
        self.setDefaultTextColor(QColor.fromRgbF(*style.color_rgb))
        self.setFont(QFont(style.font_family, int(style.font_size)))


class OverlayImageItem(QGraphicsPixmapItem):
    def __init__(self, overlay: OverlayItem, zoom: float, on_move, on_replace, on_scale, on_resize, on_delete) -> None:
        pix = QPixmap()
        pix.loadFromData(overlay.image_bytes or b"", "PNG")
        w = int((overlay.rect[2] - overlay.rect[0]) * zoom)
        h = int((overlay.rect[3] - overlay.rect[1]) * zoom)
        super().__init__(pix.scaled(w, h))
        self.overlay = overlay
        self.zoom = zoom
        self.base_pixmap = pix
        self.on_move = on_move
        self.on_replace = on_replace
        self.on_scale = on_scale
        self.on_resize = on_resize
        self.on_delete = on_delete
        self.setPos(overlay.rect[0] * zoom, overlay.rect[1] * zoom)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsFocusable, True)

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        super().mouseReleaseEvent(event)
        x = self.pos().x() / self.zoom
        y = self.pos().y() / self.zoom
        w = (self.overlay.rect[2] - self.overlay.rect[0])
        h = (self.overlay.rect[3] - self.overlay.rect[1])
        self.on_move(self.overlay.uid, (x, y, x + w, y + h))

    def resize_by_factor(self, factor: float) -> None:
        x1, y1, x2, y2 = self.overlay.rect
        new_w = max(20.0, (x2 - x1) * factor)
        new_h = max(20.0, (y2 - y1) * factor)
        self.set_size(new_w, new_h)

    def set_size(self, width: float, height: float) -> None:
        x1, y1, _, _ = self.overlay.rect
        width = max(20.0, width)
        height = max(20.0, height)
        self.overlay.rect = (x1, y1, x1 + width, y1 + height)
        self.setPixmap(self.base_pixmap.scaled(int(width * self.zoom), int(height * self.zoom)))
        self.on_move(self.overlay.uid, self.overlay.rect)

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            replace_action = menu.addAction("Reemplazar imagen")
            scale_action = menu.addAction("Re-escalar (%)")
            resize_action = menu.addAction("Ajustar ancho/alto")
            delete_action = menu.addAction("Eliminar imagen/firma")
            chosen = menu.exec(event.screenPos())
            if chosen == replace_action:
                self.on_replace(self.overlay.uid)
            elif chosen == scale_action:
                self.on_scale(self.overlay.uid)
            elif chosen == resize_action:
                self.on_resize(self.overlay.uid)
            elif chosen == delete_action:
                self.on_delete(self.overlay.uid)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):  # type: ignore[override]
        super().mouseDoubleClickEvent(event)
        self.on_replace(self.overlay.uid)


class PDFEditorWindow(QMainWindow):
    def __init__(self, pdf_path: Path) -> None:
        super().__init__()
        self.pdf_path = pdf_path
        self.service = PDFEditorService()
        self.page_index = 0
        self.zoom = 1.2
        self.mode = "text_add"
        self.current_color = QColor("black")
        self._syncing_toolbar = False
        self.mode_map = {
            "Agregar texto nuevo": "text_add",
            "Insertar imagen": "image_add",
            "Firmar documento": "sign",
        }

        self.setWindowTitle(f"PDF Editor - {pdf_path.name}")
        self.resize(1300, 820)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.view.mousePressEvent = self._on_view_click  # type: ignore[assignment]
        self.view.wheelEvent = self._on_view_wheel  # type: ignore[assignment]
        self.scene.selectionChanged.connect(self._on_selection_changed)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.view)
        self.setCentralWidget(central)

        self._build_toolbar()
        self._render_page()

    def _build_toolbar(self) -> None:
        bar = QToolBar("Editor")
        self.addToolBar(bar)

        mode_box = QComboBox()
        mode_box.addItems(list(self.mode_map.keys()))
        mode_box.currentTextChanged.connect(self._set_mode_from_label)
        bar.addWidget(mode_box)

        self.font_box = QFontComboBox()
        self.font_box.currentFontChanged.connect(self._on_toolbar_font_changed)
        bar.addWidget(self.font_box)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self._on_toolbar_font_size_changed)
        bar.addWidget(self.font_size)

        color_btn = QPushButton("Color")
        color_btn.clicked.connect(self._pick_color)
        bar.addWidget(color_btn)

        prev_page = QAction("◀ Página", self)
        prev_page.triggered.connect(self._prev_page)
        bar.addAction(prev_page)

        next_page = QAction("Página ▶", self)
        next_page.triggered.connect(self._next_page)
        bar.addAction(next_page)

        zoom_in = QAction("Zoom +", self)
        zoom_in.triggered.connect(lambda: self._change_zoom(0.2))
        bar.addAction(zoom_in)

        zoom_out = QAction("Zoom -", self)
        zoom_out.triggered.connect(lambda: self._change_zoom(-0.2))
        bar.addAction(zoom_out)

        export = QAction("Exportar PDF", self)
        export.triggered.connect(self._export_pdf)
        bar.addAction(export)

        help_action = QAction("Instrucciones", self)
        help_action.triggered.connect(self._show_instructions)
        bar.addAction(help_action)

    def _set_mode_from_label(self, label: str) -> None:
        self.mode = self.mode_map.get(label, "text_add")

    def _set_mode(self, mode: str) -> None:
        self.mode = mode

    def _pick_color(self) -> None:
        selected = self._selected_text_item()
        if selected is None:
            chosen = QColorDialog.getColor(self.current_color, self, "Color texto")
            if chosen.isValid():
                self.current_color = chosen
            return

        original = QColor.fromRgbF(*selected.overlay.style.color_rgb)
        dlg = QColorDialog(original, self)
        dlg.setWindowTitle("Color texto")
        dlg.currentColorChanged.connect(lambda color: self._apply_selected_text_style(color=color))
        if dlg.exec():
            self.current_color = dlg.currentColor()
            self._apply_selected_text_style(color=self.current_color)
        else:
            self._apply_selected_text_style(color=original)

    def _change_zoom(self, delta: float) -> None:
        self.zoom = max(0.4, min(3.0, self.zoom + delta))
        self._render_page()

    def _prev_page(self) -> None:
        self.page_index = max(0, self.page_index - 1)
        self._render_page()

    def _next_page(self) -> None:
        total = self.service.page_count(self.pdf_path)
        self.page_index = min(total - 1, self.page_index + 1)
        self._render_page()

    def _style(self) -> OverlayStyle:
        c = self.current_color
        return OverlayStyle(
            font_family=self.font_box.currentFont().family(),
            font_size=float(self.font_size.value()),
            color_rgb=(c.redF(), c.greenF(), c.blueF()),
        )

    def _render_page(self) -> None:
        self.scene.clear()
        png = self.service.render_page(self.pdf_path, self.page_index, self.zoom)
        pix = QPixmap()
        pix.loadFromData(png, "PNG")
        self.page_item = QGraphicsPixmapItem(pix)
        self.scene.addItem(self.page_item)

        self._render_overlays()

    def _render_overlays(self) -> None:
        for overlay in self.service.list_overlays():
            if overlay.page_index != self.page_index:
                continue
            if overlay.kind in {"text_add", "text_edit", "signature_text"}:
                self._draw_overlay_text(overlay)
            elif overlay.kind in {"signature_image", "signature_draw", "image_add"} and overlay.image_bytes:
                self._draw_overlay_image(overlay)

    def _on_view_click(self, event):  # type: ignore[override]
        clicked_item = self.view.itemAt(event.pos())
        if isinstance(clicked_item, (OverlayTextItem, OverlayImageItem)):
            QGraphicsView.mousePressEvent(self.view, event)
            return

        pos = self.view.mapToScene(event.pos())
        x_pdf = pos.x() / self.zoom
        y_pdf = pos.y() / self.zoom

        if self.mode == "text_add":
            self._add_text_overlay(x_pdf, y_pdf)
        elif self.mode == "image_add":
            self._add_image_overlay(x_pdf, y_pdf)
        else:
            self._add_signature_overlay(x_pdf, y_pdf)

    def _on_view_wheel(self, event):  # type: ignore[override]
        hovered = self.view.itemAt(event.position().toPoint())
        if isinstance(hovered, OverlayImageItem):
            factor = 1.08 if event.angleDelta().y() > 0 else 0.92
            hovered.resize_by_factor(factor)
            event.accept()
            return
        if isinstance(hovered, OverlayTextItem):
            factor = 1.08 if event.angleDelta().y() > 0 else 0.92
            hovered.resize_by_factor(factor)
            event.accept()
            return
        QGraphicsView.wheelEvent(self.view, event)

    def _add_text_overlay(self, x: float, y: float) -> None:
        text, ok = QInputDialog.getMultiLineText(self, "Agregar texto", "Texto:")
        if not ok or not text.strip():
            return
        rect = (x, y, x + 280, y + 80)
        overlay = self.service.add_text_overlay(self.page_index, rect, text, self._style())
        self._draw_overlay_text(overlay)

    def _add_signature_overlay(self, x: float, y: float) -> None:
        sig_type, ok = QInputDialog.getItem(
            self,
            "Tipo de firma",
            "Selecciona:",
            ["Texto", "Imagen PNG", "Dibujo"],
            0,
            False,
        )
        if not ok:
            return

        rect = (x, y, x + 250, y + 70)
        if sig_type == "Texto":
            txt, ok2 = QInputDialog.getText(self, "Firma texto", "Texto firma:")
            if ok2 and txt.strip():
                self.service.add_signature_text_overlay(self.page_index, rect, txt, self._style())
                self._render_page()
        elif sig_type == "Imagen PNG":
            file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona firma", "", "PNG (*.png)")
            if file_path:
                image_bytes = Path(file_path).read_bytes()
                self.service.add_signature_image_overlay(self.page_index, rect, image_bytes, image_ext="png")
                self._render_page()
        else:
            dlg = DrawSignatureDialog(self)
            if dlg.exec():
                image_bytes = dlg.signature_png()
                self.service.add_signature_draw_overlay(self.page_index, rect, image_bytes)
                self._render_page()

    def _add_image_overlay(self, x: float, y: float) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona imagen para insertar",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_path:
            return
        image_bytes = Path(file_path).read_bytes()
        rect = (x, y, x + 250, y + 120)
        self.service.add_image_overlay(self.page_index, rect, image_bytes, image_ext=Path(file_path).suffix.lstrip("."))
        self._render_page()

    def _draw_overlay_text(self, overlay: OverlayItem) -> None:
        item = OverlayTextItem(
            overlay=overlay,
            zoom=self.zoom,
            on_move=self.service.update_overlay_rect,
            on_edit=self._edit_existing_overlay_text,
            on_resize=self.service.update_overlay_rect,
        )
        self.scene.addItem(item)

    def _draw_overlay_image(self, overlay: OverlayItem) -> None:
        item = OverlayImageItem(
            overlay=overlay,
            zoom=self.zoom,
            on_move=self.service.update_overlay_rect,
            on_replace=self._replace_existing_overlay_image,
            on_scale=self._scale_existing_overlay_image,
            on_resize=self._resize_existing_overlay_image,
            on_delete=self._delete_overlay,
        )
        self.scene.addItem(item)

    def _delete_overlay(self, overlay_uid: str) -> None:
        self.service.remove_overlay(overlay_uid)
        self._render_page()

    def _find_overlay(self, overlay_uid: str) -> OverlayItem | None:
        for overlay in self.service.list_overlays():
            if overlay.uid == overlay_uid:
                return overlay
        return None

    def _find_image_item(self, overlay_uid: str) -> OverlayImageItem | None:
        for item in self.scene.items():
            if isinstance(item, OverlayImageItem) and item.overlay.uid == overlay_uid:
                return item
        return None

    def _selected_text_item(self) -> OverlayTextItem | None:
        for item in self.scene.selectedItems():
            if isinstance(item, OverlayTextItem):
                return item
        return None

    def _on_selection_changed(self) -> None:
        selected = self._selected_text_item()
        if selected is None:
            return
        style = selected.overlay.style
        self._syncing_toolbar = True
        self.font_box.setCurrentFont(QFont(style.font_family))
        self.font_size.setValue(int(style.font_size))
        self.current_color = QColor.fromRgbF(*style.color_rgb)
        self._syncing_toolbar = False

    def _on_toolbar_font_changed(self, font) -> None:
        if self._syncing_toolbar:
            return
        self._apply_selected_text_style(font_family=font.family())

    def _on_toolbar_font_size_changed(self, size: int) -> None:
        if self._syncing_toolbar:
            return
        self._apply_selected_text_style(font_size=float(size))

    def _apply_selected_text_style(
        self,
        *,
        font_family: str | None = None,
        font_size: float | None = None,
        color: QColor | None = None,
    ) -> None:
        selected = self._selected_text_item()
        if selected is None:
            return
        style = selected.overlay.style
        updated = OverlayStyle(
            font_family=font_family or style.font_family,
            font_size=font_size or style.font_size,
            color_rgb=(
                color.redF() if color else style.color_rgb[0],
                color.greenF() if color else style.color_rgb[1],
                color.blueF() if color else style.color_rgb[2],
            ),
        )
        selected.apply_style(updated)
        self.service.update_overlay_text(selected.overlay.uid, selected.toPlainText(), style=updated)

    def _export_pdf(self) -> None:
        out_path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", str(self.pdf_path.with_name("editado.pdf")), "PDF (*.pdf)")
        if not out_path:
            return
        try:
            self.service.export(self.pdf_path, Path(out_path))
            QMessageBox.information(self, "Éxito", f"PDF exportado en:\n{out_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _edit_existing_overlay_text(self, overlay_uid: str, current_text: str) -> None:
        new_text, ok = QInputDialog.getMultiLineText(self, "Editar texto", "Contenido:", current_text)
        if not ok:
            return

        cleaned = new_text.strip()
        if cleaned == "":
            self.service.remove_overlay(overlay_uid)
            self._render_page()
            return

        # Reaplica estilo actual de toolbar para permitir cambiar fuente/tamaño/color
        self.service.update_overlay_text(overlay_uid, cleaned, style=self._style())
        self._render_page()

    def _show_instructions(self) -> None:
        QMessageBox.information(
            self,
            "Instrucciones de uso",
            (
                "🧭 Flujo general\n"
                "• Selecciona un modo: Agregar texto, Insertar imagen o Firmar.\n"
                "• Haz click sobre la página para insertar el elemento.\n"
                "• Arrastra texto/imagen/firma para ubicarlo con precisión.\n\n"
                "📝 Texto\n"
                "• Doble click en texto para editar contenido.\n"
                "• Si el contenido queda vacío, el texto se elimina.\n"
                "• Si seleccionas un texto, puedes ajustar fuente/tamaño/color desde la barra y ver cambios en tiempo real.\n\n"
                "🖼️ Imágenes y firmas\n"
                "• Click derecho en imagen/firma: reemplazar, re-escalar (%), ajustar ancho/alto o eliminar.\n"
                "• Doble click en imagen/firma para reemplazar rápidamente.\n"
                "• Usa la rueda del mouse sobre imagen o texto para redimensionar en tiempo real.\n\n"
                "⌨️ Atajos\n"
                "• Tecla Delete/Backspace: elimina overlays seleccionados (texto, imagen o firma).\n\n"
                "📄 Navegación y exportación\n"
                "• Navega páginas con ◀/▶.\n"
                "• Usa Zoom +/- para más precisión visual.\n"
                "• Al terminar, pulsa Exportar PDF para generar un archivo nuevo con overlays."
            ),
        )

    def keyPressEvent(self, event):  # type: ignore[override]
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            selected_items = self.scene.selectedItems()
            if selected_items:
                for item in selected_items:
                    if isinstance(item, (OverlayTextItem, OverlayImageItem)):
                        self.service.remove_overlay(item.overlay.uid)
                self._render_page()
                event.accept()
                return
        super().keyPressEvent(event)

    def _replace_existing_overlay_image(self, overlay_uid: str) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Reemplazar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_path:
            return
        self.service.update_overlay_image(
            overlay_uid=overlay_uid,
            image_bytes=Path(file_path).read_bytes(),
            image_ext=Path(file_path).suffix.lstrip("."),
        )
        self._render_page()

    def _scale_existing_overlay_image(self, overlay_uid: str) -> None:
        overlay = self._find_overlay(overlay_uid)
        if overlay is None:
            return
        image_item = self._find_image_item(overlay_uid)
        if image_item is None:
            return
        x1, y1, x2, y2 = overlay.rect
        original_w = x2 - x1
        original_h = y2 - y1

        dlg = QDialog(self)
        dlg.setWindowTitle("Re-escalar imagen")
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Escala (%)"))
        percent_spin = QDoubleSpinBox()
        percent_spin.setRange(10.0, 500.0)
        percent_spin.setDecimals(1)
        percent_spin.setValue(100.0)
        layout.addWidget(percent_spin)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        def _preview_scale(value: float) -> None:
            factor = value / 100.0
            image_item.set_size(original_w * factor, original_h * factor)

        percent_spin.valueChanged.connect(_preview_scale)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if not dlg.exec():
            image_item.set_size(original_w, original_h)
            return

    def _resize_existing_overlay_image(self, overlay_uid: str) -> None:
        overlay = self._find_overlay(overlay_uid)
        if overlay is None:
            return
        image_item = self._find_image_item(overlay_uid)
        if image_item is None:
            return
        x1, y1, x2, y2 = overlay.rect
        current_width = x2 - x1
        current_height = y2 - y1
        dlg = QDialog(self)
        dlg.setWindowTitle("Ajustar tamaño")
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Ancho (pt)"))
        width_spin = QDoubleSpinBox()
        width_spin.setRange(20.0, 2000.0)
        width_spin.setDecimals(1)
        width_spin.setValue(current_width)
        layout.addWidget(width_spin)
        layout.addWidget(QLabel("Alto (pt)"))
        height_spin = QDoubleSpinBox()
        height_spin.setRange(20.0, 2000.0)
        height_spin.setDecimals(1)
        height_spin.setValue(current_height)
        layout.addWidget(height_spin)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        def _preview_resize() -> None:
            image_item.set_size(width_spin.value(), height_spin.value())

        width_spin.valueChanged.connect(lambda _: _preview_resize())
        height_spin.valueChanged.connect(lambda _: _preview_resize())
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if not dlg.exec():
            image_item.set_size(current_width, current_height)
