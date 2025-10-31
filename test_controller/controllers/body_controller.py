"""
Body Controller - FIXED & COMPLETE
Step-based control for head, arms, hands with async execution.

IMPROVEMENTS:
- Uses angleInterpolationWithSpeed for smooth movement
- Step-based increments (like keyboard)
- Async execution (non-blocking)
- Proper joint limits
- Better error handling
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from .. import config

logger = logging.getLogger(__name__)

class BodyController:
    """Controls head, arms, and hands with step-based movements."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.body_speed = config.BODY_SPEED_DEFAULT  # 0.3 default
        
        # Step sizes (radians per command)
        self.head_step = config.HEAD_STEP  # 0.1 rad ≈ 5.7°
        self.arm_step = config.ARM_STEP    # 0.1 rad
        self.wrist_step = config.WRIST_STEP  # 0.2 rad
        
        # State
        self._emergency_stopped = False
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Async executor (allows multiple body parts to move simultaneously)
        self._executor = ThreadPoolExecutor(
            max_workers=4,  # Can move head + both arms at once
            thread_name_prefix="BodyMove"
        )
    
    # ========================================================================
    # HEAD CONTROL
    # ========================================================================
    
    def move_head(self, direction):
        """
        Move head in small increments.
        
        Args:
            direction: 'up', 'down', 'left', 'right'
        """
        if self._emergency_stopped:
            return False
        
        # Get current angles (cached where possible)
        try:
            current_yaw = self.motion.getAngles("HeadYaw", True)[0]
            current_pitch = self.motion.getAngles("HeadPitch", True)[0]
        except:
            logger.warning("Could not get current head angles")
            return False
        
        # Calculate new angles
        new_yaw = current_yaw
        new_pitch = current_pitch
        
        if direction == 'left':
            new_yaw = current_yaw + self.head_step
        elif direction == 'right':
            new_yaw = current_yaw - self.head_step
        elif direction == 'up':
            new_pitch = current_pitch - self.head_step
        elif direction == 'down':
            new_pitch = current_pitch + self.head_step
        else:
            logger.warning(f"Unknown head direction: {direction}")
            return False
        
        # Clamp to limits
        new_yaw = config.clamp(new_yaw, config.HEAD_YAW_MIN, config.HEAD_YAW_MAX)
        new_pitch = config.clamp(new_pitch, config.HEAD_PITCH_MIN, config.HEAD_PITCH_MAX)
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            ["HeadYaw", "HeadPitch"],
            [new_yaw, new_pitch],
            self.body_speed,
            f"Head {direction}"
        )
        
        return True
    
    def reset_head(self):
        """Reset head to center position."""
        if self._emergency_stopped:
            return False
        
        self._executor.submit(
            self._move_joints_smooth,
            ["HeadYaw", "HeadPitch"],
            [0.0, 0.0],
            self.body_speed,
            "Head reset"
        )
        
        return True
    
    # ========================================================================
    # SHOULDER CONTROL (Pitch)
    # ========================================================================
    
    def move_shoulder_pitch(self, side, direction):
        """
        Move shoulder up/down.
        
        Args:
            side: 'L' or 'R'
            direction: 'up' or 'down'
        """
        if self._emergency_stopped:
            return False
        
        joint = f"{side}ShoulderPitch"
        
        try:
            current = self.motion.getAngles(joint, True)[0]
        except:
            logger.warning(f"Could not get {joint} angle")
            return False
        
        # Calculate new angle (negative = up for shoulder pitch)
        if direction == 'up':
            new_angle = current - self.arm_step
        elif direction == 'down':
            new_angle = current + self.arm_step
        else:
            return False
        
        # Clamp
        new_angle = config.clamp(
            new_angle,
            config.SHOULDER_PITCH_MIN,
            config.SHOULDER_PITCH_MAX
        )
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            [joint],
            [new_angle],
            self.body_speed,
            f"{side} shoulder {direction}"
        )
        
        return True
    
    # ========================================================================
    # SHOULDER CONTROL (Roll - out/in)
    # ========================================================================
    
    def move_shoulder_roll(self, side, direction):
        """
        Move arm out/in (shoulder roll).
        
        Args:
            side: 'L' or 'R'
            direction: 'out' or 'in'
        """
        if self._emergency_stopped:
            return False
        
        joint = f"{side}ShoulderRoll"
        
        try:
            current = self.motion.getAngles(joint, True)[0]
        except:
            return False
        
        # Calculate new angle
        if direction == 'out':
            # Left arm: positive = out, Right arm: negative = out
            new_angle = current + self.arm_step if side == 'L' else current - self.arm_step
        elif direction == 'in':
            new_angle = current - self.arm_step if side == 'L' else current + self.arm_step
        else:
            return False
        
        # Clamp to side-specific limits
        if side == 'L':
            new_angle = config.clamp(new_angle, config.L_SHOULDER_ROLL_MIN, config.L_SHOULDER_ROLL_MAX)
        else:
            new_angle = config.clamp(new_angle, config.R_SHOULDER_ROLL_MIN, config.R_SHOULDER_ROLL_MAX)
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            [joint],
            [new_angle],
            self.body_speed,
            f"{side} arm {direction}"
        )
        
        return True
    
    # ========================================================================
    # ELBOW CONTROL
    # ========================================================================
    
    def move_elbow_roll(self, side, direction):
        """
        Bend/straighten elbow.
        
        Args:
            side: 'L' or 'R'
            direction: 'bend' or 'straighten'
        """
        if self._emergency_stopped:
            return False
        
        joint = f"{side}ElbowRoll"
        
        try:
            current = self.motion.getAngles(joint, True)[0]
        except:
            return False
        
        # Calculate new angle
        if direction == 'bend':
            # Left: negative = bend, Right: positive = bend
            new_angle = current - self.arm_step if side == 'L' else current + self.arm_step
        elif direction == 'straighten':
            new_angle = current + self.arm_step if side == 'L' else current - self.arm_step
        else:
            return False
        
        # Clamp
        if side == 'L':
            new_angle = config.clamp(new_angle, config.L_ELBOW_ROLL_MIN, config.L_ELBOW_ROLL_MAX)
        else:
            new_angle = config.clamp(new_angle, config.R_ELBOW_ROLL_MIN, config.R_ELBOW_ROLL_MAX)
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            [joint],
            [new_angle],
            self.body_speed,
            f"{side} elbow {direction}"
        )
        
        return True
    
    # ========================================================================
    # WRIST CONTROL
    # ========================================================================
    
    def rotate_wrist(self, side, direction):
        """
        Rotate wrist.
        
        Args:
            side: 'L' or 'R'
            direction: 'cw' (clockwise) or 'ccw' (counter-clockwise)
        """
        if self._emergency_stopped:
            return False
        
        joint = f"{side}WristYaw"
        
        try:
            current = self.motion.getAngles(joint, True)[0]
        except:
            return False
        
        # Calculate new angle
        if direction == 'cw':
            new_angle = current + self.wrist_step
        elif direction == 'ccw':
            new_angle = current - self.wrist_step
        else:
            return False
        
        # Clamp
        new_angle = config.clamp(new_angle, config.WRIST_YAW_MIN, config.WRIST_YAW_MAX)
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            [joint],
            [new_angle],
            self.body_speed,
            f"{side} wrist {direction}"
        )
        
        return True
    
    # ========================================================================
    # HAND CONTROL
    # ========================================================================
    
    def move_hand(self, side, action):
        """
        Open/close hand.
        
        Args:
            side: 'L' or 'R'
            action: 'open' or 'close'
        """
        if self._emergency_stopped:
            return False
        
        joint = f"{side}Hand"
        
        # Hand is 0.0 = closed, 1.0 = open
        target = 1.0 if action == 'open' else 0.0
        
        # Execute async
        self._executor.submit(
            self._move_joints_smooth,
            [joint],
            [target],
            self.body_speed,
            f"{side} hand {action}"
        )
        
        return True
    
    # ========================================================================
    # SPEED CONTROL
    # ========================================================================
    
    def increase_speed(self):
        """Increase body movement speed."""
        with self._lock:
            self.body_speed = min(self.body_speed + 0.1, 1.0)
            speed = self.body_speed
        
        logger.info(f"⬆️ Body speed: {speed:.2f}")
        return speed
    
    def decrease_speed(self):
        """Decrease body movement speed."""
        with self._lock:
            self.body_speed = max(self.body_speed - 0.1, 0.1)
            speed = self.body_speed
        
        logger.info(f"⬇️ Body speed: {speed:.2f}")
        return speed
    
    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================
    
    def _move_joints_smooth(self, joint_names, angles, speed, description=""):
        """
        Internal method to move joints smoothly.
        Uses angleInterpolationWithSpeed for smooth motion.
        Runs in thread pool (non-blocking).
        """
        if self._emergency_stopped:
            return
        
        try:
            # Use smooth interpolation
            if len(joint_names) == 1:
                self.motion.angleInterpolationWithSpeed(
                    joint_names[0],
                    angles[0],
                    speed
                )
            else:
                self.motion.angleInterpolationWithSpeed(
                    joint_names,
                    angles,
                    speed
                )
            
            if description:
                logger.debug(f"Body: {description}")
        
        except Exception as e:
            logger.error(f"Body movement error: {e}")
    
    def emergency_stop(self):
        """Emergency stop."""
        self._emergency_stopped = True
        logger.error("🚨 EMERGENCY STOP - Body")
    
    def resume_from_emergency(self):
        """Resume from emergency."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared - Body")
    
    def get_state(self):
        """Get current state."""
        with self._lock:
            return {
                'body_speed': self.body_speed,
                'head_step': self.head_step,
                'arm_step': self.arm_step,
                'emergency_stopped': self._emergency_stopped
            }
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up body controller...")
        self._executor.shutdown(wait=False)
        logger.info("✓ Body controller cleaned up")