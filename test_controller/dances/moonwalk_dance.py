"""
Moonwalk Dance Animation - Michael Jackson Style
Full sequence: Crotch grab → Hip thrust → Spin → Moonwalk glide
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class MoonwalkDance(BaseDance):
    """Michael Jackson moonwalk sequence."""
    
    def perform(self):
        """Perform the full MJ moonwalk sequence."""
        logger.info("🌙 Starting MOONWALK animation - Michael Jackson style!")
        
        self.ensure_stiffness()
        time.sleep(0.2)
        
        # === PHASE 1: CROTCH GRAB POSE ===
        logger.info("Phase 1: Crotch grab pose")
        
        # Right hand low/center (crotch grab position)
        self.safe_set_angles("RShoulderPitch", 1.0, 0.3)
        self.safe_set_angles("RShoulderRoll", -0.2, 0.3)
        time.sleep(0.3)
        
        # Left arm out for drama
        self.safe_set_angles("LShoulderPitch", 0.0, 0.3)
        self.safe_set_angles("LShoulderRoll", 0.8, 0.3)
        time.sleep(0.5)
        
        # Stand tall
        self.safe_set_angles("HipPitch", 0.0, 0.3)
        time.sleep(0.5)
        
        # === PHASE 2: HIP THRUST (3 times) ===
        logger.info("Phase 2: Hip thrusts x3")
        
        for thrust in range(3):
            # Thrust forward
            self.safe_set_angles("HipPitch", 0.15, 0.8)
            time.sleep(0.25)
            
            # Pull back
            self.safe_set_angles("HipPitch", 0.0, 0.8)
            time.sleep(0.25)
        
        # === PHASE 3: THE SPIN (360°) ===
        logger.info("Phase 3: 360° spin")
        
        # Arms slightly out for drama
        self.safe_set_angles(
            ["LShoulderRoll", "RShoulderRoll"],
            [0.5, -0.5],
            0.3
        )
        time.sleep(0.3)
        
        # Execute spin (2π radians = 360°)
        self.motion.moveTo(0.0, 0.0, 6.28)  # Full rotation
        time.sleep(1.0)
        
        # === PHASE 4: MOONWALK PREP ===
        logger.info("Phase 4: Moonwalk prep - lean forward (SAFE)")
        
        # Head down
        self.safe_set_angles("HeadPitch", -0.3, 0.3)
        time.sleep(0.3)
        
        # Slight forward lean (SAFE - only 12° to prevent tipping)
        self.safe_set_angles("HipPitch", config.MOONWALK_LEAN_ANGLE, 0.3)
        time.sleep(0.3)
        
        # Knee bend for stability
        self.safe_set_angles("KneePitch", config.MOONWALK_KNEE_BEND, 0.3)
        time.sleep(0.3)
        
        # Right arm out and slightly back (classic MJ pose)
        self.safe_set_angles("RShoulderPitch", -0.5, 0.3)
        self.safe_set_angles("RShoulderRoll", -0.8, 0.3)
        time.sleep(0.3)
        
        # Left arm down
        self.safe_set_angles("LShoulderPitch", 0.5, 0.3)
        time.sleep(0.5)
        
        # === PHASE 5: THE GLIDE (Moonwalk) ===
        logger.info("Phase 5: The GLIDE - moonwalking backward!")
        
        # Smooth backward glide while holding pose
        self.motion.moveTo(config.MOONWALK_GLIDE_DISTANCE, 0.0, 0.0)
        time.sleep(3.0)
        
        # === PHASE 6: FINISH ===
        logger.info("Phase 6: Finish - victory!")
        
        # Stand up straight
        self.safe_set_angles("KneePitch", 0.0, 0.5)
        self.safe_set_angles("HipPitch", 0.0, 0.5)
        self.safe_set_angles("HeadPitch", 0.0, 0.5)
        time.sleep(0.5)
        
        # Victory pose - both arms up
        self.safe_set_angles(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.0, -1.0],
            0.3
        )
        time.sleep(1.0)
        
        # Return to stand
        logger.info("🌙 MOONWALK COMPLETE! That's how MJ did it!")
        self.return_to_stand(0.6)