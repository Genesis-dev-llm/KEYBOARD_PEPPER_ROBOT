"""
Body Controller
Handles Pepper's upper body: head, arms, wrists, and hands.

PHASE 1 IMPROVEMENTS:
- Added thread safety with locks
- Better error handling
- Joint state tracking
- Emergency stop support
"""

import logging
import threading
from .. import config

logger = logging.getLogger(__name__)

class BodyController:
    """Controls Pepper's head, arms, wrists, and hands - Thread-safe version."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Body movement speed (can be adjusted with [/] keys)
        self.body_speed = config.BODY_SPEED_DEFAULT
        
        # Current head position
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        
        # Safety flag
        self._emergency_stopped = False
    
    # ========================================================================
    # HEAD CONTROL
    # ========================================================================
    
    def move_head(self, direction):
        """Move head incrementally (thread-safe)."""
        with self._lock:
            if self._emergency_stopped:
                logger.warning("Emergency stop active - movement blocked")
                return
            
            if direction == 'up':
                self.head_pitch = config.clamp_joint(
                    'HeadPitch',
                    self.head_pitch + config.HEAD_STEP
                )
            elif direction == 'down':
                self.head_pitch = config.clamp_joint(
                    'HeadPitch',
                    self.head_pitch - config.HEAD_STEP
                )
            elif direction == 'left':
                self.head_yaw = config.clamp_joint(
                    'HeadYaw',
                    self.head_yaw + config.HEAD_STEP
                )
            elif direction == 'right':
                self.head_yaw = config.clamp_joint(
                    'HeadYaw',
                    self.head_yaw - config.HEAD_STEP
                )
            
            try:
                self.motion.setAngles(
                    ["HeadYaw", "HeadPitch"], 
                    [self.head_yaw, self.head_pitch], 
                    self.body_speed
                )
                logger.info(f"Head: yaw={self.head_yaw:.2f}, pitch={self.head_pitch:.2f}")
            except Exception as e:
                logger.error(f"Head movement failed: {e}")
    
    def reset_head(self):
        """Reset head to center position (thread-safe)."""
        with self._lock:
            self.head_yaw = 0.0
            self.head_pitch = 0.0
            
            try:
                self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], self.body_speed)
                logger.info("Head reset to center")
            except Exception as e:
                logger.error(f"Head reset failed: {e}")
    
    # ========================================================================
    # ARM CONTROL - SHOULDERS
    # ========================================================================
    
    def move_shoulder_pitch(self, side, direction):
        """Move shoulder pitch (up/down) - Thread-safe."""
        with self._lock:
            if self._emergency_stopped:
                return
            
            joint_name = f"{side}ShoulderPitch"
            
            try:
                current = self.motion.getAngles(joint_name, True)[0]
                
                if direction == 'up':
                    new_angle = current - config.ARM_STEP
                else:  # down
                    new_angle = current + config.ARM_STEP
                
                new_angle = config.clamp_joint(joint_name, new_angle)
                self.motion.setAngles(joint_name, new_angle, self.body_speed)
                logger.info(f"{joint_name}: {new_angle:.2f}")
            except Exception as e:
                logger.error(f"Shoulder movement failed: {e}")
    
    def move_shoulder_roll(self, side, direction='out'):
        """Move shoulder roll (extend arm sideways) - Thread-safe."""
        with self._lock:
            if self._emergency_stopped:
                return
            
            joint_name = f"{side}ShoulderRoll"
            
            try:
                current = self.motion.getAngles(joint_name, True)[0]
                
                if side == 'L':
                    # Left arm: positive = out
                    new_angle = current + config.ARM_STEP if direction == 'out' else current - config.ARM_STEP
                else:  # Right arm
                    # Right arm: negative = out
                    new_angle = current - config.ARM_STEP if direction == 'out' else current + config.ARM_STEP
                
                new_angle = config.clamp_joint(joint_name, new_angle)
                self.motion.setAngles(joint_name, new_angle, self.body_speed)
                logger.info(f"{joint_name}: {new_angle:.2f}")
            except Exception as e:
                logger.error(f"Shoulder roll failed: {e}")
    
    # ========================================================================
    # ARM CONTROL - ELBOWS
    # ========================================================================
    
    def move_elbow_roll(self, side, direction):
        """Move elbow roll (bend/straighten) - Thread-safe."""
        with self._lock:
            if self._emergency_stopped:
                return
            
            joint_name = f"{side}ElbowRoll"
            
            try:
                current = self.motion.getAngles(joint_name, True)[0]
                
                if side == 'L':
                    # Left arm: more negative = more bent
                    if direction == 'bend':
                        new_angle = current - config.ARM_STEP
                    else:  # straighten
                        new_angle = current + config.ARM_STEP
                else:  # Right arm
                    # Right arm: more positive = more bent
                    if direction == 'bend':
                        new_angle = current + config.ARM_STEP
                    else:  # straighten
                        new_angle = current - config.ARM_STEP
                
                new_angle = config.clamp_joint(joint_name, new_angle)
                self.motion.setAngles(joint_name, new_angle, self.body_speed)
                logger.info(f"{joint_name}: {new_angle:.2f}")
            except Exception as e:
                logger.error(f"Elbow movement failed: {e}")
    
    # ========================================================================
    # WRIST CONTROL
    # ========================================================================
    
    def rotate_wrist(self, side, direction):
        """Rotate wrist - Thread-safe."""
        with self._lock:
            if self._emergency_stopped:
                return
            
            joint_name = f"{side}WristYaw"
            
            try:
                current = self.motion.getAngles(joint_name, True)[0]
                
                if direction == 'ccw':  # Counter-clockwise
                    new_angle = current + config.WRIST_STEP
                else:  # cw (clockwise)
                    new_angle = current - config.WRIST_STEP
                
                new_angle = config.clamp_joint(joint_name, new_angle)
                self.motion.setAngles(joint_name, new_angle, self.body_speed)
                logger.info(f"{joint_name} rotated: {new_angle:.2f}")
            except Exception as e:
                logger.error(f"Wrist rotation failed: {e}")
    
    # ========================================================================
    # HAND CONTROL
    # ========================================================================
    
    def move_hand(self, side, state):
        """Open or close hand - Thread-safe."""
        with self._lock:
            if self._emergency_stopped:
                return
            
            joint_name = f"{side}Hand"
            value = 1.0 if state == 'open' else 0.0
            
            try:
                self.motion.setAngles(joint_name, value, 0.3)
                logger.info(f"{joint_name} {state}")
            except Exception as e:
                logger.error(f"Hand movement failed: {e}")
    
    # ========================================================================
    # SPEED CONTROL
    # ========================================================================
    
    def increase_speed(self):
        """Increase body movement speed (thread-safe)."""
        with self._lock:
            self.body_speed = config.clamp(
                self.body_speed + config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            logger.info(f"Body speed increased: {self.body_speed:.2f}")
            return self.body_speed
    
    def decrease_speed(self):
        """Decrease body movement speed (thread-safe)."""
        with self._lock:
            self.body_speed = config.clamp(
                self.body_speed - config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            logger.info(f"Body speed decreased: {self.body_speed:.2f}")
            return self.body_speed
    
    # ========================================================================
    # EMERGENCY CONTROL
    # ========================================================================
    
    def emergency_stop(self):
        """Emergency stop - blocks all body movement."""
        with self._lock:
            logger.error("🚨 EMERGENCY STOP - Body movement")
            self._emergency_stopped = True
    
    def resume_from_emergency(self):
        """Resume movement after emergency stop."""
        with self._lock:
            self._emergency_stopped = False
            logger.info("✓ Emergency stop cleared - body movement enabled")
    
    # ========================================================================
    # STATE QUERIES
    # ========================================================================
    
    def get_state(self):
        """Get current body state (thread-safe)."""
        with self._lock:
            return {
                'head_yaw': self.head_yaw,
                'head_pitch': self.head_pitch,
                'body_speed': self.body_speed,
                'emergency_stopped': self._emergency_stopped
            }
    
    def get_joint_angles(self, joint_names):
        """Get current joint angles safely."""
        try:
            return self.motion.getAngles(joint_names, True)
        except Exception as e:
            logger.error(f"Failed to get joint angles: {e}")
            return [0.0] * len(joint_names)