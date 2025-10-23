"""
Base Dance Class
Provides common functionality for all dance animations.
"""

import time
import logging
from .. import config

logger = logging.getLogger(__name__)

class BaseDance:
    """Base class for all dance animations."""
    
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
        
        self.motion.setAngles(joint_names, clamped_angles, speed)
    
    def return_to_stand(self, speed=0.5):
        """Return robot to Stand posture."""
        logger.info("Returning to Stand posture...")
        self.posture.goToPosture("Stand", speed)
        time.sleep(1.0)
    
    def ensure_stiffness(self, body_part="Body", stiffness=1.0):
        """Ensure body part has stiffness enabled."""
        self.motion.setStiffnesses(body_part, stiffness)