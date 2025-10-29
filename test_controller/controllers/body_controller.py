"""
Body Controller - FULLY DEBUGGED VERSION
Fast, non-blocking arm/head control.

FIXES APPLIED:
- Added missing 'time' import
- Initialize cache dictionaries properly
- Fixed async thread handling
- Added proper error handling
"""

import logging
import threading
import time  # FIX: Was missing this import!
from .. import config

logger = logging.getLogger(__name__)

class BodyController:
    """Ultra-fast body movement controller."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed setting
        self.body_speed = config.BODY_SPEED_DEFAULT
        
        # Cached head position (avoid constant queries)
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        
        # Emergency flag
        self._emergency_stopped = False
        
        # FIX: Initialize cache dictionaries
        self._angle_cache = {}
        self._cache_time = {}
        
        # Thread tracking
        self._active_threads = []
    
    def move_head(self, direction):
        """Move head - FAST version with caching."""
        if self._emergency_stopped:
            return
        
        # Update cached position
        if direction == 'up':
            self.head_pitch = config.clamp_joint('HeadPitch', self.head_pitch + config.HEAD_STEP)
        elif direction == 'down':
            self.head_pitch = config.clamp_joint('HeadPitch', self.head_pitch - config.HEAD_STEP)
        elif direction == 'left':
            self.head_yaw = config.clamp_joint('HeadYaw', self.head_yaw + config.HEAD_STEP)
        elif direction == 'right':
            self.head_yaw = config.clamp_joint('HeadYaw', self.head_yaw - config.HEAD_STEP)
        
        # Send command asynchronously
        self._send_async(["HeadYaw", "HeadPitch"], [self.head_yaw, self.head_pitch])
    
    def reset_head(self):
        """Reset head to center."""
        if self._emergency_stopped:
            return
        
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        self._send_async(["HeadYaw", "HeadPitch"], [0.0, 0.0])
        logger.info("Head reset to center")
    
    def move_shoulder_pitch(self, side, direction):
        """Move shoulder - OPTIMIZED."""
        if self._emergency_stopped:
            return
        
        joint_name = f"{side}ShoulderPitch"
        
        try:
            # Get current (cached if possible)
            current = self._get_cached_angle(joint_name)
            
            # Calculate new
            delta = -config.ARM_STEP if direction == 'up' else config.ARM_STEP
            new_angle = config.clamp_joint(joint_name, current + delta)
            
            # Send async
            self._send_async(joint_name, new_angle)
            
        except Exception as e:
            logger.error(f"Shoulder movement error: {e}")
    
    def move_shoulder_roll(self, side, direction='out'):
        """Move shoulder roll."""
        if self._emergency_stopped:
            return
        
        joint_name = f"{side}ShoulderRoll"
        
        try:
            current = self._get_cached_angle(joint_name)
            
            if side == 'L':
                delta = config.ARM_STEP if direction == 'out' else -config.ARM_STEP
            else:
                delta = -config.ARM_STEP if direction == 'out' else config.ARM_STEP
            
            new_angle = config.clamp_joint(joint_name, current + delta)
            self._send_async(joint_name, new_angle)
            
        except Exception as e:
            logger.error(f"Shoulder roll error: {e}")
    
    def move_elbow_roll(self, side, direction):
        """Move elbow."""
        if self._emergency_stopped:
            return
        
        joint_name = f"{side}ElbowRoll"
        
        try:
            current = self._get_cached_angle(joint_name)
            
            if side == 'L':
                delta = -config.ARM_STEP if direction == 'bend' else config.ARM_STEP
            else:
                delta = config.ARM_STEP if direction == 'bend' else -config.ARM_STEP
            
            new_angle = config.clamp_joint(joint_name, current + delta)
            self._send_async(joint_name, new_angle)
            
        except Exception as e:
            logger.error(f"Elbow error: {e}")
    
    def rotate_wrist(self, side, direction):
        """Rotate wrist."""
        if self._emergency_stopped:
            return
        
        joint_name = f"{side}WristYaw"
        
        try:
            current = self._get_cached_angle(joint_name)
            delta = config.WRIST_STEP if direction == 'ccw' else -config.WRIST_STEP
            new_angle = config.clamp_joint(joint_name, current + delta)
            self._send_async(joint_name, new_angle)
            
        except Exception as e:
            logger.error(f"Wrist error: {e}")
    
    def move_hand(self, side, state):
        """Open/close hand."""
        if self._emergency_stopped:
            return
        
        joint_name = f"{side}Hand"
        value = 1.0 if state == 'open' else 0.0
        
        self._send_async(joint_name, value, speed=0.5)
        logger.debug(f"{joint_name}: {state}")
    
    def _send_async(self, joint_names, angles, speed=None):
        """
        Send command asynchronously - CRITICAL OPTIMIZATION!
        Uses background thread for non-blocking execution.
        """
        if speed is None:
            speed = self.body_speed
        
        # Normalize inputs
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            angles = [angles]
        
        # Launch in background thread (non-blocking)
        def send():
            try:
                self.motion.angleInterpolationWithSpeed(
                    joint_names if len(joint_names) > 1 else joint_names[0],
                    angles if len(angles) > 1 else angles[0],
                    speed
                )
            except Exception as e:
                logger.error(f"Async send error: {e}")
        
        # Fire and forget
        thread = threading.Thread(target=send, daemon=True)
        thread.start()
        
        # Clean up old threads (keep list from growing)
        self._active_threads = [t for t in self._active_threads if t.is_alive()]
        self._active_threads.append(thread)
    
    def _get_cached_angle(self, joint_name):
        """
        Get joint angle with caching to avoid constant queries.
        Only queries robot if cache is stale.
        """
        cache_timeout = 0.5  # 500ms cache
        current_time = time.time()
        
        # Check cache
        if joint_name in self._angle_cache:
            if current_time - self._cache_time.get(joint_name, 0) < cache_timeout:
                return self._angle_cache[joint_name]
        
        # Query robot
        try:
            angle = self.motion.getAngles(joint_name, True)[0]
            self._angle_cache[joint_name] = angle
            self._cache_time[joint_name] = current_time
            return angle
        except Exception as e:
            logger.warning(f"Failed to get angle for {joint_name}: {e}")
            return 0.0
    
    def increase_speed(self):
        """Increase speed."""
        self.body_speed = config.clamp(
            self.body_speed + config.SPEED_STEP,
            config.MIN_SPEED,
            1.0
        )
        logger.info(f"⬆️ Body speed: {self.body_speed:.2f}")
        return self.body_speed
    
    def decrease_speed(self):
        """Decrease speed."""
        self.body_speed = config.clamp(
            self.body_speed - config.SPEED_STEP,
            config.MIN_SPEED,
            1.0
        )
        logger.info(f"⬇️ Body speed: {self.body_speed:.2f}")
        return self.body_speed
    
    def emergency_stop(self):
        """Emergency stop."""
        self._emergency_stopped = True
        logger.error("🚨 EMERGENCY STOP - Body")
    
    def resume_from_emergency(self):
        """Resume."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared - Body")
    
    def get_state(self):
        """Get state."""
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