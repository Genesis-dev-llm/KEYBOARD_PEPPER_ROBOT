"""
Keyboard Input Handler
Processes keyboard events and dispatches to appropriate controllers.

PHASE 1 IMPROVEMENTS:
- Added key debouncing to prevent spam
- Better emergency stop handling
- Improved error handling
- Clear status messages
"""

import logging
import time
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
        
        # Debouncing (prevent command spam)
        self._last_command_time = {}
        self._debounce_delay = 0.1  # 100ms between same commands
        
        # Dance execution tracking
        self._dance_running = False
        
        self.running = True
    
    def _should_execute(self, command_id):
        """Check if enough time has passed to execute command again (debouncing)."""
        current_time = time.time()
        last_time = self._last_command_time.get(command_id, 0)
        
        if current_time - last_time >= self._debounce_delay:
            self._last_command_time[command_id] = current_time
            return True
        return False
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # ================================================================
            # EMERGENCY STOP - No debouncing, instant response
            # ================================================================
            if key == Key.esc:
                logger.info("ESC pressed - shutting down...")
                self.tablet.set_action("Emergency Stop", "Shutting down...")
                self.running = False
                self.base.stop()
                self.video.stop()
                return False
            
            # ================================================================
            # MODE TOGGLE
            # ================================================================
            if hasattr(key, 'char') and key.char == 't':
                if not self._should_execute('mode_toggle'):
                    return
                
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
                if key == Key.up and self._should_execute('move_forward'):
                    self.base.move_incremental('forward')
                elif key == Key.down and self._should_execute('move_back'):
                    self.base.move_incremental('back')
                elif key == Key.left and self._should_execute('move_left'):
                    self.base.move_incremental('left')
                elif key == Key.right and self._should_execute('move_right'):
                    self.base.move_incremental('right')
                elif hasattr(key, 'char'):
                    if key.char == 'q' and self._should_execute('rotate_left'):
                        self.base.move_incremental('rotate_left')
                    elif key.char == 'e' and self._should_execute('rotate_right'):
                        self.base.move_incremental('rotate_right')
            
            if hasattr(key, 'char'):
                # ============================================================
                # TABLET CONTROLS
                # ============================================================
                if key.char == 'm' and self._should_execute('tablet_mode'):
                    self.tablet.cycle_mode()
                    logger.info(f"📱 Tablet mode: {self.tablet.get_current_mode()}")
                    return
                elif key.char == 'h' and self._should_execute('greeting'):
                    self.tablet.show_greeting()
                    self.pepper.tts.say("Hello!")
                    logger.info("👋 Showing greeting")
                    return
                
                # ============================================================
                # VIDEO TOGGLE
                # ============================================================
                elif key.char == 'v' and self._should_execute('video_toggle'):
                    if self.video.is_active():
                        self.video.stop()
                    else:
                        self.video.start()
                    return
                
                # ============================================================
                # HEAD CONTROLS
                # ============================================================
                if key.char == 'w' and self._should_execute('head_up'):
                    self.body.move_head('up')
                    self.tablet.set_action("Looking Around", "Head up")
                elif key.char == 's' and self._should_execute('head_down'):
                    self.body.move_head('down')
                    self.tablet.set_action("Looking Around", "Head down")
                elif key.char == 'a' and self._should_execute('head_left'):
                    self.body.move_head('left')
                    self.tablet.set_action("Looking Around", "Head left")
                elif key.char == 'd' and self._should_execute('head_right'):
                    self.body.move_head('right')
                    self.tablet.set_action("Looking Around", "Head right")
                elif key.char == 'r' and self._should_execute('head_reset'):
                    self.body.reset_head()
                    self.tablet.set_action("Ready", "Head centered")
                
                # ============================================================
                # SHOULDER CONTROLS
                # ============================================================
                elif key.char == 'u' and self._should_execute('l_shoulder_up'):
                    self.body.move_shoulder_pitch('L', 'up')
                    self.tablet.set_action("Moving Arms", "Left shoulder up")
                elif key.char == 'j' and self._should_execute('l_shoulder_down'):
                    self.body.move_shoulder_pitch('L', 'down')
                    self.tablet.set_action("Moving Arms", "Left shoulder down")
                elif key.char == 'i' and self._should_execute('r_shoulder_up'):
                    self.body.move_shoulder_pitch('R', 'up')
                    self.tablet.set_action("Moving Arms", "Right shoulder up")
                elif key.char == 'k' and self._should_execute('r_shoulder_down'):
                    self.body.move_shoulder_pitch('R', 'down')
                    self.tablet.set_action("Moving Arms", "Right shoulder down")
                elif key.char == 'o' and self._should_execute('l_arm_out'):
                    self.body.move_shoulder_roll('L', 'out')
                    self.tablet.set_action("Moving Arms", "Left arm out")
                elif key.char == 'l' and self._should_execute('r_arm_out'):
                    self.body.move_shoulder_roll('R', 'out')
                    self.tablet.set_action("Moving Arms", "Right arm out")
                
                # ============================================================
                # ELBOW CONTROLS
                # ============================================================
                elif key.char == '7' and self._should_execute('l_elbow_bend'):
                    self.body.move_elbow_roll('L', 'bend')
                elif key.char == '9' and self._should_execute('l_elbow_straight'):
                    self.body.move_elbow_roll('L', 'straighten')
                elif key.char == '8' and self._should_execute('r_elbow_bend'):
                    self.body.move_elbow_roll('R', 'bend')
                elif key.char == '0' and self._should_execute('r_elbow_straight'):
                    self.body.move_elbow_roll('R', 'straighten')
                
                # ============================================================
                # WRIST CONTROLS
                # ============================================================
                elif key.char == ',' and self._should_execute('l_wrist_ccw'):
                    self.body.rotate_wrist('L', 'ccw')
                elif key.char == '.' and self._should_execute('l_wrist_cw'):
                    self.body.rotate_wrist('L', 'cw')
                elif key.char == ';' and self._should_execute('r_wrist_ccw'):
                    self.body.rotate_wrist('R', 'ccw')
                elif key.char == "'" and self._should_execute('r_wrist_cw'):
                    self.body.rotate_wrist('R', 'cw')
                
                # ============================================================
                # HAND CONTROLS (with Shift)
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
                # SPEED CONTROLS
                # ============================================================
                elif key.char in ['+', '='] and self._should_execute('speed_up_base'):
                    speed = self.base.increase_speed()
                    logger.info(f"⬆️  Base speed: {speed:.2f} m/s")
                elif key.char in ['-', '_'] and self._should_execute('speed_down_base'):
                    speed = self.base.decrease_speed()
                    logger.info(f"⬇️  Base speed: {speed:.2f} m/s")
                elif key.char == '[' and self._should_execute('speed_up_body'):
                    speed = self.body.increase_speed()
                    logger.info(f"⬆️  Body speed: {speed:.2f}")
                elif key.char == ']' and self._should_execute('speed_down_body'):
                    speed = self.body.decrease_speed()
                    logger.info(f"⬇️  Body speed: {speed:.2f}")
                
                # TURBO MODE (NEW!)
                elif key.char == 'x' and self._should_execute('turbo_toggle'):
                    turbo = self.base.toggle_turbo()
                    status = "ENABLED 🚀" if turbo else "DISABLED"
                    logger.info(f"Turbo mode: {status}")
                    self.tablet.set_action("Turbo Mode", status)("⬇️  Body speed: {speed:.2f}")
                
                # ============================================================
                # DANCES - Only if not already dancing
                # ============================================================
                elif key.char == '1' and not self._dance_running:
                    self._execute_dance('wave', "Hello!")
                elif key.char == '2' and not self._dance_running:
                    self._execute_dance('special', "Let's dance!")
                elif key.char == '3' and not self._dance_running:
                    self._execute_dance('robot', "Beep boop!")
                elif key.char == '4' and not self._dance_running:
                    self._execute_dance('moonwalk', "Shamone!")
                
                # ============================================================
                # SYSTEM COMMANDS
                # ============================================================
                elif key.char == 'p' and self._should_execute('status'):
                    self._print_status()
                elif key.char == 'z' and self._should_execute('reset_pos'):
                    self.base.reset_position()
            
            # ============================================================
            # SPACE BAR - STOP
            # ============================================================
            elif key == Key.space:
                self.base.stop()
                self.tablet.set_action("Stopped", "All movement halted")
                logger.info("⏸️  All movement stopped")
                
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
    
    def _execute_dance(self, dance_id, speech_text):
        """Execute a dance animation in a separate thread."""
        if self._dance_running:
            logger.warning(f"Dance already running, ignoring {dance_id}")
            return
        
        logger.info(f"🎭 Triggering: {dance_id.capitalize()}")
        self.tablet.set_action(dance_id.capitalize(), "Starting...")
        self.pepper.tts.say(speech_text)
        
        import threading
        
        def dance_thread():
            try:
                self._dance_running = True
                if dance_id in self.dances:
                    self.dances[dance_id].perform()
                    self.tablet.set_action("Ready", f"{dance_id.capitalize()} complete")
                    logger.info(f"✓ {dance_id.capitalize()} dance complete")
                else:
                    logger.error(f"Dance not found: {dance_id}")
            except Exception as e:
                logger.error(f"Dance error: {e}")
                self.tablet.set_action("Ready", "Dance failed")
            finally:
                self._dance_running = False
        
        thread = threading.Thread(target=dance_thread, daemon=True)
        thread.start()
    
    def _print_status(self):
        """Print current robot status."""
        try:
            status = self.pepper.get_status()
            base_state = self.base.get_state()
            body_state = self.body.get_state()
            
            print("\n" + "="*60)
            print("🤖 PEPPER ROBOT STATUS")
            print("="*60)
            print(f"Battery: {status.get('battery', 'Unknown')}%")
            print(f"Body Stiffness: {status.get('stiffness', 0.0):.2f}")
            print(f"Connected: {status.get('connected', False)}")
            print()
            print("--- MOVEMENT ---")
            print(f"Base Speed: {base_state['linear_speed']:.2f} m/s")
            print(f"Body Speed: {body_state['body_speed']:.2f}")
            print(f"Movement Mode: {'CONTINUOUS' if self.continuous_mode else 'INCREMENTAL'}")
            print(f"Currently Moving: {'YES' if self.base.is_moving() else 'NO'}")
            print()
            print("--- DISPLAYS ---")
            print(f"Video Active: {'YES' if self.video.is_active() else 'NO'}")
            print(f"Tablet Mode: {self.tablet.get_current_mode()}")
            print(f"Dance Running: {'YES' if self._dance_running else 'NO'}")
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
        print("  🎮 PEPPER KEYBOARD CONTROLS - PHASE 1")
        print("="*60)
        print(f"  Movement Mode: {mode_str}")
        print("  T: Toggle mode | V: Video | M: Tablet mode | H: Greeting")
        print("  P: Status | SPACE: Stop | ESC: Quit")
        print()
        print("  MOVEMENT:")
        print("    Arrow Keys: Move | Q/E: Rotate | Z: Reset position")
        print("    +/-: Base speed | [/]: Body speed | X: Turbo mode 🚀")
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
        print("    M: Cycle display mode")
        print("    H: Show greeting")
        print()
        print("  DANCES:")
        print("    1: Wave | 2: Special 💃 | 3: Robot 🤖 | 4: Moonwalk 🌙")
        print()
        print("  ✨ NEW: Smooth movement with velocity ramping!")
        print("  ✨ NEW: Thread-safe controls!")
        print("  ✨ NEW: Dance blocking (one at a time)!")
        print("="*60 + "\n")