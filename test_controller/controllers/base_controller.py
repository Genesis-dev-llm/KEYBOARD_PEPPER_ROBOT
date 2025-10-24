"""
Base Movement Controller
Handles Pepper's wheel-based movement (translation and rotation).

PHASE 1 IMPROVEMENTS:
- Added thread safety with locks
- Added velocity smoothing/ramping
- Better error handling
- Movement state tracking
"""

import logging
import threading
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Controls Pepper's base movement (wheels) - Thread-safe version."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Speed settings (can be adjusted with +/- keys)
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current movement state (for continuous mode)
        self.base_x = 0.0  # forward/back
        self.base_y = 0.0  # strafe left/right
        self.base_theta = 0.0  # rotation
        
        # Target velocities (for smooth ramping)
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_theta = 0.0
        
        # Smoothing parameters
        self._smoothing_factor = 0.3  # How fast to reach target (0=instant, 1=never)
        
        # Accumulated position (for incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        # Safety flag
        self._emergency_stopped = False
    
    def move_continuous(self):
        """Update base movement in continuous mode (called repeatedly at 20Hz)."""
        with self._lock:
            # Don't move if emergency stopped
            if self._emergency_stopped:
                return
            
            # Smooth velocity ramping (prevents jerky movement)
            self.base_x += (self._target_x - self.base_x) * self._smoothing_factor
            self.base_y += (self._target_y - self.base_y) * self._smoothing_factor
            self.base_theta += (self._target_theta - self.base_theta) * self._smoothing_factor
            
            # Only send command if moving (save bandwidth)
            if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
                try:
                    self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                except Exception as e:
                    logger.error(f"Movement command failed: {e}")
                    self.stop()
            else:
                # Stopped - ensure robot knows
                try:
                    self.motion.stopMove()
                except Exception as e:
                    logger.error(f"Stop command failed: {e}")
    
    def move_incremental(self, direction):
        """Move by a fixed step in incremental mode (thread-safe)."""
        with self._lock:
            if self._emergency_stopped:
                logger.warning("Emergency stop active - movement blocked")
                return
            
            # Update accumulated position
            if direction == 'forward':
                self.accumulated_x += config.LINEAR_STEP
            elif direction == 'back':
                self.accumulated_x -= config.LINEAR_STEP
            elif direction == 'left':
                self.accumulated_y += config.LINEAR_STEP
            elif direction == 'right':
                self.accumulated_y -= config.LINEAR_STEP
            elif direction == 'rotate_left':
                self.accumulated_theta += config.ANGULAR_STEP
            elif direction == 'rotate_right':
                self.accumulated_theta -= config.ANGULAR_STEP
            
            # Execute movement
            try:
                self.motion.moveTo(
                    self.accumulated_x, 
                    self.accumulated_y, 
                    self.accumulated_theta
                )
                logger.info(f"Position: ({self.accumulated_x:.2f}, "
                          f"{self.accumulated_y:.2f}, {self.accumulated_theta:.2f})")
            except Exception as e:
                logger.error(f"Incremental movement failed: {e}")
    
    def reset_position(self):
        """Reset accumulated position to origin."""
        with self._lock:
            self.accumulated_x = 0.0
            self.accumulated_y = 0.0
            self.accumulated_theta = 0.0
            logger.info("Position reset to origin (0, 0, 0)")
    
    def set_continuous_velocity(self, direction, value):
        """
        Set target velocity for continuous mode (thread-safe).
        Actual velocity will ramp smoothly to this target.
        """
        with self._lock:
            if self._emergency_stopped:
                return
            
            # Set target velocity (will be ramped to smoothly)
            if direction == 'x':
                self._target_x = value * self.linear_speed
            elif direction == 'y':
                self._target_y = value * self.linear_speed
            elif direction == 'theta':
                self._target_theta = value * self.angular_speed
    
    def stop(self):
        """Stop all base movement (thread-safe)."""
        with self._lock:
            # Reset both current and target velocities
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
            self._target_x = 0.0
            self._target_y = 0.0
            self._target_theta = 0.0
            
            try:
                self.motion.stopMove()
            except Exception as e:
                logger.error(f"Stop command failed: {e}")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt, blocks future movement."""
        with self._lock:
            logger.error("🚨 EMERGENCY STOP - Base movement")
            self._emergency_stopped = True
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
            self._target_x = 0.0
            self._target_y = 0.0
            self._target_theta = 0.0
            
            try:
                self.motion.stopMove()
            except Exception as e:
                logger.error(f"Emergency stop failed: {e}")
    
    def resume_from_emergency(self):
        """Resume movement after emergency stop."""
        with self._lock:
            self._emergency_stopped = False
            logger.info("✓ Emergency stop cleared - movement enabled")
    
    def increase_speed(self):
        """Increase base movement speed (thread-safe)."""
        with self._lock:
            self.linear_speed = config.clamp(
                self.linear_speed + config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            self.angular_speed = config.clamp(
                self.angular_speed + config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            logger.info(f"Base speed increased: {self.linear_speed:.2f} m/s")
            return self.linear_speed
    
    def decrease_speed(self):
        """Decrease base movement speed (thread-safe)."""
        with self._lock:
            self.linear_speed = config.clamp(
                self.linear_speed - config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            self.angular_speed = config.clamp(
                self.angular_speed - config.SPEED_STEP,
                config.MIN_SPEED,
                config.MAX_SPEED
            )
            logger.info(f"Base speed decreased: {self.linear_speed:.2f} m/s")
            return self.linear_speed
    
    def get_state(self):
        """Get current movement state (thread-safe)."""
        with self._lock:
            return {
                'x': self.base_x,
                'y': self.base_y,
                'theta': self.base_theta,
                'target_x': self._target_x,
                'target_y': self._target_y,
                'target_theta': self._target_theta,
                'linear_speed': self.linear_speed,
                'angular_speed': self.angular_speed,
                'emergency_stopped': self._emergency_stopped
            }
    
    def is_moving(self):
        """Check if robot is currently moving."""
        with self._lock:
            return (abs(self.base_x) > 0.01 or 
                   abs(self.base_y) > 0.01 or 
                   abs(self.base_theta) > 0.01)