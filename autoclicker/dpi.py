from __future__ import annotations

import sys


def set_windows_dpi_awareness_early() -> None:
    """Best-effort Per-Monitor-V2 DPI awareness.

    Must be called BEFORE importing screenshot / GUI libs.
    """

    if sys.platform != "win32":
        return

    try:
        import ctypes

        # Windows 10+: Per-monitor v2
        DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        return
    except Exception:
        pass

    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        import ctypes

        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
