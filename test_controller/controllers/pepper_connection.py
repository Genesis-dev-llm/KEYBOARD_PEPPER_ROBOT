"""
Pepper Robot Connection Handler - FIXED VERSION
Proper motion configuration for smooth, responsive movement.

KEY FIXES:
- Balanced collision protection (not fully disabled)
- Proper stiffness management
- Correct motion mode initialization
- Smart autonomous life handling
"""

import qi
import logging
import time

logger = logging.getLogger(__name__)

class PepperConnection:
    """Handles connection to Pepper robot and service initialization."""
    
    def __init__(self, ip, port=9559):
        self.ip = ip
        self.port = port
        self.session = None
        self.motion = None
        self.posture = None
        self.tts = None
        self.battery = None
        self.autonomous_life = None
        self.awareness = None
        
        self._connect()
        self._initialize_services()
        self._configure_motion()  # CRITICAL: Proper motion setup
        self._initialize_robot()
    
    def _connect(self):
        """Establish connection to Pepper using qi framework."""
        logger.info(f"Connecting to Pepper at {self.ip}:{self.port}...")
        self.session = qi.Session()
        
        try:
            self.session.connect(f"tcp://{self.ip}:{self.port}")
            logger.info("✓ Connected successfully!")
        except qi.Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise ConnectionError(f"Could not connect to Pepper at {self.ip}:{self.port}")
    
    def _initialize_services(self):
        """Initialize all required NAOqi services."""
        try:
            self.motion = self.session.service("ALMotion")
            self.posture = self.session.service("ALRobotPosture")
            self.tts = self.session.service("ALTextToSpeech")
            self.battery = self.session.service("ALBattery")
            logger.info("✓ Core services initialized")
            
            # CRITICAL: Handle Autonomous Life and Basic Awareness
            try:
                self.autonomous_life = self.session.service("ALAutonomousLife")
                self.awareness = self.session.service("ALBasicAwareness")
                
                # Disable autonomous life
                current_state = self.autonomous_life.getState()
                if current_state != "disabled":
                    logger.info(f"Disabling Autonomous Life (currently: {current_state})")
                    self.autonomous_life.setState("disabled")
                    time.sleep(0.5)
                    logger.info("✓ Autonomous Life disabled")
                
                # Disable basic awareness (prevents random head movements)
                if self.awareness.isEnabled():
                    self.awareness.stopAwareness()
                    logger.info("✓ Basic Awareness disabled")
                    
            except Exception as e:
                logger.warning(f"Could not fully disable autonomous behaviors: {e}")
                
        except qi.Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _configure_motion(self):
        """
        Configure motion service for optimal base movement.
        BALANCED approach - not too restrictive, not too permissive.
        """
        logger.info("Configuring motion settings...")
        
        try:
            # ===== ARM MOVEMENT DURING BASE MOTION =====
            # Disable arm sway (prevents interference with base movement)
            self.motion.setMoveArmsEnabled(False, False)
            logger.info("✓ Disabled arm sway during movement")
            
            # ===== COLLISION PROTECTION =====
            # IMPORTANT: Keep collision protection ENABLED but set to permissive mode
            # Don't disable completely - this is dangerous!
            try:
                # Set collision protection to "Move" mode (less restrictive)
                self.motion.setExternalCollisionProtectionEnabled("Move", True)
                logger.info("✓ Collision protection: MOVE mode (permissive)")
            except Exception as e:
                logger.warning(f"Could not set collision protection mode: {e}")
                # Fallback: just reduce sensitivity
                try:
                    self.motion.setCollisionProtectionEnabled("Arms", False)
                    logger.info("✓ Arm collision protection reduced")
                except:
                    pass
            
            # ===== FOOT CONTACT PROTECTION =====
            # Keep ENABLED for safety (prevents falling)
            # Only disable if you have balance issues
            try:
                self.motion.setMotionConfig([
                    ["ENABLE_FOOT_CONTACT_PROTECTION", True],  # KEEP ENABLED
                ])
                logger.info("✓ Foot contact protection: ENABLED (safe)")
            except Exception as e:
                logger.warning(f"Motion config warning: {e}")
            
            # ===== SMART STIFFNESS =====
            # ENABLE smart stiffness for better movement
            try:
                self.motion.setSmartStiffnessEnabled(True)
                logger.info("✓ Smart stiffness: ENABLED")
            except Exception as e:
                logger.warning(f"Smart stiffness warning: {e}")
            
            # ===== IDLE POSTURE MANAGEMENT =====
            # Disable idle posture family (prevents random movements)
            try:
                self.motion.setIdlePostureEnabled("Body", False)
                logger.info("✓ Idle posture disabled")
            except:
                pass
            
            # ===== BREATHING =====
            # Disable breathing (subtle chest movements can interfere)
            try:
                self.motion.setBreathEnabled("Body", False)
                logger.info("✓ Breathing disabled")
            except:
                pass
            
            logger.info("✓ Motion configuration complete")
            
        except Exception as e:
            logger.error(f"Motion configuration error: {e}")
            logger.warning("Movement may be affected")
    
    def _initialize_robot(self):
        """Set robot to ready state with proper stiffness and posture."""
        try:
            logger.info("Initializing robot...")
            
            # ===== WAKE UP =====
            # Ensure robot is awake
            try:
                self.motion.wakeUp()
                time.sleep(1.0)
                logger.info("✓ Robot awake")
            except Exception as e:
                logger.warning(f"Wake up warning: {e}")
            
            # ===== STIFFNESS =====
            # Set full body stiffness gradually
            logger.info("Setting body stiffness...")
            self.motion.setStiffnesses("Body", 0.0)  # Start at 0
            time.sleep(0.2)
            self.motion.setStiffnesses("Body", 0.5)  # Gradual increase
            time.sleep(0.3)
            self.motion.setStiffnesses("Body", 1.0)  # Full stiffness
            time.sleep(0.5)
            logger.info("✓ Body stiffness: 1.0")
            
            # ===== POSTURE =====
            # Go to Stand posture
            logger.info("Moving to Stand posture...")
            self.posture.goToPosture("Stand", 0.6)  # 60% speed
            time.sleep(0.5)
            logger.info("✓ Robot in Stand posture")
            
            # ===== MOVEMENT TEST =====
            # Small movement test to verify
            logger.info("Testing base movement...")
            try:
                self.motion.moveToward(0.05, 0.0, 0.0)  # Tiny forward
                time.sleep(0.5)
                self.motion.stopMove()
                logger.info("✓ Base movement test PASSED")
            except Exception as e:
                logger.error(f"⚠ Base movement test FAILED: {e}")
            
            logger.info("🤖 Robot ready for control")
            
        except Exception as e:
            logger.error(f"Failed to initialize robot state: {e}")
            raise
    
    def get_status(self):
        """Get current robot status for monitoring."""
        try:
            battery_level = self.battery.getBatteryCharge()
            stiffness = self.motion.getStiffnesses("Body")
            
            # Check if wheels are moveable
            try:
                wheel_stiffness = self.motion.getStiffnesses(["WheelFL", "WheelFR", "WheelB"])
                wheels_enabled = all(s > 0.5 for s in wheel_stiffness)
            except:
                wheels_enabled = True
            
            return {
                "battery": battery_level,
                "stiffness": stiffness[0] if stiffness else 0.0,
                "wheels_enabled": wheels_enabled,
                "connected": True
            }
        except Exception as e:
            logger.warning(f"Could not retrieve robot status: {e}")
            return {"connected": False}
    
    def emergency_stop(self):
        """Emergency stop - halt all movement."""
        logger.error("🚨 EMERGENCY STOP")
        try:
            self.motion.stopMove()
            self.motion.killAll()
            logger.info("✓ Robot stopped")
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def rest(self):
        """Put robot in rest mode (low stiffness)."""
        try:
            logger.info("Putting robot to rest...")
            self.motion.rest()
            logger.info("✓ Robot at rest")
        except Exception as e:
            logger.error(f"Rest error: {e}")
    
    def close(self):
        """Safely close the connection."""
        logger.info("Closing connection to Pepper...")
        try:
            self.motion.stopMove()
            # Don't rest automatically - let user decide
            if self.session:
                self.session.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")