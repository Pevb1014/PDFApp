from __future__ import annotations

from pathlib import Path

from src.adapters.pdf_overlay_adapter import PDFOverlayAdapter
from src.core.editor_models import OverlayItem, OverlayStyle


class PDFEditorService:
    """Casos de uso para editor PDF por superposiciones."""

    def __init__(self, adapter: PDFOverlayAdapter | None = None) -> None:
        self._adapter = adapter or PDFOverlayAdapter()
        self._overlays: list[OverlayItem] = []

    def clear_overlays(self) -> None:
        self._overlays = []

    def list_overlays(self) -> list[OverlayItem]:
        return list(self._overlays)

    def page_count(self, pdf_path: Path) -> int:
        return self._adapter.page_count(pdf_path)

    def render_page(self, pdf_path: Path, page_index: int, zoom: float) -> bytes:
        return self._adapter.render_page_png(pdf_path, page_index, zoom)

    def get_text_blocks(self, pdf_path: Path, page_index: int) -> list[tuple[float, float, float, float, str]]:
        return self._adapter.text_blocks(pdf_path, page_index)

    def add_overlay(self, overlay: OverlayItem) -> None:
        self._overlays.append(overlay)

    def add_text_overlay(
        self,
        page_index: int,
        rect: tuple[float, float, float, float],
        text: str,
        style: OverlayStyle,
    ) -> None:
        self.add_overlay(OverlayItem(kind="text_add", page_index=page_index, rect=rect, text=text, style=style))

    def add_text_edit_overlay(
        self,
        page_index: int,
        rect: tuple[float, float, float, float],
        text: str,
        style: OverlayStyle,
    ) -> None:
        self.add_overlay(OverlayItem(kind="text_edit", page_index=page_index, rect=rect, text=text, style=style))

    def add_signature_text_overlay(
        self,
        page_index: int,
        rect: tuple[float, float, float, float],
        text: str,
        style: OverlayStyle,
    ) -> None:
        self.add_overlay(OverlayItem(kind="signature_text", page_index=page_index, rect=rect, text=text, style=style))

    def add_signature_image_overlay(
        self,
        page_index: int,
        rect: tuple[float, float, float, float],
        image_bytes: bytes,
        image_ext: str = "png",
    ) -> None:
        self.add_overlay(
            OverlayItem(
                kind="signature_image",
                page_index=page_index,
                rect=rect,
                image_bytes=image_bytes,
                image_ext=image_ext,
            )
        )

    def add_signature_draw_overlay(
        self,
        page_index: int,
        rect: tuple[float, float, float, float],
        image_bytes: bytes,
    ) -> None:
        self.add_overlay(
            OverlayItem(
                kind="signature_draw",
                page_index=page_index,
                rect=rect,
                image_bytes=image_bytes,
                image_ext="png",
            )
        )

    def export(self, input_pdf: Path, output_pdf: Path) -> Path:
        return self._adapter.export_with_overlays(input_pdf, output_pdf, self._overlays)
