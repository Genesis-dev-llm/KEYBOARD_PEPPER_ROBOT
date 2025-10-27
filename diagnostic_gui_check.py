#!/usr/bin/env python
"""
GUI Diagnostic Script
Run this to diagnose why GUI isn't launching.

Usage:
    python diagnostic_gui_check.py
"""

import sys
import os

print("\n" + "="*70)
print("  🔍 PEPPER GUI DIAGNOSTIC")
print("="*70 + "\n")

# Check 1: Python version
print("1️⃣  Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 6):
    print("   ⚠️  WARNING: Python 3.6+ recommended")
else:
    print("   ✓ Version OK")
print()

# Check 2: PyQt5
print("2️⃣  Checking PyQt5...")
try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    print(f"   ✓ PyQt5 {PyQt5.QtCore.PYQT_VERSION_STR} installed")
    
    # Try creating QApplication
    try:
        app = QApplication([])
        print("   ✓ QApplication can be created")
        app.quit()
    except Exception as e:
        print(f"   ⚠️  WARNING: Cannot create QApplication: {e}")
except ImportError as e:
    print(f"   ❌ PyQt5 NOT installed: {e}")
    print("   Install: pip install PyQt5")
print()

# Check 3: GUI dependencies
print("3️⃣  Checking GUI dependencies...")
deps_ok = True

try:
    import cv2
    print(f"   ✓ opencv-python installed")
except ImportError:
    print(f"   ❌ opencv-python NOT installed")
    deps_ok = False

try:
    from PIL import Image
    print(f"   ✓ Pillow installed")
except ImportError:
    print(f"   ❌ Pillow NOT installed")
    deps_ok = False

try:
    import numpy
    print(f"   ✓ numpy installed")
except ImportError:
    print(f"   ❌ numpy NOT installed")
    deps_ok = False

if not deps_ok:
    print("\n   Install missing packages:")
    print("   pip install opencv-python Pillow numpy")
print()

# Check 4: GUI module structure
print("4️⃣  Checking GUI module structure...")
gui_files = [
    "test_controller/__init__.py",
    "test_controller/gui/__init__.py",
    "test_controller/gui/main_window.py",
    "test_controller/gui/styles.py",
    "test_controller/gui/control_panel.py",
    "test_controller/gui/camera_panel.py",
]

all_exist = True
for filepath in gui_files:
    if os.path.exists(filepath):
        print(f"   ✓ {filepath}")
    else:
        print(f"   ❌ MISSING: {filepath}")
        all_exist = False

if not all_exist:
    print("\n   ⚠️  Some GUI files are missing!")
print()

# Check 5: Can import GUI module?
print("5️⃣  Testing GUI import...")
try:
    from test_controller.gui import launch_gui
    print("   ✓ GUI module can be imported")
    print(f"   ✓ launch_gui function found: {launch_gui}")
except ImportError as e:
    print(f"   ❌ CANNOT import GUI module")
    print(f"   Error: {e}")
    print("\n   This is likely the problem!")
except Exception as e:
    print(f"   ❌ Error during import: {e}")
print()

# Check 6: Display available?
print("6️⃣  Checking display (Linux/Mac)...")
if sys.platform in ['linux', 'darwin']:
    display = os.environ.get('DISPLAY')
    if display:
        print(f"   ✓ DISPLAY={display}")
    else:
        print(f"   ⚠️  WARNING: No DISPLAY environment variable")
        print(f"   This is required for GUI on Linux")
else:
    print(f"   Platform: {sys.platform} (Windows/Other)")
print()

# Summary
print("="*70)
print("  📋 SUMMARY")
print("="*70)

if all_exist and 'PyQt5' in sys.modules and deps_ok:
    print("\n✅ All checks passed!")
    print("\nYour GUI should work. Try:")
    print("  python launch_gui.py 192.168.1.100")
    print("\nOr with the main script:")
    print("  python test_keyboard_control.py 192.168.1.100 --gui")
else:
    print("\n❌ Issues found:")
    if 'PyQt5' not in sys.modules:
        print("  - PyQt5 not installed")
    if not deps_ok:
        print("  - Missing dependencies")
    if not all_exist:
        print("  - Missing GUI files")
    
    print("\n🔧 To fix:")
    print("  1. Install dependencies:")
    print("     pip install -r requirements_gui.txt")
    print("  2. Verify all GUI files exist")
    print("  3. Try the new launch_gui.py script")

print("="*70 + "\n")