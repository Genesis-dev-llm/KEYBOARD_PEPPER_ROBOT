"""
MODULE: test_controller/dances/special_dance.py
Special Dance Animation - FIXED VERSION
Enhanced twerk with squat motion - SAFE and smooth.

FIXED: Changed all setAngles() to angleInterpolationWithSpeed()
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class SpecialDance(BaseDance):
    """Enhanced special dance with proper squat and throw back motion - smooth."""
    
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
        if not self.smooth_move_to_smooth("KneePitch", 0.4, 0.3, steps=5):
            return
        if not self.safe_wait(0.3):
            return
        
        # Position arms (hands near knees vibe)
        if not self.safe_set_angles_smooth(
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
        
        # === PHASE 2: THE DANCE - Hip oscillation ===
        logger.info("Phase 2: DANCING! (8 cycles - safe speed)")
        self.log_progress(2, 5)
        
        cycles = 8
        speed = 0.6
        timing = 0.15
        
        for cycle in range(cycles):
            if self.should_abort():
                break
            
            # Every 3rd cycle, check balance
            if cycle % 3 == 0:
                if not self.validate_balance():
                    logger.warning("Balance unstable - slowing down")
                    speed = 0.5
            
            # DOWN position - squat + throw it back
            if not self.safe_set_angles_smooth(
                ["HipPitch", "KneePitch"],
                [0.30, 0.50],
                speed,
                f"Down {cycle+1}"
            ):
                break
            
            if not self.safe_wait(timing):
                break
            
            # UP position - pop back up slightly
            if not self.safe_set_angles_smooth(
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
            if not self.safe_set_angles_smooth(
                ["LShoulderPitch", "RShoulderPitch", "HipPitch"],
                [-0.8, -0.8, 0.3],
                0.6,
                f"Flair down {cycle+1}"
            ):
                break
            
            if not self.safe_wait(0.15):
                break
            
            # Arms DOWN + pop UP
            if not self.safe_set_angles_smooth(
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
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.3, -1.3],
            0.4,
            "Arms up"
        ):
            return
        
        # Low squat (but not extreme)
        if not self.safe_set_angles_smooth("KneePitch", 0.7, 0.3, "Deep squat"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Pop back up!
        if not self.safe_set_angles_smooth("KneePitch", 0.0, 0.5, "Pop up"):
            return
        if not self.safe_wait(0.3):
            return
        
        # === PHASE 5: Victory pose ===
        logger.info("Phase 5: Victory pose!")
        self.log_progress(5, 5)
        
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"],
            [-0.5, -0.5, -1.4, 1.4],
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
    
    def smooth_move_to_smooth(self, joint_names, target_angles, speed, steps=5):
        """Move to target angles smoothly with interpolation."""
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            target_angles = [target_angles]
        
        try:
            current_angles = [self.motion.getAngles(j, True)[0] for j in joint_names]
        except:
            return self.safe_set_angles_smooth(joint_names, target_angles, speed)
        
        for step in range(1, steps + 1):
            if self.should_abort():
                return False
            
            t = step / steps
            interpolated = [
                current + (target - current) * t
                for current, target in zip(current_angles, target_angles)
            ]
            
            if not self.safe_set_angles_smooth(joint_names, interpolated, speed):
                return False
            
            time.sleep(0.05)
        
        return True