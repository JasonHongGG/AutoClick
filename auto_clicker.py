"""Backward-compatible entrypoint.

Keep this file for:
- Running `python auto_clicker.py`
- Existing `auto_clicker.spec` PyInstaller build

Implementation lives in the `autoclicker` package.
"""

from autoclicker.dpi import set_windows_dpi_awareness_early


set_windows_dpi_awareness_early()


from autoclicker.app import main


if __name__ == "__main__":
    # CLI args are currently ignored; keep behavior compatible with prior versions.
    main()
