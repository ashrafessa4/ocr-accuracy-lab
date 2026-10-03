import json
from pathlib import Path

from ocrbench.evaluator import _to_logical_order, evaluate_manifest


class FakeEngine:
    version = "fake-1.0"

    def __init__(self, predictions: dict[str, str]) -> None:
        self.predictions = predictions

    def read(self, image_path: Path, language: str) -> str:
        assert language == "eng"
        return self.predictions[image_path.name]


def test_evaluator_summarizes_field_and_language_accuracy(tmp_path: Path) -> None:
    manifest = {
        "license": "CC0-1.0",
        "sample_count": 1,
        "samples": [
            {
                "sample_id": "eng-clean",
                "language": "eng",
                "language_name": "English",
                "degradation": "clean",
                "fields": {
                    "name": {"expected": "DEMO HOLDER", "image": "name.png"},
                    "document_id": {"expected": "1234", "image": "document_id.png"},
                },
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    report = evaluate_manifest(
        path, FakeEngine({"name.png": "DEMO HOLDER", "document_id.png": "123X"})
    )

    assert report["overall"]["field_count"] == 2
    assert report["overall"]["field_accuracy"] == 0.5
    assert report["overall"]["character_error_rate"] == 0.125
    assert report["by_language"]["English"]["field_accuracy"] == 0.5


def test_rtl_visual_order_is_converted_to_logical_order() -> None:
    assert _to_logical_order("ילארשי", "heb") == "ישראלי"
    assert _to_logical_order("12345", "heb") == "12345"
