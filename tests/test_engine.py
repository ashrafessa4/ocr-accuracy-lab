import os
from pathlib import Path

from PIL import Image

from ocrbench.engine import TesseractEngine


def test_engine_configures_runtime_and_reads_image(tmp_path: Path, monkeypatch) -> None:
    executable = tmp_path / "tesseract.exe"
    executable.touch()
    tessdata = tmp_path / "models"
    tessdata.mkdir()
    image_path = tmp_path / "field.png"
    Image.new("RGB", (10, 10), "white").save(image_path)
    observed: dict[str, str] = {}

    def fake_image_to_string(image, lang: str, config: str) -> str:
        observed.update({"lang": lang, "config": config, "size": str(image.size)})
        return " DEMO \n"

    monkeypatch.setattr("ocrbench.engine.pytesseract.image_to_string", fake_image_to_string)
    monkeypatch.setattr("ocrbench.engine.pytesseract.get_tesseract_version", lambda: "5.5.3")

    engine = TesseractEngine(executable, tessdata, page_segmentation_mode=6)

    assert engine.version == "5.5.3"
    assert engine.read(image_path, "eng") == "DEMO"
    assert observed == {"lang": "eng", "config": "--psm 6", "size": "(10, 10)"}
    assert os.environ["TESSDATA_PREFIX"] == str(tessdata.resolve())


def test_find_executable_uses_path_lookup(tmp_path: Path, monkeypatch) -> None:
    executable = tmp_path / "tesseract.exe"
    executable.touch()
    monkeypatch.setattr("ocrbench.engine.shutil.which", lambda _: str(executable))

    assert TesseractEngine._find_executable() == executable
