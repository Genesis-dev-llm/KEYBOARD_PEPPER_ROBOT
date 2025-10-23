"""
Special Dance Animation - ENHANCED VERSION
Features squat motion, hip throw back, and hands on knees position.
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class SpecialDance(BaseDance):
    """Enhanced special dance with proper squat and throw back motion."""
    
    def perform(self):
        """Perform the REAL special dance animation."""
        logger.info("🍑 Starting ENHANCED Special Dance animation...")
        logger.info("💃 Pepper is about to DROP IT!")
        
        self.ensure_stiffness()
        time.sleep(0.2)
        
        # === PHASE 1: GET LOW ===
        logger.info("Phase 1: Getting low...")
        self.safe_set_angles("KneePitch", 0.5, 0.3)
        time.sleep(0.5)
        
        # Position arms down/forward (hands near knees vibe)
        self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch"],
            [1.2, 1.2],
            0.3
        )
        time.sleep(0.3)
        
        # === PHASE 2: THE SPECIAL DANCE - Rapid hip oscillation with squat ===
        logger.info("Phase 2: DANCING! (15 cycles)")
        
        for cycle in range(config.SPECIAL_DANCE_CYCLES):
            # DOWN position - squat + throw it back
            self.safe_set_angles(
                ["HipPitch", "KneePitch"],
                [config.SPECIAL_DANCE_HIP_ANGLE, config.SPECIAL_DANCE_KNEE_ANGLE],
                config.SPECIAL_DANCE_SPEED
            )
            time.sleep(config.SPECIAL_DANCE_TIMING)
            
            # UP position - pop back up slightly
            self.safe_set_angles(
                ["HipPitch", "KneePitch"],
                [-0.2, 0.3],
                config.SPECIAL_DANCE_SPEED
            )
            time.sleep(config.SPECIAL_DANCE_TIMING)
        
        # === PHASE 3: Add arm flair (last 4 cycles) ===
        logger.info("Phase 3: Adding arm flair...")
        
        for cycle in range(4):
            # Arms UP + squat DOWN
            self.safe_set_angles(
                ["LShoulderPitch", "RShoulderPitch"],
                [-1.0, -1.0],
                0.6
            )
            self.safe_set_angles("HipPitch", config.SPECIAL_DANCE_HIP_ANGLE, config.SPECIAL_DANCE_SPEED)
            time.sleep(0.15)
            
            # Arms DOWN + pop UP
            self.safe_set_angles(
                ["LShoulderPitch", "RShoulderPitch"],
                [0.5, 0.5],
                0.6
            )
            self.safe_set_angles("HipPitch", -0.15, config.SPECIAL_DANCE_SPEED)
            time.sleep(0.15)
        
        # === PHASE 4: FINALE - Big move ===
        logger.info("Phase 4: FINALE!")
        
        # Arms way up
        self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.5, -1.5],
            0.4
        )
        # REALLY low squat
        self.safe_set_angles("KneePitch", 0.8, 0.3)
        time.sleep(0.5)
        
        # Pop back up!
        self.safe_set_angles("KneePitch", 0.0, 0.5)
        time.sleep(0.3)
        
        # === PHASE 5: Victory pose ===
        logger.info("Phase 5: Victory pose!")
        self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"],
            [-0.5, -0.5, -1.5, 1.5],
            0.3
        )
        time.sleep(0.5)
        
        # Return to normal
        logger.info("💃 SPECIAL DANCE COMPLETE! Pepper's got MOVES!")
        self.return_to_stand(0.6)