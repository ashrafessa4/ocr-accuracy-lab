from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytesseract
from PIL import Image


class TesseractEngine:
    def __init__(
        self,
        executable: Path | None = None,
        tessdata_dir: Path | None = None,
        page_segmentation_mode: int = 7,
    ) -> None:
        resolved = executable or self._find_executable()
        pytesseract.pytesseract.tesseract_cmd = str(resolved)
        self.tessdata_dir = tessdata_dir
        if tessdata_dir:
            os.environ["TESSDATA_PREFIX"] = str(tessdata_dir.resolve())
        self.page_segmentation_mode = page_segmentation_mode

    @staticmethod
    def _find_executable() -> Path:
        on_path = shutil.which("tesseract")
        candidates = [
            Path(on_path) if on_path else None,
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe",
        ]
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        raise FileNotFoundError("Tesseract was not found. Install it or pass --tesseract-cmd.")

    @property
    def version(self) -> str:
        return str(pytesseract.get_tesseract_version()).splitlines()[0]

    def read(self, image_path: Path, language: str) -> str:
        config_parts = [f"--psm {self.page_segmentation_mode}"]
        with Image.open(image_path) as image:
            return pytesseract.image_to_string(
                image,
                lang=language,
                config=" ".join(config_parts),
            ).strip()
