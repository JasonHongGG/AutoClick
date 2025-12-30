"""Auto Clicker package.

Keeps the single-file entrypoint (auto_clicker.py) small while allowing
clean, testable modules.
"""

def main(*args, **kwargs):
	# Lazy import so callers can set Windows DPI awareness before GUI libs load.
	from .app import main as _main

	return _main(*args, **kwargs)
