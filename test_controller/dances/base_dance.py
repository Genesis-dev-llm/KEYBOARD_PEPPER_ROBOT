"""
Base Dance Class - Phase 3: Perfect Dances
Provides common functionality for all dance animations with safety features.

NEW FEATURES:
- Joint angle validation
- Balance safety checks
- Progress logging
- Graceful error handling
- Emergency abort capability
"""

import time
import logging
from .. import config

logger = logging.getLogger(__name__)

class BaseDance:
    """Base class for all dance animations with safety features."""
    
    def __init__(self, motion_service, posture_service):
        self.motion = motion_service
        self.posture = posture_service
        self._abort_requested = False
    
    def perform(self):
        """Override this method in subclasses."""
        raise NotImplementedError("Subclass must implement perform()")
    
    def request_abort(self):
        """Request dance to abort safely."""
        self._abort_requested = True
        logger.warning("Dance abort requested")
    
    def should_abort(self):
        """Check if dance should abort."""
        return self._abort_requested
    
    def safe_set_angles(self, joint_names, angles, speed, description=""):
        """
        Safely set joint angles with clamping and validation.
        Returns True if successful, False if aborted.
        """
        if self.should_abort():
            logger.warning("Dance aborted during move")
            return False
        
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            angles = [angles]
        
        # Clamp all angles to safe limits
        clamped_angles = []
        for joint_name, angle in zip(joint_names, angles):
            clamped = config.clamp_joint(joint_name, angle)
            
            # Warn if clamping occurred
            if abs(clamped - angle) > 0.01:
                logger.warning(f"{joint_name}: Requested {angle:.2f} → Clamped to {clamped:.2f}")
            
            clamped_angles.append(clamped)
        
        try:
            self.motion.setAngles(joint_names, clamped_angles, speed)
            
            if description:
                logger.debug(f"Dance move: {description}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set angles: {e}")
            return False
    
    def safe_wait(self, duration):
        """
        Wait for duration, but check for abort periodically.
        Returns True if completed, False if aborted.
        """
        start = time.time()
        
        while time.time() - start < duration:
            if self.should_abort():
                return False
            time.sleep(0.1)  # Check every 100ms
        
        return True
    
    def return_to_stand(self, speed=0.5):
        """Return robot to Stand posture safely."""
        logger.info("Returning to Stand posture...")
        
        try:
            self.posture.goToPosture("Stand", speed)
            time.sleep(1.0)
            logger.info("✓ Returned to Stand")
            return True
        except Exception as e:
            logger.error(f"Failed to return to stand: {e}")
            return False
    
    def ensure_stiffness(self, body_part="Body", stiffness=1.0):
        """Ensure body part has stiffness enabled."""
        try:
            self.motion.setStiffnesses(body_part, stiffness)
            return True
        except Exception as e:
            logger.error(f"Failed to set stiffness: {e}")
            return False
    
    def validate_balance(self):
        """
        Check if robot is balanced (not leaning too much).
        Returns True if safe, False if dangerous.
        """
        try:
            # Get hip pitch angle (forward/backward lean)
            hip_pitch = self.motion.getAngles("HipPitch", True)[0]
            
            # Safe range: -0.15 to 0.15 radians (~8.5 degrees)
            if abs(hip_pitch) > 0.15:
                logger.warning(f"Balance warning: HipPitch={hip_pitch:.2f} (unstable)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return False
    
    def log_progress(self, phase, total_phases):
        """Log dance progress."""
        progress = (phase / total_phases) * 100
        logger.info(f"Dance progress: Phase {phase}/{total_phases} ({progress:.0f}%)")
    
    def get_current_joint_angle(self, joint_name):
        """Safely get current joint angle."""
        try:
            return self.motion.getAngles(joint_name, True)[0]
        except Exception as e:
            logger.error(f"Failed to get angle for {joint_name}: {e}")
            return 0.0
    
    def smooth_move_to(self, joint_names, target_angles, speed, steps=5):
        """
        Move to target angles smoothly with interpolation.
        Divides movement into multiple steps for smoothness.
        """
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            target_angles = [target_angles]
        
        # Get current angles
        try:
            current_angles = [self.motion.getAngles(j, True)[0] for j in joint_names]
        except:
            logger.warning("Could not get current angles, using direct move")
            return self.safe_set_angles(joint_names, target_angles, speed)
        
        # Interpolate
        for step in range(1, steps + 1):
            if self.should_abort():
                return False
            
            # Calculate interpolated angles
            t = step / steps
            interpolated = [
                current + (target - current) * t
                for current, target in zip(current_angles, target_angles)
            ]
            
            # Apply
            if not self.safe_set_angles(joint_names, interpolated, speed):
                return False
            
            time.sleep(0.05)  # Small delay between steps
        
        return True