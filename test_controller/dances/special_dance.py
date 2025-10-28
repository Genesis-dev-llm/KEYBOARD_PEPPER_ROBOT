"""
MODULE: test_controller/dances/special_dance.py
Special Dance - ANATOMICALLY ACCURATE TWERK

IMPROVEMENTS:
- Proper squat mechanics (gradual descent)
- Accurate hip isolation (HipPitch oscillation)
- Correct arm positioning (hands near knees for balance)
- Head positioning (looking down during low, up during pop)
- Realistic rhythm (8 counts per cycle at ~130 BPM)
- Progressive intensity (starts slow, builds up, finale)
- Smooth inverse kinematics throughout

Based on actual human twerk biomechanics mapped to Pepper's joints.
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class SpecialDance(BaseDance):
    """
    Anatomically accurate twerk dance for Pepper.
    
    Sequence:
    1. Prep: Get into squat position with proper form
    2. Warm-up: Slow hip pops (4 cycles)
    3. Main: Fast twerk (12 cycles at rhythm)
    4. Build: Add arm movement (8 cycles)
    5. Finale: Deep squat + big pop + victory
    """
    
    def perform(self):
        """Perform the anatomically accurate twerk dance."""
        logger.info("🍑 Starting ANATOMICALLY ACCURATE Special Dance!")
        logger.info("💃 Pepper is about to get DOWN with PROPER FORM!")
        
        if not self.ensure_stiffness():
            return
        
        if not self.safe_wait(0.3):
            return
        
        # ====================================================================
        # PHASE 1: PREP - GET INTO POSITION (Proper squat form)
        # ====================================================================
        logger.info("Phase 1: Getting into position (proper squat form)")
        self.log_progress(1, 6)
        
        # Step 1: Feet position (already set by Stand posture)
        # Step 2: Start squat descent - GRADUAL and controlled
        logger.debug("  Descending into squat...")
        
        # Gradual knee bend (prevents sudden drops)
        for knee_angle in [0.1, 0.2, 0.3, 0.4]:
            if self.should_abort():
                return
            if not self.safe_set_angles_smooth("KneePitch", knee_angle, 0.25):
                return
            if not self.safe_wait(0.15):
                return
        
        # Step 3: Position arms for balance (like hands on knees)
        logger.debug("  Positioning arms for balance...")
        
        # Shoulders forward and down (reaching toward knees)
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch"],
            [1.2, 1.2],  # Forward
            0.3
        ):
            return
        if not self.safe_wait(0.2):
            return
        
        # Elbows slightly out (natural arm position)
        if not self.safe_set_angles_smooth(
            ["LShoulderRoll", "RShoulderRoll"],
            [0.3, -0.3],  # Slightly out
            0.3
        ):
            return
        if not self.safe_wait(0.2):
            return
        
        # Step 4: Head position (look down - proper form)
        if not self.safe_set_angles_smooth("HeadPitch", -0.3, 0.25):
            return
        if not self.safe_wait(0.2):
            return
        
        # Validate position is safe
        if not self.validate_balance():
            logger.error("Balance check failed - aborting")
            self.return_to_stand()
            return
        
        logger.info("  ✓ In position - ready to twerk!")
        if not self.safe_wait(0.3):
            return
        
        # ====================================================================
        # PHASE 2: WARM-UP - Slow Hip Pops (Learn the movement)
        # ====================================================================
        logger.info("Phase 2: Warm-up - Slow hip pops (4 cycles)")
        self.log_progress(2, 6)
        
        warm_up_cycles = 4
        warm_up_speed = 0.4  # Slow and controlled
        warm_up_timing = 0.35  # ~85 BPM (slow)
        
        for cycle in range(warm_up_cycles):
            if self.should_abort():
                break
            
            # POP BACK - Hip goes back (butt out)
            # This is the main twerk motion!
            if not self.safe_set_angles_smooth(
                ["HipPitch", "KneePitch"],
                [0.25, 0.45],  # Hip back, knees bent
                warm_up_speed
            ):
                break
            
            if not self.safe_wait(warm_up_timing):
                break
            
            # POP FORWARD - Hip comes forward (engage core)
            if not self.safe_set_angles_smooth(
                ["HipPitch", "KneePitch"],
                [-0.05, 0.35],  # Hip forward, slightly less knee bend
                warm_up_speed
            ):
                break
            
            if not self.safe_wait(warm_up_timing):
                break
            
            logger.debug(f"  Warm-up cycle {cycle + 1}/{warm_up_cycles}")
        
        # ====================================================================
        # PHASE 3: MAIN TWERK - Fast Hip Isolation (The Real Thing)
        # ====================================================================
        logger.info("Phase 3: MAIN TWERK - Fast hip pops (12 cycles at rhythm)")
        self.log_progress(3, 6)
        
        main_cycles = 12
        main_speed = 0.7  # Fast
        main_timing = 0.18  # ~130 BPM (twerk rhythm)
        
        # Hip angles for fast oscillation
        hip_back = 0.28  # Butt OUT
        hip_forward = -0.08  # Engage core
        knee_deep = 0.48  # Stay low
        knee_medium = 0.38  # Slight variation
        
        for cycle in range(main_cycles):
            if self.should_abort():
                break
            
            # Balance check every 4 cycles
            if cycle % 4 == 0 and cycle > 0:
                if not self.validate_balance():
                    logger.warning("Balance wavering - adjusting...")
                    main_speed = 0.5  # Slow down for safety
            
            # BACK POP (main twerk motion)
            if not self.safe_set_angles_smooth(
                ["HipPitch", "KneePitch"],
                [hip_back, knee_deep],
                main_speed
            ):
                break
            
            if not self.safe_wait(main_timing):
                break
            
            # FORWARD ENGAGE
            if not self.safe_set_angles_smooth(
                ["HipPitch", "KneePitch"],
                [hip_forward, knee_medium],
                main_speed
            ):
                break
            
            if not self.safe_wait(main_timing):
                break
            
            # Progress indicator
            if cycle % 4 == 0:
                logger.debug(f"  Twerking: {cycle + 1}/{main_cycles}")
        
        # ====================================================================
        # PHASE 4: BUILD-UP - Add Arm Flair (More dynamic)
        # ====================================================================
        logger.info("Phase 4: BUILD-UP - Adding arm movement (8 cycles)")
        self.log_progress(4, 6)
        
        build_cycles = 8
        build_speed = 0.65
        build_timing = 0.16  # Slightly faster (~140 BPM)
        
        for cycle in range(build_cycles):
            if self.should_abort():
                break
            
            # Arms UP + Hip BACK
            if not self.safe_set_angles_smooth(
                ["LShoulderPitch", "RShoulderPitch", "HipPitch", "KneePitch"],
                [-0.8, -0.8, hip_back, knee_deep],  # Arms up, hip back
                build_speed
            ):
                break
            
            # Head UP (attitude!)
            if cycle % 2 == 0:  # Every other cycle
                if not self.safe_set_angles_smooth("HeadPitch", 0.1, 0.6):
                    break
            
            if not self.safe_wait(build_timing):
                break
            
            # Arms DOWN + Hip FORWARD
            if not self.safe_set_angles_smooth(
                ["LShoulderPitch", "RShoulderPitch", "HipPitch", "KneePitch"],
                [0.8, 0.8, hip_forward, knee_medium],  # Arms down, hip forward
                build_speed
            ):
                break
            
            # Head DOWN
            if cycle % 2 == 0:
                if not self.safe_set_angles_smooth("HeadPitch", -0.3, 0.6):
                    break
            
            if not self.safe_wait(build_timing):
                break
            
            if cycle % 4 == 0:
                logger.debug(f"  Build-up: {cycle + 1}/{build_cycles}")
        
        # ====================================================================
        # PHASE 5: FINALE - BIG DROP (Dramatic ending)
        # ====================================================================
        logger.info("Phase 5: FINALE - Big drop and recovery!")
        self.log_progress(5, 6)
        
        # Build anticipation - slow rise
        logger.debug("  Building anticipation...")
        if not self.safe_set_angles_smooth(
            ["KneePitch", "HipPitch"],
            [0.2, -0.15],  # Rise up slightly
            0.3
        ):
            return
        if not self.safe_wait(0.4):
            return
        
        # Arms WAY UP (dramatic)
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch"],
            [-1.4, -1.4],
            0.4
        ):
            return
        if not self.safe_wait(0.3):
            return
        
        # THE DROP - Go LOW (but safe)
        logger.debug("  THE DROP!")
        if not self.safe_set_angles_smooth(
            ["KneePitch", "HipPitch"],
            [0.65, 0.35],  # Deep squat + hip back
            0.35
        ):
            return
        if not self.safe_wait(0.5):
            return
        
        # BIG POP - Explosive rise
        logger.debug("  BIG POP UP!")
        if not self.safe_set_angles_smooth(
            ["KneePitch", "HipPitch"],
            [0.15, -0.1],  # Jump up (within limits)
            0.6  # Fast
        ):
            return
        if not self.safe_wait(0.4):
            return
        
        # ====================================================================
        # PHASE 6: VICTORY POSE
        # ====================================================================
        logger.info("Phase 6: VICTORY POSE!")
        self.log_progress(6, 6)
        
        # Arms in victory V
        if not self.safe_set_angles_smooth(
            ["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"],
            [-0.5, -0.5, -1.3, 1.3],
            0.3
        ):
            return
        if not self.safe_wait(0.4):
            return
        
        # Head UP (proud!)
        if not self.safe_set_angles_smooth("HeadPitch", 0.2, 0.3):
            return
        if not self.safe_wait(0.5):
            return
        
        # Hold pose
        if not self.safe_wait(0.8):
            return
        
        # ====================================================================
        # RETURN TO STAND
        # ====================================================================
        logger.info("💃 SPECIAL DANCE COMPLETE! Pepper's got RHYTHM!")
        if not self.return_to_stand(0.7):
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
                logger.debug(f"  {description}")
            return True
        except Exception as e:
            logger.error(f"Failed to set angles: {e}")
            return False