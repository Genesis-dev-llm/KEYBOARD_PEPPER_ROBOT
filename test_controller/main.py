"""
Main Entry Point for Pepper Keyboard Test Controller
Orchestrates all components and starts the controller.

Updated: Phase 2 - Added GUI support with PyQt5
FIXED: Better error handling, optional video/tablet, proper cleanup
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

# Try to import tablet controller (optional)
try:
    from .tablet import TabletController
    TABLET_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Tablet controller not available: {e}")
    TABLET_AVAILABLE = False

def run():
    """Main entry point for the test controller."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Pepper Robot Keyboard Test Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_keyboard_control.py 192.168.1.100
  python -m test_controller.main --ip 192.168.1.100
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
    
    parser.add_argument(
        '--no-video',
        action='store_true',
        help="Disable video feed"
    )
    
    parser.add_argument(
        '--no-tablet',
        action='store_true',
        help="Disable tablet display"
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
        print("  2. python -m test_controller.main --ip 192.168.1.100")
        print("  3. Enter IP now:")
        print()
        pepper_ip = input("Enter Pepper's IP address: ").strip()
        
        if not pepper_ip:
            print("No IP provided. Exiting.")
            sys.exit(1)
    
    # ========================================================================
    # INITIALIZE COMPONENTS
    # ========================================================================
    
    pepper_conn = None
    base_ctrl = None
    body_ctrl = None
    video_ctrl = None
    tablet_ctrl = None
    input_handler = None
    base_thread = None
    
    try:
        print("\n" + "="*60)
        print("  🤖 PEPPER KEYBOARD TEST CONTROLLER")
        print("  Version 2.0.0 - Modular Edition")
        print("="*60 + "\n")
        
        # Connect to Pepper
        logger.info("Initializing Pepper connection...")
        try:
            pepper_conn = PepperConnection(pepper_ip)
        except Exception as e:
            logger.error(f"Failed to connect to Pepper: {e}")
            raise ConnectionError(f"Could not connect to Pepper at {pepper_ip}")
        
        # Initialize movement controllers
        logger.info("Initializing movement controllers...")
        try:
            base_ctrl = BaseController(pepper_conn.motion)
            body_ctrl = BodyController(pepper_conn.motion)
        except Exception as e:
            logger.error(f"Failed to initialize controllers: {e}")
            raise
        
        # Initialize video controller (optional)
        if not args.no_video:
            logger.info("Initializing video controller...")
            try:
                video_ctrl = VideoController(pepper_ip)
                logger.info("✓ Video controller ready (press V to toggle)")
            except Exception as e:
                logger.warning(f"Video controller initialization failed: {e}")
                logger.warning("Video feed will not be available")
                video_ctrl = None
        else:
            logger.info("Video controller disabled (--no-video)")
            video_ctrl = None
        
        # Initialize tablet display (optional)
        if not args.no_tablet and TABLET_AVAILABLE:
            logger.info("Initializing tablet display...")
            try:
                tablet_ctrl = TabletController(pepper_conn.session, pepper_ip)
                logger.info("✓ Tablet display ready")
            except Exception as e:
                logger.warning(f"Tablet initialization failed: {e}")
                logger.warning("Tablet display will not be available")
                tablet_ctrl = None
        else:
            if args.no_tablet:
                logger.info("Tablet display disabled (--no-tablet)")
            else:
                logger.warning("Tablet module not available")
            tablet_ctrl = None
        
        # Create dummy tablet controller if needed
        if tablet_ctrl is None:
            class DummyTablet:
                def set_action(self, action, detail=""): pass
                def set_movement_mode(self, mode): pass
                def cycle_mode(self): pass
                def show_greeting(self): pass
                def get_current_mode(self): return "DISABLED"
                def refresh_display(self): pass
            
            tablet_ctrl = DummyTablet()
            logger.info("Using dummy tablet controller")
        
        # Initialize dances
        logger.info("Loading dance animations...")
        try:
            dances = {
                'wave': WaveDance(pepper_conn.motion, pepper_conn.posture),
                'special': SpecialDance(pepper_conn.motion, pepper_conn.posture),
                'robot': RobotDance(pepper_conn.motion, pepper_conn.posture),
                'moonwalk': MoonwalkDance(pepper_conn.motion, pepper_conn.posture)
            }
            logger.info(f"✓ Loaded {len(dances)} dance animations")
        except Exception as e:
            logger.error(f"Failed to load dances: {e}")
            raise
        
        # Check if GUI mode requested
        if args.gui:
            logger.info("Launching GUI mode...")
            try:
                from .gui import launch_gui
            except ImportError as e:
                logger.error(f"Failed to import GUI: {e}")
                logger.error("Install GUI dependencies: pip install -r requirements_gui.txt")
                sys.exit(1)
            
            # Package controllers for GUI
            controllers_dict = {
                'base': base_ctrl,
                'body': body_ctrl
            }
            
            # Add video only if initialized
            if video_ctrl:
                controllers_dict['video'] = video_ctrl
            
            # Launch GUI (blocking call)
            sys.exit(launch_gui(pepper_conn, controllers_dict, dances, tablet_ctrl))
        
        # ====================================================================
        # KEYBOARD MODE (non-GUI)
        # ====================================================================
        
        # Start base movement update thread (for continuous mode)
        def base_update_loop():
            while input_handler and input_handler.running:
                try:
                    if input_handler.continuous_mode:
                        base_ctrl.move_continuous()
                    time.sleep(0.05)  # 20Hz
                except Exception as e:
                    logger.error(f"Error in base update loop: {e}")
                    break
        
        # Initialize input handler
        logger.info("Initializing keyboard input handler...")
        try:
            input_handler = InputHandler(
                pepper_conn, base_ctrl, body_ctrl, 
                video_ctrl, tablet_ctrl, dances
            )
        except Exception as e:
            logger.error(f"Failed to initialize input handler: {e}")
            raise
        
        # Start base update thread
        base_thread = threading.Thread(target=base_update_loop, daemon=True)
        base_thread.start()
        
        logger.info("✓ All systems ready!")
        print()
        
        # Run input handler (blocks until ESC pressed)
        input_handler.run()
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
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
        logger.info("\nShutting down...")
        
        # Stop input handler
        if input_handler:
            input_handler.running = False
        
        # Wait for base thread to finish
        if base_thread and base_thread.is_alive():
            base_thread.join(timeout=1.0)
        
        # Stop video
        if video_ctrl:
            try:
                video_ctrl.stop()
            except Exception as e:
                logger.debug(f"Error stopping video: {e}")
        
        # Stop base movement
        if base_ctrl:
            try:
                base_ctrl.stop()
            except Exception as e:
                logger.debug(f"Error stopping base: {e}")
        
        # Close Pepper connection
        if pepper_conn:
            try:
                pepper_conn.close()
            except Exception as e:
                logger.debug(f"Error closing connection: {e}")
        
        logger.info("Goodbye!")

if __name__ == "__main__":
    run()