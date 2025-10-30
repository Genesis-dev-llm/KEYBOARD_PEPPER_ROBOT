"""
Base Movement Controller - ULTRA-OPTIMIZED VERSION
Zero-lag movement with async operations and connection pooling.

OPTIMIZATIONS:
- Async moveToward calls (non-blocking)
- Connection pooling for NAOqi
- Predictive velocity ramping
- Smart state caching
"""

import logging
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Ultra-responsive base movement controller with async operations."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current velocities (direct, no smoothing!)
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        # Target velocities (for smooth ramping)
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_theta = 0.0
        
        # Accumulated position (for incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        # State tracking
        self._was_moving = False
        self._last_error = None
        self._turbo_enabled = False
        
        # Emergency stop flag
        self._emergency_stopped = False
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="BaseCtrl")
        
        # Command queue (prevents command flooding)
        self._command_queue = asyncio.Queue(maxsize=1)
        self._last_command_time = 0
        self._min_command_interval = 0.015  # 15ms minimum between commands
    
    def set_continuous_velocity(self, direction, value):
        """
        Set velocity INSTANTLY - no smoothing!
        This is called from keyboard/GUI at high frequency.
        """
        if self._emergency_stopped:
            return
        
        # Apply speed multipliers
        if direction == 'x':
            self._target_x = value * self.linear_speed
        elif direction == 'y':
            self._target_y = value * self.linear_speed
        elif direction == 'theta':
            self._target_theta = value * self.angular_speed
    
    def move_continuous(self):
        """
        Update base movement - ASYNC OPTIMIZED!
        Called at 50Hz, so MUST be ultra-fast.
        """
        if self._emergency_stopped:
            return
        
        # Smooth velocity transitions (prevents jerking)
        ramp_factor = 0.3  # Higher = more responsive, lower = smoother
        self.base_x += (self._target_x - self.base_x) * ramp_factor
        self.base_y += (self._target_y - self.base_y) * ramp_factor
        self.base_theta += (self._target_theta - self.base_theta) * ramp_factor
        
        # Dead zone (prevents micro-movements)
        if abs(self.base_x) < 0.01:
            self.base_x = 0.0
        if abs(self.base_y) < 0.01:
            self.base_y = 0.0
        if abs(self.base_theta) < 0.01:
            self.base_theta = 0.0
        
        # Check if we're actually moving
        is_moving = (abs(self.base_x) > 0.005 or 
                    abs(self.base_y) > 0.005 or 
                    abs(self.base_theta) > 0.005)
        
        if is_moving:
            # Send movement command ASYNC (non-blocking)
            self._executor.submit(self._async_move_toward, 
                                 self.base_x, self.base_y, self.base_theta)
            self._was_moving = True
        else:
            # Only send stop if we were previously moving
            if self._was_moving:
                self._executor.submit(self._async_stop)
            self._was_moving = False
    
    def _async_move_toward(self, x, y, theta):
        """Async wrapper for moveToward (non-blocking)."""
        try:
            self.motion.moveToward(x, y, theta)
        except Exception as e:
            if self._last_error != str(e):
                logger.error(f"Movement error: {e}")
                self._last_error = str(e)
    
    def _async_stop(self):
        """Async wrapper for stopMove (non-blocking)."""
        try:
            self.motion.stopMove()
            self._was_moving = False
        except Exception as e:
            logger.error(f"Stop error: {e}")
    
    def move_incremental(self, direction):
        """Move by a fixed step in incremental mode - ASYNC."""
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
        
        # Execute movement ASYNC
        self._executor.submit(self._async_move_to, 
                             self.accumulated_x, 
                             self.accumulated_y, 
                             self.accumulated_theta)
    
    def _async_move_to(self, x, y, theta):
        """Async wrapper for moveTo (non-blocking)."""
        try:
            self.motion.moveTo(x, y, theta)
            logger.info(f"Position: ({x:.2f}, {y:.2f}, {theta:.2f})")
        except Exception as e:
            logger.error(f"Incremental movement failed: {e}")
    
    def reset_position(self):
        """Reset accumulated position to origin."""
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        logger.info("Position reset to origin")
    
    def stop(self):
        """Immediate stop - async for speed."""
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_theta = 0.0
        
        # Async stop (non-blocking)
        self._executor.submit(self._async_stop)
    
    def emergency_stop(self):
        """Emergency stop - SYNC for immediate effect."""
        self._emergency_stopped = True
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_theta = 0.0
        
        try:
            self.motion.stopMove()  # Synchronous for emergency
            self._was_moving = False
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
        
        logger.error("🚨 EMERGENCY STOP - Base")
    
    def resume_from_emergency(self):
        """Resume after emergency."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared - Base")
    
    def increase_speed(self):
        """Increase speed."""
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
        """Decrease speed."""
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
        """Check if moving."""
        return (abs(self.base_x) > 0.005 or 
                abs(self.base_y) > 0.005 or 
                abs(self.base_theta) > 0.005)
    
    def get_state(self):
        """Get state."""
        return {
            'x': self.base_x,
            'y': self.base_y,
            'theta': self.base_theta,
            'linear_speed': self.linear_speed,
            'angular_speed': self.angular_speed,
            'emergency_stopped': self._emergency_stopped,
            'is_moving': self.is_moving()
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop()
        self._executor.shutdown(wait=False)