import pytest

from ocrbench.metrics import character_error_rate, exact_match, levenshtein_distance, normalize_text


def test_normalization_handles_spacing_case_and_bidi_controls() -> None:
    assert normalize_text("\u200f  Demo   HOLDER \n") == "demo holder"


@pytest.mark.parametrize(
    ("reference", "hypothesis", "distance"),
    [
        ("identity", "identity", 0),
        ("identity", "ident1ty", 1),
        ("kitten", "sitting", 3),
        ("", "abc", 3),
    ],
)
def test_levenshtein_distance(reference: str, hypothesis: str, distance: int) -> None:
    assert levenshtein_distance(reference, hypothesis) == distance


def test_character_error_rate_counts_character_edits() -> None:
    assert character_error_rate("123456789", "12345678g") == pytest.approx(1 / 9)


def test_exact_match_uses_normalized_text() -> None:
    assert exact_match("DEMO HOLDER", " demo  holder ")


def test_character_error_rate_handles_empty_reference() -> None:
    assert character_error_rate("", "") == 0.0
    assert character_error_rate("", "unexpected") == 1.0
