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