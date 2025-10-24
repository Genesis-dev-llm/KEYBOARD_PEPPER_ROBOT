"""
Tablet Controller - Phase 2
Main logic for controlling Pepper's chest tablet display.

FEATURES:
- 4 display modes (STATUS, CUSTOM_IMAGE, PEPPER_CAM, HOVERCAM)
- Preset image support for dances/movements
- Safe fallbacks (no crashes if images missing)
- Image serving via HTTP
"""

import logging
import os
import socket
from .display_modes import DisplayMode
from .html_templates import (
    get_status_display_html,
    get_custom_image_html,
    get_camera_feed_html,
    get_blank_screen_html,
    get_error_html
)

logger = logging.getLogger(__name__)

class TabletController:
    """Controls Pepper's tablet display with multiple modes."""
    
    def __init__(self, session, robot_ip, video_server=None):
        self.session = session
        self.robot_ip = robot_ip
        self.video_server = video_server
        self.tablet = None
        self.battery_service = None
        
        # Get PC's IP address (for serving images to Pepper)
        self.pc_ip = self._get_pc_ip()
        
        # Current state
        self.current_mode = DisplayMode.STATUS
        self.current_action = "Ready"
        self.action_detail = "Waiting for input..."
        self.continuous_mode = True
        
        # Custom image
        self.custom_image_path = None
        
        # Preset images directory
        self.preset_dir = "assets/tablet_images"
        os.makedirs(self.preset_dir, exist_ok=True)
        
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
    
    def _get_pc_ip(self):
        """Get PC's local IP address with fallbacks."""
        try:
            # Method 1: Socket connection test
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))  # Doesn't actually connect
            ip = s.getsockname()[0]
            s.close()
            
            if ip and ip != '127.0.0.1':
                logger.info(f"PC IP address: {ip}")
                return ip
        except:
            pass
        
        try:
            # Method 2: Get hostname IP
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            if ip and ip != '127.0.0.1':
                logger.info(f"PC IP address (hostname): {ip}")
                return ip
        except:
            pass
        
        # Method 3: Try to get from robot IP (same subnet)
        try:
            robot_parts = self.robot_ip.split('.')
            # Assume PC is on same subnet, try common IPs
            base = '.'.join(robot_parts[:3])
            
            # Try .100, .101, .102... (common PC IPs)
            for i in range(100, 200):
                test_ip = f"{base}.{i}"
                # This is a guess - log warning
                logger.warning(f"Could not detect PC IP reliably, guessing: {test_ip}")
                logger.warning("If images don't load, check your PC's actual IP")
                return test_ip
        except:
            pass
        
        logger.error("Could not determine PC IP address!")
        logger.error("Images and camera feeds may not work")
        logger.error("Manual fix: Set tablet_ctrl.pc_ip = 'YOUR_PC_IP'")
        return "localhost"
    
    def _get_battery_level(self):
        """Get current battery percentage."""
        try:
            if self.battery_service:
                return self.battery_service.getBatteryCharge()
        except Exception as e:
            logger.warning(f"Could not get battery level: {e}")
        return 50  # Default fallback
    
    def _get_preset_image_url(self, name):
        """
        Get URL for preset image (served via HTTP).
        Returns None if image doesn't exist.
        """
        # Check for PNG
        path = os.path.join(self.preset_dir, f"{name}.png")
        if os.path.exists(path):
            # Serve via video server (we'll add image serving endpoint)
            return f"http://{self.pc_ip}:8080/image/{name}.png"
        
        # Check for JPG
        path = os.path.join(self.preset_dir, f"{name}.jpg")
        if os.path.exists(path):
            return f"http://{self.pc_ip}:8080/image/{name}.jpg"
        
        return None
    
    # ========================================================================
    # PUBLIC API - State Updates
    # ========================================================================
    
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
    
    def set_custom_image(self, image_path):
        """Set custom image to display."""
        if os.path.exists(image_path):
            self.custom_image_path = image_path
            logger.info(f"Custom image set: {os.path.basename(image_path)}")
            
            # Auto-switch to CUSTOM_IMAGE mode
            self.current_mode = DisplayMode.CUSTOM_IMAGE
            self.refresh_display()
        else:
            logger.error(f"Image not found: {image_path}")
    
    def cycle_mode(self):
        """Cycle to the next display mode."""
        self.current_mode = self.current_mode.next()
        logger.info(f"Tablet mode changed to: {self.current_mode}")
        self.refresh_display()
    
    def set_mode(self, mode):
        """Set specific display mode."""
        if isinstance(mode, DisplayMode):
            self.current_mode = mode
            self.refresh_display()
        else:
            logger.error(f"Invalid mode: {mode}")
    
    # ========================================================================
    # DISPLAY MODES
    # ========================================================================
    
    def refresh_display(self):
        """Refresh the tablet display based on current mode."""
        if not self.tablet:
            return
        
        try:
            if self.current_mode == DisplayMode.STATUS:
                self._show_status_display()
            elif self.current_mode == DisplayMode.CUSTOM_IMAGE:
                self._show_custom_image()
            elif self.current_mode == DisplayMode.PEPPER_CAM:
                self._show_pepper_camera()
            elif self.current_mode == DisplayMode.HOVERCAM:
                self._show_hovercam()
        except Exception as e:
            logger.error(f"Error refreshing tablet display: {e}")
            self._show_error(str(e))
    
    def _show_status_display(self):
        """Show status + action display (with preset images if available)."""
        battery = self._get_battery_level()
        
        # Try to get preset image for current action
        image_url = None
        action_lower = self.current_action.lower().replace(" ", "_")
        
        # Map actions to preset image names
        image_mapping = {
            "ready": "standby",
            "standby": "standby",
            "wave": "wave",
            "special_dance": "special",
            "special": "special",
            "robot_dance": "robot",
            "robot": "robot",
            "moonwalk": "moonwalk",
            "moving_forward": "moving_forward",
            "moving_backward": "moving_back"
        }
        
        image_name = image_mapping.get(action_lower)
        if image_name:
            image_url = self._get_preset_image_url(image_name)
        
        html = get_status_display_html(
            action=self.current_action,
            action_detail=self.action_detail,
            battery=battery,
            mode=self.continuous_mode,
            image_url=image_url
        )
        
        self.tablet.showWebview(html)
    
    def _show_custom_image(self):
        """Show custom static image."""
        if not self.custom_image_path or not os.path.exists(self.custom_image_path):
            # Fallback: show message
            html = get_error_html("No image selected")
            self.tablet.showWebview(html)
            return
        
        # Generate URL for custom image
        filename = os.path.basename(self.custom_image_path)
        image_url = f"http://{self.pc_ip}:8080/custom_image/{filename}"
        
        html = get_custom_image_html(
            image_url=image_url,
            caption=os.path.splitext(filename)[0]
        )
        
        self.tablet.showWebview(html)
    
    def _show_pepper_camera(self):
        """Show Pepper's camera feed."""
        if not self.video_server:
            html = get_error_html("Video server not running")
            self.tablet.showWebview(html)
            return
        
        camera_url = self.video_server.get_pepper_url(self.pc_ip)
        
        html = get_camera_feed_html(
            camera_url=camera_url,
            camera_name="Pepper's View"
        )
        
        self.tablet.showWebview(html)
    
    def _show_hovercam(self):
        """Show HoverCam feed."""
        if not self.video_server:
            html = get_error_html("Video server not running")
            self.tablet.showWebview(html)
            return
        
        camera_url = self.video_server.get_hover_url(self.pc_ip)
        
        html = get_camera_feed_html(
            camera_url=camera_url,
            camera_name="HoverCam"
        )
        
        self.tablet.showWebview(html)
    
    def _show_error(self, message):
        """Show error message on tablet."""
        html = get_error_html(message)
        self.tablet.showWebview(html)
    
    def show_blank(self):
        """Show blank screen."""
        html = get_blank_screen_html()
        self.tablet.showWebview(html)
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
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
    
    def is_video_mode(self):
        """Check if currently showing video feed."""
        return self.current_mode in [DisplayMode.PEPPER_CAM, DisplayMode.HOVERCAM]