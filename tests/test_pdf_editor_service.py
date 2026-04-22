from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

from src.core.editor_models import OverlayStyle
from src.services.pdf_editor_service import PDFEditorService


def _make_text_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def test_editor_service_detects_blocks_and_exports_overlay(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    out = tmp_path / "out.pdf"
    _make_text_pdf(source, "Texto base")

    service = PDFEditorService()
    blocks = service.get_text_blocks(source, 0)
    assert len(blocks) >= 1

    service.add_text_overlay(
        page_index=0,
        rect=(100, 100, 260, 160),
        text="Overlay texto",
        style=OverlayStyle(font_size=14),
    )
    service.export(source, out)

    assert out.exists()
    exported = fitz.open(str(out))
    text = exported[0].get_text()
    exported.close()
    assert "Overlay texto" in text


def test_editor_service_updates_overlay_rect() -> None:
    service = PDFEditorService()
    overlay = service.add_text_overlay(
        page_index=0,
        rect=(10, 10, 100, 40),
        text="Mover",
        style=OverlayStyle(),
    )
    service.update_overlay_rect(overlay.uid, (20, 30, 110, 60))
    updated = service.list_overlays()[0]
    assert updated.rect == (20, 30, 110, 60)


def test_editor_service_updates_overlay_text_and_style() -> None:
    service = PDFEditorService()
    overlay = service.add_text_overlay(
        page_index=0,
        rect=(10, 10, 100, 40),
        text="Texto A",
        style=OverlayStyle(font_family="Helvetica", font_size=12),
    )
    service.update_overlay_text(
        overlay.uid,
        "Texto B",
        style=OverlayStyle(font_family="Times", font_size=18, color_rgb=(1, 0, 0)),
    )
    updated = service.list_overlays()[0]
    assert updated.text == "Texto B"
    assert updated.style.font_size == 18


def test_editor_service_remove_overlay() -> None:
    service = PDFEditorService()
    overlay = service.add_text_overlay(
        page_index=0,
        rect=(10, 10, 100, 40),
        text="Eliminar",
        style=OverlayStyle(),
    )
    service.remove_overlay(overlay.uid)
    assert service.list_overlays() == []
