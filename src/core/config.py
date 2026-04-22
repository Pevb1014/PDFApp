from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Configuración base de la app y rutas de proyecto."""

    app_name: str = "PDF Processor"
    app_version: str = "0.1.0"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def assets_dir(self) -> Path:
        return self.project_root / "assets"


CONFIG = AppConfig()
