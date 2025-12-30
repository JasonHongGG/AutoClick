from __future__ import annotations

from PIL import Image
import pyscreeze


def locate_center(needle, haystack_img, confidence: float, grayscale: bool):
    """Return center (x, y) in haystack image coordinates or None."""

    if hasattr(pyscreeze, "locateCenter"):
        return pyscreeze.locateCenter(
            needle,
            haystack_img,
            confidence=confidence,
            grayscale=grayscale,
        )

    if not hasattr(pyscreeze, "locate"):
        raise AttributeError("pyscreeze has no locate/locateCenter")

    try:
        box = pyscreeze.locate(
            needle,
            haystack_img,
            confidence=confidence,
            grayscale=grayscale,
        )
    except TypeError:
        box = pyscreeze.locate(
            needle,
            haystack_img,
            grayscale=grayscale,
        )

    if not box:
        return None

    if hasattr(box, "left") and hasattr(box, "top") and hasattr(box, "width") and hasattr(box, "height"):
        left, top, width, height = box.left, box.top, box.width, box.height
    else:
        left, top, width, height = box

    return (left + (width // 2), top + (height // 2))


def resize_needle(needle_img: Image.Image, scale: float) -> Image.Image:
    if scale == 1.0:
        return needle_img

    width, height = needle_img.size
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))

    resample = getattr(Image, "Resampling", Image).LANCZOS
    return needle_img.resize((new_width, new_height), resample=resample)


class MultiScaleTemplateMatcher:
    def __init__(self, confidence: float, grayscale: bool, scales: list[float]):
        self.confidence = confidence
        self.grayscale = grayscale
        self.scales = scales
        self._cache: dict[object, object] = {}

    def locate_center(self, needle_path: str, haystack_img):
        if needle_path not in self._cache:
            self._cache[needle_path] = Image.open(needle_path)

        base = self._cache[needle_path]

        for scale in self.scales:
            key = (needle_path, scale)
            if key not in self._cache:
                self._cache[key] = resize_needle(base, scale)

            needle_img = self._cache[key]
            found = locate_center(needle_img, haystack_img, confidence=self.confidence, grayscale=self.grayscale)
            if found:
                return found, scale

        return None, None
