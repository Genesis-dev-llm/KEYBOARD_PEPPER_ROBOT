"""
Base Movement Controller - SIMPLE VERSION (Like original chunky code)
Just sends the velocity directly, no fancy smoothing!

THE FIX: Don't smooth inside move_continuous() - just send the target!
"""

import logging
import threading
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Controls Pepper's base movement - SIMPLE working version."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Speed settings (can be adjusted with +/- keys)
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # SIMPLE: Just store target velocities directly
        # No "current" vs "target" - just target!
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        # Accumulated position (for incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        # Safety flag
        self._emergency_stopped = False
    
    def move_continuous(self):
        """
        Update base movement in continuous mode.
        SIMPLE VERSION - just send the velocity!
        """
        with self._lock:
            if self._emergency_stopped:
                return
            
            # THE FIX: Just send the velocity directly, like original code!
            # Pepper's moveToward() does its own smoothing internally!
            if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
                try:
                    self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                except Exception as e:
                    logger.error(f"Movement command failed: {e}")
                    self.stop()
            else:
                # Fully stopped
                try:
                    self.motion.stopMove()
                except Exception as e:
                    logger.error(f"Stop command failed: {e}")
    
    def move_incremental(self, direction):
        """Move by a fixed step in incremental mode."""
        with self._lock:
            if self._emergency_stopped:
                logger.warning("Emergency stop active")
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
            logger.info("Position reset to origin")
    
    def set_continuous_velocity(self, direction, value):
        """
        Set velocity for continuous mode.
        SIMPLE VERSION - set directly, no target/current separation!
        """
        with self._lock:
            if self._emergency_stopped:
                return
            
            # THE FIX: Set directly, don't use "target" variable
            if direction == 'x':
                self.base_x = value * self.linear_speed
            elif direction == 'y':
                self.base_y = value * self.linear_speed
            elif direction == 'theta':
                self.base_theta = value * self.angular_speed
    
    def stop(self):
        """Stop all base movement - IMMEDIATE."""
        with self._lock:
            # Set all to zero
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
            
            try:
                self.motion.stopMove()
            except Exception as e:
                logger.error(f"Stop command failed: {e}")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt."""
        with self._lock:
            logger.error("🚨 EMERGENCY STOP - Base")
            self._emergency_stopped = True
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
            
            try:
                self.motion.stopMove()
            except Exception as e:
                logger.error(f"Emergency stop failed: {e}")
    
    def resume_from_emergency(self):
        """Resume movement after emergency stop."""
        with self._lock:
            self._emergency_stopped = False
            logger.info("✓ Emergency stop cleared")
    
    def increase_speed(self):
        """Increase base movement speed."""
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
            logger.info(f"⬆️ Base speed: {self.linear_speed:.2f} m/s")
            return self.linear_speed
    
    def decrease_speed(self):
        """Decrease base movement speed."""
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
            logger.info(f"⬇️ Base speed: {self.linear_speed:.2f} m/s")
            return self.linear_speed
    
    def toggle_turbo(self):
        """Toggle turbo mode (1.5x speed)."""
        with self._lock:
            if hasattr(self, '_turbo_enabled'):
                self._turbo_enabled = not self._turbo_enabled
            else:
                self._turbo_enabled = True
            
            if self._turbo_enabled:
                self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
                self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
                logger.info("🚀 Turbo mode: ENABLED")
            else:
                self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
                self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
                logger.info("Turbo mode: DISABLED")
            
            return self._turbo_enabled
    
    def get_state(self):
        """Get current movement state."""
        with self._lock:
            return {
                'x': self.base_x,
                'y': self.base_y,
                'theta': self.base_theta,
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