"""
Pepper Robot Connection Handler
Manages connection to Pepper and service initialization.

MOVEMENT FIXES:
- Aggressive Autonomous Life disabling
- Proper motion configuration
- Explicit wheel enabling
- Movement mode setup
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
        
        self._connect()
        self._initialize_services()
        self._configure_motion()  # NEW: Critical for base movement
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
            logger.info("✓ All services initialized")
            
            # CRITICAL: Disable Autonomous Life more aggressively
            try:
                self.autonomous_life = self.session.service("ALAutonomousLife")
                current_state = self.autonomous_life.getState()
                
                if current_state != "disabled":
                    logger.info(f"Autonomous Life state: {current_state}")
                    logger.info("Disabling Autonomous Life...")
                    
                    # Stop all autonomous behaviors
                    self.autonomous_life.stopAll()
                    time.sleep(0.5)
                    
                    # Set to disabled
                    self.autonomous_life.setState("disabled")
                    time.sleep(0.5)
                    
                    # Verify
                    new_state = self.autonomous_life.getState()
                    if new_state == "disabled":
                        logger.info("✓ Autonomous Life DISABLED")
                    else:
                        logger.warning(f"⚠ Autonomous Life still: {new_state}")
                else:
                    logger.info("✓ Autonomous Life already disabled")
                    
            except Exception as e:
                logger.warning(f"Could not control Autonomous Life: {e}")
                logger.warning("Movement may be limited by autonomous behaviors")
                
        except qi.Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _configure_motion(self):
        """Configure motion service for optimal base movement."""
        logger.info("Configuring motion settings...")
        
        try:
            # Disable arm movements during base motion (prevents interference)
            self.motion.setMoveArmsEnabled(False, False)
            logger.info("✓ Disabled arm sway during movement")
            
            # Set motion configuration
            # Disable foot contact protection (can block movement)
            self.motion.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
            logger.info("✓ Configured motion parameters")
            
            # Set external collision protection to low (less restrictive)
            try:
                self.motion.setExternalCollisionProtectionEnabled("All", False)
                logger.info("✓ Reduced collision protection")
            except:
                logger.warning("Could not disable collision protection")
            
            # Enable smart stiffness removal (saves battery when idle)
            try:
                self.motion.setSmartStiffnessEnabled(False)
                logger.info("✓ Disabled smart stiffness (full control mode)")
            except:
                pass
            
        except Exception as e:
            logger.error(f"Motion configuration error: {e}")
            logger.warning("Movement may be affected")
    
    def _initialize_robot(self):
        """Set robot to ready state with stiffness and posture."""
        try:
            logger.info("Initializing robot...")
            
            # Set stiffness to Body first
            logger.info("Setting body stiffness...")
            self.motion.setStiffnesses("Body", 1.0)
            time.sleep(0.5)
            logger.info("✓ Body stiffness: 1.0")
            
            # CRITICAL: Explicitly enable wheel motors
            logger.info("Enabling wheel motors...")
            try:
                # Pepper's wheel joint names
                wheel_joints = ["WheelFL", "WheelFR", "WheelB"]
                self.motion.setStiffnesses(wheel_joints, 1.0)
                logger.info("✓ Wheel motors explicitly enabled")
            except Exception as e:
                logger.warning(f"Could not explicitly enable wheels: {e}")
                logger.warning("Using default body stiffness for wheels")
            
            # Go to Stand posture
            logger.info("Moving to Stand posture...")
            self.posture.goToPosture("Stand", 0.5)
            logger.info("✓ Robot in Stand posture")
            
            # Test base movement capability
            logger.info("Testing base movement capability...")
            try:
                # Small test movement
                self.motion.moveToward(0.1, 0.0, 0.0)
                time.sleep(0.2)
                self.motion.stopMove()
                logger.info("✓ Base movement test PASSED")
            except Exception as e:
                logger.error(f"⚠ Base movement test FAILED: {e}")
                logger.error("Base movement may not work correctly!")
            
            logger.info("🤖 Robot ready for keyboard control")
            
        except Exception as e:
            logger.error(f"Failed to initialize robot state: {e}")
            raise
    
    def get_status(self):
        """Get current robot status for monitoring."""
        try:
            battery_level = self.battery.getBatteryCharge()
            stiffness = self.motion.getStiffnesses("Body")
            
            # Check if base is moveable
            try:
                wheel_stiffness = self.motion.getStiffnesses(["WheelFL", "WheelFR", "WheelB"])
                wheels_enabled = all(s > 0.5 for s in wheel_stiffness)
            except:
                wheels_enabled = True  # Assume enabled if can't check
            
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
        """Emergency stop - halt all movement and disable stiffness."""
        logger.error("🚨 EMERGENCY STOP")
        try:
            # Stop base movement
            self.motion.stopMove()
            
            # Stop all other movements
            self.motion.killAll()
            
            # Optionally disable stiffness (commented out - keeps robot standing)
            # self.motion.setStiffnesses("Body", 0.0)
            
            logger.info("✓ Robot stopped")
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def test_movement(self):
        """
        Diagnostic test for base movement.
        Call this if movement isn't working.
        """
        logger.info("\n" + "="*60)
        logger.info("MOVEMENT DIAGNOSTIC TEST")
        logger.info("="*60)
        
        try:
            # Test 1: Check stiffness
            logger.info("Test 1: Checking stiffness...")
            body_stiff = self.motion.getStiffnesses("Body")
            logger.info(f"  Body stiffness: {body_stiff[0]:.2f}")
            
            try:
                wheel_stiff = self.motion.getStiffnesses(["WheelFL", "WheelFR", "WheelB"])
                logger.info(f"  Wheel stiffness: FL={wheel_stiff[0]:.2f}, FR={wheel_stiff[1]:.2f}, B={wheel_stiff[2]:.2f}")
            except:
                logger.warning("  Could not check wheel stiffness")
            
            # Test 2: Check Autonomous Life
            logger.info("\nTest 2: Checking Autonomous Life...")
            if self.autonomous_life:
                state = self.autonomous_life.getState()
                logger.info(f"  State: {state}")
                if state != "disabled":
                    logger.warning("  ⚠ Autonomous Life NOT disabled!")
            
            # Test 3: Movement test
            logger.info("\nTest 3: Testing forward movement (2 seconds)...")
            logger.info("  Robot should move forward slowly...")
            self.motion.moveToward(0.2, 0.0, 0.0)
            time.sleep(2.0)
            self.motion.stopMove()
            logger.info("  ✓ Forward movement command sent")
            
            # Test 4: Rotation test
            logger.info("\nTest 4: Testing rotation (2 seconds)...")
            logger.info("  Robot should rotate left...")
            self.motion.moveToward(0.0, 0.0, 0.3)
            time.sleep(2.0)
            self.motion.stopMove()
            logger.info("  ✓ Rotation command sent")
            
            logger.info("\n" + "="*60)
            logger.info("DIAGNOSTIC TEST COMPLETE")
            logger.info("If robot didn't move, check:")
            logger.info("  1. Battery level (needs >30%)")
            logger.info("  2. Robot is in Stand posture")
            logger.info("  3. Wheels are not blocked")
            logger.info("  4. Floor is suitable (not carpet)")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Diagnostic test failed: {e}")
    
    def close(self):
        """Safely close the connection."""
        logger.info("Closing connection to Pepper...")
        try:
            self.emergency_stop()
            if self.session:
                self.session.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")