from pathlib import Path

import pytest

from src.services.viewer_service import ViewerService


class FakeSystemAdapter:
    def __init__(self) -> None:
        self.opened: Path | None = None

    def open_file(self, path: Path) -> None:
        self.opened = path


def test_open_pdf_calls_system_adapter(tmp_path: Path) -> None:
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    adapter = FakeSystemAdapter()
    service = ViewerService(system_adapter=adapter)
    service.open_pdf(pdf_path)

    assert adapter.opened == pdf_path


def test_open_pdf_raises_for_non_pdf(tmp_path: Path) -> None:
    txt_path = tmp_path / "doc.txt"
    txt_path.write_text("hola", encoding="utf-8")

    service = ViewerService(system_adapter=FakeSystemAdapter())
    with pytest.raises(ValueError):
        service.open_pdf(txt_path)
