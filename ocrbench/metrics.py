from __future__ import annotations

import re
import unicodedata

_BIDI_CONTROLS = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def normalize_text(value: str) -> str:
    """Normalize OCR output without hiding meaningful character errors."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = _BIDI_CONTROLS.sub("", normalized)
    return " ".join(normalized.split()).casefold()


def levenshtein_distance(reference: str, hypothesis: str) -> int:
    """Return edit distance using O(min(n, m)) memory."""
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for row, ref_character in enumerate(reference, start=1):
        current = [row]
        for column, hyp_character in enumerate(hypothesis, start=1):
            insertion = current[column - 1] + 1
            deletion = previous[column] + 1
            substitution = previous[column - 1] + (ref_character != hyp_character)
            current.append(min(insertion, deletion, substitution))
        previous = current
    return previous[-1]


def character_error_rate(reference: str, hypothesis: str) -> float:
    expected = normalize_text(reference)
    actual = normalize_text(hypothesis)
    if not expected:
        return 0.0 if not actual else 1.0
    return levenshtein_distance(expected, actual) / len(expected)


def exact_match(reference: str, hypothesis: str) -> bool:
    return normalize_text(reference) == normalize_text(hypothesis)
