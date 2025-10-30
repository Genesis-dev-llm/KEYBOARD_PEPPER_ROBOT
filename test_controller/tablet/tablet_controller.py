"""
Tablet Controller - FULLY FIXED & ROBUST VERSION
Main logic for controlling Pepper's chest tablet display.

FIXES APPLIED:
- Better error handling (no crashes!)
- Automatic fallbacks if images missing
- Smart PC IP detection
- Throttled updates (no spam)
- Cached battery/status queries
- Works even if video server is disabled
"""

import logging
import os
import socket
import time
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
        self.custom_dir = os.path.join(self.preset_dir, "custom")
        
        # Create directories if they don't exist
        os.makedirs(self.preset_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
        
        # Cache for battery/status (reduce queries)
        self._last_battery_query = 0
        self._cached_battery = 50
        self._battery_cache_timeout = 2.0  # 2 seconds
        
        # Throttle display updates
        self._last_display_update = 0
        self._display_update_throttle = 0.5  # 500ms minimum between updates
        
        # Initialize tablet service
        self._initialize()
    
    def _initialize(self):
        """Initialize tablet and battery services."""
        try:
            self.tablet = self.session.service("ALTabletService")
            logger.info("✓ Tablet service connected")
            
            try:
                self.battery_service = self.session.service("ALBattery")
                logger.info("✓ Battery service connected")
            except Exception as e:
                logger.warning(f"Battery service unavailable: {e}")
            
            # Show initial display
            self.refresh_display()
            
        except Exception as e:
            logger.error(f"Failed to initialize tablet: {e}")
            logger.warning("⚠️  Tablet display will be disabled")
            self.tablet = None
    
    def _get_pc_ip(self):
        """Get PC's local IP address with multiple fallback methods."""
        # Method 1: Connect to Google DNS (doesn't actually connect)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            if ip and ip != '127.0.0.1':
                logger.info(f"✓ PC IP detected: {ip}")
                return ip
        except Exception as e:
            logger.debug(f"Method 1 IP detection failed: {e}")
        
        # Method 2: Get hostname IP
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            if ip and ip != '127.0.0.1':
                logger.info(f"✓ PC IP detected (hostname): {ip}")
                return ip
        except Exception as e:
            logger.debug(f"Method 2 IP detection failed: {e}")
        
        # Method 3: Use same subnet as robot
        try:
            robot_parts = self.robot_ip.split('.')
            base = '.'.join(robot_parts[:3])
            
            # Try common PC IPs on same subnet
            for i in [100, 101, 102, 50, 51, 52, 200, 201]:
                test_ip = f"{base}.{i}"
                logger.info(f"📡 PC IP: {test_ip} (estimated, same subnet as Pepper)")
                logger.info("   If images don't load, manually set: tablet_ctrl.pc_ip = 'YOUR_IP'")
                return test_ip
        except:
            pass
        
        # Fallback
        logger.warning("⚠️  Could not detect PC IP reliably!")
        logger.warning("   Set manually: tablet_ctrl.pc_ip = 'YOUR_PC_IP'")
        logger.warning("   Images may not load on tablet")
        return "localhost"
    
    def _get_battery_level(self):
        """Get current battery percentage with caching."""
        current_time = time.time()
        
        # Use cached value if recent
        if current_time - self._last_battery_query < self._battery_cache_timeout:
            return self._cached_battery
        
        # Query robot
        try:
            if self.battery_service:
                battery = self.battery_service.getBatteryCharge()
                self._cached_battery = battery
                self._last_battery_query = current_time
                return battery
        except Exception as e:
            logger.debug(f"Battery query failed: {e}")
        
        # Return cached/default
        return self._cached_battery
    
    def _get_preset_image_url(self, name):
        """
        Get URL for preset image (served via HTTP).
        Returns None if image doesn't exist.
        Checks multiple extensions.
        """
        extensions = ['.png', '.jpg', '.jpeg', '.gif']
        
        for ext in extensions:
            filepath = os.path.join(self.preset_dir, f"{name}{ext}")
            if os.path.exists(filepath):
                # Serve via video server (or direct file://)
                if self.video_server and self.video_server.is_running:
                    return f"http://{self.pc_ip}:8080/image/{name}{ext}"
                else:
                    # Fallback to file:// URL
                    abs_path = os.path.abspath(filepath)
                    return f"file://{abs_path}"
        
        return None
    
    def _should_update_display(self):
        """Check if enough time has passed to update display (throttling)."""
        current_time = time.time()
        if current_time - self._last_display_update >= self._display_update_throttle:
            self._last_display_update = current_time
            return True
        return False
    
    # ========================================================================
    # PUBLIC API - State Updates
    # ========================================================================
    
    def set_action(self, action, detail=""):
        """Update the current action being performed."""
        self.current_action = action
        self.action_detail = detail
        
        # Only refresh if in STATUS mode and not throttled
        if self.current_mode == DisplayMode.STATUS and self._should_update_display():
            self.refresh_display()
    
    def set_movement_mode(self, continuous):
        """Update movement mode (continuous/incremental)."""
        self.continuous_mode = continuous
        
        # Only refresh if in STATUS mode
        if self.current_mode == DisplayMode.STATUS:
            self.refresh_display()
    
    def set_custom_image(self, image_path):
        """Set custom image to display."""
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return False
        
        self.custom_image_path = image_path
        logger.info(f"Custom image set: {os.path.basename(image_path)}")
        
        # Auto-switch to CUSTOM_IMAGE mode
        self.current_mode = DisplayMode.CUSTOM_IMAGE
        self.refresh_display()
        return True
    
    def cycle_mode(self):
        """Cycle to the next display mode."""
        self.current_mode = self.current_mode.next()
        logger.info(f"📱 Tablet mode: {self.current_mode}")
        self.refresh_display()
    
    def set_mode(self, mode):
        """Set specific display mode."""
        if isinstance(mode, DisplayMode):
            self.current_mode = mode
            logger.info(f"📱 Tablet mode: {self.current_mode}")
            self.refresh_display()
        else:
            logger.error(f"Invalid mode: {mode}")
    
    # ========================================================================
    # DISPLAY MODES
    # ========================================================================
    
    def refresh_display(self):
        """Refresh the tablet display based on current mode."""
        if not self.tablet:
            logger.debug("Tablet not available - skipping display update")
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
            logger.error(f"Error refreshing tablet: {e}")
            # Don't crash - show error screen instead
            try:
                self._show_error(f"Display error: {str(e)[:50]}")
            except:
                pass
    
    def _show_status_display(self):
        """Show status + action display with preset images."""
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
            "moving_backward": "moving_back",
            "moving_back": "moving_back",
            "strafing_left": "moving_forward",  # Fallback
            "strafing_right": "moving_forward",  # Fallback
            "rotating_left": "standby",  # Fallback
            "rotating_right": "standby"  # Fallback
        }
        
        image_name = image_mapping.get(action_lower)
        if image_name:
            image_url = self._get_preset_image_url(image_name)
            if image_url:
                logger.debug(f"Using preset image: {image_name}")
        
        html = get_status_display_html(
            action=self.current_action,
            action_detail=self.action_detail,
            battery=battery,
            mode=self.continuous_mode,
            image_url=image_url
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show status display: {e}")
    
    def _show_custom_image(self):
        """Show custom static image."""
        if not self.custom_image_path or not os.path.exists(self.custom_image_path):
            logger.warning("No custom image available")
            html = get_error_html("No image selected")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        # Generate URL for custom image
        filename = os.path.basename(self.custom_image_path)
        
        # Use video server if available
        if self.video_server and self.video_server.is_running:
            image_url = f"http://{self.pc_ip}:8080/custom_image/{filename}"
        else:
            # Fallback to file:// URL
            abs_path = os.path.abspath(self.custom_image_path)
            image_url = f"file://{abs_path}"
        
        html = get_custom_image_html(
            image_url=image_url,
            caption=os.path.splitext(filename)[0]
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show custom image: {e}")
    
    def _show_pepper_camera(self):
        """Show Pepper's camera feed."""
        if not self.video_server:
            logger.warning("Video server not available")
            html = get_error_html("Video server not running")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        if not self.video_server.is_running:
            logger.warning("Video server not started")
            html = get_error_html("Video server not started")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        camera_url = self.video_server.get_pepper_url(self.pc_ip)
        
        if not camera_url:
            logger.warning("Could not get Pepper camera URL")
            html = get_error_html("Camera feed unavailable")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        html = get_camera_feed_html(
            camera_url=camera_url,
            camera_name="Pepper's View"
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show Pepper camera: {e}")
    
    def _show_hovercam(self):
        """Show HoverCam feed."""
        if not self.video_server:
            logger.warning("Video server not available")
            html = get_error_html("Video server not running")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        if not self.video_server.is_running:
            logger.warning("Video server not started")
            html = get_error_html("Video server not started")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        camera_url = self.video_server.get_hover_url(self.pc_ip)
        
        if not camera_url:
            logger.warning("Could not get HoverCam URL")
            html = get_error_html("HoverCam unavailable")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        html = get_camera_feed_html(
            camera_url=camera_url,
            camera_name="HoverCam"
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show HoverCam: {e}")
    
    def _show_error(self, message):
        """Show error message on tablet."""
        if not self.tablet:
            return
        
        html = get_error_html(message)
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show error screen: {e}")
    
    def show_blank(self):
        """Show blank screen."""
        if not self.tablet:
            return
        
        html = get_blank_screen_html()
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show blank screen: {e}")
    
    def show_greeting(self):
        """Show greeting screen."""
        if not self.tablet:
            return
        
        logger.info("👋 Showing greeting on tablet")
        
        # Try to find greeting image
        greeting_image = self._get_preset_image_url("hello")
        
        if greeting_image:
            html = get_custom_image_html(
                image_url=greeting_image,
                caption="Hello!"
            )
        else:
            # Fallback to status display with greeting
            html = get_status_display_html(
                action="Hello!",
                action_detail="Nice to meet you!",
                battery=self._get_battery_level(),
                mode=self.continuous_mode,
                image_url=None
            )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Failed to show greeting: {e}")
    
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
    
    def is_available(self):
        """Check if tablet service is available."""
        return self.tablet is not None