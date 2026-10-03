from __future__ import annotations

import urllib.request
from pathlib import Path

TESSDATA_FAST_BASE = "https://github.com/tesseract-ocr/tessdata_fast/raw/main"


def download_models(destination: Path, languages: list[str]) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for language in languages:
        target = destination / f"{language}.traineddata"
        if not target.exists():
            urllib.request.urlretrieve(f"{TESSDATA_FAST_BASE}/{target.name}", target)
        downloaded.append(target)
    return downloaded
