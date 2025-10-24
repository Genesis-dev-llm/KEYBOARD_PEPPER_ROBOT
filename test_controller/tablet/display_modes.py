"""
Display Mode Management - Phase 2
Handles different tablet display modes.

MODES:
1. STATUS - Movement status with text/images
2. CUSTOM_IMAGE - User-selected image
3. PEPPER_CAM - Pepper's camera feed
4. HOVERCAM - External USB camera feed
"""

from enum import Enum

class DisplayMode(Enum):
    """Available display modes for the tablet."""
    STATUS = "status"               # Status + Action display (with preset images)
    CUSTOM_IMAGE = "custom_image"   # User-selected static image
    PEPPER_CAM = "pepper_camera"    # Pepper's camera mirror
    HOVERCAM = "hovercam"           # External USB camera (Solo8)
    
    def next(self):
        """Get the next mode in the cycle."""
        modes = list(DisplayMode)
        current_index = modes.index(self)
        next_index = (current_index + 1) % len(modes)
        return modes[next_index]
    
    def __str__(self):
        """String representation."""
        display_names = {
            DisplayMode.STATUS: "STATUS",
            DisplayMode.CUSTOM_IMAGE: "CUSTOM IMAGE",
            DisplayMode.PEPPER_CAM: "PEPPER CAMERA",
            DisplayMode.HOVERCAM: "HOVERCAM"
        }
        return display_names.get(self, self.value.upper())