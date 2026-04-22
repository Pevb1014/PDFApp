from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QBuffer, QByteArray, QPoint, QPointF, QRectF, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.core.editor_models import OverlayStyle
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


class InlineTextEdit(QTextEdit):
    """Editor inline que notifica al perder foco sin tocar objetos eliminados."""

    editing_finished = pyqtSignal()
    submit_requested = pyqtSignal()

    def focusOutEvent(self, event):  # type: ignore[override]
        super().focusOutEvent(event)
        # Evita reentrancia/destrucción durante el propio focusOut.
        QTimer.singleShot(0, self.editing_finished.emit)

    def keyPressEvent(self, event):  # type: ignore[override]
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.submit_requested.emit()
            return
        super().keyPressEvent(event)


class PDFEditorWindow(QMainWindow):
    def __init__(self, pdf_path: Path) -> None:
        super().__init__()
        self.pdf_path = pdf_path
        self.service = PDFEditorService()
        self.page_index = 0
        self.zoom = 1.2
        self.mode = "text_edit"
        self.current_color = QColor("black")
        self.mode_map = {
            "Editar texto existente": "text_edit",
            "Agregar texto nuevo": "text_add",
            "Firmar documento": "sign",
        }
        self._active_commit = None

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

    def _set_mode_from_label(self, label: str) -> None:
        self._commit_active_editor()
        self.mode = self.mode_map.get(label, "text_edit")

    def _set_mode(self, mode: str) -> None:
        self.mode = mode

    def _pick_color(self) -> None:
        chosen = QColorDialog.getColor(self.current_color, self, "Color texto")
        if chosen.isValid():
            self.current_color = chosen

    def _change_zoom(self, delta: float) -> None:
        self._commit_active_editor()
        self.zoom = max(0.4, min(3.0, self.zoom + delta))
        self._render_page()

    def _prev_page(self) -> None:
        self._commit_active_editor()
        self.page_index = max(0, self.page_index - 1)
        self._render_page()

    def _next_page(self) -> None:
        self._commit_active_editor()
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
        self._active_commit = None
        self.scene.clear()
        png = self.service.render_page(self.pdf_path, self.page_index, self.zoom)
        pix = QPixmap()
        pix.loadFromData(png, "PNG")
        self.page_item = QGraphicsPixmapItem(pix)
        self.scene.addItem(self.page_item)

        if self.mode == "text_edit":
            for x0, y0, x1, y1, _ in self.service.get_text_blocks(self.pdf_path, self.page_index):
                rect = QGraphicsRectItem(
                    QRectF(x0 * self.zoom, y0 * self.zoom, (x1 - x0) * self.zoom, (y1 - y0) * self.zoom)
                )
                rect.setPen(QPen(QColor(50, 130, 255, 120), 1))
                self.scene.addItem(rect)

        self._render_overlays()

    def _render_overlays(self) -> None:
        for overlay in self.service.list_overlays():
            if overlay.page_index != self.page_index:
                continue
            if overlay.kind in {"text_add", "text_edit", "signature_text"}:
                self._draw_overlay_text(overlay.rect, overlay.text, color=QColor.fromRgbF(*overlay.style.color_rgb))
            elif overlay.kind in {"signature_image", "signature_draw"} and overlay.image_bytes:
                self._draw_overlay_image(overlay.rect, overlay.image_bytes)

    def _commit_active_editor(self) -> None:
        if callable(self._active_commit):
            self._active_commit()
            self._active_commit = None

    def _on_view_click(self, event):  # type: ignore[override]
        self._commit_active_editor()
        pos = self.view.mapToScene(event.pos())
        x_pdf = pos.x() / self.zoom
        y_pdf = pos.y() / self.zoom

        if self.mode == "text_add":
            self._add_text_overlay(x_pdf, y_pdf)
        elif self.mode == "text_edit":
            self._edit_text_block(x_pdf, y_pdf)
        else:
            self._add_signature_overlay(x_pdf, y_pdf)

    def _add_text_overlay(self, x: float, y: float) -> None:
        text, ok = QInputDialog.getMultiLineText(self, "Agregar texto", "Texto:")
        if not ok or not text.strip():
            return
        rect = (x, y, x + 280, y + 80)
        self.service.add_text_overlay(self.page_index, rect, text, self._style())
        self._draw_overlay_text(rect, text)

    def _edit_text_block(self, x: float, y: float) -> None:
        self._commit_active_editor()
        blocks = self.service.get_text_blocks(self.pdf_path, self.page_index)
        target = None
        for x0, y0, x1, y1, t in blocks:
            if (x0 - 8) <= x <= (x1 + 8) and (y0 - 8) <= y <= (y1 + 8):
                target = (x0, y0, x1, y1, t)
                break
        if target is None:
            return

        x0, y0, x1, y1, t = target
        rect = QGraphicsRectItem(QRectF(x0 * self.zoom, y0 * self.zoom, (x1 - x0) * self.zoom, (y1 - y0) * self.zoom))
        rect.setPen(QPen(QColor("red"), 2))
        self.scene.addItem(rect)

        editor = InlineTextEdit()
        editor.setText(t)
        editor.setGeometry(0, 0, int((x1 - x0) * self.zoom), int((y1 - y0) * self.zoom))
        proxy = self.scene.addWidget(editor)
        proxy.setPos(QPointF(x0 * self.zoom, y0 * self.zoom))

        committed = {"done": False}

        def commit():
            if committed["done"]:
                return
            committed["done"] = True
            new_text = editor.toPlainText().strip()
            if new_text:
                self.service.add_text_edit_overlay(self.page_index, (x0, y0, x1, y1), new_text, self._style())
            self._render_page()

        editor.editing_finished.connect(commit)
        editor.submit_requested.connect(commit)
        self._active_commit = commit
        editor.setFocus()

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
                self._draw_overlay_text(rect, txt)
        elif sig_type == "Imagen PNG":
            file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona firma", "", "PNG (*.png)")
            if file_path:
                image_bytes = Path(file_path).read_bytes()
                self.service.add_signature_image_overlay(self.page_index, rect, image_bytes, image_ext="png")
                self._draw_overlay_image(rect, image_bytes)
        else:
            dlg = DrawSignatureDialog(self)
            if dlg.exec():
                image_bytes = dlg.signature_png()
                self.service.add_signature_draw_overlay(self.page_index, rect, image_bytes)
                self._draw_overlay_image(rect, image_bytes)

    def _draw_overlay_text(
        self, rect: tuple[float, float, float, float], text: str, color: QColor | None = None
    ) -> None:
        x0, y0, x1, y1 = rect
        item = QGraphicsTextItem(text)
        item.setDefaultTextColor(color or self.current_color)
        item.setPos(x0 * self.zoom, y0 * self.zoom)
        item.setTextWidth((x1 - x0) * self.zoom)
        item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(item)

    def _draw_overlay_image(self, rect: tuple[float, float, float, float], image_bytes: bytes) -> None:
        x0, y0, x1, y1 = rect
        pix = QPixmap()
        pix.loadFromData(image_bytes, "PNG")
        item = QGraphicsPixmapItem(pix.scaled(int((x1 - x0) * self.zoom), int((y1 - y0) * self.zoom)))
        item.setPos(x0 * self.zoom, y0 * self.zoom)
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(item)

    def _export_pdf(self) -> None:
        self._commit_active_editor()
        out_path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", str(self.pdf_path.with_name("editado.pdf")), "PDF (*.pdf)")
        if not out_path:
            return
        try:
            self.service.export(self.pdf_path, Path(out_path))
            QMessageBox.information(self, "Éxito", f"PDF exportado en:\n{out_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
