"""
Configuration file for Pepper Keyboard Test Controller
Contains all speed settings, limits, and constants.

MOVEMENT FIXES:
- Increased default speeds
- Increased step sizes
- Added turbo settings
"""

# ============================================================================
# SPEED SETTINGS (INCREASED FOR BETTER RESPONSIVENESS)
# ============================================================================

# Base Movement Speeds (for translation/rotation)
BASE_LINEAR_SPEED_DEFAULT = 0.5     # m/s (increased from 0.3)
BASE_ANGULAR_SPEED_DEFAULT = 0.7    # rad/s (increased from 0.5)

# Body Movement Speed (for joints: arms, head, hands)
BODY_SPEED_DEFAULT = 0.3            # joint speed fraction (0.0-1.0)

# Speed adjustment step size
SPEED_STEP = 0.05                   # How much +/- changes speed

# Speed limits
MIN_SPEED = 0.1
MAX_SPEED = 1.0  # Increased from 0.5 for turbo mode

# Turbo mode
TURBO_MULTIPLIER = 1.5  # Turbo is 1.5x normal speed

# ============================================================================
# MOVEMENT SETTINGS (INCREASED FOR VISIBILITY)
# ============================================================================

# Incremental mode step sizes
LINEAR_STEP = 0.1       # 10cm per keypress (increased from 5cm)
ANGULAR_STEP = 0.3      # ~17 degrees per keypress (increased from ~11)
HEAD_STEP = 0.1         # radians per keypress
ARM_STEP = 0.1          # radians per keypress
WRIST_STEP = 0.2        # radians per keypress

# Smoothing factor (for continuous mode)
SMOOTHING_FACTOR = 0.5  # 0.0=instant, 1.0=never reach target (increased from 0.3)

# Update rate
BASE_UPDATE_HZ = 50     # Movement update frequency (increased from 20Hz)

# ============================================================================
# JOINT LIMITS (radians)
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

# Hand limits (open/close)
HAND_MIN = 0.0  # Closed
HAND_MAX = 1.0  # Open

# Hip/Knee limits (for dances)
HIP_PITCH_MIN = -1.0
HIP_PITCH_MAX = 1.0
KNEE_PITCH_MIN = 0.0
KNEE_PITCH_MAX = 1.0

# ============================================================================
# VIDEO SETTINGS
# ============================================================================

VIDEO_PORT = 8080
VIDEO_TIMEOUT = 5  # seconds

# ============================================================================
# DANCE SETTINGS
# ============================================================================

# Special dance settings (REDUCED for safety - Phase 3)
SPECIAL_DANCE_CYCLES = 10           # Reduced from 15
SPECIAL_DANCE_SPEED = 0.7           # Reduced from 0.95
SPECIAL_DANCE_HIP_ANGLE = 0.35      # Reduced from 0.4
SPECIAL_DANCE_KNEE_ANGLE = 0.55     # Reduced from 0.6
SPECIAL_DANCE_TIMING = 0.15         # Increased from 0.12

# Robot dance settings
ROBOT_SPEED = 0.4
ROBOT_PAUSE = 0.4  # Increased from 0.3

# Moonwalk settings (SAFE - Phase 3)
MOONWALK_LEAN_ANGLE = 0.08          # REDUCED from 0.12 - CRITICAL SAFETY
MOONWALK_KNEE_BEND = 0.20           # Reduced from 0.25
MOONWALK_GLIDE_DISTANCE = -0.2      # Reduced from -0.3

# ============================================================================
# MOTION CONFIGURATION
# ============================================================================

# Autonomous Life control
DISABLE_AUTONOMOUS_LIFE = True

# Motion protections
ENABLE_FOOT_CONTACT_PROTECTION = False      # Disable for better movement
ENABLE_EXTERNAL_COLLISION_PROTECTION = False # Reduce restrictions
ENABLE_MOVE_ARMS_DURING_MOVEMENT = False     # No arm sway

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
    
    return value  # No limit found, return as-is