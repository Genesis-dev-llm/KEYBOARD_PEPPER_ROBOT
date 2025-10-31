"""
Base Movement Controller - SIMPLE + ASYNC OPTIMIZED
Proven logic with async optimizations for speed.

TWO MODES:
1. CONTINUOUS: Hold key = moveToward() continuously (async)
2. INCREMENTAL: Click key = moveTo() with accumulated position (async)

OPTIMIZATIONS:
- Async moveToward/moveTo calls (non-blocking)
- Thread pool for parallel execution
- No blocking waits in hot path
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Simple, proven base movement controller with async optimizations."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current velocities (for CONTINUOUS mode)
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        
        # Accumulated position (for INCREMENTAL mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        # State
        self._turbo_enabled = False
        self._emergency_stopped = False
        self._was_moving = False
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Async executor (for non-blocking operations)
        self._executor = ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="BaseMove"
        )
        
        # Command throttling (prevent flooding)
        self._last_command_time = 0
        self._min_command_interval = 0.01  # 10ms minimum between commands
    
    # ========================================================================
    # CONTINUOUS MODE - Hold to move (async optimized)
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
        Execute continuous movement with async optimization.
        Called at 50Hz (20ms) by main update loop.
        
        OPTIMIZATION: Uses async calls so we don't block waiting for NAOqi.
        """
        if self._emergency_stopped:
            return
        
        # Get current velocities (quick, no blocking)
        with self._lock:
            x = self.base_x
            y = self.base_y
            theta = self.base_theta
        
        # Check if we're moving
        is_moving = (abs(x) > 0.01 or abs(y) > 0.01 or abs(theta) > 0.01)
        
        if is_moving:
            # Send movement command ASYNC (non-blocking)
            self._executor.submit(self._async_move_toward, x, y, theta)
            self._was_moving = True
        else:
            # Only stop if we were previously moving
            if self._was_moving:
                self._executor.submit(self._async_stop)
                self._was_moving = False
    
    def _async_move_toward(self, x, y, theta):
        """
        Async wrapper for moveToward.
        Runs in thread pool, doesn't block main loop.
        """
        try:
            self.motion.moveToward(x, y, theta)
        except Exception as e:
            logger.error(f"Movement error: {e}")
    
    def _async_stop(self):
        """
        Async wrapper for stopMove.
        Runs in thread pool, doesn't block main loop.
        """
        try:
            self.motion.stopMove()
        except Exception as e:
            logger.error(f"Stop error: {e}")
    
    # ========================================================================
    # INCREMENTAL MODE - Click to step (async optimized)
    # ========================================================================
    
    def move_incremental(self, direction):
        """
        Move a fixed distance, accumulating position.
        
        OPTIMIZATION: moveTo() call is async, doesn't block input.
        
        Args:
            direction: 'forward', 'back', 'left', 'right', 'rotate_left', 'rotate_right'
        """
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
            
            # Get current accumulated position
            x = self.accumulated_x
            y = self.accumulated_y
            theta = self.accumulated_theta
        
        # Execute movement ASYNC (non-blocking)
        self._executor.submit(self._async_move_to, x, y, theta)
    
    def _async_move_to(self, x, y, theta):
        """
        Async wrapper for moveTo.
        Runs in thread pool, doesn't block input.
        """
        try:
            self.motion.moveTo(x, y, theta)
            logger.info(f"Position: ({x:.2f}, {y:.2f}, {theta:.2f})")
        except Exception as e:
            logger.error(f"Incremental movement failed: {e}")
    
    def reset_position(self):
        """Reset accumulated position to origin."""
        with self._lock:
            self.accumulated_x = 0.0
            self.accumulated_y = 0.0
            self.accumulated_theta = 0.0
        logger.info("Position reset to origin (0, 0, 0)")
    
    # ========================================================================
    # CONTROL
    # ========================================================================
    
    def stop(self):
        """Stop all movement immediately."""
        with self._lock:
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
        
        # Stop SYNC for immediate effect
        try:
            self.motion.stopMove()
            self._was_moving = False
        except Exception as e:
            logger.error(f"Stop failed: {e}")
    
    def emergency_stop(self):
        """Emergency stop - SYNC for safety."""
        self._emergency_stopped = True
        
        with self._lock:
            self.base_x = 0.0
            self.base_y = 0.0
            self.base_theta = 0.0
        
        # Emergency stop is SYNCHRONOUS (blocking) for immediate safety
        try:
            self.motion.stopMove()
            self._was_moving = False
            logger.error("🚨 EMERGENCY STOP - Base")
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
    
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
            speed = self.linear_speed
        
        logger.info(f"⬆️ Speed: {speed:.2f} m/s")
        return speed
    
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
            speed = self.linear_speed
        
        logger.info(f"⬇️ Speed: {speed:.2f} m/s")
        return speed
    
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
                'accumulated_x': self.accumulated_x,
                'accumulated_y': self.accumulated_y,
                'accumulated_theta': self.accumulated_theta,
                'linear_speed': self.linear_speed,
                'angular_speed': self.angular_speed,
                'turbo': self._turbo_enabled,
                'emergency_stopped': self._emergency_stopped,
                'is_moving': self.is_moving()
            }
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up base controller...")
        self.stop()
        self._executor.shutdown(wait=False)
        logger.info("✓ Base controller cleaned up")