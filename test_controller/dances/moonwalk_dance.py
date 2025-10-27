"""
MODULE: test_controller/dances/moonwalk_dance.py
Moonwalk Dance Animation - FIXED VERSION
Full sequence: Crotch grab → Hip thrust → Spin → Moonwalk glide

FIXED: Changed all setAngles() to angleInterpolationWithSpeed()
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class MoonwalkDance(BaseDance):
    """Michael Jackson moonwalk sequence - smooth version."""
    
    def perform(self):
        """Perform the full MJ moonwalk sequence."""
        logger.info("🌙 Starting MOONWALK animation - Michael Jackson style!")
        logger.warning("⚠️  Complex dance - monitoring balance")
        
        if not self.ensure_stiffness():
            return
        if not self.safe_wait(0.2):
            return
        
        # === PHASE 1: CROTCH GRAB POSE ===
        logger.info("Phase 1: Crotch grab pose")
        self.log_progress(1, 6)
        
        # Right hand low/center (crotch grab position)
        if not self.safe_set_angles_smooth("RShoulderPitch", 1.0, 0.3, "R arm down"):
            return
        if not self.safe_wait(0.3):
            return
        
        if not self.safe_set_angles_smooth("RShoulderRoll", -0.2, 0.3, "R arm center"):
            return
        if not self.safe_wait(0.3):
            return
        
        # Left arm out for drama
        if not self.safe_set_angles_smooth("LShoulderPitch", 0.0, 0.3, "L arm out"):
            return
        if not self.safe_wait(0.3):
            return
        
        if not self.safe_set_angles_smooth("LShoulderRoll", 0.8, 0.3, "L arm extend"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Stand tall
        if not self.safe_set_angles_smooth("HipPitch", 0.0, 0.3, "Stand tall"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Balance check
        if not self.validate_balance():
            logger.error("Balance failed in Phase 1 - aborting")
            self.return_to_stand()
            return
        
        # === PHASE 2: HIP THRUST (3 times) ===
        logger.info("Phase 2: Hip thrusts x3")
        self.log_progress(2, 6)
        
        for thrust in range(3):
            if self.should_abort():
                break
            
            # Thrust forward
            if not self.safe_set_angles_smooth("HipPitch", 0.10, 0.7, f"Thrust {thrust+1}"):
                break
            if not self.safe_wait(0.25):
                break
            
            # Pull back
            if not self.safe_set_angles_smooth("HipPitch", 0.0, 0.7, f"Back {thrust+1}"):
                break
            if not self.safe_wait(0.25):
                break
        
        # Balance check after thrusts
        if not self.validate_balance():
            logger.error("Balance failed after thrusts - aborting")
            self.return_to_stand()
            return
        
        # === PHASE 3: THE SPIN (360°) ===
        logger.info("Phase 3: 360° spin")
        self.log_progress(3, 6)
        
        # Arms slightly out for drama
        if not self.safe_set_angles_smooth(
            ["LShoulderRoll", "RShoulderRoll"],
            [0.5, -0.5],
            0.3,
            "Arms out for spin"
        ):
            return
        if not self.safe_wait(0.3):
            return
        
        # Execute spin (2π radians = 360°)
        try:
            logger.debug("Executing 360° spin...")
            self.motion.moveTo(0.0, 0.0, 6.28)
            if not self.safe_wait(2.0):
                return
        except Exception as e:
            logger.error(f"Spin failed: {e}")
            self.return_to_stand()
            return
        
        # Balance check after spin
        if not self.validate_balance():
            logger.error("Balance failed after spin - aborting moonwalk")
            self.return_to_stand()
            return
        
        # === PHASE 4: MOONWALK PREP ===
        logger.info("Phase 4: Moonwalk prep - SAFE lean")
        self.log_progress(4, 6)
        
        # Head down
        if not self.safe_set_angles_smooth("HeadPitch", -0.25, 0.3, "Head down"):
            return
        if not self.safe_wait(0.3):
            return
        
        # SAFE forward lean
        logger.warning("⚠️  Applying forward lean")
        if not self.safe_set_angles_smooth("HipPitch", 0.08, 0.2, "Safe lean"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Balance check - CRITICAL
        if not self.validate_balance():
            logger.error("⚠️  UNSAFE lean detected - aborting!")
            self.safe_set_angles_smooth("HipPitch", 0.0, 0.5)
            self.safe_wait(0.5)
            self.return_to_stand()
            return
        
        # Knee bend for stability
        if not self.safe_set_angles_smooth("KneePitch", 0.20, 0.3, "Knee bend"):
            return
        if not self.safe_wait(0.3):
            return
        
        # Right arm out and slightly back (classic MJ pose)
        if not self.safe_set_angles_smooth("RShoulderPitch", -0.5, 0.3, "R arm back"):
            return
        if not self.safe_set_angles_smooth("RShoulderRoll", -0.8, 0.3, "R arm out"):
            return
        if not self.safe_wait(0.3):
            return
        
        # Left arm down
        if not self.safe_set_angles_smooth("LShoulderPitch", 0.5, 0.3, "L arm down"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Final balance check before glide
        if not self.validate_balance():
            logger.error("⚠️  Balance unstable - aborting!")
            self.safe_set_angles_smooth("HipPitch", 0.0, 0.5)
            self.safe_set_angles_smooth("KneePitch", 0.0, 0.5)
            self.safe_wait(0.5)
            self.return_to_stand()
            return
        
        # === PHASE 5: THE GLIDE (Moonwalk) ===
        logger.info("Phase 5: The GLIDE - moonwalking backward!")
        self.log_progress(5, 6)
        
        glide_distance = -0.2
        
        try:
            logger.debug(f"Executing backward glide: {glide_distance}m")
            self.motion.moveTo(glide_distance, 0.0, 0.0)
            
            if not self.safe_wait(2.5):
                logger.warning("Glide interrupted")
                return
            
        except Exception as e:
            logger.error(f"Glide failed: {e}")
            self.safe_set_angles_smooth("HipPitch", 0.0, 0.5)
            self.safe_set_angles_smooth("KneePitch", 0.0, 0.5)
            self.safe_wait(0.5)
            self.return_to_stand()
            return
        
        # === PHASE 6: FINISH ===
        logger.info("Phase 6: Finish - victory!")
        self.log_progress(6, 6)
        
        # Stand up straight - GRADUAL
        if not self.safe_set_angles_smooth("KneePitch", 0.0, 0.4, "Stand up"):
            return
        if not self.safe_wait(0.3):
            return
        
        if not self.safe_set_angles_smooth("HipPitch", 0.0, 0.4, "Straighten"):
            return
        if not self.safe_wait(0.3):
            return
        
        if not self.safe_set_angles_smooth("HeadPitch", 0.0, 0.4, "Head up"):
            return
        if not self.safe_wait(0.5):
            return
        
        # Victory pose - both arms up
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.0, -1.0],
            0.3,
            "Victory"
        ):
            return
        if not self.safe_wait(1.0):
            return
        
        # Return to stand
        logger.info("🌙 MOONWALK COMPLETE! That's how MJ did it (safely)!")
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