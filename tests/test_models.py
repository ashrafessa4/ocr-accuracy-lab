from pathlib import Path

from ocrbench.models import download_models


def test_download_models_fetches_missing_and_reuses_existing(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []

    def fake_download(url: str, target: Path) -> None:
        calls.append(url)
        Path(target).write_bytes(b"model")

    monkeypatch.setattr("ocrbench.models.urllib.request.urlretrieve", fake_download)

    first = download_models(tmp_path, ["eng", "heb"])
    second = download_models(tmp_path, ["eng", "heb"])

    assert first == second
    assert all(path.read_bytes() == b"model" for path in first)
    assert len(calls) == 2
