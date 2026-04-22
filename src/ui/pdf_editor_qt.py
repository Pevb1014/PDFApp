from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QBuffer, QByteArray, QPoint, Qt
from PyQt6.QtGui import QAction, QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
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
    def __init__(self, overlay: OverlayItem, zoom: float, on_move, on_edit) -> None:
        super().__init__(overlay.text)
        self.overlay = overlay
        self.zoom = zoom
        self.on_move = on_move
        self.on_edit = on_edit
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


class OverlayImageItem(QGraphicsPixmapItem):
    def __init__(self, overlay: OverlayItem, zoom: float, on_move) -> None:
        pix = QPixmap()
        pix.loadFromData(overlay.image_bytes or b"", "PNG")
        w = int((overlay.rect[2] - overlay.rect[0]) * zoom)
        h = int((overlay.rect[3] - overlay.rect[1]) * zoom)
        super().__init__(pix.scaled(w, h))
        self.overlay = overlay
        self.zoom = zoom
        self.on_move = on_move
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

    def wheelEvent(self, event):  # type: ignore[override]
        delta = event.delta() if hasattr(event, "delta") else event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        new_w = max(20.0, (self.overlay.rect[2] - self.overlay.rect[0]) * factor)
        new_h = max(20.0, (self.overlay.rect[3] - self.overlay.rect[1]) * factor)
        x, y = self.overlay.rect[0], self.overlay.rect[1]
        self.on_move(self.overlay.uid, (x, y, x + new_w, y + new_h))
        event.accept()


class PDFEditorWindow(QMainWindow):
    def __init__(self, pdf_path: Path) -> None:
        super().__init__()
        self.pdf_path = pdf_path
        self.service = PDFEditorService()
        self.page_index = 0
        self.zoom = 1.2
        self.mode = "text_add"
        self.current_color = QColor("black")
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
        bar.addWidget(self.font_box)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
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
        chosen = QColorDialog.getColor(self.current_color, self, "Color texto")
        if chosen.isValid():
            self.current_color = chosen

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
        )
        self.scene.addItem(item)

    def _draw_overlay_image(self, overlay: OverlayItem) -> None:
        item = OverlayImageItem(overlay=overlay, zoom=self.zoom, on_move=self.service.update_overlay_rect)
        self.scene.addItem(item)

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
                "1) Selecciona modo: Agregar texto, Insertar imagen o Firmar.\n"
                "2) Haz click en el PDF para crear el elemento.\n"
                "3) Arrastra texto/imagen/firma para ajustar posición.\n"
                "4) Doble click en un texto para editarlo; si queda vacío se elimina.\n"
                "5) Para imágenes, usa la rueda del mouse sobre la imagen para redimensionar.\n"
                "6) Usa Exportar PDF para guardar los cambios en un nuevo archivo."
            ),
        )
