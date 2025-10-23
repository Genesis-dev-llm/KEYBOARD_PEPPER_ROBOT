"""
Keyboard Input Handler
Processes keyboard events and dispatches to appropriate controllers.
"""

import logging
from pynput import keyboard
from pynput.keyboard import Key

logger = logging.getLogger(__name__)

class InputHandler:
    """Handles keyboard input and routes commands to controllers."""
    
    def __init__(self, pepper_conn, base_ctrl, body_ctrl, video_ctrl, tablet_ctrl, dances):
        self.pepper = pepper_conn
        self.base = base_ctrl
        self.body = body_ctrl
        self.video = video_ctrl
        self.tablet = tablet_ctrl
        self.dances = dances
        
        # Movement mode
        self.continuous_mode = True  # True = hold to move, False = click to step
        
        self.running = True
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # ================================================================
            # MODE TOGGLE
            # ================================================================
            if hasattr(key, 'char') and key.char == 't':
                self.continuous_mode = not self.continuous_mode
                mode = "CONTINUOUS (hold keys)" if self.continuous_mode else "INCREMENTAL (click to step)"
                logger.info(f"Movement mode: {mode}")
                self.tablet.set_movement_mode(self.continuous_mode)
                if not self.continuous_mode:
                    self.base.stop()
                    self.tablet.set_action("Stopped", "Switched to incremental mode")
                return
            
            # ================================================================
            # BASE MOVEMENT
            # ================================================================
            if self.continuous_mode:
                # CONTINUOUS MODE - Hold to move
                if key == Key.up:
                    self.base.set_continuous_velocity('x', 1.0)
                    self.tablet.set_action("Moving Forward", "")
                elif key == Key.down:
                    self.base.set_continuous_velocity('x', -1.0)
                    self.tablet.set_action("Moving Backward", "")
                elif key == Key.left:
                    self.base.set_continuous_velocity('y', 1.0)
                    self.tablet.set_action("Strafing Left", "")
                elif key == Key.right:
                    self.base.set_continuous_velocity('y', -1.0)
                    self.tablet.set_action("Strafing Right", "")
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.base.set_continuous_velocity('theta', 1.0)
                        self.tablet.set_action("Rotating Left", "")
                    elif key.char == 'e':
                        self.base.set_continuous_velocity('theta', -1.0)
                        self.tablet.set_action("Rotating Right", "")
            else:
                # INCREMENTAL MODE - Click to step
                if key == Key.up:
                    self.base.move_incremental('forward')
                elif key == Key.down:
                    self.base.move_incremental('back')
                elif key == Key.left:
                    self.base.move_incremental('left')
                elif key == Key.right:
                    self.base.move_incremental('right')
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.base.move_incremental('rotate_left')
                    elif key.char == 'e':
                        self.base.move_incremental('rotate_right')
            
            if hasattr(key, 'char'):
                # ============================================================
                # TABLET CONTROLS (NEW!)
                # ============================================================
                if key.char == 'm':
                    self.tablet.cycle_mode()
                    logger.info(f"📱 Tablet mode: {self.tablet.get_current_mode()}")
                    return
                elif key.char == 'h':
                    self.tablet.show_greeting()
                    self.pepper.tts.say("Hello!")
                    logger.info("👋 Showing greeting")
                    return
                
                # ============================================================
                # VIDEO TOGGLE
                # ============================================================
                elif key.char == 'v':
                    if self.video.is_active():
                        self.video.stop()
                    else:
                        self.video.start()
                    return
                
                # ============================================================
                # HEAD CONTROLS
                # ============================================================
                if key.char == 'w':
                    self.body.move_head('up')
                    self.tablet.set_action("Looking Around", "Head up")
                elif key.char == 's':
                    self.body.move_head('down')
                    self.tablet.set_action("Looking Around", "Head down")
                elif key.char == 'a':
                    self.body.move_head('left')
                    self.tablet.set_action("Looking Around", "Head left")
                elif key.char == 'd':
                    self.body.move_head('right')
                    self.tablet.set_action("Looking Around", "Head right")
                elif key.char == 'r':
                    self.body.reset_head()
                    self.tablet.set_action("Ready", "Head centered")
                
                # ============================================================
                # SHOULDER CONTROLS
                # ============================================================
                elif key.char == 'u':
                    self.body.move_shoulder_pitch('L', 'up')
                    self.tablet.set_action("Moving Arms", "Left shoulder up")
                elif key.char == 'j':
                    self.body.move_shoulder_pitch('L', 'down')
                    self.tablet.set_action("Moving Arms", "Left shoulder down")
                elif key.char == 'i':
                    self.body.move_shoulder_pitch('R', 'up')
                    self.tablet.set_action("Moving Arms", "Right shoulder up")
                elif key.char == 'k':
                    self.body.move_shoulder_pitch('R', 'down')
                    self.tablet.set_action("Moving Arms", "Right shoulder down")
                elif key.char == 'o':
                    self.body.move_shoulder_roll('L', 'out')
                    self.tablet.set_action("Moving Arms", "Left arm out")
                elif key.char == 'l':
                    self.body.move_shoulder_roll('R', 'out')
                    self.tablet.set_action("Moving Arms", "Right arm out")
                
                # ============================================================
                # ELBOW CONTROLS
                # ============================================================
                elif key.char == '7':
                    self.body.move_elbow_roll('L', 'bend')
                elif key.char == '9':
                    self.body.move_elbow_roll('L', 'straighten')
                elif key.char == '8':
                    self.body.move_elbow_roll('R', 'bend')
                elif key.char == '0':
                    self.body.move_elbow_roll('R', 'straighten')
                
                # ============================================================
                # WRIST CONTROLS (NEW!)
                # ============================================================
                elif key.char == ',':
                    self.body.rotate_wrist('L', 'ccw')
                elif key.char == '.':
                    self.body.rotate_wrist('L', 'cw')
                elif key.char == ';':
                    self.body.rotate_wrist('R', 'ccw')
                elif key.char == "'":
                    self.body.rotate_wrist('R', 'cw')
                
                # ============================================================
                # HAND CONTROLS
                # ============================================================
                elif key.char == '<':  # Shift+,
                    self.body.move_hand('L', 'open')
                elif key.char == '>':  # Shift+.
                    self.body.move_hand('L', 'close')
                elif key.char == '(':  # Shift+9
                    self.body.move_hand('R', 'open')
                elif key.char == ')':  # Shift+0
                    self.body.move_hand('R', 'close')
                
                # ============================================================
                # SPEED CONTROLS (NEW!)
                # ============================================================
                elif key.char == '+' or key.char == '=':
                    speed = self.base.increase_speed()
                    logger.info(f"⬆️  Base speed: {speed:.2f} m/s")
                elif key.char == '-' or key.char == '_':
                    speed = self.base.decrease_speed()
                    logger.info(f"⬇️  Base speed: {speed:.2f} m/s")
                elif key.char == '[':
                    speed = self.body.increase_speed()
                    logger.info(f"⬆️  Body speed: {speed:.2f}")
                elif key.char == ']':
                    speed = self.body.decrease_speed()
                    logger.info(f"⬇️  Body speed: {speed:.2f}")
                
                # ============================================================
                # DANCES
                # ============================================================
                elif key.char == '1':
                    logger.info("🎭 Triggering: Wave")
                    self.tablet.set_action("Wave", "Starting wave animation...")
                    self.pepper.tts.say("Hello!")
                    self.dances['wave'].perform()
                    self.tablet.set_action("Ready", "Wave complete")
                elif key.char == '2':
                    logger.info("💃 Triggering: SPECIAL DANCE")
                    self.tablet.set_action("Special Dance", "Let's dance!")
                    self.pepper.tts.say("Let's dance!")
                    self.dances['special'].perform()
                    self.tablet.set_action("Ready", "Special dance complete")
                elif key.char == '3':
                    logger.info("🤖 Triggering: Robot Dance")
                    self.tablet.set_action("Robot Dance", "Beep boop!")
                    self.pepper.tts.say("Beep boop!")
                    self.dances['robot'].perform()
                    self.tablet.set_action("Ready", "Robot dance complete")
                elif key.char == '4':
                    logger.info("🌙 Triggering: MOONWALK")
                    self.tablet.set_action("Moonwalk", "Shamone!")
                    self.pepper.tts.say("Shamone!")
                    self.dances['moonwalk'].perform()
                    self.tablet.set_action("Ready", "Moonwalk complete")
                
                # ============================================================
                # SYSTEM COMMANDS
                # ============================================================
                elif key.char == 'p':
                    self._print_status()
                elif key.char == 'z':
                    self.base.reset_position()
            
            # ============================================================
            # SPACE BAR - STOP
            # ============================================================
            elif key == Key.space:
                self.base.stop()
                self.tablet.set_action("Stopped", "All movement halted")
                logger.info("⏸️  All movement stopped")
            
            # ============================================================
            # ESC - QUIT
            # ============================================================
            elif key == Key.esc:
                logger.info("ESC pressed - shutting down...")
                self.tablet.set_action("Emergency Stop", "Shutting down...")
                self.running = False
                self.base.stop()
                self.video.stop()
                return False
                
        except AttributeError:
            pass
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def on_release(self, key):
        """Handle key release events."""
        try:
            if self.continuous_mode:
                if key == Key.up or key == Key.down:
                    self.base.set_continuous_velocity('x', 0.0)
                    self.tablet.set_action("Ready", "Waiting for input...")
                elif key == Key.left or key == Key.right:
                    self.base.set_continuous_velocity('y', 0.0)
                    self.tablet.set_action("Ready", "Waiting for input...")
                elif hasattr(key, 'char'):
                    if key.char in ['q', 'e']:
                        self.base.set_continuous_velocity('theta', 0.0)
                        self.tablet.set_action("Ready", "Waiting for input...")
        except:
            pass
    
    def _print_status(self):
        """Print current robot status."""
        try:
            status = self.pepper.get_status()
            
            print("\n" + "="*60)
            print("🤖 PEPPER ROBOT STATUS")
            print("="*60)
            print(f"Battery: {status.get('battery', 'Unknown')}%")
            print(f"Body Stiffness: {status.get('stiffness', 0.0):.2f}")
            print(f"Base Speed: {self.base.linear_speed:.2f} m/s")
            print(f"Body Speed: {self.body.body_speed:.2f}")
            print(f"Movement Mode: {'CONTINUOUS' if self.continuous_mode else 'INCREMENTAL'}")
            print(f"Video Active: {'YES' if self.video.is_active() else 'NO'}")
            print(f"Tablet Mode: {self.tablet.get_current_mode()}")
            print("="*60 + "\n")
        except Exception as e:
            logger.error(f"Could not retrieve status: {e}")
    
    def run(self):
        """Start the keyboard listener."""
        self._print_controls()
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
    def _print_controls(self):
        """Print control instructions."""
        mode_str = "CONTINUOUS (hold)" if self.continuous_mode else "INCREMENTAL (click)"
        print("\n" + "="*60)
        print("  🎮 PEPPER KEYBOARD CONTROLS")
        print("="*60)
        print(f"  Movement Mode: {mode_str}")
        print("  T: Toggle mode | V: Video | M: Tablet mode | H: Greeting")
        print("  P: Status | ESC: Quit")
        print()
        print("  MOVEMENT:")
        print("    Arrow Keys: Move | Q/E: Rotate | Z: Reset position")
        print("    +/-: Base speed | [/]: Body speed")
        print()
        print("  HEAD:")
        print("    W/S: Pitch | A/D: Yaw | R: Reset")
        print()
        print("  ARMS:")
        print("    U/J: Left shoulder | I/K: Right shoulder")
        print("    O: Left arm out | L: Right arm out")
        print("    7/9: Left elbow | 8/0: Right elbow")
        print()
        print("  WRISTS:")
        print("    ,/.: Left wrist | ;/': Right wrist")
        print()
        print("  HANDS (use Shift):")
        print("    </> (Shift+,/.): Left hand")
        print("    (/) (Shift+9/0): Right hand")
        print()
        print("  TABLET:")
        print("    M: Cycle display mode (Status/Camera/Greeting)")
        print("    H: Show greeting")
        print()
        print("  DANCES:")
        print("    1: Wave | 2: Special Dance 💃 | 3: Robot 🤖 | 4: Moonwalk 🌙")
        print("="*60 + "\n")