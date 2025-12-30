from __future__ import annotations

import os
import sys


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource.

    Prioritizes the folder next to the executable/script.
    Falls back to _MEIPASS if present.
    """

    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
        path = os.path.join(base_path, relative_path)
        if os.path.exists(path):
            return path

        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)

        return path

    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def list_target_images(targets_dir: str) -> list[tuple[str, str]]:
    image_paths: list[tuple[str, str]] = []
    for filename in os.listdir(targets_dir):
        if filename.lower().endswith(".png"):
            full_path = os.path.join(targets_dir, filename)
            image_paths.append((filename, full_path))
    return image_paths
