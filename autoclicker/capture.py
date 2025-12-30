from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from PIL import Image


def get_virtual_screen_bbox_windows() -> tuple[tuple[int, int, int, int], tuple[int, int]]:
    import ctypes

    user32 = ctypes.windll.user32
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    left = int(user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
    top = int(user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
    width = int(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
    height = int(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))

    return (left, top, left + width, top + height), (left, top)


@dataclass(frozen=True)
class VirtualDesktopGeometry:
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True)
class CaptureResult:
    image: Image.Image
    geometry: VirtualDesktopGeometry


class VirtualDesktopCapture:
    """Captures the full virtual desktop and returns (PIL.Image, origin_xy)."""

    def screenshot(self) -> CaptureResult:
        if sys.platform == "win32":
            # Prefer mss on Windows for multi-monitor reliability.
            try:
                import mss

                with mss.mss() as sct:
                    mon = sct.monitors[0]  # virtual screen
                    left = int(mon["left"])
                    top = int(mon["top"])
                    width = int(mon["width"])
                    height = int(mon["height"])
                    grabbed = sct.grab(mon)

                    img = Image.frombytes(
                        "RGB",
                        (grabbed.width, grabbed.height),
                        grabbed.rgb,
                    )
                    geom = VirtualDesktopGeometry(left=left, top=top, width=width, height=height)
                    return CaptureResult(image=img, geometry=geom)
            except Exception:
                pass

            # Fallback to Pillow ImageGrab
            from PIL import ImageGrab

            bbox, origin = get_virtual_screen_bbox_windows()
            img = ImageGrab.grab(bbox=bbox)
            left, top, right, bottom = bbox
            geom = VirtualDesktopGeometry(left=int(left), top=int(top), width=int(right - left), height=int(bottom - top))
            return CaptureResult(image=img, geometry=geom)

        import pyautogui

        img = pyautogui.screenshot()
        w, h = img.size
        geom = VirtualDesktopGeometry(left=0, top=0, width=int(w), height=int(h))
        return CaptureResult(image=img, geometry=geom)
