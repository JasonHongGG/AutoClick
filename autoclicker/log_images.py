from __future__ import annotations

import os
import time
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .capture import VirtualDesktopGeometry


@dataclass(frozen=True)
class ClickLogInfo:
    target_name: str
    click_point_screen: tuple[int, int]
    found_scale: float | None


def _safe_filename_part(s: str) -> str:
    keep = []
    for ch in s:
        if ch.isalnum() or ch in {"-", "_", "."}:
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep)[:80] or "target"


def save_annotated_click_screenshot(
    *,
    screenshot_img: Image.Image,
    geometry: VirtualDesktopGeometry,
    info: ClickLogInfo,
    log_dir: str,
) -> str:
    os.makedirs(log_dir, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%S")
    ms = int((time.time() % 1) * 1000)

    target = _safe_filename_part(info.target_name)
    scale_part = ""
    if info.found_scale is not None and info.found_scale != 1.0:
        scale_part = f"_s{info.found_scale:.3f}".replace(".", "p")

    filename = f"{ts}-{ms:03d}_{target}{scale_part}.png"
    out_path = os.path.abspath(os.path.join(log_dir, filename))

    img = screenshot_img.copy()
    draw = ImageDraw.Draw(img)

    screen_x, screen_y = info.click_point_screen
    img_x = int(screen_x - geometry.left)
    img_y = int(screen_y - geometry.top)

    w, h = img.size

    # Draw crosshair if inside screenshot bounds; otherwise mark as out-of-bounds.
    if 0 <= img_x < w and 0 <= img_y < h:
        r = 18
        draw.ellipse((img_x - r, img_y - r, img_x + r, img_y + r), outline=(255, 0, 0), width=3)
        draw.line((img_x - r * 2, img_y, img_x + r * 2, img_y), fill=(255, 0, 0), width=3)
        draw.line((img_x, img_y - r * 2, img_x, img_y + r * 2), fill=(255, 0, 0), width=3)
    else:
        # Big border as a strong signal something is mismatched.
        draw.rectangle((2, 2, w - 3, h - 3), outline=(255, 0, 0), width=6)

    label = (
        f"target={info.target_name}  "
        f"screen=({screen_x},{screen_y})  "
        f"img=({img_x},{img_y})  "
        f"vd_left_top=({geometry.left},{geometry.top})"
    )
    if info.found_scale is not None:
        label += f"  scale={info.found_scale}"
    if not (0 <= img_x < w and 0 <= img_y < h):
        label += "  OUT_OF_BOUNDS"

    # Simple readable label box.
    pad = 6
    text_pos = (10, 10)
    # Estimate text background size (ImageDraw without font gives decent fallback)
    bbox = draw.textbbox(text_pos, label)
    draw.rectangle(
        (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
        fill=(0, 0, 0),
    )
    draw.text(text_pos, label, fill=(255, 255, 255))

    img.save(out_path)
    return out_path
