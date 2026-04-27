from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

import fitz

from src.core.signature.detector import SignatureDetector
from src.core.signature.models import BatchSigningResult, PDFSigningPreview, SignatureRule
from src.core.signature.placer import SignaturePlacer


class BatchSigningProcessor:
    def __init__(self, detector: SignatureDetector | None = None, placer: SignaturePlacer | None = None) -> None:
        self._detector = detector or SignatureDetector()
        self._placer = placer or SignaturePlacer()

    def build_preview(self, pdf_paths: list[Path], signers: list[SignatureRule]) -> list[PDFSigningPreview]:
        previews: list[PDFSigningPreview] = []
        for pdf_path in pdf_paths:
            doc = fitz.open(str(pdf_path))
            try:
                placements = []
                for page_index, page in enumerate(doc):
                    placements.extend(self._detector.detect_page_zones(page, page_index, signers))
                previews.append(PDFSigningPreview(pdf_path=str(pdf_path), placements=placements))
            finally:
                doc.close()
        return previews

    def sign_documents(
        self,
        pdf_paths: list[Path],
        signers: list[SignatureRule],
        output_dir: Path,
        overwrite: bool = False,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> BatchSigningResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        signed_dir = output_dir / "firmados"
        unsigned_dir = output_dir / "sin_firma"
        signed_dir.mkdir(parents=True, exist_ok=True)
        unsigned_dir.mkdir(parents=True, exist_ok=True)

        processed = 0
        total_signatures = 0
        output_files: list[str] = []
        unsigned_files: list[str] = []
        errors: list[str] = []

        for index, pdf_path in enumerate(pdf_paths, start=1):
            doc: fitz.Document | None = None
            try:
                doc = fitz.open(str(pdf_path))
                placements = []
                for page_index, page in enumerate(doc):
                    placements.extend(self._detector.detect_page_zones(page, page_index, signers))

                for placement in placements:
                    page = doc[placement.page_index]
                    signer = signers[placement.signer_index]
                    self._placer.place_signature(page, placement.rect, signer)

                if overwrite and placements:
                    output_path = pdf_path
                    doc.save(str(output_path))
                    output_files.append(str(output_path))
                elif placements:
                    output_path = signed_dir / f"{pdf_path.stem}_signed.pdf"
                    doc.save(str(output_path))
                    output_files.append(str(output_path))
                else:
                    output_path = unsigned_dir / pdf_path.name
                    doc.close()
                    doc = None
                    shutil.copy2(pdf_path, output_path)
                    unsigned_files.append(str(output_path))
                    processed += 1
                    if progress_callback:
                        progress_callback(index, len(pdf_paths), pdf_path.name)
                    continue
                doc.close()
                doc = None

                processed += 1
                total_signatures += len(placements)
                if progress_callback:
                    progress_callback(index, len(pdf_paths), pdf_path.name)
            except Exception as exc:
                errors.append(f"{pdf_path.name}: {exc}")
            finally:
                if doc is not None:
                    doc.close()

        return BatchSigningResult(
            total_documents=len(pdf_paths),
            processed_documents=processed,
            total_signatures=total_signatures,
            output_files=output_files,
            unsigned_files=unsigned_files,
            errors=errors,
        )
