"""
Dance animations package for Pepper robot.

Modules:
- base_dance: Base class for all dances
- wave_dance: Simple wave animation
- Special_dance: Enhanced special dance with squat motion
- robot_dance: Mechanical robot-style dance
- moonwalk_dance: Michael Jackson moonwalk sequence
"""
from .base_dance import BaseDance
from .wave_dance import WaveDance
from .special_dance import SpecialDance
from .robot_dance import RobotDance
from .moonwalk_dance import MoonwalkDance
__all__ = [
    'BaseDance',
    'WaveDance',
    'SpecialDance',
    'RobotDance',
    'MoonwalkDance'
]