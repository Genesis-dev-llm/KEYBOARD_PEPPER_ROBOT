#!/usr/bin/env python
"""
Quick Test Script
Runs basic diagnostics without full system initialization.

Usage:
    python quick_test.py 192.168.1.100
"""

import sys
import os

def main():
    print("\n" + "="*60)
    print("  🔍 PEPPER QUICK DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Get IP
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py PEPPER_IP")
        sys.exit(1)
    
    pepper_ip = sys.argv[1]
    
    # Test 1: Network
    print("1️⃣  Testing network connection...")
    from test_controller.network_diagnostics import NetworkDiagnostics
    
    if NetworkDiagnostics.quick_check(pepper_ip):
        print("   ✓ Pepper is reachable")
    else:
        print("   ❌ Cannot reach Pepper")
        print("   Check: IP address, network, Pepper power")
        sys.exit(1)
    
    # Test 2: Detailed network test
    print("\n2️⃣  Running latency test...")
    NetworkDiagnostics.ping_test(pepper_ip, count=5)
    
    # Test 3: Configuration
    print("\n3️⃣  Validating configuration...")
    from test_controller.config_validator import ConfigValidator
    ConfigValidator.validate_all()
    
    # Test 4: Dependencies
    print("\n4️⃣  Checking dependencies...")
    deps = {
        'qi': 'NAOqi (required)',
        'cv2': 'OpenCV (required)',
        'numpy': 'NumPy (required)',
        'pynput': 'Pynput (required)',
        'flask': 'Flask (required)',
        'PyQt5': 'PyQt5 (optional - GUI)',
    }
    
    all_good = True
    for module, desc in deps.items():
        try:
            __import__(module)
            print(f"   ✓ {desc}")
        except ImportError:
            print(f"   ❌ {desc} - MISSING")
            all_good = False
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("  ✅ ALL TESTS PASSED")
        print("="*60)
        print("\n  Ready to launch:")
        print(f"    python test_keyboard_control.py {pepper_ip}")
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("="*60)
        print("\n  Install missing dependencies:")
        print("    pip install -r requirements.txt")
        print("    pip install -r requirements_gui.txt")
    print()

if __name__ == "__main__":
    main()