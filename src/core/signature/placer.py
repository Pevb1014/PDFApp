from __future__ import annotations

import io
from typing import Sequence

import fitz

from src.core.signature.models import SignatureRule


class SignaturePlacer:
    @staticmethod
    def place_signature(page: fitz.Page, rect: tuple[float, float, float, float], signature: SignatureRule) -> None:
        target = fitz.Rect(*rect)

        if signature.signature_type == "image":
            page.insert_image(target, filename=str(signature.value), keep_proportion=True)
            return

        if signature.signature_type == "text":
            page.insert_textbox(target, str(signature.value), fontsize=12, color=(0, 0, 0), align=0)
            return

        image_bytes = SignaturePlacer._draw_signature_to_png(signature.value)
        page.insert_image(target, stream=image_bytes, keep_proportion=True)

    @staticmethod
    def _draw_signature_to_png(strokes: str | bytes) -> bytes:
        import json
        from PIL import Image, ImageDraw

        if isinstance(strokes, bytes):
            return strokes

        points: Sequence[Sequence[tuple[float, float]]] = json.loads(strokes)
        image = Image.new("RGBA", (400, 120), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        for stroke in points:
            if len(stroke) < 2:
                continue
            draw.line([tuple(p) for p in stroke], fill=(0, 0, 0, 255), width=3)

        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
