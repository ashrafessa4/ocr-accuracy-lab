from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_reports(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_csv(report, output_dir / "results.csv")
    _write_markdown(report, output_dir / "summary.md")
    _write_chart(report, output_dir / "accuracy-chart.png")


def _write_csv(report: dict, path: Path) -> None:
    fieldnames = [
        "sample_id",
        "language",
        "language_name",
        "degradation",
        "field",
        "expected",
        "predicted",
        "predicted_raw",
        "character_error_rate",
        "exact_match",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report["results"])


def _write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# OCR benchmark summary",
        "",
        f"Engine: {report['metadata']['engine']} {report['metadata']['engine_version']}",
        "",
        "| Scope | Character error rate | Exact field accuracy | Fields |",
        "| --- | ---: | ---: | ---: |",
        (
            f"| Overall | {_percent(report['overall']['character_error_rate'])} | "
            f"{_percent(report['overall']['field_accuracy'])} | "
            f"{report['overall']['field_count']} |"
        ),
    ]
    for name, summary in report["by_language"].items():
        lines.append(
            f"| {name} | {_percent(summary['character_error_rate'])} | "
            f"{_percent(summary['field_accuracy'])} | {summary['field_count']} |"
        )
    lines.extend(
        [
            "",
            "All inputs are programmatically generated and licensed CC0-1.0.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_chart(report: dict, path: Path) -> None:
    labels = list(report["by_degradation"])
    cer = [report["by_degradation"][label]["character_error_rate"] * 100 for label in labels]
    accuracy = [report["by_degradation"][label]["field_accuracy"] * 100 for label in labels]

    figure, (top, bottom) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    figure.suptitle("OCR robustness by image degradation", fontsize=16, fontweight="bold")
    top.bar(labels, accuracy, color="#16867a")
    top.set_ylabel("Exact field accuracy (%)")
    top.set_ylim(0, 105)
    top.grid(axis="y", alpha=0.25)
    bottom.bar(labels, cer, color="#dd6b20")
    bottom.set_ylabel("Character error rate (%)")
    bottom.set_ylim(0, max(10, max(cer) * 1.2))
    bottom.grid(axis="y", alpha=0.25)
    bottom.set_xlabel("Synthetic condition")
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)
