from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import fitz

from src.core.signature.models import SignaturePlacement, SignatureRule


@dataclass(slots=True)
class _KeywordHit:
    signer_index: int
    keyword: str
    rect: fitz.Rect


class SignatureDetector:
    def __init__(self, vertical_threshold: float = 50.0) -> None:
        self._vertical_threshold = vertical_threshold

    def detect_page_zones(
        self,
        page: fitz.Page,
        page_index: int,
        signers: list[SignatureRule],
    ) -> list[SignaturePlacement]:
        words = [fitz.Rect(*w[:4]) for w in page.get_text("words")]
        lines = self._extract_horizontal_lines(page)
        keyword_hits = self._extract_keyword_hits(page, signers)

        placements: list[SignaturePlacement] = []
        occupied = list(words)

        for hit in keyword_hits:
            signer = signers[hit.signer_index]
            candidate_rects = self._build_candidates(hit.rect, signer, lines)
            accepted = self._first_valid_candidate(candidate_rects, occupied, page.rect)
            if accepted is None:
                continue
            placements.append(
                SignaturePlacement(
                    page_index=page_index,
                    rect=(accepted.x0, accepted.y0, accepted.x1, accepted.y1),
                    signer_index=hit.signer_index,
                    keyword=hit.keyword,
                )
            )
            occupied.append(accepted)
        return placements

    def _first_valid_candidate(
        self,
        candidate_rects: Iterable[fitz.Rect],
        occupied: list[fitz.Rect],
        page_rect: fitz.Rect,
    ) -> fitz.Rect | None:
        for rect in candidate_rects:
            if not self._inside_page(rect, page_rect):
                continue
            if any(rect.intersects(existing) for existing in occupied):
                continue
            return rect
        return None

    @staticmethod
    def _inside_page(rect: fitz.Rect, page_rect: fitz.Rect) -> bool:
        return rect.x0 >= page_rect.x0 and rect.y0 >= page_rect.y0 and rect.x1 <= page_rect.x1 and rect.y1 <= page_rect.y1

    def _build_candidates(
        self,
        keyword_rect: fitz.Rect,
        signer: SignatureRule,
        lines: list[fitz.Rect],
    ) -> list[fitz.Rect]:
        width = signer.width
        height = signer.height
        candidates: list[fitz.Rect] = []

        nearby_line = self._closest_line(keyword_rect, lines)
        if nearby_line is not None:
            overlap_left = max(keyword_rect.x0, nearby_line.x0)
            overlap_right = min(keyword_rect.x1, nearby_line.x1)
            center_x = (overlap_left + overlap_right) / 2 if overlap_right > overlap_left else keyword_rect.x0
            x0 = center_x - (width / 2)
            y1 = nearby_line.y0 - 2
            candidates.append(fitz.Rect(x0, y1 - height, x0 + width, y1))

        candidates.append(
            fitz.Rect(keyword_rect.x0, keyword_rect.y0 - height - 4, keyword_rect.x0 + width, keyword_rect.y0 - 4)
        )
        candidates.append(
            fitz.Rect(keyword_rect.x0, keyword_rect.y1 + 4, keyword_rect.x0 + width, keyword_rect.y1 + 4 + height)
        )
        candidates.append(
            fitz.Rect(keyword_rect.x1 + 8, keyword_rect.y0 - (height / 3), keyword_rect.x1 + 8 + width, keyword_rect.y0 - (height / 3) + height)
        )
        return candidates

    def _closest_line(self, keyword_rect: fitz.Rect, lines: list[fitz.Rect]) -> fitz.Rect | None:
        best_line: fitz.Rect | None = None
        best_distance = float("inf")
        for line in lines:
            if line.x1 < keyword_rect.x0 or line.x0 > keyword_rect.x1:
                continue
            distance = abs(line.y0 - keyword_rect.y1)
            if distance > self._vertical_threshold:
                continue
            if distance < best_distance:
                best_distance = distance
                best_line = line
        return best_line

    @staticmethod
    def _extract_horizontal_lines(page: fitz.Page) -> list[fitz.Rect]:
        horizontal: list[fitz.Rect] = []
        for drawing in page.get_drawings():
            for item in drawing.get("items", []):
                if len(item) < 3 or item[0] != "l":
                    continue
                p1, p2 = item[1], item[2]
                if abs(float(p1.y) - float(p2.y)) > 2:
                    continue
                x0 = min(float(p1.x), float(p2.x))
                x1 = max(float(p1.x), float(p2.x))
                if x1 - x0 < 20:
                    continue
                y = float(p1.y)
                horizontal.append(fitz.Rect(x0, y - 1, x1, y + 1))
        return horizontal

    @staticmethod
    def _extract_keyword_hits(page: fitz.Page, signers: list[SignatureRule]) -> list[_KeywordHit]:
        hits: list[_KeywordHit] = []
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = str(span.get("text", ""))
                    if not text.strip():
                        continue
                    span_rect = fitz.Rect(*span.get("bbox"))
                    lowered = text.lower()
                    for signer_index, signer in enumerate(signers):
                        if signer.keyword.lower() in lowered:
                            hits.append(_KeywordHit(signer_index=signer_index, keyword=signer.keyword, rect=span_rect))
        return hits
