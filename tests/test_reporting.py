import json
from pathlib import Path

from ocrbench.reporting import write_reports


def _sample_report() -> dict:
    summary = {"character_error_rate": 0.1, "field_accuracy": 0.5, "field_count": 2}
    return {
        "metadata": {"engine": "Tesseract", "engine_version": "5.5"},
        "overall": summary,
        "by_language": {"English": summary},
        "by_degradation": {"clean": summary, "blur": summary},
        "by_field": {"name": summary},
        "results": [
            {
                "sample_id": "eng-clean",
                "language": "eng",
                "language_name": "English",
                "degradation": "clean",
                "field": "name",
                "expected": "DEMO",
                "predicted": "DEM0",
                "predicted_raw": "DEM0",
                "character_error_rate": 0.25,
                "exact_match": False,
            }
        ],
    }


def test_write_reports_creates_machine_and_human_readable_outputs(tmp_path: Path) -> None:
    write_reports(_sample_report(), tmp_path)

    assert json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))["overall"]
    assert "Character error rate" in (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert (tmp_path / "results.csv").stat().st_size > 0
    assert (tmp_path / "accuracy-chart.png").stat().st_size > 0
