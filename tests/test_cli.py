from pathlib import Path

from ocrbench import cli


def test_generate_command(tmp_path: Path) -> None:
    result = cli.main(
        [
            "generate",
            "--output-dir",
            str(tmp_path / "synthetic"),
            "--manifest",
            str(tmp_path / "manifest.json"),
        ]
    )
    assert result == 0
    assert (tmp_path / "manifest.json").exists()


def test_download_command(tmp_path: Path, monkeypatch) -> None:
    model = tmp_path / "eng.traineddata"
    monkeypatch.setattr(cli, "download_models", lambda destination, languages: [model])
    assert cli.main(["download-models", "--destination", str(tmp_path)]) == 0


def test_evaluate_command(tmp_path: Path, monkeypatch) -> None:
    report = {
        "overall": {"character_error_rate": 0.1, "field_accuracy": 0.9},
    }
    written: list[Path] = []
    monkeypatch.setattr(cli, "TesseractEngine", lambda **kwargs: object())
    monkeypatch.setattr(cli, "evaluate_manifest", lambda manifest, engine: report)
    monkeypatch.setattr(cli, "write_reports", lambda value, output: written.append(output))

    result = cli.main(
        ["evaluate", "--manifest", str(tmp_path / "manifest.json"), "--output-dir", str(tmp_path)]
    )

    assert result == 0
    assert written == [tmp_path]


def test_compare_command_returns_nonzero_for_regression(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "compare_files", lambda *args, **kwargs: {"passed": False})
    result = cli.main(["compare", str(tmp_path / "base.json"), str(tmp_path / "new.json")])
    assert result == 1
