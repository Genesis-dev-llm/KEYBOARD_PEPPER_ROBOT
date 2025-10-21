#!/usr/bin/env python
"""
Pepper Robot Keyboard Test Controller - Launcher
=================================================
Simple launcher script that imports and runs the modular test controller.

Usage:
    python test_keyboard_control.py 192.168.1.100
    python test_keyboard_control.py --ip 192.168.1.100

The actual implementation is in test_controller/ package.
"""

from test_controller import run

if __name__ == "__main__":
    run()

"""
    ============================================================
  🎮 PEPPER KEYBOARD CONTROLS
============================================================
  Movement Mode: CONTINUOUS (hold)
  T: Toggle mode | V: Video | P: Status | ESC: Quit

  MOVEMENT:
    Arrow Keys: Move | Q/E: Rotate | Z: Reset position
    +/-: Base speed | [/]: Body speed

  HEAD:
    W/S: Pitch | A/D: Yaw | R: Reset

  ARMS:
    U/J: Left shoulder | I/K: Right shoulder
    O: Left arm out | L: Right arm out
    7/9: Left elbow | 8/0: Right elbow

  WRISTS:
    ,/.: Left wrist | ;/': Right wrist

  HANDS (use Shift):
    </> (Shift+,/.): Left hand
    (/) (Shift+9/0): Right hand

  DANCES:
    1: Wave | 2: Special Dance 💃 | 3: Robot 🤖 | 4: Moonwalk 🌙
============================================================
"""
