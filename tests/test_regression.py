import json
from pathlib import Path

from ocrbench.regression import compare_files, compare_reports


def _report(cer: float, accuracy: float) -> dict:
    summary = {"character_error_rate": cer, "field_accuracy": accuracy, "field_count": 10}
    return {"overall": summary, "by_language": {"English": summary}}


def test_comparison_passes_within_thresholds() -> None:
    result = compare_reports(
        _report(0.10, 0.80),
        _report(0.12, 0.77),
        max_cer_increase=0.03,
        max_accuracy_drop=0.05,
    )
    assert result["passed"]


def test_comparison_flags_accuracy_regression() -> None:
    result = compare_reports(
        _report(0.10, 0.80),
        _report(0.11, 0.70),
        max_cer_increase=0.03,
        max_accuracy_drop=0.05,
    )
    assert not result["passed"]
    assert {check["scope"] for check in result["checks"] if not check["passed"]} == {
        "overall",
        "language:English",
    }


def test_compare_files_writes_markdown_result(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    output = tmp_path / "comparison.md"
    baseline.write_text(json.dumps(_report(0.1, 0.8)), encoding="utf-8")
    current.write_text(json.dumps(_report(0.11, 0.79)), encoding="utf-8")

    result = compare_files(baseline, current, output, 0.03, 0.05)

    assert result["passed"]
    assert "Result: **PASS**" in output.read_text(encoding="utf-8")
