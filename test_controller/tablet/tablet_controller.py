"""
Tablet Controller
Main logic for controlling Pepper's chest tablet display.
"""

import logging
import os
import random
from .display_modes import DisplayMode
from .html_templates import (
    get_status_display_html,
    get_camera_mirror_html,
    get_greeting_html
)

logger = logging.getLogger(__name__)

class TabletController:
    """Controls Pepper's tablet display with multiple modes."""
    
    def __init__(self, session, robot_ip):
        self.session = session
        self.robot_ip = robot_ip
        self.tablet = None
        self.battery_service = None
        
        # Current state
        self.current_mode = DisplayMode.STATUS
        self.current_action = "Ready"
        self.action_detail = "Waiting for input..."
        self.continuous_mode = True
        
        # Greeting images
        self.greeting_images = self._load_greeting_images()
        
        # Initialize tablet service
        self._initialize()
    
    def _initialize(self):
        """Initialize tablet and battery services."""
        try:
            self.tablet = self.session.service("ALTabletService")
            self.battery_service = self.session.service("ALBattery")
            logger.info("✓ Tablet controller initialized")
            
            # Show initial display
            self.refresh_display()
        except Exception as e:
            logger.error(f"Failed to initialize tablet: {e}")
            logger.warning("Tablet display will be disabled")
    
    def _load_greeting_images(self):
        """Load greeting images from assets folder (if available)."""
        greeting_images = []
        greeting_path = "assets/greetings"
        
        if os.path.exists(greeting_path):
            for filename in os.listdir(greeting_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    greeting_images.append(os.path.join(greeting_path, filename))
            
            if greeting_images:
                logger.info(f"✓ Loaded {len(greeting_images)} greeting image(s)")
            else:
                logger.info("No greeting images found (will use text fallback)")
        else:
            logger.info("No greeting images folder (will use text fallback)")
        
        return greeting_images
    
    def _get_battery_level(self):
        """Get current battery percentage."""
        try:
            if self.battery_service:
                return self.battery_service.getBatteryCharge()
        except Exception as e:
            logger.warning(f"Could not get battery level: {e}")
        return 50  # Default fallback
    
    def set_action(self, action, detail=""):
        """Update the current action being performed."""
        self.current_action = action
        self.action_detail = detail
        
        # Only refresh if in STATUS mode
        if self.current_mode == DisplayMode.STATUS:
            self.refresh_display()
    
    def set_movement_mode(self, continuous):
        """Update movement mode (continuous/incremental)."""
        self.continuous_mode = continuous
        
        # Only refresh if in STATUS mode
        if self.current_mode == DisplayMode.STATUS:
            self.refresh_display()
    
    def cycle_mode(self):
        """Cycle to the next display mode."""
        self.current_mode = self.current_mode.next()
        logger.info(f"Tablet mode changed to: {self.current_mode}")
        self.refresh_display()
    
    def show_greeting(self):
        """Show greeting display (with image if available)."""
        self.current_mode = DisplayMode.GREETING
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the tablet display based on current mode."""
        if not self.tablet:
            return
        
        try:
            if self.current_mode == DisplayMode.STATUS:
                self._show_status_display()
            elif self.current_mode == DisplayMode.CAMERA:
                self._show_camera_display()
            elif self.current_mode == DisplayMode.GREETING:
                self._show_greeting_display()
        except Exception as e:
            logger.error(f"Error refreshing tablet display: {e}")
    
    def _show_status_display(self):
        """Show status + action display."""
        battery = self._get_battery_level()
        
        html = get_status_display_html(
            action=self.current_action,
            action_detail=self.action_detail,
            battery=battery,
            mode=self.continuous_mode
        )
        
        self.tablet.showWebview(html)
    
    def _show_camera_display(self):
        """Show camera mirror feed."""
        # Camera feed URL (from video server)
        camera_url = f"http://{self.robot_ip}:8080/video_feed"
        
        html = get_camera_mirror_html(
            camera_url=camera_url,
            action=self.current_action
        )
        
        self.tablet.showWebview(html)
    
    def _show_greeting_display(self):
        """Show greeting (with random image if available)."""
        greeting_image_url = None
        
        # Pick random greeting image if available
        if self.greeting_images:
            # For local files, we need to serve them via HTTP
            # For now, use None and show text (you can add HTTP server later)
            logger.info("Showing greeting with text (image serving not yet implemented)")
        
        html = get_greeting_html(
            greeting_image_url=greeting_image_url,
            greeting_text="Hello! 👋"
        )
        
        self.tablet.showWebview(html)
    
    def reset(self):
        """Reset tablet to default state."""
        if self.tablet:
            try:
                self.tablet.resetTablet()
                logger.info("Tablet reset")
            except Exception as e:
                logger.error(f"Error resetting tablet: {e}")
    
    def get_current_mode(self):
        """Get the current display mode."""
        return self.current_mode