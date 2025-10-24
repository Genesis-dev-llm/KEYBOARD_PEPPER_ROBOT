"""
Robot Dance Animation - Phase 3: Perfect Version
Mechanical, choppy movements with sharp angles and pauses.

IMPROVEMENTS:
- Validated extreme angles
- Better pause timing
- Smoother sequence flow
- Progress tracking
"""

import time
import logging
from .base_dance import BaseDance

logger = logging.getLogger(__name__)

class RobotDance(BaseDance):
    """Mechanical robot-style dance with choppy movements - perfected."""
    
    def perform(self):
        """Perform robot dance animation."""
        logger.info("🤖 Starting Robot Dance animation...")
        
        if not self.ensure_stiffness():
            return
        
        speed = 0.4  # Mechanical speed
        pause = 0.4  # Increased from 0.3 for better effect
        
        # === SEQUENCE 1: Head snap left-right ===
        logger.info("Sequence 1: Head snaps")
        self.log_progress(1, 7)
        
        if not self.safe_set_angles("HeadYaw", 1.4, speed, "Head left"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles("HeadYaw", -1.4, speed, "Head right"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles("HeadYaw", 0.0, speed, "Head center"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 2: Right arm up ===
        logger.info("Sequence 2: Right arm up")
        self.log_progress(2, 7)
        
        if not self.safe_set_angles("RShoulderPitch", -1.4, speed, "R arm up"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles("RElbowRoll", 1.4, speed, "R elbow bend"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 3: Left arm out ===
        logger.info("Sequence 3: Left arm out")
        self.log_progress(3, 7)
        
        if not self.safe_set_angles("LShoulderRoll", 1.4, speed, "L arm out"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles("LElbowRoll", -1.4, speed, "L elbow bend"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 4: Both arms forward ===
        logger.info("Sequence 4: Arms forward")
        self.log_progress(4, 7)
        
        if not self.safe_set_angles(
            ["RShoulderPitch", "LShoulderPitch"],
            [0.0, 0.0],
            speed,
            "Arms forward"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles(
            ["RShoulderRoll", "LShoulderRoll"],
            [0.0, 0.0],
            speed,
            "Arms center"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 5: Elbows bend sharp ===
        logger.info("Sequence 5: Sharp elbow bends")
        self.log_progress(5, 7)
        
        if not self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [1.4, -1.4],
            speed,
            "Elbows bent"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [0.1, -0.1],
            speed,
            "Elbows straight"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 6: Wrist rotation (REDUCED from ±1.8) ===
        logger.info("Sequence 6: Wrist rotations")
        self.log_progress(6, 7)
        
        if not self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [1.5, -1.5],  # Reduced from 1.8
            speed,
            "Wrists rotated"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [-1.5, 1.5],
            speed,
            "Wrists opposite"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [0.0, 0.0],
            speed,
            "Wrists neutral"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 7: Finale - Both arms up ===
        logger.info("Sequence 7: Finale")
        self.log_progress(7, 7)
        
        if not self.safe_set_angles(
            ["RShoulderPitch", "LShoulderPitch"],
            [-1.4, -1.4],
            speed,
            "Arms up"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [1.4, -1.4],
            speed,
            "Elbows bent final"
        ):
            return
        if not self.safe_wait(0.5):
            return
        
        # Return to stand
        logger.info("🤖 Robot Dance complete!")
        if not self.return_to_stand(0.5):
            logger.warning("Failed to return to stand cleanly")