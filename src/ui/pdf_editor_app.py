from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from src.ui.pdf_editor_qt import PDFEditorWindow


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python -m src.ui.pdf_editor_app <archivo.pdf>")
        return 1

    pdf_path = Path(sys.argv[1]).expanduser().resolve()
    app = QApplication(sys.argv)
    window = PDFEditorWindow(pdf_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
