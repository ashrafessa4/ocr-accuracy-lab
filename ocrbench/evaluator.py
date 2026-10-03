from __future__ import annotations

import json
import platform
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from ocrbench.metrics import character_error_rate, exact_match


class OcrEngine(Protocol):
    @property
    def version(self) -> str: ...

    def read(self, image_path: Path, language: str) -> str: ...


_RTL_CHARACTER = re.compile(r"[\u0590-\u08ff]")


def _to_logical_order(value: str, language: str) -> str:
    """Convert Tesseract's visual-order output for an isolated RTL-only line."""
    if language in {"heb", "ara"} and _RTL_CHARACTER.search(value):
        return value[::-1]
    return value


def _summary(rows: list[dict]) -> dict[str, float | int]:
    if not rows:
        return {"character_error_rate": 0.0, "field_accuracy": 0.0, "field_count": 0}
    return {
        "character_error_rate": sum(row["character_error_rate"] for row in rows) / len(rows),
        "field_accuracy": sum(row["exact_match"] for row in rows) / len(rows),
        "field_count": len(rows),
    }


def _group(rows: list[dict], key: str) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return {name: _summary(group_rows) for name, group_rows in sorted(grouped.items())}


def evaluate_manifest(manifest_path: Path, engine: OcrEngine) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for sample in manifest["samples"]:
        for field_name, field in sample["fields"].items():
            image_path = manifest_path.parent / field["image"]
            ocr_language = sample["language"]
            if ocr_language in {"heb", "ara"}:
                ocr_language = f"{ocr_language}+eng"
            predicted_raw = engine.read(image_path, ocr_language)
            predicted = _to_logical_order(predicted_raw, sample["language"])
            rows.append(
                {
                    "sample_id": sample["sample_id"],
                    "language": sample["language"],
                    "language_name": sample["language_name"],
                    "degradation": sample["degradation"],
                    "field": field_name,
                    "expected": field["expected"],
                    "predicted": predicted,
                    "predicted_raw": predicted_raw,
                    "character_error_rate": character_error_rate(field["expected"], predicted),
                    "exact_match": exact_match(field["expected"], predicted),
                }
            )

    return {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "engine": "Tesseract",
            "engine_version": engine.version,
            "platform": platform.platform(),
            "data_license": manifest["license"],
            "sample_count": manifest["sample_count"],
        },
        "overall": _summary(rows),
        "by_language": _group(rows, "language_name"),
        "by_degradation": _group(rows, "degradation"),
        "by_field": _group(rows, "field"),
        "results": rows,
    }
