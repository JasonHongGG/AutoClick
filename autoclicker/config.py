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
    scan_interval: float
    click_delay: float
    log_clicks: bool
    log_dir: str


def load_config() -> AppConfig:
    # Load .env once (no-op if missing)
    load_dotenv()

    confidence = max(0.0, min(1.0, _env_float("AUTO_CLICKER_CONFIDENCE", 0.9)))
    grayscale = _env_bool("AUTO_CLICKER_GRAYSCALE", True)
    scales = _env_scales("AUTO_CLICKER_SCALES", "1.0")
    # Throttle scanning to reduce CPU usage.
    scan_interval = _env_float("AUTO_CLICKER_SCAN_INTERVAL", 1.0)
    if scan_interval < 0:
        scan_interval = 1.0

    click_delay = _env_float("AUTO_CLICKER_CLICK_DELAY", 2.0)
    if click_delay < 0:
        click_delay = 2.0
    log_clicks = _env_bool("AUTO_CLICKER_LOG_CLICKS", False)
    log_dir = os.getenv("AUTO_CLICKER_LOG_DIR", "logs")
    if log_dir is None or log_dir.strip() == "":
        log_dir = "logs"

    return AppConfig(
        confidence=confidence,
        grayscale=grayscale,
        scales=scales,
        scan_interval=scan_interval,
        click_delay=click_delay,
        log_clicks=log_clicks,
        log_dir=log_dir,
    )
