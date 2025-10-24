"""
Main Entry Point for Pepper Keyboard Test Controller
Orchestrates all components and starts the controller.

PHASE 1 FIXES:
- Fixed dances scope bug (moved before GUI check)
- Better error handling
- Proper cleanup on exit
"""

import sys
import os
import logging
import argparse
import threading
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import controllers
from .controllers import PepperConnection, BaseController, BodyController, VideoController
from .dances import WaveDance, SpecialDance, RobotDance, MoonwalkDance
from .input_handler import InputHandler
from .tablet import TabletController

def run():
    """Main entry point for the test controller."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Pepper Robot Keyboard Test Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_keyboard_control.py 192.168.1.100
  python test_keyboard_control.py --gui
  python -m test_controller.main --ip 192.168.1.100 --gui
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help="Launch with GUI interface (PyQt5)"
    )
    
    parser.add_argument(
        'ip',
        nargs='?',
        type=str,
        help="Pepper robot's IP address"
    )
    
    parser.add_argument(
        '--ip',
        dest='ip_flag',
        type=str,
        help="Pepper robot's IP address (alternative)"
    )
    
    args = parser.parse_args()
    
    # Get IP from either positional or flag argument
    pepper_ip = args.ip or args.ip_flag
    
    # Try to load from saved file if no IP provided
    if not pepper_ip and os.path.exists(".pepper_ip"):
        try:
            with open(".pepper_ip", "r") as f:
                pepper_ip = f.read().strip()
            logger.info(f"Using saved Pepper IP: {pepper_ip}")
        except:
            pass
    
    # If still no IP, ask user
    if not pepper_ip:
        print("\n" + "="*60)
        print("  PEPPER IP ADDRESS REQUIRED")
        print("="*60)
        print("Options:")
        print("  1. python test_keyboard_control.py 192.168.1.100")
        print("  2. python test_keyboard_control.py 192.168.1.100 --gui")
        print("  3. python -m test_controller.main --ip 192.168.1.100")
        print("  4. Enter IP now:")
        print()
        pepper_ip = input("Enter Pepper's IP address: ").strip()
        
        if not pepper_ip:
            print("No IP provided. Exiting.")
            sys.exit(1)
        
        # Save IP for next time
        try:
            with open(".pepper_ip", "w") as f:
                f.write(pepper_ip)
            logger.info(f"Saved IP to .pepper_ip")
        except:
            pass
    
    # ========================================================================
    # INITIALIZE COMPONENTS
    # ========================================================================
    
    pepper_conn = None
    base_ctrl = None
    body_ctrl = None
    video_ctrl = None
    tablet_ctrl = None
    input_handler = None
    
    try:
        print("\n" + "="*60)
        print("  🤖 PEPPER KEYBOARD TEST CONTROLLER")
        print("  Version 2.0.0 - Phase 1: Smooth Movement")
        print("="*60 + "\n")
        
        # Connect to Pepper
        logger.info("Initializing Pepper connection...")
        pepper_conn = PepperConnection(pepper_ip)
        
        # Initialize controllers
        logger.info("Initializing movement controllers...")
        base_ctrl = BaseController(pepper_conn.motion)
        body_ctrl = BodyController(pepper_conn.motion)
        video_ctrl = VideoController(pepper_ip)
        
        # Initialize tablet display
        logger.info("Initializing tablet display...")
        tablet_ctrl = TabletController(pepper_conn.session, pepper_ip)
        
        # Initialize dances (MOVED BEFORE GUI CHECK - CRITICAL FIX!)
        logger.info("Loading dance animations...")
        dances = {
            'wave': WaveDance(pepper_conn.motion, pepper_conn.posture),
            'special': SpecialDance(pepper_conn.motion, pepper_conn.posture),
            'robot': RobotDance(pepper_conn.motion, pepper_conn.posture),
            'moonwalk': MoonwalkDance(pepper_conn.motion, pepper_conn.posture)
        }
        
        # Initialize video server (PHASE 2 - CRITICAL!)
        logger.info("Starting video streaming server...")
        from .video_server import create_video_server
        video_server = create_video_server(pepper_conn.session)
        video_server.start()
        
        # Update tablet controller with video server
        tablet_ctrl.video_server = video_server
        
        # Check if GUI mode requested
        if args.gui:
            logger.info("Launching GUI mode...")
            try:
                from .gui import launch_gui
            except ImportError as e:
                logger.error(f"Failed to import GUI: {e}")
                logger.error("Install GUI dependencies: pip install -r requirements_gui.txt")
                logger.error("Required: PyQt5, pyaudio, SpeechRecognition, Pillow")
                sys.exit(1)
            
            # Package controllers for GUI
            controllers_dict = {
                'base': base_ctrl,
                'body': body_ctrl,
                'video': video_ctrl
            }
            
            # Launch GUI (blocking call)
            exit_code = launch_gui(pepper_conn, controllers_dict, dances, tablet_ctrl)
            sys.exit(exit_code)
        
        # ====================================================================
        # KEYBOARD MODE (non-GUI)
        # ====================================================================
        
        # Initialize input handler
        logger.info("Initializing keyboard input handler...")
        input_handler = InputHandler(
            pepper_conn, base_ctrl, body_ctrl, 
            video_ctrl, tablet_ctrl, dances
        )
        
        # Start base movement update thread (for continuous mode)
        # CRITICAL: Update at 50Hz for smooth base movement!
        def base_update_loop():
            """Update base movement continuously at 50Hz"""
            while input_handler.running:
                try:
                    if input_handler.continuous_mode:
                        base_ctrl.move_continuous()
                    time.sleep(0.02)  # 20ms = 50Hz (increased from 50ms/20Hz)
                except Exception as e:
                    logger.error(f"Movement update error: {e}")
                    time.sleep(0.1)
        
        base_thread = threading.Thread(target=base_update_loop, daemon=True)
        base_thread.start()
        
        logger.info("✓ All systems ready!")
        logger.info("✓ Keyboard control active")
        logger.info("✓ Base movement: 50Hz update rate")
        
        # Optional: Run movement diagnostic
        if '--test-movement' in sys.argv:
            logger.info("\n🔧 Running movement diagnostic...")
            pepper_conn.test_movement()
        
        print()
        
        # Run input handler (blocks until ESC pressed)
        input_handler.run()
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user (Ctrl+C)")
    except ConnectionError as e:
        logger.error(f"\n❌ CONNECTION FAILED: {e}")
        logger.error("Please check:")
        logger.error("  1. Pepper's IP address is correct")
        logger.error("  2. Pepper is powered on")
        logger.error("  3. Both devices on same network")
        logger.error(f"  4. Test: ping {pepper_ip}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("\nShutting down safely...")
        try:
            # Stop video if running
            if video_ctrl:
                video_ctrl.stop()
                logger.info("✓ Video feed stopped")
            
            # Stop all movement
            if base_ctrl:
                base_ctrl.stop()
                logger.info("✓ Movement stopped")
            
            # Close connection
            if pepper_conn:
                pepper_conn.close()
                logger.info("✓ Connection closed")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("Goodbye! 👋")

if __name__ == "__main__":
    run()