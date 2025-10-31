"""
Input Handler - SIMPLIFIED VERSION
All movement is now step-based (like head movement).
No more continuous/incremental mode toggle - just simple, reliable steps.

IMPROVEMENTS:
- Single movement mode (step-based)
- No mode toggle complexity
- Better debouncing
- Cleaner key handling
"""

import logging
import time
from pynput import keyboard
from pynput.keyboard import Key

logger = logging.getLogger(__name__)

class InputHandler:
    """Simplified keyboard input handler - all step-based."""
    
    def __init__(self, pepper_conn, base_ctrl, body_ctrl, video_ctrl, tablet_ctrl, dances):
        self.pepper = pepper_conn
        self.base = base_ctrl
        self.body = body_ctrl
        self.video = video_ctrl
        self.tablet = tablet_ctrl
        self.dances = dances
        
        # Debouncing (prevent spam)
        self._last_command_time = {}
        self._debounce_delay = 0.15  # 150ms between same commands
        
        # Dance state
        self._dance_running = False
        
        self.running = True
    
    def _should_execute(self, command_id):
        """Check if enough time passed (debouncing)."""
        current_time = time.time()
        last_time = self._last_command_time.get(command_id, 0)
        
        if current_time - last_time >= self._debounce_delay:
            self._last_command_time[command_id] = current_time
            return True
        return False
    
    def on_press(self, key):
        """Handle key press - all commands are immediate."""
        try:
            # EMERGENCY STOP
            if key == Key.esc:
                logger.info("ESC - Emergency stop & quit")
                self.tablet.set_action("Emergency Stop", "Shutting down...")
                self.running = False
                self.base.emergency_stop()
                self.body.emergency_stop()
                return False
            
            # BASE MOVEMENT (step-based)
            if key == Key.up and self._should_execute('move_forward'):
                self.base.move_step('forward')
                self.tablet.set_action("Moving", "Forward")
                return
            elif key == Key.down and self._should_execute('move_back'):
                self.base.move_step('back')
                self.tablet.set_action("Moving", "Backward")
                return
            elif key == Key.left and self._should_execute('move_left'):
                self.base.move_step('left')
                self.tablet.set_action("Moving", "Strafe Left")
                return
            elif key == Key.right and self._should_execute('move_right'):
                self.base.move_step('right')
                self.tablet.set_action("Moving", "Strafe Right")
                return
            
            if hasattr(key, 'char'):
                # ROTATION
                if key.char == 'q' and self._should_execute('rotate_left'):
                    self.base.move_step('rotate_left')
                    self.tablet.set_action("Moving", "Rotate Left")
                elif key.char == 'e' and self._should_execute('rotate_right'):
                    self.base.move_step('rotate_right')
                    self.tablet.set_action("Moving", "Rotate Right")
                
                # SPACE - STOP
                elif key.char == ' ':
                    self.base.stop()
                    self.tablet.set_action("Stopped", "")
                    logger.info("⏸️ Stopped")
                
                # HEAD CONTROLS
                elif key.char == 'w' and self._should_execute('head_up'):
                    self.body.move_head('up')
                    self.tablet.set_action("Looking", "Head up")
                elif key.char == 's' and self._should_execute('head_down'):
                    self.body.move_head('down')
                    self.tablet.set_action("Looking", "Head down")
                elif key.char == 'a' and self._should_execute('head_left'):
                    self.body.move_head('left')
                    self.tablet.set_action("Looking", "Head left")
                elif key.char == 'd' and self._should_execute('head_right'):
                    self.body.move_head('right')
                    self.tablet.set_action("Looking", "Head right")
                elif key.char == 'r' and self._should_execute('head_reset'):
                    self.body.reset_head()
                    self.tablet.set_action("Ready", "Head centered")
                
                # SHOULDER CONTROLS
                elif key.char == 'u' and self._should_execute('l_shoulder_up'):
                    self.body.move_shoulder_pitch('L', 'up')
                    self.tablet.set_action("Arms", "L shoulder up")
                elif key.char == 'j' and self._should_execute('l_shoulder_down'):
                    self.body.move_shoulder_pitch('L', 'down')
                    self.tablet.set_action("Arms", "L shoulder down")
                elif key.char == 'i' and self._should_execute('r_shoulder_up'):
                    self.body.move_shoulder_pitch('R', 'up')
                    self.tablet.set_action("Arms", "R shoulder up")
                elif key.char == 'k' and self._should_execute('r_shoulder_down'):
                    self.body.move_shoulder_pitch('R', 'down')
                    self.tablet.set_action("Arms", "R shoulder down")
                elif key.char == 'o' and self._should_execute('l_arm_out'):
                    self.body.move_shoulder_roll('L', 'out')
                    self.tablet.set_action("Arms", "L arm out")
                elif key.char == 'l' and self._should_execute('r_arm_out'):
                    self.body.move_shoulder_roll('R', 'out')
                    self.tablet.set_action("Arms", "R arm out")
                
                # ELBOW CONTROLS
                elif key.char == '7' and self._should_execute('l_elbow_bend'):
                    self.body.move_elbow_roll('L', 'bend')
                elif key.char == '9' and self._should_execute('l_elbow_straight'):
                    self.body.move_elbow_roll('L', 'straighten')
                elif key.char == '8' and self._should_execute('r_elbow_bend'):
                    self.body.move_elbow_roll('R', 'bend')
                elif key.char == '0' and self._should_execute('r_elbow_straight'):
                    self.body.move_elbow_roll('R', 'straighten')
                
                # WRIST CONTROLS
                elif key.char == ',' and self._should_execute('l_wrist_ccw'):
                    self.body.rotate_wrist('L', 'ccw')
                elif key.char == '.' and self._should_execute('l_wrist_cw'):
                    self.body.rotate_wrist('L', 'cw')
                elif key.char == ';' and self._should_execute('r_wrist_ccw'):
                    self.body.rotate_wrist('R', 'ccw')
                elif key.char == "'" and self._should_execute('r_wrist_cw'):
                    self.body.rotate_wrist('R', 'cw')
                
                # HAND CONTROLS (with Shift)
                elif key.char == '<':  # Shift+,
                    self.body.move_hand('L', 'open')
                elif key.char == '>':  # Shift+.
                    self.body.move_hand('L', 'close')
                elif key.char == '(':  # Shift+9
                    self.body.move_hand('R', 'open')
                elif key.char == ')':  # Shift+0
                    self.body.move_hand('R', 'close')
                
                # SPEED CONTROLS
                elif key.char in ['+', '='] and self._should_execute('speed_up_base'):
                    step = self.base.increase_speed()
                    logger.info(f"⬆️ Base step: {step:.2f}m")
                elif key.char in ['-', '_'] and self._should_execute('speed_down_base'):
                    step = self.base.decrease_speed()
                    logger.info(f"⬇️ Base step: {step:.2f}m")
                elif key.char == '[' and self._should_execute('speed_up_body'):
                    speed = self.body.increase_speed()
                    logger.info(f"⬆️ Body speed: {speed:.2f}")
                elif key.char == ']' and self._should_execute('speed_down_body'):
                    speed = self.body.decrease_speed()
                    logger.info(f"⬇️ Body speed: {speed:.2f}")
                
                # TURBO MODE
                elif key.char == 'x' and self._should_execute('turbo_toggle'):
                    turbo = self.base.toggle_turbo()
                    status = "ENABLED 🚀" if turbo else "DISABLED"
                    logger.info(f"Turbo: {status}")
                    self.tablet.set_action("Turbo", status)
                
                # TABLET CONTROLS
                elif key.char == 'm' and self._should_execute('tablet_mode'):
                    self.tablet.cycle_mode()
                    logger.info(f"📱 Tablet: {self.tablet.get_current_mode()}")
                elif key.char == 'h' and self._should_execute('greeting'):
                    self.tablet.show_greeting()
                    self.pepper.tts.say("Hello!")
                    logger.info("👋 Greeting")
                
                # VIDEO TOGGLE
                elif key.char == 'v' and self._should_execute('video_toggle'):
                    if self.video.is_active():
                        self.video.stop()
                    else:
                        self.video.start()
                
                # DANCES
                elif key.char == '1' and not self._dance_running:
                    self._execute_dance('wave', "Hello!")
                elif key.char == '2' and not self._dance_running:
                    self._execute_dance('special', "Let's dance!")
                elif key.char == '3' and not self._dance_running:
                    self._execute_dance('robot', "Beep boop!")
                elif key.char == '4' and not self._dance_running:
                    self._execute_dance('moonwalk', "Shamone!")
                
                # SYSTEM COMMANDS
                elif key.char == 'p' and self._should_execute('status'):
                    self._print_status()
            
            # SPACE BAR (special case for Key object)
            elif key == Key.space:
                self.base.stop()
                self.tablet.set_action("Stopped", "")
                logger.info("⏸️ Stopped")
                
        except AttributeError:
            pass
        except Exception as e:
            logger.error(f"Key press error: {e}")
    
    def on_release(self, key):
        """Handle key release - not used in step-based mode."""
        # In step-based mode, we don't need to handle releases
        pass
    
    def _execute_dance(self, dance_id, speech_text):
        """Execute dance in background thread."""
        if self._dance_running:
            logger.warning(f"Dance already running")
            return
        
        logger.info(f"🎭 Dance: {dance_id}")
        self.tablet.set_action(dance_id.capitalize(), "Starting...")
        self.pepper.tts.say(speech_text)
        
        import threading
        
        def dance_thread():
            try:
                self._dance_running = True
                if dance_id in self.dances:
                    self.dances[dance_id].perform()
                    self.tablet.set_action("Ready", f"{dance_id} complete")
                    logger.info(f"✓ {dance_id} complete")
            except Exception as e:
                logger.error(f"Dance error: {e}")
                self.tablet.set_action("Ready", "Dance failed")
            finally:
                self._dance_running = False
        
        thread = threading.Thread(target=dance_thread, daemon=True)
        thread.start()
    
    def _print_status(self):
        """Print status."""
        try:
            status = self.pepper.get_status()
            base_state = self.base.get_state()
            body_state = self.body.get_state()
            
            print("\n" + "="*60)
            print("🤖 PEPPER ROBOT STATUS")
            print("="*60)
            print(f"Battery: {status.get('battery', '?')}%")
            print(f"Connected: {status.get('connected', False)}")
            print()
            print("--- BASE MOVEMENT ---")
            print(f"Step Size: {base_state['linear_step']:.2f}m")
            print(f"Rotation Step: {base_state['angular_step']:.2f} rad")
            print(f"Turbo: {base_state['turbo']}")
            print(f"Moving: {base_state['is_moving']}")
            print()
            print("--- BODY ---")
            print(f"Speed: {body_state['body_speed']:.2f}")
            print(f"Head Step: {body_state['head_step']:.2f} rad")
            print(f"Arm Step: {body_state['arm_step']:.2f} rad")
            print()
            print("--- DISPLAYS ---")
            print(f"Video: {self.video.is_active()}")
            print(f"Tablet: {self.tablet.get_current_mode()}")
            print("="*60 + "\n")
        except Exception as e:
            logger.error(f"Status error: {e}")
    
    def run(self):
        """Start keyboard listener."""
        self._print_controls()
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
    def _print_controls(self):
        """Print control instructions."""
        print("\n" + "="*60)
        print("  🎮 PEPPER KEYBOARD CONTROLS - STEP-BASED")
        print("="*60)
        print("  All movement is step-based (reliable & predictable)")
        print("  V: Video | M: Tablet | H: Greeting | P: Status")
        print("  SPACE: Stop | ESC: Emergency stop & quit")
        print()
        print("  BASE MOVEMENT (each press = one step):")
        print("    Arrow Keys: Move | Q/E: Rotate")
        print("    +/-: Step size | X: Turbo")
        print()
        print("  HEAD:")
        print("    W/S: Up/Down | A/D: Left/Right | R: Reset")
        print()
        print("  ARMS:")
        print("    U/J: L shoulder | I/K: R shoulder")
        print("    O: L arm out | L: R arm out")
        print("    7/9: L elbow | 8/0: R elbow")
        print()
        print("  WRISTS:")
        print("    ,/.: L wrist | ;/': R wrist")
        print()
        print("  HANDS (Shift):")
        print("    </> : L hand | (/): R hand")
        print()
        print("  DANCES:")
        print("    1: Wave | 2: Special | 3: Robot | 4: Moonwalk")
        print()
        print("  ✨ SIMPLE, FAST, RELIABLE!")
        print("="*60 + "\n")