#!/usr/bin/env python3
"""
Zwift Ride On Auto-Clicker for macOS (Template Matching)
=========================================================
Uses OpenCV template matching to find the Ride On button on screen
and clicks it automatically. Much more accurate than color detection.

Requirements:
    pip3 install pyautogui numpy mss opencv-python

macOS Setup:
    System Settings → Privacy & Security → Screen Recording → enable Terminal
    System Settings → Privacy & Security → Accessibility → enable Terminal

Usage:
    python3 zwift_rideon_clicker.py
    Press Ctrl+C or move mouse to top-left corner to stop.
"""

import time
import sys
import logging
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import mss

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Path to the Ride On button template image
TEMPLATE_PATH = Path(__file__).parent / "rideon_template.png"

# Match confidence threshold (0.0 to 1.0).
# Higher = stricter matching, fewer false positives.
# Lower = more tolerant, catches the button in more conditions.
# Start at 0.7, raise to 0.8 if false positives, lower to 0.6 if missing clicks.
MATCH_THRESHOLD = 0.7

# How often to scan (seconds)
SCAN_INTERVAL = 0.5

# Cooldown after a click (seconds)
CLICK_COOLDOWN = 3.0

# Which monitor to scan:
#   0 = all screens combined
#   1 = primary display
#   2 = secondary display
MONITOR_INDEX = 0

# Retina scale: 2 for built-in Retina, 1 for external non-Retina
RETINA_SCALE = 2

# Template scaling: the template might not match the in-game size exactly.
# The script tries multiple scales to find the best match.
# Range: (min_scale, max_scale, steps)
MULTI_SCALE = True
SCALE_RANGE = (0.5, 2.0, 10)  # 10 steps between 50% and 200%

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
# TEMPLATE MATCHING
# ---------------------------------------------------------------------------

def load_template():
    """Load and prepare the template image."""
    if not TEMPLATE_PATH.exists():
        print(f"\n  ❌ Template not found: {TEMPLATE_PATH}")
        print(f"     Place 'rideon_template.png' next to this script.")
        sys.exit(1)

    template = cv2.imread(str(TEMPLATE_PATH))
    if template is None:
        print(f"\n  ❌ Could not read template image: {TEMPLATE_PATH}")
        sys.exit(1)

    return template


def find_template(screenshot_bgr, template):
    """
    Find the template in the screenshot using multi-scale matching.
    Returns (x, y, confidence) in screenshot pixel coords, or None.
    """
    gray_screen = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    th, tw = gray_template.shape[:2]

    best_match = None
    best_val = 0

    if MULTI_SCALE:
        min_s, max_s, steps = SCALE_RANGE
        scales = np.linspace(min_s, max_s, steps)
    else:
        scales = [1.0]

    for scale in scales:
        new_w = int(tw * scale)
        new_h = int(th * scale)

        # Skip if scaled template is larger than the screen
        if new_w > gray_screen.shape[1] or new_h > gray_screen.shape[0]:
            continue
        # Skip if template becomes too small
        if new_w < 10 or new_h < 10:
            continue

        resized = cv2.resize(gray_template, (new_w, new_h))
        result = cv2.matchTemplate(gray_screen, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_val:
            best_val = max_val
            best_match = (
                max_loc[0] + new_w // 2,  # center x
                max_loc[1] + new_h // 2,  # center y
                max_val,
            )

    if best_match and best_match[2] >= MATCH_THRESHOLD:
        return best_match

    return None

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    log = setup_logging()
    template = load_template()
    th, tw = template.shape[:2]

    log.info("=" * 50)
    log.info("  Zwift Ride On Auto-Clicker (Template Matching)")
    log.info("=" * 50)
    log.info(f"  Template:       {TEMPLATE_PATH.name} ({tw}x{th}px)")
    log.info(f"  Threshold:      {MATCH_THRESHOLD}")
    log.info(f"  Multi-scale:    {'ON' if MULTI_SCALE else 'OFF'}")
    log.info(f"  Monitor:        {'all screens' if MONITOR_INDEX == 0 else f'monitor {MONITOR_INDEX}'}")
    log.info(f"  Scan interval:  {SCAN_INTERVAL}s")
    log.info(f"  Click cooldown: {CLICK_COOLDOWN}s")
    log.info(f"  Retina scale:   {RETINA_SCALE}x")
    log.info(f"  Log file:       {LOG_FILE}")
    log.info("  Ctrl+C or mouse to top-left to stop.")
    log.info("=" * 50)
    log.info("")
    log.info("  🔍 Scanning for Ride On buttons...")

    sct = mss.mss()
    last_click_time = 0
    clicks = 0

    try:
        while True:
            try:
                monitor = sct.monitors[MONITOR_INDEX]
                screenshot = sct.grab(monitor)

                # mss returns BGRA, OpenCV uses BGR
                img = np.array(screenshot)[:, :, :3]  # drop alpha → BGR

                result = find_template(img, template)

                if result:
                    sx, sy, confidence = result
                    now = time.time()
                    if now - last_click_time >= CLICK_COOLDOWN:
                        # Convert screenshot pixels to logical screen coords
                        click_x = (monitor["left"] + sx) // RETINA_SCALE
                        click_y = (monitor["top"] + sy) // RETINA_SCALE

                        clicks += 1
                        log.info(
                            f"🤙 Ride On #{clicks} — clicked ({click_x}, {click_y}) "
                            f"[confidence: {confidence:.2f}]"
                        )
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
