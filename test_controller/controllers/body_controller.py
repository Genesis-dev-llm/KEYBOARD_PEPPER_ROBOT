"""
Base Movement Controller - SIMPLE & RELIABLE VERSION
No complex accumulation - just direct movement commands.

TWO MODES:
1. CONTINUOUS: Hold key = robot moves (velocity-based)
2. INCREMENTAL: Press key = robot moves fixed distance (moveTo-based)
"""

import logging
import threading
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Simple, reliable base movement controller."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current velocities (for continuous mode)
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        # State
        self._turbo_enabled = False
        self._emergency_stopped = False
        self._was_moving = False
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    # ========================================================================
    # CONTINUOUS MODE (Velocity-based, hold to move)
    # ========================================================================
    
    def set_continuous_velocity(self, direction, value):
        """
        Set velocity for continuous movement.
        Called when keys are pressed/released.
        
        Args:
            direction: 'x', 'y', or 'theta'
            value: -1.0 to 1.0 (multiplied by speed)
        """
        if self._emergency_stopped:
            return
        
        with self._lock:
            if direction == 'x':
                self.base_x = value * self.linear_speed
            elif direction == 'y':
                self.base_y = value * self.linear_speed
            elif direction == 'theta':
                self.base_theta = value * self.angular_speed
    
    def move_continuous(self):
        """
        Execute continuous movement.
        Called at 50Hz by main loop.
        """
        if self._emergency_stopped:
            return
        
        with self._lock:
            # Check if we're moving
            is_moving = (abs(self.base_x) > 0.01 or 
                        abs(self.base_y) > 0.01 or 
                        abs(self.base_theta) > 0.01)
            
            try:
                if is_moving:
                    # Send movement command
                    self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                    self._was_moving = True
                else:
                    # Only stop if we were moving
                    if self._was_moving:
                        self.motion.stopMove()
                        self._was_moving = False
            except Exception as e:
                logger.error(f"Movement error: {e}")
    
    # ========================================================================
    # INCREMENTAL MODE (Fixed distance per click)
    # ========================================================================
    
    def move_incremental(self, direction):
        """
        Move a fixed distance in one direction.
        Simple and reliable - no accumulation.
        
        Args:
            direction: 'forward', 'back', 'left', 'right', 'rotate_left', 'rotate_right'
        """
        if self._emergency_stopped:
            logger.warning("Emergency stop active")
            return
        
        # Define movement amounts
        linear_step = config.LINEAR_STEP  # e.g., 0.1m = 10cm
        angular_step = config.ANGULAR_STEP  # e.g., 0.3 rad = ~17 degrees
        
        # Execute movement based on direction
        try:
            if direction == 'forward':
                logger.debug(f"Moving forward {linear_step}m")
                self.motion.moveTo(linear_step, 0.0, 0.0)
                
            elif direction == 'back':
                logger.debug(f"Moving back {linear_step}m")
                self.motion.moveTo(-linear_step, 0.0, 0.0)
                
            elif direction == 'left':
                logger.debug(f"Strafing left {linear_step}m")
                self.motion.moveTo(0.0, linear_step, 0.0)
                
            elif direction == 'right':
                logger.debug(f"Strafing right {linear_step}m")
                self.motion.moveTo(0.0, -linear_step, 0.0)
                
            elif direction == 'rotate_left':
                logger.debug(f"Rotating left {angular_step} rad")
                self.motion.moveTo(0.0, 0.0, angular_step)
                
            elif direction == 'rotate_right':
                logger.debug(f"Rotating right {angular_step} rad")
                self.motion.moveTo(0.0, 0.0, -angular_step)
            
            else:
                logger.warning(f"Unknown direction: {direction}")
                
        except Exception as e:
            logger.error(f"Incremental movement failed: {e}")
    
    # ========================================================================
    # CONTROL
    # ========================================================================
    
    def stop(self):
        """Stop all movement immediately."""
        with self._lock:
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
        """Resume from emergency stop."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared - Base")
    
    # ========================================================================
    # SPEED CONTROL
    # ========================================================================
    
    def increase_speed(self):
        """Increase movement speed."""
        with self._lock:
            self.linear_speed = min(
                self.linear_speed + config.SPEED_STEP,
                config.MAX_SPEED
            )
            self.angular_speed = min(
                self.angular_speed + config.SPEED_STEP,
                config.MAX_SPEED
            )
        
        logger.info(f"⬆️ Speed: {self.linear_speed:.2f} m/s")
        return self.linear_speed
    
    def decrease_speed(self):
        """Decrease movement speed."""
        with self._lock:
            self.linear_speed = max(
                self.linear_speed - config.SPEED_STEP,
                config.MIN_SPEED
            )
            self.angular_speed = max(
                self.angular_speed - config.SPEED_STEP,
                config.MIN_SPEED
            )
        
        logger.info(f"⬇️ Speed: {self.linear_speed:.2f} m/s")
        return self.linear_speed
    
    def toggle_turbo(self):
        """Toggle turbo mode."""
        self._turbo_enabled = not self._turbo_enabled
        
        with self._lock:
            if self._turbo_enabled:
                self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
                self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT * config.TURBO_MULTIPLIER
                logger.info("🚀 Turbo: ENABLED")
            else:
                self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
                self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
                logger.info("Turbo: DISABLED")
        
        return self._turbo_enabled
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    def is_moving(self):
        """Check if robot is moving."""
        with self._lock:
            return (abs(self.base_x) > 0.01 or 
                   abs(self.base_y) > 0.01 or 
                   abs(self.base_theta) > 0.01)
    
    def get_state(self):
        """Get current state."""
        with self._lock:
            return {
                'x': self.base_x,
                'y': self.base_y,
                'theta': self.base_theta,
                'linear_speed': self.linear_speed,
                'angular_speed': self.angular_speed,
                'turbo': self._turbo_enabled,
                'emergency_stopped': self._emergency_stopped,
                'is_moving': self.is_moving()
            }