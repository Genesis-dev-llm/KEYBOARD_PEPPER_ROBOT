"""
Configuration file for Pepper Keyboard Test Controller
OPTIMIZED VERSION - Balanced for responsiveness and safety

KEY FEATURES:
- Responsive movement (no lag)
- Safe speed limits
- Proper joint limits
- Configurable dance parameters
"""

# ============================================================================
# SPEED SETTINGS
# ============================================================================

# Base Movement Speeds (m/s and rad/s)
BASE_LINEAR_SPEED_DEFAULT = 0.4     # m/s - safe default
BASE_ANGULAR_SPEED_DEFAULT = 0.6    # rad/s - safe default

# Body Movement Speed (0.0-1.0, fraction of max speed)
BODY_SPEED_DEFAULT = 0.3

# Speed adjustment step
SPEED_STEP = 0.05

# Speed limits
MIN_SPEED = 0.1
MAX_SPEED = 1.0

# Turbo mode multiplier
TURBO_MULTIPLIER = 1.5

# ============================================================================
# MOVEMENT SETTINGS
# ============================================================================

# Incremental mode step sizes
LINEAR_STEP = 0.08      # 8cm per keypress
ANGULAR_STEP = 0.25     # ~14 degrees
HEAD_STEP = 0.08        # radians per keypress
ARM_STEP = 0.08         # radians per keypress
WRIST_STEP = 0.15       # radians per keypress

# Update rate
BASE_UPDATE_HZ = 50     # 50Hz for smooth movement
UPDATE_INTERVAL = 1.0 / BASE_UPDATE_HZ

# ============================================================================
# JOINT LIMITS (radians) - From Pepper Documentation
# ============================================================================

# Head limits
HEAD_YAW_MIN = -2.0857
HEAD_YAW_MAX = 2.0857
HEAD_PITCH_MIN = -0.6720
HEAD_PITCH_MAX = 0.5149

# Shoulder limits
SHOULDER_PITCH_MIN = -2.0857
SHOULDER_PITCH_MAX = 2.0857
L_SHOULDER_ROLL_MIN = 0.0087
L_SHOULDER_ROLL_MAX = 1.5620
R_SHOULDER_ROLL_MIN = -1.5620
R_SHOULDER_ROLL_MAX = -0.0087

# Elbow limits
ELBOW_YAW_MIN = -2.0857
ELBOW_YAW_MAX = 2.0857
L_ELBOW_ROLL_MIN = -1.5620
L_ELBOW_ROLL_MAX = -0.0087
R_ELBOW_ROLL_MIN = 0.0087
R_ELBOW_ROLL_MAX = 1.5620

# Wrist limits
WRIST_YAW_MIN = -1.8238
WRIST_YAW_MAX = 1.8238

# Hand limits
HAND_MIN = 0.0
HAND_MAX = 1.0

# Hip/Knee limits (for dances)
HIP_PITCH_MIN = -1.0
HIP_PITCH_MAX = 1.0
KNEE_PITCH_MIN = 0.0
KNEE_PITCH_MAX = 1.0

# ============================================================================
# VIDEO SETTINGS
# ============================================================================

VIDEO_PORT = 8080
VIDEO_TIMEOUT = 5
VIDEO_FPS = 10  # Frames per second for streaming

# ============================================================================
# DANCE SETTINGS
# ============================================================================

# Wave dance
WAVE_SPEED = 0.25
WAVE_DURATION = 0.4

# Special dance (twerk)
SPECIAL_DANCE_CYCLES = 8
SPECIAL_DANCE_SPEED = 0.6
SPECIAL_DANCE_HIP_ANGLE = 0.30
SPECIAL_DANCE_KNEE_ANGLE = 0.50
SPECIAL_DANCE_TIMING = 0.15

# Robot dance
ROBOT_SPEED = 0.4
ROBOT_PAUSE = 0.4

# Moonwalk - SAFE PARAMETERS
MOONWALK_LEAN_ANGLE = 0.08      # Safe forward lean
MOONWALK_KNEE_BEND = 0.20       # Moderate knee bend
MOONWALK_GLIDE_DISTANCE = -0.2  # 20cm backward glide

# ============================================================================
# MOTION CONFIGURATION
# ============================================================================

# Autonomous Life
DISABLE_AUTONOMOUS_LIFE = True

# Motion protections (BALANCED - safety first!)
ENABLE_FOOT_CONTACT_PROTECTION = True       # ALWAYS ENABLED
ENABLE_EXTERNAL_COLLISION_PROTECTION = True  # ENABLED but permissive
ENABLE_MOVE_ARMS_DURING_MOVEMENT = False     # No arm sway

# Stiffness management
ENABLE_SMART_STIFFNESS = True    # Adaptive stiffness control
ENABLE_IDLE_POSTURE = False      # Disable random movements
ENABLE_BREATHING = False         # Disable breathing motion

# ============================================================================
# GUI SETTINGS
# ============================================================================

# Window defaults
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Camera feed refresh rate (ms)
CAMERA_UPDATE_INTERVAL = 100  # 10 FPS

# Battery warning thresholds (%)
BATTERY_WARNING_THRESHOLD = 30
BATTERY_CRITICAL_THRESHOLD = 15

# Status update interval (ms)
STATUS_UPDATE_INTERVAL = 1000  # 1 second

# ============================================================================
# TABLET SETTINGS
# ============================================================================

# Image directories
TABLET_PRESET_DIR = "assets/tablet_images"
TABLET_CUSTOM_DIR = "assets/tablet_images/custom"

# Image serving
IMAGE_SERVER_PORT = 8080

# Tablet display modes
TABLET_MODES = [
    "STATUS",           # Movement status with images
    "CUSTOM_IMAGE",     # User-selected image
    "PEPPER_CAM",       # Pepper's camera feed
    "HOVERCAM"          # External USB camera
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def clamp_joint(joint_name, value):
    """Clamp a joint angle to its safe limits."""
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
    """Get the min/max limits for a joint."""
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
    assert MIN_SPEED < MAX_SPEED, "MIN_SPEED must be less than MAX_SPEED"
    assert 0.0 < BODY_SPEED_DEFAULT <= 1.0, "BODY_SPEED_DEFAULT must be between 0 and 1"
    assert BASE_UPDATE_HZ > 0, "BASE_UPDATE_HZ must be positive"
    assert VIDEO_FPS > 0, "VIDEO_FPS must be positive"
    return True


# Run validation on import
validate_config()