#!/usr/bin/env python3
"""
Creates a "Ride On Clicker" shortcut on your Desktop.
Double-click it to start (opens a Terminal window). Close the terminal to stop.

Usage:
    python3 create_desktop_app.py
"""

import shutil
import stat
from pathlib import Path

PYTHON = shutil.which("python3") or "/usr/bin/python3"
INSTALL_DIR = Path.home() / ".zwift-rideon"
SCRIPT = "zwift_rideon_clicker.py"
APP_NAME = "Ride On Clicker"
DESKTOP = Path.home() / "Desktop"


def create_command_file():
    """Create a .command file — macOS opens these in Terminal when double-clicked."""
    print(f"\n  Setting up Ride On Clicker...\n")

    # 1. Copy script to ~/.zwift-rideon/
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent / SCRIPT
    dest = INSTALL_DIR / SCRIPT
    if source.exists():
        shutil.copy2(source, dest)
        print(f"  ✅ Script installed to {dest}")
    else:
        print(f"  ❌ {SCRIPT} not found next to this file.")
        print(f"     Put both files in the same folder and try again.")
        return

    # 2. Create a .command file on Desktop
    #    macOS natively opens .command files in Terminal.app
    cmd_file = DESKTOP / f"{APP_NAME}.command"
    cmd_file.write_text(f"""#!/bin/bash
clear
echo ""
echo "  ========================================"
echo "  🤙 Ride On Clicker"
echo "  ========================================"
echo "  Close this window to stop."
echo ""
cd "{INSTALL_DIR}"
"{PYTHON}" "{dest}"
""")

    # Make it executable
    cmd_file.chmod(cmd_file.stat().st_mode | stat.S_IEXEC)

    print(f"  ✅ Shortcut created: {cmd_file}")
    print(f"\n  {'='*50}")
    print(f"  Done! Double-click '{APP_NAME}' on your Desktop.")
    print(f"  It opens a Terminal window — close it to stop.")
    print(f"  Log file: {INSTALL_DIR / 'rideon.log'}")
    print(f"  {'='*50}")
    print(f"\n  ⚠️  First launch: grant permissions when macOS asks:")
    print(f"     System Settings → Privacy & Security →")
    print(f"       • Screen Recording → enable Terminal")
    print(f"       • Accessibility  → enable Terminal\n")


if __name__ == "__main__":
    create_command_file()
