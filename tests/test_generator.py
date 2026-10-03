import json
from pathlib import Path

from PIL import Image

from ocrbench.generator import generate_dataset


def test_generator_creates_three_languages_and_five_conditions(tmp_path: Path) -> None:
    manifest_path = tmp_path / "data" / "manifest.json"
    manifest = generate_dataset(tmp_path / "data" / "synthetic", manifest_path)

    assert manifest["sample_count"] == 15
    assert {sample["language"] for sample in manifest["samples"]} == {"eng", "heb", "ara"}
    assert {sample["degradation"] for sample in manifest["samples"]} == {
        "clean",
        "blur",
        "rotation",
        "low_light",
        "noise",
    }

    on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
    example = on_disk["samples"][0]
    card = manifest_path.parent / example["card_image"]
    field = manifest_path.parent / example["fields"]["name"]["image"]
    assert card.exists()
    assert field.exists()
    with Image.open(card) as image:
        assert image.size == (1000, 620)
