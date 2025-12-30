from __future__ import annotations

import sys

from .capture import VirtualDesktopGeometry


def _to_int_xy(point):
    x, y = point
    return int(x), int(y)


def click(point, geometry: VirtualDesktopGeometry | None = None):
    x, y = _to_int_xy(point)

    if sys.platform == "win32":
        try:
            _click_windows_virtual_desktop(x, y, geometry)
            return
        except Exception:
            pass

    import pyautogui

    pyautogui.click((x, y))


def _click_windows_virtual_desktop(x: int, y: int, geometry: VirtualDesktopGeometry | None) -> None:
    import ctypes

    user32 = ctypes.windll.user32

    # SendInput with MOUSEEVENTF_VIRTUALDESK maps absolute coordinates using the
    # system's virtual screen metrics. Therefore, we always normalize against
    # system metrics, and (optionally) map coordinates from the capture backend
    # geometry into system space when they differ.
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79
    sys_left = int(user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
    sys_top = int(user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
    sys_width = int(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
    sys_height = int(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))

    if sys_width <= 1 or sys_height <= 1:
        import pyautogui

        pyautogui.click((x, y))
        return

    # Map capture-space coordinates into system-space if capture geometry is provided.
    # This fixes mixed-DPI setups where the screenshot backend reports a different
    # virtual desktop size than the system metrics used by SendInput.
    click_x = int(x)
    click_y = int(y)
    if geometry is not None:
        cap_left = int(geometry.left)
        cap_top = int(geometry.top)
        cap_width = int(geometry.width)
        cap_height = int(geometry.height)

        if cap_width > 1 and cap_height > 1:
            if (
                cap_left != sys_left
                or cap_top != sys_top
                or cap_width != sys_width
                or cap_height != sys_height
            ):
                # Scale relative position from capture-space into system-space.
                rx = (click_x - cap_left) / (cap_width - 1)
                ry = (click_y - cap_top) / (cap_height - 1)
                click_x = int(round(sys_left + rx * (sys_width - 1)))
                click_y = int(round(sys_top + ry * (sys_height - 1)))

    click_x = max(sys_left, min(sys_left + sys_width - 1, int(click_x)))
    click_y = max(sys_top, min(sys_top + sys_height - 1, int(click_y)))

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def _get_cursor_pos() -> tuple[int, int]:
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return int(pt.x), int(pt.y)

    def _get_physical_cursor_pos() -> tuple[int, int] | None:
        try:
            if hasattr(user32, "GetPhysicalCursorPos"):
                user32.GetPhysicalCursorPos.argtypes = [ctypes.POINTER(POINT)]
                user32.GetPhysicalCursorPos.restype = ctypes.c_bool
                pt = POINT()
                if bool(user32.GetPhysicalCursorPos(ctypes.byref(pt))):
                    return int(pt.x), int(pt.y)
        except Exception:
            return None
        return None

    def _set_cursor(px: int, py: int) -> bool:
        # Prefer SetPhysicalCursorPos when available.
        try:
            if hasattr(user32, "SetPhysicalCursorPos"):
                user32.SetPhysicalCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
                user32.SetPhysicalCursorPos.restype = ctypes.c_bool
                if bool(user32.SetPhysicalCursorPos(int(px), int(py))):
                    return True
        except Exception:
            pass

        try:
            user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
            user32.SetCursorPos.restype = ctypes.c_bool
            return bool(user32.SetCursorPos(int(px), int(py)))
        except Exception:
            return False

    def _maybe_empirical_compensate(target_x: int, target_y: int, actual_x: int, actual_y: int) -> tuple[int, int, str] | None:
        # Empirical compensation for DPI-virtualized cursor movement.
        # We assume a mapping like: actual = origin + (requested-origin) * factor.
        # If we requested target and got actual, estimate factor and invert it.
        if abs(actual_x - target_x) <= 2 and abs(actual_y - target_y) <= 2:
            return None

        ox, oy = sys_left, sys_top
        dx_t = float(target_x - ox)
        dy_t = float(target_y - oy)
        dx_a = float(actual_x - ox)
        dy_a = float(actual_y - oy)

        # Avoid division by zero.
        if abs(dx_a) < 1.0 or abs(dy_a) < 1.0:
            return None

        ratio_x = dx_t / dx_a
        ratio_y = dy_t / dy_a

        # Clamp to sane range to avoid wild jumps.
        ratio_x = max(0.5, min(2.0, ratio_x))
        ratio_y = max(0.5, min(2.0, ratio_y))

        req_x = int(round(ox + dx_t * ratio_x))
        req_y = int(round(oy + dy_t * ratio_y))

        # Keep within virtual desktop bounds.
        req_x = max(sys_left, min(sys_left + sys_width - 1, req_x))
        req_y = max(sys_top, min(sys_top + sys_height - 1, req_y))

        details = f"emp_fix ratio=({ratio_x:.3f},{ratio_y:.3f}) requested=({req_x},{req_y})"
        return req_x, req_y, details

    # Prefer moving cursor via SetPhysicalCursorPos/SetCursorPos.
    kernel32 = ctypes.windll.kernel32
    moved = _set_cursor(click_x, click_y)
    try:
        kernel32.Sleep(10)
    except Exception:
        pass
    after1_x, after1_y = _get_cursor_pos()
    phys1 = _get_physical_cursor_pos()

    fix_details = None
    after2_x, after2_y = after1_x, after1_y
    phys2 = phys1
    compensated = False
    correction = _maybe_empirical_compensate(click_x, click_y, after1_x, after1_y)
    if correction is not None:
        req_x, req_y, fix_details = correction
        moved = _set_cursor(req_x, req_y) or moved
        compensated = True
        try:
            kernel32.Sleep(10)
        except Exception:
            pass
        after2_x, after2_y = _get_cursor_pos()
        phys2 = _get_physical_cursor_pos()

    # Fallback: move using SendInput absolute mapping.
    nx = int(round((click_x - sys_left) * 65535 / (sys_width - 1)))
    ny = int(round((click_y - sys_top) * 65535 / (sys_height - 1)))

    INPUT_MOUSE = 0
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_VIRTUALDESK = 0x4000

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT)]

        _anonymous_ = ("i",)
        _fields_ = [("type", ctypes.c_ulong), ("i", _I)]

    def _send(flags):
        inp = INPUT(
            type=INPUT_MOUSE,
            mi=MOUSEINPUT(dx=nx, dy=ny, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=None),
        )
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    if not moved:
        _send(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK)

    _send(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK)
    _send(MOUSEEVENTF_LEFTUP | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK)
