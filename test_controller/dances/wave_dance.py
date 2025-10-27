"""
MODULE: test_controller/dances/wave_dance.py
Wave Dance Animation - FIXED VERSION
Simple friendly wave gesture with smooth, natural motion.

FIXED: Changed all setAngles() to angleInterpolationWithSpeed()
"""

import time
import logging
from .base_dance import BaseDance

logger = logging.getLogger(__name__)

class WaveDance(BaseDance):
    """Simple wave animation - smooth version."""
    
    def perform(self):
        """Perform wave animation."""
        logger.info("🎭 Starting Wave animation...")
        self.log_progress(1, 5)
        
        if not self.ensure_stiffness():
            return
        
        # === PHASE 1: Raise arm ===
        logger.debug("Phase 1: Raising arm")
        if not self.safe_set_angles_smooth("RShoulderPitch", -0.5, 0.25, "Raise arm"):
            return
        if not self.safe_wait(0.4):
            return
        
        self.log_progress(2, 5)
        
        # === PHASE 2: Extend arm sideways ===
        logger.debug("Phase 2: Extending sideways")
        if not self.safe_set_angles_smooth("RShoulderRoll", -1.2, 0.25, "Extend sideways"):
            return
        if not self.safe_wait(0.4):
            return
        
        self.log_progress(3, 5)
        
        # === PHASE 3: Bend elbow ===
        logger.debug("Phase 3: Bending elbow")
        if not self.safe_set_angles_smooth("RElbowRoll", 1.4, 0.25, "Bend elbow"):
            return
        if not self.safe_wait(0.4):
            return
        
        self.log_progress(4, 5)
        
        # === PHASE 4: Wave wrist (smoother motion) ===
        logger.debug("Phase 4: Waving")
        
        wave_angles = [-0.8, 0.8, -0.8, 0.8, 0.0]  # End at neutral
        wave_speed = 0.5  # Faster for natural wave
        
        for i, angle in enumerate(wave_angles):
            if self.should_abort():
                break
            
            if not self.safe_set_angles_smooth("RWristYaw", angle, wave_speed, f"Wave {i+1}"):
                return
            
            if not self.safe_wait(0.25):
                return
        
        self.log_progress(5, 5)
        
        # === PHASE 5: Return to stand ===
        logger.debug("Phase 5: Returning to stand")
        if not self.return_to_stand(0.5):
            logger.warning("Failed to return to stand cleanly")
        
        logger.info("✓ Wave animation complete")
    
    def safe_set_angles_smooth(self, joint_names, angles, speed, description=""):
        """
        Safely set joint angles using angleInterpolationWithSpeed (SMOOTH).
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
            # FIXED: Use angleInterpolationWithSpeed for smooth movement
            self.motion.angleInterpolationWithSpeed(
                joint_names if len(joint_names) > 1 else joint_names[0],
                clamped_angles if len(clamped_angles) > 1 else clamped_angles[0],
                speed
            )
            
            if description:
                logger.debug(f"Dance move: {description}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set angles: {e}")
            return False