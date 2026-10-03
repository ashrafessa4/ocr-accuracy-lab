from __future__ import annotations

import argparse
from pathlib import Path

from ocrbench.engine import TesseractEngine
from ocrbench.evaluator import evaluate_manifest
from ocrbench.generator import generate_dataset
from ocrbench.models import download_models
from ocrbench.regression import compare_files
from ocrbench.reporting import write_reports


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ocrbench", description="Synthetic multilingual OCR accuracy benchmark"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate synthetic identity images")
    generate.add_argument("--output-dir", type=Path, default=Path("data/synthetic"))
    generate.add_argument("--manifest", type=Path, default=Path("data/manifest.json"))

    models = commands.add_parser("download-models", help="Download open Tesseract models")
    models.add_argument("--destination", type=Path, default=Path(".tessdata"))
    models.add_argument("--languages", nargs="+", default=["eng", "heb", "ara"])

    evaluate = commands.add_parser("evaluate", help="Run OCR and produce reports")
    evaluate.add_argument("--manifest", type=Path, default=Path("data/manifest.json"))
    evaluate.add_argument("--output-dir", type=Path, default=Path("reports/current"))
    evaluate.add_argument("--tesseract-cmd", type=Path)
    evaluate.add_argument("--tessdata-dir", type=Path)
    evaluate.add_argument("--psm", type=int, default=7)

    compare = commands.add_parser("compare", help="Fail when OCR accuracy regresses")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("current", type=Path)
    compare.add_argument("--output", type=Path, default=Path("reports/comparison.md"))
    compare.add_argument("--max-cer-increase", type=float, default=0.03)
    compare.add_argument("--max-accuracy-drop", type=float, default=0.05)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "generate":
        manifest = generate_dataset(args.output_dir, args.manifest)
        print(f"Generated {manifest['sample_count']} synthetic samples at {args.output_dir}")
        return 0
    if args.command == "download-models":
        paths = download_models(args.destination, args.languages)
        print(f"Available models: {', '.join(path.name for path in paths)}")
        return 0
    if args.command == "evaluate":
        engine = TesseractEngine(
            executable=args.tesseract_cmd,
            tessdata_dir=args.tessdata_dir,
            page_segmentation_mode=args.psm,
        )
        report = evaluate_manifest(args.manifest, engine)
        write_reports(report, args.output_dir)
        print(
            f"CER={report['overall']['character_error_rate']:.3f}; "
            f"field accuracy={report['overall']['field_accuracy']:.3f}"
        )
        return 0
    if args.command == "compare":
        comparison = compare_files(
            args.baseline,
            args.current,
            args.output,
            max_cer_increase=args.max_cer_increase,
            max_accuracy_drop=args.max_accuracy_drop,
        )
        print(f"Regression check: {'PASS' if comparison['passed'] else 'FAIL'}")
        return 0 if comparison["passed"] else 1
    return 2
