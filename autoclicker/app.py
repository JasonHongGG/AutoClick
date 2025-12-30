from __future__ import annotations

import os
import sys
import time
import traceback

import pyscreeze

from .config import load_config
from .capture import VirtualDesktopCapture
from .click import click
from .match import MultiScaleTemplateMatcher
from .paths import list_target_images, resource_path


class AutoClickerApp:
    def __init__(self):
        self.config = load_config()
        self.capture = VirtualDesktopCapture()
        self.matcher = MultiScaleTemplateMatcher(
            confidence=self.config.confidence,
            grayscale=self.config.grayscale,
            scales=self.config.scales,
        )

    def run(self) -> None:
        targets_dir = resource_path("targets")
        print(f"Looking for images in: {os.path.abspath(targets_dir)}")

        if not os.path.exists(targets_dir):
            print(f"Error: Directory '{targets_dir}' not found.")
            return

        image_paths = list_target_images(targets_dir)
        if not image_paths:
            print("No .png images found in the 'targets' directory.")
            return

        print(f"Found {len(image_paths)} images: {[name for name, _ in image_paths]}")
        print("Started looking for buttons... Press Ctrl+C to stop.")

        logged_scan_error = False
        logged_not_found_hint = False

        while True:
            capture = self.capture.screenshot()
            screenshot_img = capture.image
            geom = capture.geometry
            origin_x, origin_y = geom.left, geom.top

            for img_name, img_path in image_paths:
                try:
                    found, found_scale = self.matcher.locate_center(img_path, screenshot_img)
                    if not found:
                        continue

                    x, y = (found.x, found.y) if hasattr(found, "x") else (found[0], found[1])
                    click_point = (int(x + origin_x), int(y + origin_y))

                    if found_scale and found_scale != 1.0:
                        print(f"Button '{img_name}' found at {click_point} (scale={found_scale}). Clicking...")
                    else:
                        print(f"Button '{img_name}' found at {click_point}. Clicking...")

                    click(click_point, geometry=geom)
                    time.sleep(2)
                    break

                except pyscreeze.ImageNotFoundException as not_found:
                    if not logged_not_found_hint:
                        logged_not_found_hint = True
                        print(
                            "Image not found (this is normal). "
                            "If it never finds anything, your target PNG may not match current DPI/scaling. "
                            "You can tune matching via env vars: "
                            "AUTO_CLICKER_CONFIDENCE (e.g. 0.58) and AUTO_CLICKER_GRAYSCALE (0/1). "
                            f"Details: {not_found}"
                        )
                    continue

                except Exception as inner_e:
                    if not logged_scan_error:
                        logged_scan_error = True
                        print(f"Scan error (first occurrence): {type(inner_e).__name__}: {inner_e}")
                    continue

            time.sleep(0.5)


def main() -> None:
    try:
        app = AutoClickerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception:
        print("\nCRITICAL ERROR OCCURRED:")
        traceback.print_exc()
    finally:
        try:
            input("\nPress Enter to exit...")
        except EOFError:
            pass
