"""
Main Entry Point - ULTRA OPTIMIZED VERSION
Minimal startup, fast execution, optional features.

OPTIMIZATIONS:
- Lazy loading (only load what's needed)
- Optional video server
- Fast keyboard mode by default
- Minimal imports
"""

import sys
import os
import logging
import argparse
import threading
import time

# Minimal logging
logging.basicConfig(
    level=logging.WARNING,  # Less spam!
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Set important loggers to INFO
logging.getLogger('test_controller').setLevel(logging.INFO)

def run():
    """Main entry - OPTIMIZED."""
    
    parser = argparse.ArgumentParser(description="Pepper Control - FAST MODE")
    
    parser.add_argument('ip', nargs='?', help="Pepper's IP")
    parser.add_argument('--ip', dest='ip_flag', help="Pepper's IP (alt)")
    parser.add_argument('--no-gui', action='store_true', help="Keyboard only (FAST)")
    parser.add_argument('--gui', action='store_true', help="Launch GUI (slower)")
    parser.add_argument('--no-video', action='store_true', help="Disable video server")
    parser.add_argument('--minimal', action='store_true', help="Absolute minimal mode")
    
    args = parser.parse_args()
    
    # Determine mode
    use_gui = args.gui and not args.no_gui
    enable_video = not args.no_video and not args.minimal
    minimal_mode = args.minimal
    
    # Get IP
    pepper_ip = args.ip or args.ip_flag
    
    if not pepper_ip and os.path.exists(".pepper_ip"):
        try:
            with open(".pepper_ip", "r") as f:
                pepper_ip = f.read().strip()
        except:
            pass
    
    if not pepper_ip:
        pepper_ip = input("Enter Pepper's IP: ").strip()
        if not pepper_ip:
            print("No IP provided.")
            sys.exit(1)
        
        try:
            with open(".pepper_ip", "w") as f:
                f.write(pepper_ip)
        except:
            pass
    
    # ========================================================================
    # FAST INITIALIZATION
    # ========================================================================
    
    print("\n" + "="*60)
    mode_desc = "MINIMAL" if minimal_mode else ("GUI" if use_gui else "KEYBOARD")
    print(f"  🤖 PEPPER CONTROL - {mode_desc} MODE")
    print("="*60 + "\n")
    
    try:
        # Import only what we need
        from .controllers import PepperConnection, BaseController, BodyController
        
        # Connect
        logger.info("Connecting to Pepper...")
        pepper_conn = PepperConnection(pepper_ip)
        
        # Initialize controllers
        logger.info("Initializing controllers...")
        base_ctrl = BaseController(pepper_conn.motion)
        body_ctrl = BodyController(pepper_conn.motion)
        
        # Optional: Video controller (only if needed)
        video_ctrl = None
        if not minimal_mode:
            from .controllers import VideoController
            video_ctrl = VideoController(pepper_ip)
        
        # Optional: Tablet (only if needed)
        tablet_ctrl = None
        if not minimal_mode:
            from .tablet import TabletController
            tablet_ctrl = TabletController(pepper_conn.session, pepper_ip)
        
        # Optional: Dances (only if needed)
        dances = {}
        if not minimal_mode:
            logger.info("Loading dances...")
            from .dances import WaveDance, SpecialDance, RobotDance, MoonwalkDance
            dances = {
                'wave': WaveDance(pepper_conn.motion, pepper_conn.posture),
                'special': SpecialDance(pepper_conn.motion, pepper_conn.posture),
                'robot': RobotDance(pepper_conn.motion, pepper_conn.posture),
                'moonwalk': MoonwalkDance(pepper_conn.motion, pepper_conn.posture)
            }
        
        # Optional: Video server (DISABLED by default for speed!)
        video_server = None
        if enable_video and tablet_ctrl:
            logger.info("Starting video server...")
            from .video_server import create_video_server
            video_server = create_video_server(pepper_conn.session, start=True)
            tablet_ctrl.video_server = video_server
        
        # ====================================================================
        # LAUNCH MODE
        # ====================================================================
        
        if use_gui:
            # GUI MODE
            logger.info("Launching GUI...")
            try:
                from .gui import launch_gui
                
                controllers_dict = {
                    'base': base_ctrl,
                    'body': body_ctrl,
                    'video': video_ctrl
                }
                
                exit_code = launch_gui(pepper_conn, controllers_dict, dances, tablet_ctrl)
                sys.exit(exit_code)
                
            except ImportError as e:
                logger.error(f"GUI import failed: {e}")
                logger.info("Falling back to keyboard mode...")
                use_gui = False
        
        # KEYBOARD MODE (FAST!)
        if not use_gui:
            from .input_handler import InputHandler
            
            logger.info("Keyboard mode active...")
            
            input_handler = InputHandler(
                pepper_conn, base_ctrl, body_ctrl,
                video_ctrl, tablet_ctrl, dances
            )
            
            # Movement update thread (50Hz)
            def base_update_loop():
                while input_handler.running:
                    try:
                        if input_handler.continuous_mode:
                            base_ctrl.move_continuous()
                        time.sleep(0.02)  # 50Hz
                    except Exception as e:
                        logger.error(f"Update error: {e}")
                        time.sleep(0.1)
            
            update_thread = threading.Thread(target=base_update_loop, daemon=True)
            update_thread.start()
            
            logger.info("✓ Ready! (Ultra-fast mode)")
            print()
            
            # Run
            input_handler.run()
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except ConnectionError as e:
        logger.error(f"\n❌ CONNECTION FAILED: {e}")
        logger.error(f"Check: ping {pepper_ip}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("\nShutting down...")
        try:
            if video_ctrl:
                video_ctrl.stop()
            if base_ctrl:
                base_ctrl.stop()
            if video_server:
                video_server.stop()
            if pepper_conn:
                pepper_conn.close()
        except:
            pass
        
        logger.info("Done!")

if __name__ == "__main__":
    run()