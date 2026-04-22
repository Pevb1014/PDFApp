from __future__ import annotations

import io
from pathlib import Path

import fitz

from src.core.editor_models import OverlayItem


class PDFOverlayAdapter:
    """Infraestructura PyMuPDF para renderizado y exportación por superposiciones."""

    @staticmethod
    def page_count(path: Path) -> int:
        with fitz.open(str(path)) as doc:
            return len(doc)

    @staticmethod
    def render_page_png(path: Path, page_index: int, zoom: float = 1.2) -> bytes:
        with fitz.open(str(path)) as doc:
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            return pix.tobytes("png")

    @staticmethod
    def text_blocks(path: Path, page_index: int) -> list[tuple[float, float, float, float, str]]:
        with fitz.open(str(path)) as doc:
            blocks = doc[page_index].get_text("blocks")
        return [(b[0], b[1], b[2], b[3], b[4] or "") for b in blocks if len(b) >= 5 and (b[4] or "").strip()]

    @staticmethod
    def export_with_overlays(input_pdf: Path, output_pdf: Path, overlays: list[OverlayItem]) -> Path:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with fitz.open(str(input_pdf)) as doc:
            for item in overlays:
                page = doc[item.page_index]
                rect = fitz.Rect(*item.rect)
                color = item.style.color_rgb

                if item.kind == "text_edit":
                    page.draw_rect(rect, fill=(1, 1, 1), color=(1, 1, 1))
                    page.insert_textbox(
                        rect,
                        item.text,
                        fontsize=item.style.font_size,
                        fontname="helv",
                        color=color,
                    )
                elif item.kind in {"text_add", "signature_text"}:
                    page.insert_textbox(
                        rect,
                        item.text,
                        fontsize=item.style.font_size,
                        fontname="helv",
                        color=color,
                    )
                elif item.kind in {"signature_image", "signature_draw"} and item.image_bytes:
                    stream = io.BytesIO(item.image_bytes)
                    page.insert_image(rect, stream=stream.getvalue(), keep_proportion=True)

            doc.save(str(output_pdf))
        return output_pdf
