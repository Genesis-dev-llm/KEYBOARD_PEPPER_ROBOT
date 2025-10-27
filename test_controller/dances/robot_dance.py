"""
MODULE: test_controller/dances/robot_dance.py
Robot Dance Animation - FIXED VERSION
Mechanical, choppy movements with sharp angles and pauses.

FIXED: Changed all setAngles() to angleInterpolationWithSpeed()
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class RobotDance(BaseDance):
    """Mechanical robot-style dance with choppy movements - smooth version."""
    
    def perform(self):
        """Perform robot dance animation."""
        logger.info("🤖 Starting Robot Dance animation...")
        
        if not self.ensure_stiffness():
            return
        
        speed = 0.4  # Mechanical speed
        pause = 0.4
        
        # === SEQUENCE 1: Head snap left-right ===
        logger.info("Sequence 1: Head snaps")
        self.log_progress(1, 7)
        
        if not self.safe_set_angles_smooth("HeadYaw", 1.4, speed, "Head left"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth("HeadYaw", -1.4, speed, "Head right"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth("HeadYaw", 0.0, speed, "Head center"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 2: Right arm up ===
        logger.info("Sequence 2: Right arm up")
        self.log_progress(2, 7)
        
        if not self.safe_set_angles_smooth("RShoulderPitch", -1.4, speed, "R arm up"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth("RElbowRoll", 1.4, speed, "R elbow bend"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 3: Left arm out ===
        logger.info("Sequence 3: Left arm out")
        self.log_progress(3, 7)
        
        if not self.safe_set_angles_smooth("LShoulderRoll", 1.4, speed, "L arm out"):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth("LElbowRoll", -1.4, speed, "L elbow bend"):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 4: Both arms forward ===
        logger.info("Sequence 4: Arms forward")
        self.log_progress(4, 7)
        
        if not self.safe_set_angles_smooth(
            ["RShoulderPitch", "LShoulderPitch"],
            [0.0, 0.0],
            speed,
            "Arms forward"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth(
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
        
        if not self.safe_set_angles_smooth(
            ["RElbowRoll", "LElbowRoll"],
            [1.4, -1.4],
            speed,
            "Elbows bent"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth(
            ["RElbowRoll", "LElbowRoll"],
            [0.1, -0.1],
            speed,
            "Elbows straight"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        # === SEQUENCE 6: Wrist rotation ===
        logger.info("Sequence 6: Wrist rotations")
        self.log_progress(6, 7)
        
        if not self.safe_set_angles_smooth(
            ["RWristYaw", "LWristYaw"],
            [1.5, -1.5],
            speed,
            "Wrists rotated"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth(
            ["RWristYaw", "LWristYaw"],
            [-1.5, 1.5],
            speed,
            "Wrists opposite"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth(
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
        
        if not self.safe_set_angles_smooth(
            ["RShoulderPitch", "LShoulderPitch"],
            [-1.4, -1.4],
            speed,
            "Arms up"
        ):
            return
        if not self.safe_wait(pause):
            return
        
        if not self.safe_set_angles_smooth(
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
    
    def safe_set_angles_smooth(self, joint_names, angles, speed, description=""):
        """Use angleInterpolationWithSpeed for smooth movement."""
        if self.should_abort():
            return False
        
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            angles = [angles]
        
        clamped_angles = []
        for joint_name, angle in zip(joint_names, angles):
            clamped = config.clamp_joint(joint_name, angle)
            if abs(clamped - angle) > 0.01:
                logger.warning(f"{joint_name}: Clamped {angle:.2f} → {clamped:.2f}")
            clamped_angles.append(clamped)
        
        try:
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