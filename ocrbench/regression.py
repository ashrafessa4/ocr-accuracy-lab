from __future__ import annotations

import json
from pathlib import Path


def compare_reports(
    baseline: dict,
    current: dict,
    max_cer_increase: float,
    max_accuracy_drop: float,
) -> dict:
    checks: list[dict] = []

    def compare_scope(scope: str, base: dict, candidate: dict) -> None:
        cer_change = candidate["character_error_rate"] - base["character_error_rate"]
        accuracy_change = candidate["field_accuracy"] - base["field_accuracy"]
        checks.append(
            {
                "scope": scope,
                "cer_change": cer_change,
                "accuracy_change": accuracy_change,
                "passed": cer_change <= max_cer_increase
                and accuracy_change >= -max_accuracy_drop,
            }
        )

    compare_scope("overall", baseline["overall"], current["overall"])
    common_languages = baseline["by_language"].keys() & current["by_language"].keys()
    for language in sorted(common_languages):
        compare_scope(
            f"language:{language}",
            baseline["by_language"][language],
            current["by_language"][language],
        )

    return {
        "passed": all(check["passed"] for check in checks),
        "thresholds": {
            "max_cer_increase": max_cer_increase,
            "max_accuracy_drop": max_accuracy_drop,
        },
        "checks": checks,
    }


def compare_files(
    baseline_path: Path,
    current_path: Path,
    output_path: Path,
    max_cer_increase: float,
    max_accuracy_drop: float,
) -> dict:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = json.loads(current_path.read_text(encoding="utf-8"))
    comparison = compare_reports(
        baseline, current, max_cer_increase=max_cer_increase, max_accuracy_drop=max_accuracy_drop
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# OCR regression comparison",
        "",
        f"Result: **{'PASS' if comparison['passed'] else 'FAIL'}**",
        "",
        "| Scope | CER change | Accuracy change | Result |",
        "| --- | ---: | ---: | --- |",
    ]
    for check in comparison["checks"]:
        lines.append(
            f"| {check['scope']} | {check['cer_change']:+.3f} | "
            f"{check['accuracy_change']:+.3f} | "
            f"{'PASS' if check['passed'] else 'FAIL'} |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return comparison
