#!/usr/bin/env python3
"""
Zwift Ride On Auto-Clicker for macOS
=====================================
Scans the screen for the orange "Ride On" button and clicks it automatically.

Requirements:
    pip install pyautogui pillow numpy mss

macOS Setup:
    System Settings → Privacy & Security → Screen Recording → enable Terminal
    System Settings → Privacy & Security → Accessibility → enable Terminal

Usage:
    python zwift_rideon_clicker.py
    Press Ctrl+C to stop.
"""

import time
import sys
import logging
from pathlib import Path

import numpy as np
import pyautogui
import mss

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Zwift Ride On orange color range (RGB)
ORANGE_R_MIN, ORANGE_R_MAX = 220, 255
ORANGE_G_MIN, ORANGE_G_MAX = 100, 175
ORANGE_B_MIN, ORANGE_B_MAX = 0, 70

# Minimum cluster of orange pixels to count as a button
MIN_PIXEL_CLUSTER = 150

# How often to scan (seconds)
SCAN_INTERVAL = 0.5

# Cooldown after a click (seconds)
CLICK_COOLDOWN = 3.0

# Restrict scanning to a screen region? (reduces false positives)
USE_REGION = False
SCAN_REGION = (800, 600, 640, 300)  # (left, top, width, height)

# Retina scale: 2 for built-in Retina, 1 for external non-Retina
RETINA_SCALE = 2

# Log file
LOG_DIR = Path.home() / ".zwift-rideon"
LOG_FILE = LOG_DIR / "rideon.log"

# Fail-safe: move mouse to top-left corner to abort
pyautogui.FAILSAFE = True

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("rideon")
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("  %(message)s"))
    logger.addHandler(console)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)

    return logger

# ---------------------------------------------------------------------------
# SCREEN SCANNING
# ---------------------------------------------------------------------------

def find_orange_button(img):
    """Find a cluster of orange pixels. Returns (x, y) or None."""
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    mask = (
        (r >= ORANGE_R_MIN) & (r <= ORANGE_R_MAX) &
        (g >= ORANGE_G_MIN) & (g <= ORANGE_G_MAX) &
        (b >= ORANGE_B_MIN) & (b <= ORANGE_B_MAX)
    )
    coords = np.where(mask)
    if len(coords[0]) < MIN_PIXEL_CLUSTER:
        return None
    return (int(np.mean(coords[1])), int(np.mean(coords[0])))

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    log = setup_logging()

    log.info("=" * 50)
    log.info("  Zwift Ride On Auto-Clicker")
    log.info("=" * 50)
    log.info(f"  Scan interval:  {SCAN_INTERVAL}s")
    log.info(f"  Click cooldown: {CLICK_COOLDOWN}s")
    log.info(f"  Retina scale:   {RETINA_SCALE}x")
    log.info(f"  Region lock:    {'ON' if USE_REGION else 'OFF (full screen)'}")
    log.info(f"  Log file:       {LOG_FILE}")
    log.info("  Ctrl+C or mouse to top-left to stop.")
    log.info("=" * 50)

    sct = mss.mss()
    last_click_time = 0
    clicks = 0

    try:
        while True:
            try:
                if USE_REGION:
                    l, t, w, h = SCAN_REGION
                    monitor = {
                        "left": l * RETINA_SCALE,
                        "top": t * RETINA_SCALE,
                        "width": w * RETINA_SCALE,
                        "height": h * RETINA_SCALE,
                    }
                else:
                    monitor = sct.monitors[1]

                screenshot = sct.grab(monitor)
                img = np.array(screenshot)[:, :, :3][:, :, ::-1]  # BGRA → RGB

                result = find_orange_button(img)
                if result:
                    now = time.time()
                    if now - last_click_time >= CLICK_COOLDOWN:
                        sx, sy = result
                        if USE_REGION:
                            click_x = (SCAN_REGION[0] * RETINA_SCALE + sx) // RETINA_SCALE
                            click_y = (SCAN_REGION[1] * RETINA_SCALE + sy) // RETINA_SCALE
                        else:
                            click_x = sx // RETINA_SCALE
                            click_y = sy // RETINA_SCALE

                        clicks += 1
                        log.info(f"🤙 Ride On #{clicks} — clicked ({click_x}, {click_y})")
                        pyautogui.click(click_x, click_y)
                        last_click_time = now

                time.sleep(SCAN_INTERVAL)

            except pyautogui.FailSafeException:
                log.info("⛔ Fail-safe triggered (mouse in corner). Stopping.")
                sys.exit(0)

    except KeyboardInterrupt:
        log.info(f"\nStopped. Total Ride Ons: {clicks}")
        sys.exit(0)


if __name__ == "__main__":
    main()
