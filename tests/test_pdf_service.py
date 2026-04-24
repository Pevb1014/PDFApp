from pathlib import Path

import pytest

pypdf = pytest.importorskip("pypdf")
PdfReader = pypdf.PdfReader
PdfWriter = pypdf.PdfWriter

docx = pytest.importorskip("docx")
Document = docx.Document
fitz = pytest.importorskip("fitz")
Image = pytest.importorskip("PIL.Image")

from src.services.pdf_service import PDFService


def _make_pdf(path: Path, pages: int, width: int = 200) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=width, height=200)
    with path.open("wb") as f:
        writer.write(f)


def _make_encrypted_pdf(path: Path, password: str, pages: int = 1) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    writer.encrypt(password)
    with path.open("wb") as f:
        writer.write(f)


def _make_text_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def _make_image(path: Path) -> None:
    img = Image.new("RGB", (120, 40), color=(20, 20, 20))
    img.save(path)


def test_merge_and_split(tmp_path: Path) -> None:
    pdf_1 = tmp_path / "a.pdf"
    pdf_2 = tmp_path / "b.pdf"
    _make_pdf(pdf_1, 1)
    _make_pdf(pdf_2, 2)

    service = PDFService()
    merged = tmp_path / "merged.pdf"
    service.merge_pdfs([pdf_1, pdf_2], merged)
    assert merged.exists()

    split_dir = tmp_path / "split"
    parts = service.split_pdf(merged, split_dir)
    assert len(parts) == 3
    assert all(p.exists() for p in parts)


def test_merge_respects_custom_order(tmp_path: Path) -> None:
    pdf_first = tmp_path / "first.pdf"
    pdf_second = tmp_path / "second.pdf"
    pdf_third = tmp_path / "third.pdf"
    _make_pdf(pdf_first, pages=1, width=100)
    _make_pdf(pdf_second, pages=1, width=200)
    _make_pdf(pdf_third, pages=1, width=300)

    service = PDFService()
    merged = tmp_path / "ordered.pdf"
    service.merge_pdfs([pdf_third, pdf_first, pdf_second], merged)

    reader = PdfReader(str(merged))
    widths = [int(page.mediabox.width) for page in reader.pages]
    assert widths == [300, 100, 200]


def test_split_by_parts_distributes_pages_evenly(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=9)

    service = PDFService()
    output_dir = tmp_path / "parts"
    generated = service.split_pdf_by_parts(input_pdf, output_dir, num_parts=2)

    assert len(generated) == 2
    page_counts = [len(PdfReader(str(path)).pages) for path in generated]
    assert page_counts == [5, 4]


def test_split_by_parts_clamps_when_parts_exceed_total_pages(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=3)

    service = PDFService()
    generated = service.split_pdf_by_parts(input_pdf, tmp_path / "out", num_parts=4)
    assert len(generated) == 3
    page_counts = [len(PdfReader(str(path)).pages) for path in generated]
    assert page_counts == [1, 1, 1]


def test_get_total_pages(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=7)

    service = PDFService()
    assert service.get_total_pages(input_pdf) == 7


def test_get_total_pages_with_password_protected_pdf(tmp_path: Path) -> None:
    secured_pdf = tmp_path / "secure.pdf"
    _make_encrypted_pdf(secured_pdf, password="1234", pages=2)

    service = PDFService()
    service.set_password_provider(lambda _path, _retry: "1234")
    assert service.get_total_pages(secured_pdf) == 2


def test_get_total_pages_raises_when_password_is_missing(tmp_path: Path) -> None:
    secured_pdf = tmp_path / "secure.pdf"
    _make_encrypted_pdf(secured_pdf, password="secreta", pages=1)

    service = PDFService()
    with pytest.raises(RuntimeError):
        service.get_total_pages(secured_pdf)


def test_extract_multiple_ranges_generates_one_pdf_per_range(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=30)

    service = PDFService()
    out_dir = tmp_path / "ranges"
    generated = service.extract_page_ranges(input_pdf, out_dir, "2-14, 16-18, 20-29")

    assert len(generated) == 3
    page_counts = [len(PdfReader(str(path)).pages) for path in generated]
    assert page_counts == [13, 3, 10]


def test_parse_ranges_allows_overlap_but_rejects_invalid_ranges(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=10)
    service = PDFService()

    parsed = service.parse_page_ranges("2-5, 4-6", total_pages=10)
    assert parsed == [(2, 5), (4, 6)]

    with pytest.raises(ValueError):
        service.parse_page_ranges("8-3", total_pages=10)

    with pytest.raises(ValueError):
        service.parse_page_ranges("1-11", total_pages=10)


def test_extract_text_and_images_creates_text_file(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=2)

    service = PDFService()
    result = service.extract_text_and_images(input_pdf, tmp_path / "content")

    text_file = Path(result["text_file"])
    images_dir = Path(result["images_dir"])
    assert text_file.exists()
    assert images_dir.exists()


def test_convert_pdf_to_docx_creates_file(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    output_docx = tmp_path / "out.docx"
    service.convert_pdf_to_docx(input_pdf, output_docx)

    assert output_docx.exists()
    loaded = Document(str(output_docx))
    assert output_docx.stat().st_size > 0
    # Puede ocurrir que un PDF completamente en blanco no genere párrafos en modo avanzado.
    assert isinstance(loaded.paragraphs, list)


def test_extract_text_and_images_requires_pillow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    monkeypatch.setattr(service, "_image_extraction_available", lambda: False)

    with pytest.raises(RuntimeError):
        service.extract_text_and_images(input_pdf, tmp_path / "content")


def test_convert_docx_quick_without_pillow_adds_warning_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    monkeypatch.setattr(service, "_image_extraction_available", lambda: False)

    output_docx = tmp_path / "without_pillow.docx"
    service.convert_pdf_to_docx(input_pdf, output_docx, mode="quick")

    loaded = Document(str(output_docx))
    assert any("Imágenes omitidas" in p.text for p in loaded.paragraphs)


def test_convert_pdf_to_docx_advanced_mode_creates_file(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    output_docx = tmp_path / "advanced.docx"
    service.convert_pdf_to_docx(input_pdf, output_docx, mode="advanced")

    assert output_docx.exists()


def test_convert_pdf_to_docx_advanced_fallbacks_when_pdf2docx_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_pdf = tmp_path / "input.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    monkeypatch.setattr(service, "_convert_pdf_to_docx_pdf2docx", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    output_docx = tmp_path / "fallback.docx"
    service.convert_pdf_to_docx(input_pdf, output_docx, mode="advanced")

    assert output_docx.exists()


def test_replace_text_in_pdf_generates_output_with_replacement(tmp_path: Path) -> None:
    input_pdf = tmp_path / "source_text.pdf"
    output_pdf = tmp_path / "replaced.pdf"
    _make_text_pdf(input_pdf, "Hola mundo")

    service = PDFService()
    service.replace_text_in_pdf(input_pdf, output_pdf, "Hola", "Hello")

    doc = fitz.open(str(output_pdf))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    assert "Hello" in text


def test_add_text_to_pdf_inserts_text_on_selected_page(tmp_path: Path) -> None:
    input_pdf = tmp_path / "base.pdf"
    output_pdf = tmp_path / "with_text.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    service.add_text_to_pdf(input_pdf, output_pdf, text="Texto agregado", page_number=1, x=72, y=72)

    doc = fitz.open(str(output_pdf))
    text = doc[0].get_text()
    doc.close()
    assert "Texto agregado" in text


def test_sign_pdf_adds_visible_signature_text(tmp_path: Path) -> None:
    input_pdf = tmp_path / "unsigned.pdf"
    output_pdf = tmp_path / "signed.pdf"
    _make_pdf(input_pdf, pages=1)

    service = PDFService()
    service.sign_pdf(input_pdf, output_pdf, signer_name="Ana Perez", page_number=1)

    doc = fitz.open(str(output_pdf))
    text = doc[0].get_text()
    doc.close()
    assert "Firmado por: Ana Perez" in text


def test_render_pdf_page_preview_returns_png_bytes(tmp_path: Path) -> None:
    input_pdf = tmp_path / "preview.pdf"
    _make_text_pdf(input_pdf, "Vista previa")

    service = PDFService()
    image_bytes = service.render_pdf_page_preview(input_pdf, page_number=1, zoom=1.0)

    assert image_bytes.startswith(b"\x89PNG")


def test_extract_text_from_page_returns_page_content(tmp_path: Path) -> None:
    input_pdf = tmp_path / "page_text.pdf"
    _make_text_pdf(input_pdf, "Contenido pagina 1")

    service = PDFService()
    page_text = service.extract_text_from_page(input_pdf, page_number=1)

    assert "Contenido pagina 1" in page_text


def test_replace_text_at_position_updates_clicked_word(tmp_path: Path) -> None:
    input_pdf = tmp_path / "clicked_word.pdf"
    output_pdf = tmp_path / "clicked_word_out.pdf"
    _make_text_pdf(input_pdf, "Editar aqui")

    service = PDFService()
    service.replace_text_at_position(input_pdf, output_pdf, page_number=1, x=75, y=72, replacement_text="Nuevo")

    doc = fitz.open(str(output_pdf))
    text = doc[0].get_text()
    doc.close()
    assert "Nuevo" in text


def test_insert_image_to_pdf_places_image_on_page(tmp_path: Path) -> None:
    input_pdf = tmp_path / "image_input.pdf"
    output_pdf = tmp_path / "image_output.pdf"
    image_path = tmp_path / "sig.png"
    _make_pdf(input_pdf, pages=1)
    _make_image(image_path)

    service = PDFService()
    service.insert_image_to_pdf(input_pdf, output_pdf, image_path, page_number=1, x=80, y=80)

    doc = fitz.open(str(output_pdf))
    images = doc[0].get_images(full=True)
    doc.close()
    assert len(images) >= 1
