"""
Base Dance Class and All Dance Implementations
FIXED: Proper error handling with try/finally for safety
"""

import time
import logging
from .. import config

logger = logging.getLogger(__name__)

class BaseDance:
    """Base class for all dance animations with improved error handling."""
    
    def __init__(self, motion_service, posture_service):
        self.motion = motion_service
        self.posture = posture_service
    
    def perform(self):
        """Override this method in subclasses."""
        raise NotImplementedError("Subclass must implement perform()")
    
    def safe_set_angles(self, joint_names, angles, speed):
        """Safely set joint angles with clamping."""
        if isinstance(joint_names, str):
            joint_names = [joint_names]
            angles = [angles]
        
        # Clamp all angles to safe limits
        clamped_angles = []
        for joint_name, angle in zip(joint_names, angles):
            clamped = config.clamp_joint(joint_name, angle)
            clamped_angles.append(clamped)
        
        try:
            self.motion.setAngles(joint_names, clamped_angles, speed)
        except Exception as e:
            logger.error(f"Failed to set angles for {joint_names}: {e}")
    
    def return_to_stand(self, speed=0.5):
        """Return robot to Stand posture."""
        logger.info("Returning to Stand posture...")
        try:
            self.posture.goToPosture("Stand", speed)
            time.sleep(1.0)
        except Exception as e:
            logger.error(f"Failed to return to stand: {e}")
    
    def ensure_stiffness(self, body_part="Body", stiffness=1.0):
        """Ensure body part has stiffness enabled."""
        try:
            self.motion.setStiffnesses(body_part, stiffness)
        except Exception as e:
            logger.error(f"Failed to set stiffness: {e}")


class WaveDance(BaseDance):
    """Simple wave animation with proper error handling."""
    
    def perform(self):
        """Perform wave animation."""
        logger.info("🎭 Starting Wave animation...")
        
        try:
            self.ensure_stiffness()
            
            # Raise arm
            self.safe_set_angles("RShoulderPitch", -0.5, 0.2)
            time.sleep(0.5)
            
            # Extend arm sideways
            self.safe_set_angles("RShoulderRoll", -1.2, 0.2)
            time.sleep(0.5)
            
            # Bend elbow
            self.safe_set_angles("RElbowRoll", 1.5, 0.2)
            time.sleep(0.5)
            
            # Wave wrist back and forth (3 times)
            for _ in range(3):
                self.safe_set_angles("RWristYaw", -1.0, 0.4)
                time.sleep(0.3)
                self.safe_set_angles("RWristYaw", 1.0, 0.4)
                time.sleep(0.3)
            
            logger.info("✓ Wave animation complete")
            
        except KeyboardInterrupt:
            logger.info("Wave interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Wave animation error: {e}")
        finally:
            # FIXED: Always return to safe state
            self.return_to_stand()


class SpecialDance(BaseDance):
    """Enhanced special dance with proper squat and throw back motion."""
    
    def perform(self):
        """Perform the REAL special dance animation."""
        logger.info("🍑 Starting ENHANCED Special Dance animation...")
        logger.info("💃 Pepper is about to DROP IT!")
        
        try:
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
            
            logger.info("💃 SPECIAL DANCE COMPLETE! Pepper's got MOVES!")
            
        except KeyboardInterrupt:
            logger.info("Special dance interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Special dance error: {e}")
        finally:
            # FIXED: Always return to safe state
            self.return_to_stand(0.6)


class RobotDance(BaseDance):
    """Mechanical robot-style dance with choppy movements."""
    
    def perform(self):
        """Perform robot dance animation."""
        logger.info("🤖 Starting Robot Dance animation...")
        
        try:
            self.ensure_stiffness()
            
            # === SEQUENCE 1: Head snap left-right ===
            logger.info("Sequence 1: Head snaps")
            self.safe_set_angles("HeadYaw", 1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles("HeadYaw", -1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles("HeadYaw", 0.0, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 2: Right arm up ===
            logger.info("Sequence 2: Right arm up")
            self.safe_set_angles("RShoulderPitch", -1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles("RElbowRoll", 1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 3: Left arm out ===
            logger.info("Sequence 3: Left arm out")
            self.safe_set_angles("LShoulderRoll", 1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles("LElbowRoll", -1.5, config.ROBOT_SPEED)
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 4: Both arms forward ===
            logger.info("Sequence 4: Arms forward")
            self.safe_set_angles(
                ["RShoulderPitch", "LShoulderPitch"],
                [0.0, 0.0],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles(
                ["RShoulderRoll", "LShoulderRoll"],
                [0.0, 0.0],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 5: Elbows bend sharp ===
            logger.info("Sequence 5: Sharp elbow bends")
            self.safe_set_angles(
                ["RElbowRoll", "LElbowRoll"],
                [1.5, -1.5],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles(
                ["RElbowRoll", "LElbowRoll"],
                [0.1, -0.1],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 6: Wrist rotation ===
            logger.info("Sequence 6: Wrist rotations")
            self.safe_set_angles(
                ["RWristYaw", "LWristYaw"],
                [1.8, -1.8],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles(
                ["RWristYaw", "LWristYaw"],
                [-1.8, 1.8],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles(
                ["RWristYaw", "LWristYaw"],
                [0.0, 0.0],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            
            # === SEQUENCE 7: Finale - Both arms up ===
            logger.info("Sequence 7: Finale")
            self.safe_set_angles(
                ["RShoulderPitch", "LShoulderPitch"],
                [-1.5, -1.5],
                config.ROBOT_SPEED
            )
            time.sleep(config.ROBOT_PAUSE)
            self.safe_set_angles(
                ["RElbowRoll", "LElbowRoll"],
                [1.5, -1.5],
                config.ROBOT_SPEED
            )
            time.sleep(0.5)
            
            logger.info("🤖 Robot Dance complete!")
            
        except KeyboardInterrupt:
            logger.info("Robot dance interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Robot dance error: {e}")
        finally:
            # FIXED: Always return to safe state
            self.return_to_stand()


class MoonwalkDance(BaseDance):
    """Michael Jackson moonwalk sequence."""
    
    def perform(self):
        """Perform the full MJ moonwalk sequence."""
        logger.info("🌙 Starting MOONWALK animation - Michael Jackson style!")
        
        try:
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
            
            logger.info("🌙 MOONWALK COMPLETE! That's how MJ did it!")
            
        except KeyboardInterrupt:
            logger.info("Moonwalk interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Moonwalk error: {e}")
        finally:
            # FIXED: Always return to safe state
            self.return_to_stand(0.6)