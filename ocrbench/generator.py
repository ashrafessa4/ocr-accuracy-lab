from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

from ocrbench.degradations import DEGRADATIONS


@dataclass(frozen=True)
class SyntheticIdentity:
    language: str
    language_name: str
    direction: str
    title: str
    labels: dict[str, str]
    fields: dict[str, str]


IDENTITIES = (
    SyntheticIdentity(
        language="eng",
        language_name="English",
        direction="ltr",
        title="SYNTHETIC IDENTITY SAMPLE",
        labels={
            "name": "NAME",
            "document_id": "DOCUMENT ID",
            "date_of_birth": "DATE OF BIRTH",
            "expiry": "EXPIRY",
        },
        fields={
            "name": "DEMO HOLDER",
            "document_id": "123456789",
            "date_of_birth": "1990-04-12",
            "expiry": "2032-05-30",
        },
    ),
    SyntheticIdentity(
        language="heb",
        language_name="Hebrew",
        direction="rtl",
        title="דוגמת זהות סינתטית",
        labels={
            "name": "שם",
            "document_id": "מספר מסמך",
            "date_of_birth": "תאריך לידה",
            "expiry": "בתוקף עד",
        },
        fields={
            "name": "ישראל ישראלי",
            "document_id": "246813579",
            "date_of_birth": "1988-11-03",
            "expiry": "2031-08-22",
        },
    ),
    SyntheticIdentity(
        language="ara",
        language_name="Arabic",
        direction="rtl",
        title="عينة هوية اصطناعية",
        labels={
            "name": "الاسم",
            "document_id": "رقم الوثيقة",
            "date_of_birth": "تاريخ الميلاد",
            "expiry": "تاريخ الانتهاء",
        },
        fields={
            "name": "ليلى حسن",
            "document_id": "975318642",
            "date_of_birth": "1992-07-16",
            "expiry": "2033-02-14",
        },
    ),
)


FONT_CANDIDATES = {
    "eng": (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ),
    "heb": (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ),
    "ara": (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ),
}


def _font(language: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONT_CANDIDATES[language]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    raise FileNotFoundError(
        f"No Unicode font found for {language}. Install Arial, Noto Sans, or DejaVu Sans."
    )


def _text_options(identity: SyntheticIdentity) -> dict[str, str]:
    if identity.direction == "rtl" and features.check_feature("raqm"):
        return {"direction": "rtl", "language": identity.language[:2]}
    return {}


def _render_card(identity: SyntheticIdentity) -> tuple[Image.Image, dict[str, Image.Image]]:
    card = Image.new("RGB", (1000, 620), "#f7f4ec")
    draw = ImageDraw.Draw(card)
    title_font = _font(identity.language, 42)
    label_font = _font(identity.language, 23)
    value_font = _font(identity.language, 35)
    options = _text_options(identity)

    draw.rounded_rectangle((25, 25, 975, 595), radius=26, outline="#1f4c5c", width=5)
    draw.rectangle((25, 25, 975, 115), fill="#1f4c5c")
    title_position = (930, 70) if identity.direction == "rtl" else (70, 70)
    title_anchor = "rm" if identity.direction == "rtl" else "lm"
    draw.text(
        title_position,
        identity.title,
        font=title_font,
        fill="white",
        anchor=title_anchor,
        **options,
    )
    draw.ellipse((70, 165, 280, 375), fill="#d8e4e8", outline="#1f4c5c", width=4)
    draw.ellipse((138, 210, 212, 284), fill="#1f4c5c")
    draw.arc((105, 260, 245, 390), 180, 360, fill="#1f4c5c", width=30)
    draw.text((175, 455), "SYNTHETIC", font=_font("eng", 24), fill="#9b2c2c", anchor="mm")
    draw.text((175, 492), "NOT VALID", font=_font("eng", 24), fill="#9b2c2c", anchor="mm")

    field_images: dict[str, Image.Image] = {}
    for index, (field_name, expected) in enumerate(identity.fields.items()):
        y = 175 + index * 95
        if identity.direction == "rtl":
            label_x, value_x, anchor = 900, 900, "ra"
        else:
            label_x, value_x, anchor = 355, 355, "la"
        draw.text(
            (label_x, y),
            identity.labels[field_name],
            font=label_font,
            fill="#56717a",
            anchor=anchor,
            **options,
        )
        draw.text(
            (value_x, y + 36),
            expected,
            font=value_font,
            fill="#111827",
            anchor=anchor,
            **options,
        )

        field_image = Image.new("RGB", (700, 92), "white")
        field_draw = ImageDraw.Draw(field_image)
        field_position = (660, 46) if identity.direction == "rtl" else (40, 46)
        field_anchor = "rm" if identity.direction == "rtl" else "lm"
        field_draw.text(
            field_position,
            expected,
            font=value_font,
            fill="black",
            anchor=field_anchor,
            **options,
        )
        field_images[field_name] = field_image

    draw.text(
        (930, 565),
        "TEST DATA ONLY / NO REAL PERSON",
        font=_font("eng", 18),
        fill="#9b2c2c",
        anchor="ra",
    )
    return card, field_images


def generate_dataset(output_dir: Path, manifest_path: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    for identity_index, identity in enumerate(IDENTITIES):
        card, field_images = _render_card(identity)
        for degradation_index, (degradation_name, transform) in enumerate(
            DEGRADATIONS.items()
        ):
            sample_id = f"{identity.language}-{degradation_name}"
            sample_dir = output_dir / sample_id
            sample_dir.mkdir(parents=True, exist_ok=True)
            seed = identity_index * 100 + degradation_index
            card_path = sample_dir / "card.png"
            transform(card, seed).save(card_path)

            fields: dict[str, dict[str, str]] = {}
            for field_index, (field_name, expected) in enumerate(identity.fields.items()):
                field_path = sample_dir / f"{field_name}.png"
                transform(field_images[field_name], seed + field_index + 1).save(field_path)
                fields[field_name] = {
                    "expected": expected,
                    "image": field_path.relative_to(manifest_path.parent).as_posix(),
                }

            records.append(
                {
                    "sample_id": sample_id,
                    "language": identity.language,
                    "language_name": identity.language_name,
                    "direction": identity.direction,
                    "degradation": degradation_name,
                    "card_image": card_path.relative_to(manifest_path.parent).as_posix(),
                    "fields": fields,
                }
            )

    manifest = {
        "license": "CC0-1.0",
        "provenance": (
            "Programmatically generated synthetic identities; no real people or documents."
        ),
        "sample_count": len(records),
        "samples": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
