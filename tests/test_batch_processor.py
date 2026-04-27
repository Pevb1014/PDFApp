from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

from src.core.batch_processor import BatchSigningProcessor
from src.core.signature.models import SignatureRule


def _create_pdf_with_keyword_and_line(path: Path, keyword: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 220), f"Firma de {keyword}", fontsize=12)
    page.draw_line((70, 250), (320, 250))
    doc.save(str(path))
    doc.close()


def test_batch_signing_places_text_signature(tmp_path: Path) -> None:
    input_pdf = tmp_path / "contract.pdf"
    _create_pdf_with_keyword_and_line(input_pdf, keyword="Pablo")

    processor = BatchSigningProcessor()
    signers = [SignatureRule(keyword="Pablo", signature_type="text", value="Pablo Perez")]

    previews = processor.build_preview([input_pdf], signers)
    assert len(previews) == 1
    assert len(previews[0].placements) >= 1

    result = processor.sign_documents([input_pdf], signers, output_dir=tmp_path / "out")
    assert result.processed_documents == 1
    assert result.total_signatures >= 1
    assert result.unsigned_files == []

    output_pdf = Path(result.output_files[0])
    assert output_pdf.exists()
    assert output_pdf.parent.name == "firmados"

    signed_doc = fitz.open(str(output_pdf))
    text = "\n".join(page.get_text() for page in signed_doc)
    signed_doc.close()
    assert "Pablo Perez" in text


def test_batch_signing_sends_unsigned_documents_to_unsigned_folder(tmp_path: Path) -> None:
    input_pdf = tmp_path / "without_keyword.pdf"
    _create_pdf_with_keyword_and_line(input_pdf, keyword="Carlos")

    processor = BatchSigningProcessor()
    signers = [SignatureRule(keyword="Pablo", signature_type="text", value="Pablo Perez")]
    result = processor.sign_documents([input_pdf], signers, output_dir=tmp_path / "out")

    assert result.processed_documents == 1
    assert result.total_signatures == 0
    assert result.output_files == []
    assert len(result.unsigned_files) == 1
    unsigned_file = Path(result.unsigned_files[0])
    assert unsigned_file.exists()
    assert unsigned_file.parent.name == "sin_firma"
