from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw not in {"0", "false", "False", "no", "NO"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_scales(name: str, default_csv: str) -> list[float]:
    raw = os.getenv(name, default_csv)
    parts = [p.strip() for p in raw.split(",") if p.strip()]

    scales: list[float] = []
    for p in parts:
        try:
            scales.append(float(p))
        except ValueError:
            continue

    # de-dup while preserving order
    seen: set[float] = set()
    result: list[float] = []
    for s in scales:
        if s <= 0:
            continue
        if s in seen:
            continue
        seen.add(s)
        result.append(s)

    return result or [1.0]


@dataclass(frozen=True)
class AppConfig:
    confidence: float
    grayscale: bool
    scales: list[float]


def load_config() -> AppConfig:
    # Load .env once (no-op if missing)
    load_dotenv()

    confidence = max(0.0, min(1.0, _env_float("AUTO_CLICKER_CONFIDENCE", 0.9)))
    grayscale = _env_bool("AUTO_CLICKER_GRAYSCALE", True)
    scales = _env_scales("AUTO_CLICKER_SCALES", "1.0")

    return AppConfig(
        confidence=confidence,
        grayscale=grayscale,
        scales=scales,
    )
