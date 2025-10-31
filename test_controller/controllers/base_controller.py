"""
Base Movement Controller - SIMPLIFIED & RELIABLE
Uses only incremental movements (step-based) for predictable behavior.

IMPROVEMENTS:
- Removed complex continuous mode (source of lag)
- Single reliable movement mode: step-based
- Async execution for non-blocking
- Better error handling
- Cleaner state management
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from .. import config

logger = logging.getLogger(__name__)

class BaseController:
    """Simple, reliable step-based movement controller."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Speed settings
        self.linear_speed = config.BASE_LINEAR_SPEED_DEFAULT
        self.angular_speed = config.BASE_ANGULAR_SPEED_DEFAULT
        
        # Current step sizes
        self.linear_step = config.LINEAR_STEP  # 0.1m = 10cm
        self.angular_step = config.ANGULAR_STEP  # 0.3 rad ≈ 17°
        
        # State
        self._turbo_enabled = False
        self._emergency_stopped = False
        self._moving = False
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Async executor (max 1 movement at a time)
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="BaseMove"
        )
        
        # Movement queue to prevent spam
        self._pending_movement = None
    
    # ========================================================================
    # MOVEMENT - Simple step-based system
    # ========================================================================
    
    def move_step(self, direction):
        """
        Move one step in the given direction.
        Non-blocking, queues movement if one is already executing.
        
        Args:
            direction: 'forward', 'back', 'left', 'right', 
                      'rotate_left', 'rotate_right'
        """
        if self._emergency_stopped:
            logger.warning("Emergency stop active")
            return False
        
        # Calculate movement parameters
        x, y, theta = 0.0, 0.0, 0.0
        
        if direction == 'forward':
            x = self.linear_step
        elif direction == 'back':
            x = -self.linear_step
        elif direction == 'left':
            y = self.linear_step
        elif direction == 'right':
            y = -self.linear_step
        elif direction == 'rotate_left':
            theta = self.angular_step
        elif direction == 'rotate_right':
            theta = -self.angular_step
        else:
            logger.warning(f"Unknown direction: {direction}")
            return False
        
        # Apply turbo multiplier
        if self._turbo_enabled:
            x *= config.TURBO_MULTIPLIER
            y *= config.TURBO_MULTIPLIER
            theta *= config.TURBO_MULTIPLIER
        
        # Submit async (non-blocking)
        self._executor.submit(self._execute_movement, x, y, theta, direction)
        return True
    
    def _execute_movement(self, x, y, theta, direction):
        """
        Internal method to execute movement.
        Runs in thread pool, doesn't block caller.
        """
        with self._lock:
            if self._emergency_stopped:
                return
            
            self._moving = True
        
        try:
            # Execute moveTo with speed control
            # moveTo is blocking, but we're in a thread so it's fine
            self.motion.moveTo(x, y, theta)
            
            logger.debug(f"Moved {direction}: ({x:.2f}, {y:.2f}, {theta:.2f})")
            
        except Exception as e:
            logger.error(f"Movement failed: {e}")
        finally:
            with self._lock:
                self._moving = False
    
    # ========================================================================
    # CONTROL
    # ========================================================================
    
    def stop(self):
        """Stop all movement immediately (blocking for safety)."""
        with self._lock:
            self._moving = False
        
        try:
            self.motion.stopMove()
            logger.debug("Movement stopped")
        except Exception as e:
            logger.error(f"Stop failed: {e}")
    
    def emergency_stop(self):
        """Emergency stop - highest priority."""
        self._emergency_stopped = True
        
        with self._lock:
            self._moving = False
        
        try:
            self.motion.stopMove()
            self.motion.killMove()  # Force kill
            logger.error("🚨 EMERGENCY STOP")
        except Exception as e:
            logger.error(f"Emergency stop error: {e}")
    
    def resume_from_emergency(self):
        """Resume from emergency stop."""
        self._emergency_stopped = False
        logger.info("✓ Emergency cleared")
    
    # ========================================================================
    # SPEED CONTROL
    # ========================================================================
    
    def increase_speed(self):
        """Increase step size."""
        with self._lock:
            self.linear_step = min(
                self.linear_step + 0.05,  # 5cm increments
                0.5  # Max 50cm per step
            )
            self.angular_step = min(
                self.angular_step + 0.1,  # ~6° increments
                1.57  # Max 90° per step
            )
            step = self.linear_step
        
        logger.info(f"⬆️ Step size: {step:.2f}m")
        return step
    
    def decrease_speed(self):
        """Decrease step size."""
        with self._lock:
            self.linear_step = max(
                self.linear_step - 0.05,
                0.05  # Min 5cm per step
            )
            self.angular_step = max(
                self.angular_step - 0.1,
                0.1  # Min ~6° per step
            )
            step = self.linear_step
        
        logger.info(f"⬇️ Step size: {step:.2f}m")
        return step
    
    def toggle_turbo(self):
        """Toggle turbo mode."""
        self._turbo_enabled = not self._turbo_enabled
        
        status = "ENABLED 🚀" if self._turbo_enabled else "DISABLED"
        logger.info(f"Turbo: {status}")
        
        return self._turbo_enabled
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    def is_moving(self):
        """Check if currently executing a movement."""
        with self._lock:
            return self._moving
    
    def get_state(self):
        """Get current state."""
        with self._lock:
            return {
                'linear_step': self.linear_step,
                'angular_step': self.angular_step,
                'turbo': self._turbo_enabled,
                'emergency_stopped': self._emergency_stopped,
                'is_moving': self._moving
            }
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up base controller...")
        self.stop()
        self._executor.shutdown(wait=False)
        logger.info("✓ Base controller cleaned up")