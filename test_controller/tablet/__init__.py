"""
Tablet Display System for Pepper Robot - Phase 2
Provides professional UI on Pepper's chest tablet.

Modules:
- tablet_controller: Main tablet control logic
- display_modes: Different display mode handlers (4 modes)
- html_templates: Professional HTML/CSS templates

PHASE 2 FEATURES:
- STATUS mode with preset images
- CUSTOM_IMAGE mode with drag & drop
- PEPPER_CAM mode (live feed)
- HOVERCAM mode (USB camera feed)
"""

from .tablet_controller import TabletController
from .display_modes import DisplayMode

__all__ = [
    'TabletController',
    'DisplayMode'
]