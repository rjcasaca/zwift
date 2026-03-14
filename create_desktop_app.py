#!/usr/bin/env python3
"""
Creates a "Ride On Clicker" app on your Desktop.
Double-click it to start, close the terminal window to stop.

Usage:
    python create_desktop_app.py
"""

import shutil
import stat
from pathlib import Path

PYTHON = shutil.which("python3") or "/usr/bin/python3"
INSTALL_DIR = Path.home() / ".zwift-rideon"
SCRIPT = "zwift_rideon_clicker.py"
APP_NAME = "Ride On Clicker"
DESKTOP = Path.home() / "Desktop"
APP_PATH = DESKTOP / f"{APP_NAME}.app"


def create_app():
    print(f"\n  Setting up Ride On Clicker...\n")

    # 1. Copy script to ~/.zwift-rideon/
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent / SCRIPT
    dest = INSTALL_DIR / SCRIPT
    if source.exists():
        shutil.copy2(source, dest)
        print(f"  ✅ Script installed to {dest}")
    else:
        print(f"  ❌ {SCRIPT} not found next to this file. Put both files in the same folder.")
        return

    # 2. Create .app bundle
    if APP_PATH.exists():
        shutil.rmtree(APP_PATH)

    macos_dir = APP_PATH / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)

    # The launcher shell script
    launcher = macos_dir / "launcher"
    launcher.write_text(f"""#!/bin/bash
cd "{INSTALL_DIR}"
"{PYTHON}" "{dest}"
""")
    launcher.chmod(launcher.stat().st_mode | stat.S_IEXEC)

    # Info.plist
    plist = APP_PATH / "Contents" / "Info.plist"
    plist.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.rideon.zwiftclicker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
""")

    # 3. Create icon (orange circle with thumbs-up emoji via iconutil)
    _create_icon()

    print(f"  ✅ App created at: {APP_PATH}")
    print(f"\n  {'='*50}")
    print(f"  Done! You now have '{APP_NAME}' on your Desktop.")
    print(f"  Double-click it to start. Close the terminal to stop.")
    print(f"  Log file: {INSTALL_DIR / 'rideon.log'}")
    print(f"  {'='*50}")
    print(f"\n  ⚠️  First launch: macOS will ask about permissions.")
    print(f"     If it says 'unidentified developer', right-click → Open.")
    print(f"     Then grant Screen Recording + Accessibility to Terminal.\n")


def _create_icon():
    """Try to create a simple .icns icon. Fails gracefully."""
    try:
        import subprocess, tempfile

        # Create a 512x512 orange circle PNG using sips/python
        icon_script = f"""
import struct, zlib, os

def create_png(path, size=512):
    # Simple orange filled square as icon
    width = height = size
    raw = []
    for y in range(height):
        raw.append(b'\\x00')  # filter byte
        for x in range(width):
            # Circle mask
            dx, dy = x - width//2, y - height//2
            if dx*dx + dy*dy < (width//2 - 10)**2:
                raw.append(b'\\xf0\\x8c\\x28\\xff')  # orange RGBA
            else:
                raw.append(b'\\x00\\x00\\x00\\x00')  # transparent
    
    raw_data = b''.join(raw)
    
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    with open(path, 'wb') as f:
        f.write(b'\\x89PNG\\r\\n\\x1a\\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(raw_data)))
        f.write(chunk(b'IEND', b''))

create_png('{INSTALL_DIR}/icon_512.png', 512)
create_png('{INSTALL_DIR}/icon_256.png', 256)
"""
        exec(icon_script)
        
        # Create iconset and convert
        iconset = INSTALL_DIR / "icon.iconset"
        iconset.mkdir(exist_ok=True)
        shutil.copy(INSTALL_DIR / "icon_512.png", iconset / "icon_256x256@2x.png")
        shutil.copy(INSTALL_DIR / "icon_256.png", iconset / "icon_256x256.png")
        shutil.copy(INSTALL_DIR / "icon_256.png", iconset / "icon_128x128@2x.png")

        # This will only work on macOS
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(APP_PATH / "Contents" / "Resources" / "AppIcon.icns")],
            capture_output=True,
        )
        if result.returncode == 0:
            print(f"  ✅ App icon created")
        
        # Cleanup
        shutil.rmtree(iconset, ignore_errors=True)
        (INSTALL_DIR / "icon_512.png").unlink(missing_ok=True)
        (INSTALL_DIR / "icon_256.png").unlink(missing_ok=True)

    except Exception:
        pass  # Icon is cosmetic, skip if anything fails


if __name__ == "__main__":
    create_app()
