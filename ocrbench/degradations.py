from __future__ import annotations

from collections.abc import Callable

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def clean(image: Image.Image, _: int) -> Image.Image:
    return image.copy()


def blur(image: Image.Image, _: int) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(radius=1.8))


def rotate(image: Image.Image, _: int) -> Image.Image:
    return image.rotate(4.0, resample=Image.Resampling.BICUBIC, expand=False, fillcolor="white")


def low_light(image: Image.Image, _: int) -> Image.Image:
    dimmed = ImageEnhance.Brightness(image).enhance(0.42)
    return ImageEnhance.Contrast(dimmed).enhance(0.78)


def noise(image: Image.Image, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    pixels = np.asarray(image.convert("RGB"), dtype=np.int16)
    perturbation = rng.normal(0, 18, pixels.shape)
    noisy = np.clip(pixels + perturbation, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy, mode="RGB")


DEGRADATIONS: dict[str, Callable[[Image.Image, int], Image.Image]] = {
    "clean": clean,
    "blur": blur,
    "rotation": rotate,
    "low_light": low_light,
    "noise": noise,
}
