#!/usr/bin/env python
"""
GUI Launcher - FIXED VERSION
Guaranteed to launch GUI or show clear error message.

Usage:
    python launch_gui.py 192.168.1.100
    python launch_gui.py --ip 192.168.1.100
"""

import sys
import os
import logging

# Setup logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def check_gui_dependencies():
    """Check if GUI dependencies are installed."""
    missing = []
    
    # Check PyQt5
    try:
        import PyQt5
        logger.info("✓ PyQt5 found")
    except ImportError:
        missing.append("PyQt5")
    
    # Check other GUI dependencies
    try:
        import cv2
        logger.info("✓ opencv-python found")
    except ImportError:
        missing.append("opencv-python")
    
    try:
        from PIL import Image
        logger.info("✓ Pillow found")
    except ImportError:
        missing.append("Pillow")
    
    return missing

def main():
    """Main GUI launcher."""
    print("\n" + "="*70)
    print("  🖥️  PEPPER CONTROL CENTER - GUI LAUNCHER")
    print("="*70 + "\n")
    
    # Check dependencies FIRST
    logger.info("Checking GUI dependencies...")
    missing = check_gui_dependencies()
    
    if missing:
        print("\n" + "="*70)
        print("  ❌ MISSING GUI DEPENDENCIES")
        print("="*70)
        print("\nThe following packages are missing:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all GUI dependencies:")
        print("  pip install -r requirements_gui.txt")
        print("="*70 + "\n")
        sys.exit(1)
    
    logger.info("✓ All GUI dependencies found\n")
    
    # Get IP address
    pepper_ip = None
    
    # Check command line
    if len(sys.argv) >= 2:
        if sys.argv[1].startswith('--ip='):
            pepper_ip = sys.argv[1].split('=')[1]
        elif '--ip' in sys.argv:
            idx = sys.argv.index('--ip')
            if idx + 1 < len(sys.argv):
                pepper_ip = sys.argv[idx + 1]
        elif not sys.argv[1].startswith('-'):
            pepper_ip = sys.argv[1]
    
    # Try saved IP
    if not pepper_ip and os.path.exists(".pepper_ip"):
        try:
            with open(".pepper_ip", "r") as f:
                pepper_ip = f.read().strip()
            logger.info(f"Using saved IP: {pepper_ip}")
        except:
            pass
    
    # Ask user
    if not pepper_ip:
        print("No IP address provided.")
        print("\nOptions:")
        print("  python launch_gui.py 192.168.1.100")
        print("  python launch_gui.py --ip 192.168.1.100")
        print()
        pepper_ip = input("Enter Pepper's IP address: ").strip()
        
        if not pepper_ip:
            print("No IP provided. Exiting.")
            sys.exit(1)
        
        # Save for next time
        try:
            with open(".pepper_ip", "w") as f:
                f.write(pepper_ip)
        except:
            pass
    
    print(f"\n🤖 Connecting to Pepper at: {pepper_ip}")
    print("🖥️  Launching GUI...\n")
    
    # Import and launch
    try:
        logger.info("Importing GUI modules...")
        from test_controller.controllers import PepperConnection, BaseController, BodyController, VideoController
        from test_controller.dances import WaveDance, SpecialDance, RobotDance, MoonwalkDance
        from test_controller.tablet import TabletController
        from test_controller.gui import launch_gui
        
        logger.info("✓ Modules imported successfully")
        
        # Connect to Pepper
        logger.info(f"Connecting to Pepper at {pepper_ip}...")
        pepper_conn = PepperConnection(pepper_ip)
        logger.info("✓ Connected to Pepper")
        
        # Initialize controllers
        logger.info("Initializing controllers...")
        base_ctrl = BaseController(pepper_conn.motion)
        body_ctrl = BodyController(pepper_conn.motion)
        video_ctrl = VideoController(pepper_ip)
        logger.info("✓ Controllers initialized")
        
        # Initialize tablet
        logger.info("Initializing tablet display...")
        tablet_ctrl = TabletController(pepper_conn.session, pepper_ip)
        logger.info("✓ Tablet initialized")
        
        # Initialize dances
        logger.info("Loading dance animations...")
        dances = {
            'wave': WaveDance(pepper_conn.motion, pepper_conn.posture),
            'special': SpecialDance(pepper_conn.motion, pepper_conn.posture),
            'robot': RobotDance(pepper_conn.motion, pepper_conn.posture),
            'moonwalk': MoonwalkDance(pepper_conn.motion, pepper_conn.posture)
        }
        logger.info("✓ Dances loaded")
        
        # Start video server
        logger.info("Starting video streaming server...")
        from test_controller.video_server import create_video_server
        video_server = create_video_server(pepper_conn.session)
        video_server.start()
        tablet_ctrl.video_server = video_server
        logger.info("✓ Video server started")
        
        # Package controllers
        controllers_dict = {
            'base': base_ctrl,
            'body': body_ctrl,
            'video': video_ctrl
        }
        
        # LAUNCH GUI
        logger.info("\n🚀 Launching GUI window...")
        logger.info("=" * 70)
        exit_code = launch_gui(pepper_conn, controllers_dict, dances, tablet_ctrl)
        
        # Cleanup
        logger.info("\nGUI closed. Cleaning up...")
        sys.exit(exit_code)
        
    except ImportError as e:
        print("\n" + "="*70)
        print("  ❌ GUI IMPORT ERROR")
        print("="*70)
        print(f"\nError: {e}")
        print("\nPossible causes:")
        print("  1. GUI module not found")
        print("  2. Missing __init__.py files")
        print("  3. Incorrect package structure")
        print("\nCheck that these files exist:")
        print("  - test_controller/gui/__init__.py")
        print("  - test_controller/gui/main_window.py")
        print("  - test_controller/gui/styles.py")
        print("="*70 + "\n")
        sys.exit(1)
        
    except ConnectionError as e:
        print("\n" + "="*70)
        print("  ❌ CONNECTION FAILED")
        print("="*70)
        print(f"\nCould not connect to Pepper at {pepper_ip}")
        print("\nCheck:")
        print("  1. Pepper is powered on")
        print("  2. IP address is correct")
        print("  3. Both on same network")
        print(f"  4. Can ping: ping {pepper_ip}")
        print("="*70 + "\n")
        sys.exit(1)
        
    except Exception as e:
        print("\n" + "="*70)
        print("  ❌ UNEXPECTED ERROR")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()