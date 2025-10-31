"""
Configuration - COMPLETE & FIXED
All constants properly defined, optimized for step-based control.

FIXES:
- Removed SMOOTHING_FACTOR (not needed anymore)
- Optimized step sizes for responsive control
- All joint limits properly defined
- Validation functions updated
"""

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Video (DISABLE for max speed!)
VIDEO_ENABLED = False  # Set to True if you need video
VIDEO_PORT = 8080
VIDEO_TIMEOUT = 5
VIDEO_FPS = 5  # Lower FPS = less CPU
VIDEO_QUALITY = 60  # Lower quality = faster
VIDEO_RESOLUTION = 1  # 0=160x120, 1=320x240, 2=640x480

# Tablet updates
TABLET_ENABLED = True
TABLET_UPDATE_THROTTLE = 0.3  # Update every 300ms (fast enough)
TABLET_PRESET_DIR = "assets/tablet_images"
TABLET_CUSTOM_DIR = "assets/tablet_images/custom"

# Logging
LOG_LEVEL = "WARNING"  # Change to "INFO" for debugging

# Cache timeouts
JOINT_ANGLE_CACHE_TIMEOUT = 0.5  # Cache angles for 500ms
STATUS_CACHE_TIMEOUT = 2.0  # Cache status for 2s

# ============================================================================
# SPEED SETTINGS - Step-Based Control
# ============================================================================

BASE_LINEAR_SPEED_DEFAULT = 0.5     # m/s (not used in step mode)
BASE_ANGULAR_SPEED_DEFAULT = 0.7    # rad/s (not used in step mode)
BODY_SPEED_DEFAULT = 0.3            # For angleInterpolationWithSpeed

SPEED_STEP = 0.05  # Step size adjustment increment
MIN_SPEED = 0.05   # Minimum step size
MAX_SPEED = 0.5    # Maximum step size
TURBO_MULTIPLIER = 1.5  # Turbo boost

# ============================================================================
# MOVEMENT STEP SIZES - Optimized for Responsiveness
# ============================================================================

# Base movement (per key press)
LINEAR_STEP = 0.10      # 10cm per press
ANGULAR_STEP = 0.25     # ~14 degrees per press

# Body movements (per key press)
HEAD_STEP = 0.08        # ~4.5 degrees (smooth head movement)
ARM_STEP = 0.10         # ~5.7 degrees (good arm control)
WRIST_STEP = 0.15       # ~8.6 degrees (responsive wrists)

# ============================================================================
# JOINT LIMITS (radians) - From Pepper Documentation
# ============================================================================

# Head limits
HEAD_YAW_MIN = -2.0857     # -119.5°
HEAD_YAW_MAX = 2.0857      # 119.5°
HEAD_PITCH_MIN = -0.7068   # -40.5°
HEAD_PITCH_MAX = 0.6371    # 36.5°

# Shoulder limits
SHOULDER_PITCH_MIN = -2.0857  # -119.5°
SHOULDER_PITCH_MAX = 2.0857   # 119.5°
L_SHOULDER_ROLL_MIN = 0.0087   # 0.5°
L_SHOULDER_ROLL_MAX = 1.5620   # 89.5°
R_SHOULDER_ROLL_MIN = -1.5620  # -89.5°
R_SHOULDER_ROLL_MAX = -0.0087  # -0.5°

# Elbow limits
ELBOW_YAW_MIN = -2.0857    # -119.5°
ELBOW_YAW_MAX = 2.0857     # 119.5°
L_ELBOW_ROLL_MIN = -1.5620  # -89.5°
L_ELBOW_ROLL_MAX = -0.0087  # -0.5°
R_ELBOW_ROLL_MIN = 0.0087   # 0.5°
R_ELBOW_ROLL_MAX = 1.5620   # 89.5°

# Wrist limits
WRIST_YAW_MIN = -1.8238    # -104.5°
WRIST_YAW_MAX = 1.8238     # 104.5°

# Hand limits (0 = closed, 1 = open)
HAND_MIN = 0.0
HAND_MAX = 1.0

# Hip/Knee limits (for dances)
HIP_PITCH_MIN = -1.0
HIP_PITCH_MAX = 1.0
KNEE_PITCH_MIN = 0.0
KNEE_PITCH_MAX = 1.0

# ============================================================================
# MOTION CONFIGURATION - Optimized for Step-Based
# ============================================================================

DISABLE_AUTONOMOUS_LIFE = True
ENABLE_FOOT_CONTACT_PROTECTION = True   # Keep for safety
ENABLE_EXTERNAL_COLLISION_PROTECTION = False  # Disable for speed
ENABLE_MOVE_ARMS_DURING_MOVEMENT = False
ENABLE_SMART_STIFFNESS = False  # Disable for speed
ENABLE_IDLE_POSTURE = False
ENABLE_BREATHING = False

# ============================================================================
# DANCE SETTINGS
# ============================================================================

# Wave dance
WAVE_SPEED = 0.3
WAVE_DURATION = 0.4

# Special dance (twerk)
SPECIAL_DANCE_CYCLES = 6
SPECIAL_DANCE_SPEED = 0.6
SPECIAL_DANCE_HIP_ANGLE = 0.30
SPECIAL_DANCE_KNEE_ANGLE = 0.50
SPECIAL_DANCE_TIMING = 0.15

# Robot dance
ROBOT_SPEED = 0.5
ROBOT_PAUSE = 0.4

# Moonwalk
MOONWALK_LEAN_ANGLE = 0.08
MOONWALK_KNEE_BEND = 0.20
MOONWALK_GLIDE_DISTANCE = -0.2

# ============================================================================
# GUI SETTINGS
# ============================================================================

DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
CAMERA_UPDATE_INTERVAL = 100  # ms (10 FPS)
BATTERY_WARNING_THRESHOLD = 30
BATTERY_CRITICAL_THRESHOLD = 15
STATUS_UPDATE_INTERVAL = 1000  # ms (1 second)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))


def clamp_joint(joint_name, value):
    """Clamp joint angle to safe limits."""
    limits = {
        'HeadYaw': (HEAD_YAW_MIN, HEAD_YAW_MAX),
        'HeadPitch': (HEAD_PITCH_MIN, HEAD_PITCH_MAX),
        'LShoulderPitch': (SHOULDER_PITCH_MIN, SHOULDER_PITCH_MAX),
        'RShoulderPitch': (SHOULDER_PITCH_MIN, SHOULDER_PITCH_MAX),
        'LShoulderRoll': (L_SHOULDER_ROLL_MIN, L_SHOULDER_ROLL_MAX),
        'RShoulderRoll': (R_SHOULDER_ROLL_MIN, R_SHOULDER_ROLL_MAX),
        'LElbowYaw': (ELBOW_YAW_MIN, ELBOW_YAW_MAX),
        'RElbowYaw': (ELBOW_YAW_MIN, ELBOW_YAW_MAX),
        'LElbowRoll': (L_ELBOW_ROLL_MIN, L_ELBOW_ROLL_MAX),
        'RElbowRoll': (R_ELBOW_ROLL_MIN, R_ELBOW_ROLL_MAX),
        'LWristYaw': (WRIST_YAW_MIN, WRIST_YAW_MAX),
        'RWristYaw': (WRIST_YAW_MIN, WRIST_YAW_MAX),
        'LHand': (HAND_MIN, HAND_MAX),
        'RHand': (HAND_MIN, HAND_MAX),
        'HipPitch': (HIP_PITCH_MIN, HIP_PITCH_MAX),
        'KneePitch': (KNEE_PITCH_MIN, KNEE_PITCH_MAX),
    }
    
    if joint_name in limits:
        min_val, max_val = limits[joint_name]
        return clamp(value, min_val, max_val)
    
    return value


def get_joint_limits(joint_name):
    """Get min/max limits for a joint."""
    limits_map = {
        'HeadYaw': (HEAD_YAW_MIN, HEAD_YAW_MAX),
        'HeadPitch': (HEAD_PITCH_MIN, HEAD_PITCH_MAX),
        'LShoulderPitch': (SHOULDER_PITCH_MIN, SHOULDER_PITCH_MAX),
        'RShoulderPitch': (SHOULDER_PITCH_MIN, SHOULDER_PITCH_MAX),
        'LShoulderRoll': (L_SHOULDER_ROLL_MIN, L_SHOULDER_ROLL_MAX),
        'RShoulderRoll': (R_SHOULDER_ROLL_MIN, R_SHOULDER_ROLL_MAX),
        'LElbowYaw': (ELBOW_YAW_MIN, ELBOW_YAW_MAX),
        'RElbowYaw': (ELBOW_YAW_MIN, ELBOW_YAW_MAX),
        'LElbowRoll': (L_ELBOW_ROLL_MIN, L_ELBOW_ROLL_MAX),
        'RElbowRoll': (R_ELBOW_ROLL_MIN, R_ELBOW_ROLL_MAX),
        'LWristYaw': (WRIST_YAW_MIN, WRIST_YAW_MAX),
        'RWristYaw': (WRIST_YAW_MIN, WRIST_YAW_MAX),
        'LHand': (HAND_MIN, HAND_MAX),
        'RHand': (HAND_MIN, HAND_MAX),
        'HipPitch': (HIP_PITCH_MIN, HIP_PITCH_MAX),
        'KneePitch': (KNEE_PITCH_MIN, KNEE_PITCH_MAX),
    }
    
    return limits_map.get(joint_name, (0.0, 0.0))


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration values."""
    errors = []
    
    # Speed checks
    if MIN_SPEED >= MAX_SPEED:
        errors.append("MIN_SPEED must be less than MAX_SPEED")
    
    if not (0.0 < BODY_SPEED_DEFAULT <= 1.0):
        errors.append("BODY_SPEED_DEFAULT must be between 0 and 1")
    
    # Step size checks
    if LINEAR_STEP <= 0:
        errors.append("LINEAR_STEP must be positive")
    
    if ANGULAR_STEP <= 0:
        errors.append("ANGULAR_STEP must be positive")
    
    if VIDEO_FPS <= 0:
        errors.append("VIDEO_FPS must be positive")
    
    # Joint limit checks
    if HEAD_YAW_MIN >= HEAD_YAW_MAX:
        errors.append("HEAD_YAW_MIN must be less than HEAD_YAW_MAX")
    
    if HEAD_PITCH_MIN >= HEAD_PITCH_MAX:
        errors.append("HEAD_PITCH_MIN must be less than HEAD_PITCH_MAX")
    
    # Report errors
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


# Run validation on import
try:
    validate_config()
except ValueError as e:
    import logging
    logging.error(f"Config validation failed: {e}")
    raise