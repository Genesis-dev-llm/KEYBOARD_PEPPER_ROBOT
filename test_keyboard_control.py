#!/usr/bin/env python
"""
Keyboard Test Controller for Pepper Robot
=========================================
Use this to test Pepper connectivity and responsiveness before VR testing.

Controls:
---------
TOGGLE MODE:
  T             - Switch between CONTINUOUS (hold) and INCREMENTAL (click) modes

MOVEMENT (mode-dependent):
  CONTINUOUS MODE (default):
    Arrow Keys    - Hold to move (Up=forward, Down=back, Left/Right=strafe)
    Q/E           - Hold to rotate left/right
    SPACE         - Stop all movement
  
  INCREMENTAL MODE:
    Arrow Keys    - Click to move 5cm per press
    Q/E           - Click to rotate ~11° per press
    Z             - Reset accumulated position to origin (0,0,0)

HEAD (always incremental):
  W/S           - Head pitch (up/down) in small steps
  A/D           - Head yaw (left/right) in small steps
  R             - Reset head to center

ARMS (always incremental, reads current position):
  U/J           - Left shoulder pitch (U=up, J=down)
  I/K           - Right shoulder pitch (I=up, K=down)
  O             - Left arm OUT (extend sideways)
  L             - Right arm OUT (extend sideways)
  
  Note: Arms increment from CURRENT position, not absolute.
  Each press moves the joint by ~0.1 radians (~6°)

HANDS:
  [/]           - Open/Close left hand
  ;/'           - Open/Close right hand

PRE-MOTIONS:
  1             - Wave
  2             - Dance (if implemented)
  
SYSTEM:
  P             - Print robot status
  ESC           - Emergency stop and exit

ARM LOGIC EXPLANATION:
---------------------
Pepper's arm joints work as follows:
  - ShoulderPitch: Negative = arm up, Positive = arm down
    Range: -2.0857 to 2.0857 radians (~-120° to +120°)
  
  - ShoulderRoll: Controls arm lateral movement
    LEFT arm:  Positive = out (away from body), Range: 0.0087 to 1.5620
    RIGHT arm: Negative = out (away from body), Range: -1.5620 to -0.0087
  
The keyboard controller:
  1. Reads the CURRENT joint angle with getAngles()
  2. Adds/subtracts a small step (0.1 radians)
  3. Clamps to safe limits
  4. Sends new angle with setAngles()

This allows gradual, controlled movement from any starting position.

Author: VR Pepper Teleoperation Team
Date: October 2025
"""

import qi
import sys
import os
import threading
import time
import logging

# Try to import keyboard library
try:
    from pynput import keyboard
    from pynput.keyboard import Key
except ImportError:
    print("ERROR: pynput not installed. Install with: pip install pynput")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KeyboardPepperController:
    """Interactive keyboard controller for Pepper robot testing."""
    
    def __init__(self, ip, port=9559):
        self.ip = ip
        self.port = port
        self.running = True
        
        # Movement mode toggle
        self.continuous_mode = True  # True = hold to move, False = click to increment
        
        # Movement state (continuous mode)
        self.base_x = 0.0  # forward/back
        self.base_y = 0.0  # strafe
        self.base_theta = 0.0  # rotation
        
        # Accumulated position (incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        
        # Speed settings
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.head_speed = 0.2
        self.arm_speed = 0.2
        
        # Incremental movement step sizes
        self.linear_step = 0.05  # 5cm per press
        self.angular_step = 0.2  # ~11 degrees per press
        self.head_step = 0.1  # radians
        self.arm_step = 0.1  # radians
        
        # Connect to robot
        logger.info(f"Connecting to Pepper at {ip}:{port}...")
        self.session = qi.Session()
        try:
            self.session.connect(f"tcp://{ip}:{port}")
            logger.info("✓ Connected successfully!")
        except qi.Exception as e:
            logger.error(f"Failed to connect: {e}")
            sys.exit(1)
        
        # Get services
        self.motion = self.session.service("ALMotion")
        self.posture = self.session.service("ALRobotPosture")
        self.tts = self.session.service("ALTextToSpeech")
        
        # Initialize robot
        self._initialize_robot()
        
        # Start movement update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info("🎮 Keyboard controller ready! Press keys to control Pepper.")
        logger.info("    Press ESC to quit, P for status")
    
    def _initialize_robot(self):
        """Prepare robot for control."""
        logger.info("Initializing robot...")
        try:
            # Disable autonomous life
            autonomous_life = self.session.service("ALAutonomousLife")
            autonomous_life.setState("disabled")
        except:
            pass
        
        self.motion.setStiffnesses("Body", 1.0)
        self.posture.goToPosture("Stand", 0.5)
        logger.info("✓ Robot ready")
    
    def _update_loop(self):
        """Continuously update base movement (runs in background thread)."""
        while self.running:
            try:
                if self.continuous_mode:
                    # Continuous movement mode - hold keys to move
                    if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
                        self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                else:
                    # Incremental mode - doesn't use this loop
                    self.motion.stopMove()
            except Exception as e:
                logger.error(f"Movement update error: {e}")
            time.sleep(0.05)  # 20Hz update rate
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # Toggle movement mode
            if hasattr(key, 'char') and key.char == 't':
                self.continuous_mode = not self.continuous_mode
                mode = "CONTINUOUS (hold keys)" if self.continuous_mode else "INCREMENTAL (click to step)"
                logger.info(f"Movement mode: {mode}")
                if not self.continuous_mode:
                    self._stop_all()  # Stop any continuous movement
                return
            
            # Movement controls
            if self.continuous_mode:
                # CONTINUOUS MODE - Hold to move
                if key == Key.up:
                    self.base_x = self.linear_speed
                elif key == Key.down:
                    self.base_x = -self.linear_speed
                elif key == Key.left:
                    self.base_y = self.linear_speed
                elif key == Key.right:
                    self.base_y = -self.linear_speed
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.base_theta = self.angular_speed
                    elif key.char == 'e':
                        self.base_theta = -self.angular_speed
            else:
                # INCREMENTAL MODE - Click to step
                if key == Key.up:
                    self.accumulated_x += self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step forward: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.down:
                    self.accumulated_x -= self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step back: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.left:
                    self.accumulated_y += self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step left: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.right:
                    self.accumulated_y -= self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step right: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.accumulated_theta += self.angular_step
                        self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                        logger.info(f"Rotate left: theta={self.accumulated_theta:.2f}")
                    elif key.char == 'e':
                        self.accumulated_theta -= self.angular_step
                        self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                        logger.info(f"Rotate right: theta={self.accumulated_theta:.2f}")
            
            if hasattr(key, 'char'):
                # Head controls (always incremental)
                if key.char == 'w':
                    self.head_pitch = min(0.5, self.head_pitch + self.head_step)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                    logger.info(f"Head up: pitch={self.head_pitch:.2f}")
                elif key.char == 's':
                    self.head_pitch = max(-0.6, self.head_pitch - self.head_step)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                    logger.info(f"Head down: pitch={self.head_pitch:.2f}")
                elif key.char == 'a':
                    self.head_yaw = min(2.0, self.head_yaw + self.head_step)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                    logger.info(f"Head left: yaw={self.head_yaw:.2f}")
                elif key.char == 'd':
                    self.head_yaw = max(-2.0, self.head_yaw - self.head_step)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                    logger.info(f"Head right: yaw={self.head_yaw:.2f}")
                elif key.char == 'r':
                    self.head_yaw = 0.0
                    self.head_pitch = 0.0
                    self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], self.head_speed)
                    logger.info("Head reset to center")
                
                # Arm controls (incremental, each press moves arm)
                elif key.char == 'u':
                    # Left shoulder pitch UP
                    current = self.motion.getAngles("LShoulderPitch", True)[0]
                    new_angle = max(-2.0857, current - self.arm_step)
                    self.motion.setAngles("LShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Left arm up: {new_angle:.2f}")
                elif key.char == 'j':
                    # Left shoulder pitch DOWN
                    current = self.motion.getAngles("LShoulderPitch", True)[0]
                    new_angle = min(2.0857, current + self.arm_step)
                    self.motion.setAngles("LShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Left arm down: {new_angle:.2f}")
                elif key.char == 'i':
                    # Right shoulder pitch UP
                    current = self.motion.getAngles("RShoulderPitch", True)[0]
                    new_angle = max(-2.0857, current - self.arm_step)
                    self.motion.setAngles("RShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Right arm up: {new_angle:.2f}")
                elif key.char == 'k':
                    # Right shoulder pitch DOWN
                    current = self.motion.getAngles("RShoulderPitch", True)[0]
                    new_angle = min(2.0857, current + self.arm_step)
                    self.motion.setAngles("RShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Right arm down: {new_angle:.2f}")
                elif key.char == 'o':
                    # Left shoulder roll OUT (extend left arm sideways)
                    current = self.motion.getAngles("LShoulderRoll", True)[0]
                    new_angle = min(1.5620, current + self.arm_step)  # Positive = out
                    self.motion.setAngles("LShoulderRoll", new_angle, self.arm_speed)
                    logger.info(f"Left arm out: {new_angle:.2f}")
                elif key.char == 'l':
                    # Right shoulder roll OUT (extend right arm sideways)
                    current = self.motion.getAngles("RShoulderRoll", True)[0]
                    new_angle = max(-1.5620, current - self.arm_step)  # Negative = out
                    self.motion.setAngles("RShoulderRoll", new_angle, self.arm_speed)
                    logger.info(f"Right arm out: {new_angle:.2f}")
                
                # Hand controls
                elif key.char == '[':
                    self.motion.setAngles("LHand", 1.0, 0.3)
                    logger.info("Left hand opened")
                elif key.char == ']':
                    self.motion.setAngles("LHand", 0.0, 0.3)
                    logger.info("Left hand closed")
                elif key.char == ';':
                    self.motion.setAngles("RHand", 1.0, 0.3)
                    logger.info("Right hand opened")
                elif key.char == "'":
                    self.motion.setAngles("RHand", 0.0, 0.3)
                    logger.info("Right hand closed")
                
                # Pre-motions
                elif key.char == '1':
                    logger.info("Playing wave animation...")
                    self.tts.say("Hello!")
                    self._wave()
                elif key.char == '2':
                    logger.info("Dance not implemented yet")
                
                # System commands
                elif key.char == 'p':
                    self._print_status()
                elif key.char == 'z':
                    # Reset accumulated position
                    self.accumulated_x = 0.0
                    self.accumulated_y = 0.0
                    self.accumulated_theta = 0.0
                    logger.info("Position reset to origin (0, 0, 0)")
                
            # Space bar - stop
            elif key == Key.space:
                self._stop_all()
                logger.info("⏸️  All movement stopped")
            
            # ESC - quit
            elif key == Key.esc:
                logger.info("ESC pressed - shutting down...")
                self.running = False
                self._stop_all()
                return False  # Stop listener
                
        except AttributeError:
            pass  # Ignore special keys we don't handle
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def on_release(self, key):
        """Handle key release events."""
        try:
            # Only stop continuous movement when keys released
            if self.continuous_mode:
                if key == Key.up or key == Key.down:
                    self.base_x = 0.0
                elif key == Key.left or key == Key.right:
                    self.base_y = 0.0
                elif hasattr(key, 'char'):
                    if key.char in ['q', 'e']:
                        self.base_theta = 0.0
        except:
            pass
    
    def _stop_all(self):
        """Stop all movement."""
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        self.motion.stopMove()
    
    def _wave(self):
        """Simple wave animation."""
        self.motion.setAngles("RShoulderPitch", -0.5, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RShoulderRoll", -1.2, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RElbowRoll", 1.5, 0.2)
        time.sleep(0.5)
        
        for _ in range(3):
            self.motion.setAngles("RWristYaw", -1.0, 0.4)
            time.sleep(0.3)
            self.motion.setAngles("RWristYaw", 1.0, 0.4)
            time.sleep(0.3)
        
        self.posture.goToPosture("Stand", 0.5)
    
    def _print_status(self):
        """Print current robot status."""
        try:
            battery = self.session.service("ALBattery")
            battery_level = battery.getBatteryCharge()
            
            stiffness = self.motion.getStiffnesses("Body")
            
            print("\n" + "="*50)
            print("🤖 PEPPER ROBOT STATUS")
            print("="*50)
            print(f"Battery: {battery_level}%")
            print(f"Body Stiffness: {stiffness[0]:.2f}")
            print(f"Head Position: Yaw={self.head_yaw:.2f}, Pitch={self.head_pitch:.2f}")
            print(f"Base Movement: X={self.base_x:.2f}, Y={self.base_y:.2f}, Theta={self.base_theta:.2f}")
            print("="*50 + "\n")
        except Exception as e:
            logger.error(f"Could not retrieve status: {e}")
    
    def run(self):
        """Start the keyboard listener."""
        mode_str = "CONTINUOUS (hold)" if self.continuous_mode else "INCREMENTAL (click)"
        print("\n" + "="*60)
        print("  KEYBOARD CONTROLS")
        print("="*60)
        print(f"  Movement Mode: {mode_str}")
        print("  Press T to toggle between CONTINUOUS/INCREMENTAL")
        print()
        print("  CONTINUOUS MODE (hold keys):")
        print("    Arrow Keys: Hold to move | Q/E: Hold to rotate")
        print()
        print("  INCREMENTAL MODE (click to step):")
        print("    Arrow Keys: Click to move 5cm | Q/E: Click to rotate")
        print("    Z: Reset position to origin")
        print()
        print("  Always available:")
        print("    WASD: Head | U/I/J/K: Arms | O/L: Arms out")
        print("    [/]/;/': Hands | 1: Wave | P: Status | ESC: Quit")
        print("="*60 + "\n")
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        
        logger.info("Shutting down controller...")
        self.session.close()

def main():
    """Main entry point."""
    pepper_ip = None
    
    # Try to get IP from command line
    if len(sys.argv) >= 2:
        pepper_ip = sys.argv[1]
    # Try to load from saved file
    elif os.path.exists(".pepper_ip"):
        try:
            with open(".pepper_ip", "r") as f:
                pepper_ip = f.read().strip()
            print(f"Using saved Pepper IP: {pepper_ip}")
        except:
            pass
    
    # If still no IP, ask user
    if not pepper_ip:
        print("No Pepper IP provided.")
        print("\nOptions:")
        print("  1. Run with IP: python test_keyboard_control.py 192.168.1.100")
        print("  2. Enter IP now")
        print()
        pepper_ip = input("Enter Pepper's IP address: ").strip()
        
        if not pepper_ip:
            print("No IP provided. Exiting.")
            sys.exit(1)
    
    try:
        controller = KeyboardPepperController(pepper_ip)
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()