"""
Base Movement Controller - FULLY DEBUGGED VERSION
Ultra-fast, zero-lag movement with async operations.

FIXES APPLIED:
- Added _was_moving initialization
- Added _last_error initialization
- Fixed emergency stop logic
- Added proper state management
"""

import logging
import threading
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Ultra-responsive base movement controller."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current velocities (direct, no smoothing!)
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        # Accumulated position (for incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        # State tracking
        self._was_moving = False  # FIX: Initialize this!
        self._last_error = None   # FIX: Initialize this!
        self._turbo_enabled = False
        
        # Minimal locking
        self._lock = threading.Lock()
        
        # Emergency stop flag
        self._emergency_stopped = False
    
    def set_continuous_velocity(self, direction, value):
        """
        Set velocity INSTANTLY - no smoothing!
        This is called from keyboard/GUI at high frequency.
        """
        if self._emergency_stopped:
            return
        
        # No lock needed for simple assignment (atomic in Python)
        if direction == 'x':
            self.base_x = value * self.linear_speed
        elif direction == 'y':
            self.base_y = value * self.linear_speed
        elif direction == 'theta':
            self.base_theta = value * self.angular_speed
    
    def move_continuous(self):
        """
        Update base movement - OPTIMIZED!
        Called at 50Hz, so MUST be fast.
        """
        if self._emergency_stopped:
            return
        
        # CRITICAL: Direct command, no thread lock!
        # Pepper's moveToward() is thread-safe
        try:
            # Check if we're actually moving
            is_moving = (abs(self.base_x) > 0.01 or 
                        abs(self.base_y) > 0.01 or 
                        abs(self.base_theta) > 0.01)
            
            if is_moving:
                # Send movement command
                self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                self._was_moving = True
            else:
                # Only send stop if we were previously moving
                if self._was_moving:
                    self.motion.stopMove()
                self._was_moving = False
            
        except Exception as e:
            # Don't spam logs with same error
            if self._last_error != str(e):
                logger.error(f"Movement error: {e}")
                self._last_error = str(e)
    
    def move_incremental(self, direction):
        """Move by a fixed step in incremental mode."""
        if self._emergency_stopped:
            logger.warning("Emergency stop active")
            return
        
        with self._lock:
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
    
    def stop(self):
        """Immediate stop - no delays."""
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        try:
            self.motion.stopMove()
            self._was_moving = False
        except Exception as e:
            logger.error(f"Stop failed: {e}")
    
    def emergency_stop(self):
        """Emergency stop."""
        self._emergency_stopped = True
        self.stop()
        logger.error("🚨 EMERGENCY STOP - Base")
    
    def resume_from_emergency(self):
        """Resume after emergency."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared - Base")
    
    def increase_speed(self):
        """Increase speed - no lock needed."""
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
        """Decrease speed - no lock needed."""
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
        """Toggle turbo mode."""
        self._turbo_enabled = not self._turbo_enabled
        
        if self._turbo_enabled:
            self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
            self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
            logger.info("🚀 Turbo mode: ENABLED")
        else:
            self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
            self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
            logger.info("Turbo mode: DISABLED")
        
        return self._turbo_enabled
    
    def is_moving(self):
        """Check if moving - no lock needed for simple comparison."""
        return (abs(self.base_x) > 0.01 or 
                abs(self.base_y) > 0.01 or 
                abs(self.base_theta) > 0.01)
    
    def get_state(self):
        """Get state - cached to avoid spam."""
        return {
            'x': self.base_x,
            'y': self.base_y,
            'theta': self.base_theta,
            'linear_speed': self.linear_speed,
            'angular_speed': self.angular_speed,
            'emergency_stopped': self._emergency_stopped,
            'is_moving': self.is_moving()
        }