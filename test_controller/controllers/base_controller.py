"""
Base Movement Controller
Handles Pepper's wheel-based movement (translation and rotation).
"""

import logging
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Controls Pepper's base movement (wheels)."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings (can be adjusted with +/- keys)
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current movement state (for continuous mode)
        self.base_x = 0.0  # forward/back
        self.base_y = 0.0  # strafe left/right
        self.base_theta = 0.0  # rotation
        
        # Accumulated position (for incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
    
    def move_continuous(self):
        """Update base movement in continuous mode (called repeatedly)."""
        if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
            self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
        else:
            self.motion.stopMove()
    
    def move_incremental(self, direction):
        """Move by a fixed step in incremental mode."""
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
        
        self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
        logger.info(f"Position: ({self.accumulated_x:.2f}, {self.accumulated_y:.2f}, {self.accumulated_theta:.2f})")
    
    def reset_position(self):
        """Reset accumulated position to origin."""
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        logger.info("Position reset to origin (0, 0, 0)")
    
    def set_continuous_velocity(self, direction, value):
        """Set velocity for continuous mode."""
        if direction == 'x':
            self.base_x = value * self.linear_speed
        elif direction == 'y':
            self.base_y = value * self.linear_speed
        elif direction == 'theta':
            self.base_theta = value * self.angular_speed
    
    def stop(self):
        """Stop all base movement."""
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        self.motion.stopMove()
    
    def increase_speed(self):
        """Increase base movement speed."""
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
        """Decrease base movement speed."""
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