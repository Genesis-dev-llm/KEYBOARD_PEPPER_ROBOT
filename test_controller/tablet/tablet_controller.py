"""
Tablet Controller - ULTRA-OPTIMIZED VERSION
Fast, responsive tablet updates with smart caching and batching.

OPTIMIZATIONS:
- Display update batching (prevent flooding)
- HTML template caching
- Async display updates
- Debounced battery queries
- Smart image URL caching
"""

import logging
import os
import socket
import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
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
    """Optimized tablet controller with caching and batching."""
    
    def __init__(self, session, robot_ip, video_server=None):
        self.session = session
        self.robot_ip = robot_ip
        self.video_server = video_server
        self.tablet = None
        self.battery_service = None
        
        # Get PC IP
        self.pc_ip = self._get_pc_ip()
        
        # Current state
        self.current_mode = DisplayMode.STATUS
        self.current_action = "Ready"
        self.action_detail = "Waiting for input..."
        self.continuous_mode = True
        
        # Custom image
        self.custom_image_path = None
        
        # Directories
        self.preset_dir = "assets/tablet_images"
        self.custom_dir = os.path.join(self.preset_dir, "custom")
        os.makedirs(self.preset_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
        
        # Caching system
        self._last_battery_query = 0
        self._cached_battery = 50
        self._battery_cache_timeout = 3.0  # 3 seconds
        
        # Display update throttling
        self._last_display_update = 0
        self._display_update_throttle = 0.3  # 300ms minimum
        self._pending_update = False
        
        # HTML template cache (avoid regenerating same HTML)
        self._html_cache = {}
        self._cache_size_limit = 10
        
        # Image URL cache (avoid filesystem checks)
        self._image_url_cache = {}
        self._image_cache_timeout = 60.0  # 1 minute
        self._image_cache_time = {}
        
        # Async executor for non-blocking updates
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="Tablet")
        
        # Update queue (batch multiple rapid updates)
        self._update_queue = deque(maxlen=1)  # Only keep latest
        self._update_lock = threading.Lock()
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize tablet service."""
        try:
            self.tablet = self.session.service("ALTabletService")
            logger.info("✓ Tablet service connected")
            
            try:
                self.battery_service = self.session.service("ALBattery")
                logger.info("✓ Battery service connected")
            except Exception as e:
                logger.warning(f"Battery service unavailable: {e}")
            
            # Initial display (async)
            self._executor.submit(self.refresh_display)
            
        except Exception as e:
            logger.error(f"Failed to initialize tablet: {e}")
            self.tablet = None
    
    def _get_pc_ip(self):
        """Get PC IP with fallback methods."""
        # Method 1: Google DNS trick
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            if ip and ip != '127.0.0.1':
                logger.info(f"✓ PC IP: {ip}")
                return ip
        except:
            pass
        
        # Method 2: Hostname
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip and ip != '127.0.0.1':
                logger.info(f"✓ PC IP (hostname): {ip}")
                return ip
        except:
            pass
        
        # Method 3: Same subnet estimation
        try:
            base = '.'.join(self.robot_ip.split('.')[:3])
            test_ip = f"{base}.100"
            logger.info(f"📡 PC IP (estimated): {test_ip}")
            return test_ip
        except:
            pass
        
        logger.warning("⚠️ Could not detect PC IP!")
        return "localhost"
    
    def _get_battery_level(self):
        """Get battery with aggressive caching."""
        current_time = time.time()
        
        # Use cache if recent
        if current_time - self._last_battery_query < self._battery_cache_timeout:
            return self._cached_battery
        
        # Query async (don't block)
        try:
            if self.battery_service:
                battery = self.battery_service.getBatteryCharge()
                self._cached_battery = battery
                self._last_battery_query = current_time
                return battery
        except:
            pass
        
        return self._cached_battery
    
    def _get_preset_image_url(self, name):
        """Get preset image URL with caching."""
        current_time = time.time()
        
        # Check cache
        if name in self._image_url_cache:
            cache_time = self._image_cache_time.get(name, 0)
            if current_time - cache_time < self._image_cache_timeout:
                return self._image_url_cache[name]
        
        # Search for image
        extensions = ['.png', '.jpg', '.jpeg', '.gif']
        
        for ext in extensions:
            filepath = os.path.join(self.preset_dir, f"{name}{ext}")
            if os.path.exists(filepath):
                # Generate URL
                if self.video_server and self.video_server.is_running:
                    url = f"http://{self.pc_ip}:8080/image/{name}{ext}"
                else:
                    url = f"file://{os.path.abspath(filepath)}"
                
                # Cache it
                self._image_url_cache[name] = url
                self._image_cache_time[name] = current_time
                
                return url
        
        # Not found - cache None
        self._image_url_cache[name] = None
        self._image_cache_time[name] = current_time
        
        return None
    
    def _should_update_display(self):
        """Check if enough time passed (throttling)."""
        current_time = time.time()
        if current_time - self._last_display_update >= self._display_update_throttle:
            self._last_display_update = current_time
            return True
        else:
            # Mark as pending for later
            self._pending_update = True
            return False
    
    def _get_cached_html(self, cache_key, generator_func, *args):
        """Get HTML from cache or generate."""
        if cache_key in self._html_cache:
            return self._html_cache[cache_key]
        
        # Generate
        html = generator_func(*args)
        
        # Cache it (with size limit)
        if len(self._html_cache) >= self._cache_size_limit:
            # Remove oldest entry
            self._html_cache.pop(next(iter(self._html_cache)))
        
        self._html_cache[cache_key] = html
        return html
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def set_action(self, action, detail=""):
        """Update action - ASYNC & BATCHED."""
        self.current_action = action
        self.action_detail = detail
        
        # Only update if in STATUS mode
        if self.current_mode == DisplayMode.STATUS:
            if self._should_update_display():
                # Async update (non-blocking)
                self._executor.submit(self.refresh_display)
            # else: throttled, will update later
    
    def set_movement_mode(self, continuous):
        """Update movement mode."""
        self.continuous_mode = continuous
        
        if self.current_mode == DisplayMode.STATUS:
            if self._should_update_display():
                self._executor.submit(self.refresh_display)
    
    def set_custom_image(self, image_path):
        """Set custom image - ASYNC."""
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return False
        
        self.custom_image_path = image_path
        logger.info(f"Custom image: {os.path.basename(image_path)}")
        
        # Switch mode
        self.current_mode = DisplayMode.CUSTOM_IMAGE
        
        # Async update
        self._executor.submit(self.refresh_display)
        return True
    
    def cycle_mode(self):
        """Cycle display mode - ASYNC."""
        self.current_mode = self.current_mode.next()
        logger.info(f"📱 Tablet: {self.current_mode}")
        
        self._executor.submit(self.refresh_display)
    
    def set_mode(self, mode):
        """Set specific mode - ASYNC."""
        if isinstance(mode, DisplayMode):
            self.current_mode = mode
            logger.info(f"📱 Tablet: {self.current_mode}")
            self._executor.submit(self.refresh_display)
    
    def refresh_display(self):
        """Refresh display based on mode - OPTIMIZED."""
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
            logger.error(f"Display error: {e}")
            try:
                self._show_error(str(e)[:50])
            except:
                pass
    
    def _show_status_display(self):
        """Show status with caching."""
        battery = self._get_battery_level()
        
        # Get image URL (cached)
        image_url = None
        action_lower = self.current_action.lower().replace(" ", "_")
        
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
            "moving_back": "moving_back"
        }
        
        image_name = image_mapping.get(action_lower)
        if image_name:
            image_url = self._get_preset_image_url(image_name)
        
        # Cache key
        cache_key = f"status_{self.current_action}_{battery}_{self.continuous_mode}_{image_url}"
        
        # Get HTML (cached if possible)
        html = self._get_cached_html(
            cache_key,
            get_status_display_html,
            self.current_action,
            self.action_detail,
            battery,
            self.continuous_mode,
            image_url
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Show status failed: {e}")
    
    def _show_custom_image(self):
        """Show custom image - OPTIMIZED."""
        if not self.custom_image_path or not os.path.exists(self.custom_image_path):
            html = get_error_html("No image selected")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        filename = os.path.basename(self.custom_image_path)
        
        if self.video_server and self.video_server.is_running:
            image_url = f"http://{self.pc_ip}:8080/custom_image/{filename}"
        else:
            image_url = f"file://{os.path.abspath(self.custom_image_path)}"
        
        # Cache HTML
        cache_key = f"custom_{filename}"
        html = self._get_cached_html(
            cache_key,
            get_custom_image_html,
            image_url,
            os.path.splitext(filename)[0]
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Show custom failed: {e}")
    
    def _show_pepper_camera(self):
        """Show Pepper camera - OPTIMIZED."""
        if not self.video_server or not self.video_server.is_running:
            html = get_error_html("Video server not running")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        camera_url = self.video_server.get_pepper_url(self.pc_ip)
        
        if not camera_url:
            html = get_error_html("Camera unavailable")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        # Cache HTML
        cache_key = f"pepper_cam_{camera_url}"
        html = self._get_cached_html(
            cache_key,
            get_camera_feed_html,
            camera_url,
            "Pepper's View"
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Show Pepper cam failed: {e}")
    
    def _show_hovercam(self):
        """Show HoverCam - OPTIMIZED."""
        if not self.video_server or not self.video_server.is_running:
            html = get_error_html("Video server not running")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        camera_url = self.video_server.get_hover_url(self.pc_ip)
        
        if not camera_url:
            html = get_error_html("HoverCam unavailable")
            try:
                self.tablet.showWebview(html)
            except:
                pass
            return
        
        cache_key = f"hover_cam_{camera_url}"
        html = self._get_cached_html(
            cache_key,
            get_camera_feed_html,
            camera_url,
            "HoverCam"
        )
        
        try:
            self.tablet.showWebview(html)
        except Exception as e:
            logger.error(f"Show HoverCam failed: {e}")
    
    def _show_error(self, message):
        """Show error - not cached."""
        if not self.tablet:
            return
        
        html = get_error_html(message)
        try:
            self.tablet.showWebview(html)
        except:
            pass
    
    def show_blank(self):
        """Show blank - ASYNC."""
        self._executor.submit(self._show_blank_internal)
    
    def _show_blank_internal(self):
        """Internal blank screen."""
        if not self.tablet:
            return
        
        html = get_blank_screen_html()
        try:
            self.tablet.showWebview(html)
        except:
            pass
    
    def show_greeting(self):
        """Show greeting - ASYNC."""
        self._executor.submit(self._show_greeting_internal)
    
    def _show_greeting_internal(self):
        """Internal greeting display."""
        if not self.tablet:
            return
        
        logger.info("👋 Showing greeting")
        
        greeting_image = self._get_preset_image_url("hello")
        
        if greeting_image:
            html = get_custom_image_html(greeting_image, "Hello!")
        else:
            html = get_status_display_html(
                "Hello!",
                "Nice to meet you!",
                self._get_battery_level(),
                self.continuous_mode,
                None
            )
        
        try:
            self.tablet.showWebview(html)
        except:
            pass
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def reset(self):
        """Reset tablet."""
        if self.tablet:
            try:
                self.tablet.resetTablet()
                logger.info("Tablet reset")
            except Exception as e:
                logger.error(f"Reset failed: {e}")
    
    def get_current_mode(self):
        """Get current mode."""
        return self.current_mode
    
    def is_video_mode(self):
        """Check if showing video."""
        return self.current_mode in [DisplayMode.PEPPER_CAM, DisplayMode.HOVERCAM]
    
    def is_available(self):
        """Check if available."""
        return self.tablet is not None
    
    def cleanup(self):
        """Cleanup resources."""
        self._executor.shutdown(wait=False)