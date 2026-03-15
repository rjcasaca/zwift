#!/usr/bin/env python3
"""
Creates a "Ride On Clicker" shortcut on your Desktop.
Double-click it to start (opens a Terminal window). Close the terminal to stop.

Usage:
    Put these 3 files in the same folder:
      - create_desktop_app.py (this file)
      - zwift_rideon_clicker.py
      - rideon_template.png
    Then run: python3 create_desktop_app.py
"""

import shutil
import stat
from pathlib import Path

PYTHON = shutil.which("python3") or "/usr/bin/python3"
INSTALL_DIR = Path.home() / ".zwift-rideon"
SCRIPT = "zwift_rideon_clicker.py"
TEMPLATE = "rideon_template.png"
APP_NAME = "Ride On Clicker"
DESKTOP = Path.home() / "Desktop"


def create_command_file():
    print(f"\n  Setting up Ride On Clicker...\n")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    source_dir = Path(__file__).parent

    # Copy script
    script_src = source_dir / SCRIPT
    script_dst = INSTALL_DIR / SCRIPT
    if script_src.exists():
        shutil.copy2(script_src, script_dst)
        print(f"  ✅ Script → {script_dst}")
    else:
        print(f"  ❌ {SCRIPT} not found. Put it next to this file.")
        return

    # Copy template
    tmpl_src = source_dir / TEMPLATE
    tmpl_dst = INSTALL_DIR / TEMPLATE
    if tmpl_src.exists():
        shutil.copy2(tmpl_src, tmpl_dst)
        print(f"  ✅ Template → {tmpl_dst}")
    else:
        print(f"  ❌ {TEMPLATE} not found. Put it next to this file.")
        return

    # Create .command shortcut on Desktop
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
"{PYTHON}" "{script_dst}"
""")
    cmd_file.chmod(cmd_file.stat().st_mode | stat.S_IEXEC)

    print(f"  ✅ Shortcut → {cmd_file}")
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
