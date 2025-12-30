# Auto Clicker

This script automatically clicks the "Allow" button when it appears on the screen.

## How to Run
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Run the script:
   ```powershell
   python auto_clicker.py
   ```

## Troubleshooting

- **Multi-monitor / DPI scaling**: This tool captures the full *virtual desktop* and enables DPI-awareness on Windows, so it should work across multiple monitors (including monitors placed left/top of the primary).
- **Still not detecting / clicking correctly**: Try setting Windows display scaling to **100%** temporarily, and make sure the app you're clicking is not running as **Administrator** while the clicker is not (mixed privilege windows can block screenshots/clicks).

### Matching Tuning (Advanced)
- `AUTO_CLICKER_CONFIDENCE` (default `0.9`) 
- `AUTO_CLICKER_GRAYSCALE` (default `1`)
- `AUTO_CLICKER_SCALES` (default `1.0`)

### Click Logging (Debug)
If you want to verify *where* the tool is about to click (especially useful for multi-monitor / mixed-DPI setups), you can enable click logging. When enabled, the app saves a screenshot **right before each click** into a `logs/` folder and draws a red crosshair at the intended click position.

- `AUTO_CLICKER_LOG_CLICKS` (default `0`)
- `AUTO_CLICKER_LOG_DIR` (default `logs`)


## How to Build the Executable

The project includes a `auto_clicker.spec` file that handles the inclusion of the `targets` folder automatically.

1.  **Activate your virtual environment** (if using one).
2.  **Install the requirements**:
    ```powershell
    pip install -r requirements.txt
    ```
3.  **Run the build command**:
    ```powershell
    pyinstaller auto_clicker.spec
    ```

- This will create a `dist` folder containing `auto_clicker.exe`.
- All images in the `targets` folder will be bundled into the executable.

