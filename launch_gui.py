#!/usr/bin/env python
"""
Launch Pepper Control Center GUI
Simple launcher script for the PyQt5 interface.

Usage:
    python launch_gui.py 192.168.1.100
    python launch_gui.py --ip 192.168.1.100
"""

import sys
sys.argv.append('--gui')  # Force GUI mode

from test_controller import run

if __name__ == "__main__":
    sys.exit(run())