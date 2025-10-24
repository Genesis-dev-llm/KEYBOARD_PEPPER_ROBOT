"""
Wave Dance Animation - Phase 3: Perfect Version
Simple friendly wave gesture with smooth, natural motion.

IMPROVEMENTS:
- Smoother wrist motion
- Better timing
- Natural arm position
- Graceful return
"""

import time
import logging
from .base_dance import BaseDance

logger = logging.getLogger(__name__)

class WaveDance(BaseDance):
    """Simple wave animation - perfected."""
    
    def perform(self):
        """Perform wave animation."""
        logger.info("🎭 Starting Wave animation...")
        self.log_progress(1, 5)
        
        if not self.ensure_stiffness():
            return
        
        # === PHASE 1: Raise arm ===
        logger.debug("Phase 1: Raising arm")
        if not self.safe_set_angles("RShoulderPitch", -0.5, 0.25, "Raise arm"):
            return
        if not self.safe_wait(0.4):
            return
        
        self.log_progress(2, 5)
        
        # === PHASE 2: Extend arm sideways ===
        logger.debug("Phase 2: Extending sideways")
        if not self.safe_set_angles("RShoulderRoll", -1.2, 0.25, "Extend sideways"):
            return
        if not self.safe_wait(0.4):
            return
        
        self.log_progress(3, 5)
        
        # === PHASE 3: Bend elbow ===
        logger.debug("Phase 3: Bending elbow")
        if not self.safe_set_angles("RElbowRoll", 1.4, 0.25, "Bend elbow"):
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
            
            if not self.safe_set_angles("RWristYaw", angle, wave_speed, f"Wave {i+1}"):
                return
            
            if not self.safe_wait(0.25):
                return
        
        self.log_progress(5, 5)
        
        # === PHASE 5: Return to stand ===
        logger.debug("Phase 5: Returning to stand")
        if not self.return_to_stand(0.5):
            logger.warning("Failed to return to stand cleanly")
        
        logger.info("✓ Wave animation complete")