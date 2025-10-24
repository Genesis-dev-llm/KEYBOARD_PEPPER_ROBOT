"""
Special Dance Animation - Phase 3: Perfect Version
Enhanced twerk with squat motion - SAFE and smooth.

IMPROVEMENTS:
- Reduced cycles (15 → 10)
- Slower speed (0.95 → 0.7) for stability
- Balance validation
- Smoother transitions
- Better arm positioning
"""

import time
import logging
from .base_dance import BaseDance

logger = logging.getLogger(__name__)

class SpecialDance(BaseDance):
    """Enhanced special dance with proper squat and throw back motion - perfected."""
    
    def perform(self):
        """Perform the special dance animation."""
        logger.info("🍑 Starting Special Dance animation...")
        logger.info("💃 Pepper is about to DROP IT!")
        
        if not self.ensure_stiffness():
            return
        
        if not self.safe_wait(0.2):
            return
        
        # === PHASE 1: GET LOW ===
        logger.info("Phase 1: Getting low...")
        self.log_progress(1, 5)
        
        # Gradual squat for stability
        if not self.smooth_move_to("KneePitch", 0.4, 0.3, steps=5):
            return
        if not self.safe_wait(0.3):
            return
        
        # Position arms (hands near knees vibe)
        if not self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch"],
            [1.2, 1.2],
            0.3,
            "Arms down"
        ):
            return
        if not self.safe_wait(0.3):
            return
        
        # Check balance before continuing
        if not self.validate_balance():
            logger.error("Balance check failed - aborting dance")
            self.return_to_stand()
            return
        
        # === PHASE 2: THE DANCE - Hip oscillation (REDUCED CYCLES) ===
        logger.info("Phase 2: DANCING! (10 cycles - safe speed)")
        self.log_progress(2, 5)
        
        cycles = 10  # Reduced from 15
        speed = 0.7  # Slower from 0.95 for stability
        timing = 0.15  # Slightly longer for smoothness
        
        for cycle in range(cycles):
            if self.should_abort():
                break
            
            # Every 3rd cycle, check balance
            if cycle % 3 == 0:
                if not self.validate_balance():
                    logger.warning("Balance unstable - slowing down")
                    speed = 0.5
            
            # DOWN position - squat + throw it back
            if not self.safe_set_angles(
                ["HipPitch", "KneePitch"],
                [0.35, 0.55],  # Reduced from 0.4, 0.6 for safety
                speed,
                f"Down {cycle+1}"
            ):
                break
            
            if not self.safe_wait(timing):
                break
            
            # UP position - pop back up slightly
            if not self.safe_set_angles(
                ["HipPitch", "KneePitch"],
                [-0.15, 0.25],
                speed,
                f"Up {cycle+1}"
            ):
                break
            
            if not self.safe_wait(timing):
                break
        
        # === PHASE 3: Add arm flair (last 4 cycles) ===
        logger.info("Phase 3: Adding arm flair...")
        self.log_progress(3, 5)
        
        for cycle in range(4):
            if self.should_abort():
                break
            
            # Arms UP + squat DOWN
            if not self.safe_set_angles(
                ["LShoulderPitch", "RShoulderPitch", "HipPitch"],
                [-0.8, -0.8, 0.3],  # Reduced angles for safety
                0.6,
                f"Flair down {cycle+1}"
            ):
                break
            
            if not self.safe_wait(0.15):
                break
            
            # Arms DOWN + pop UP
            if not self.safe_set_angles(
                ["LShoulderPitch", "RShoulderPitch", "HipPitch"],
                [0.5, 0.5, -0.1],
                0.6,
                f"Flair up {cycle+1}"
            ):
                break
            
            if not self.safe_wait(0.15):
                break
        
        # === PHASE 4: FINALE - Big move ===
        logger.info("Phase 4: FINALE!")
        self.log_progress(4, 5)
        
        # Arms way up
        if not self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.3, -1.3],  # Reduced from -1.5
            0.4,
            "Arms up"
        ):
            return
        
        # Low squat (but not extreme)
        if not self.safe_set_angles("KneePitch", 0.7, 0.3, "Deep squat"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Pop back up!
        if not self.safe_set_angles("KneePitch", 0.0, 0.5, "Pop up"):
            return
        if not self.safe_wait(0.3):
            return
        
        # === PHASE 5: Victory pose ===
        logger.info("Phase 5: Victory pose!")
        self.log_progress(5, 5)
        
        if not self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"],
            [-0.5, -0.5, -1.4, 1.4],  # Reduced from -1.5, 1.5
            0.3,
            "Victory"
        ):
            return
        if not self.safe_wait(0.5):
            return
        
        # Return to normal
        logger.info("💃 SPECIAL DANCE COMPLETE! Pepper's got MOVES!")
        if not self.return_to_stand(0.6):
            logger.warning("Failed to return to stand cleanly")