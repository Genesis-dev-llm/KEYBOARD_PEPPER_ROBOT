"""
Video Feed Controller - FIXED WITH PROPER TOGGLE
Displays Pepper's camera feed in a window that can be toggled on/off.

FIXES APPLIED:
- Added proper start/stop toggle
- Window closes cleanly
- No zombie threads
- Press V to toggle on/off
"""

import logging
import threading
import urllib.request
import urllib.error
import cv2
import numpy as np
from .. import config

logger = logging.getLogger(__name__)

class VideoController:
    """Manages video feed from Pepper's camera with toggle control."""
    
    def __init__(self, ip):
        self.ip = ip
        self.video_url = f"http://{ip}:{config.VIDEO_PORT}/pepper_feed"
        self.is_running = False
        self.thread = None
        self._stop_requested = False
    
    def toggle(self):
        """Toggle video feed on/off."""
        if self.is_running:
            self.stop()
        else:
            self.start()
    
    def start(self):
        """Start video feed in a separate thread."""
        if self.is_running:
            logger.warning("Video feed already running")
            return
        
        # Check if server is accessible first
        if not self._check_server():
            logger.error("=" * 60)
            logger.error("VIDEO SERVER NOT ACCESSIBLE")
            logger.error("=" * 60)
            logger.error(f"Cannot connect to: {self.video_url}")
            logger.error("")
            logger.error("SOLUTION:")
            logger.error("  Video server may not be running")
            logger.error("  Or use --no-video flag to disable")
            logger.error("=" * 60)
            return
        
        self.is_running = True
        self._stop_requested = False
        self.thread = threading.Thread(target=self._display_loop, daemon=True)
        self.thread.start()
        logger.info("✓ Video feed started (press V to close)")
    
    def stop(self):
        """Stop video feed and close window."""
        if not self.is_running:
            return
        
        logger.info("Stopping video feed...")
        self.is_running = False
        self._stop_requested = True
        
        # Close any OpenCV windows
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        # Wait for thread to finish (with timeout)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        self.thread = None
        logger.info("✓ Video feed stopped")
    
    def _check_server(self):
        """Check if video server is accessible."""
        try:
            health_url = f"http://{self.ip}:{config.VIDEO_PORT}/health"
            response = urllib.request.urlopen(health_url, timeout=2)
            return response.status == 200
        except Exception as e:
            logger.debug(f"Server check failed: {e}")
            return False
    
    def _display_loop(self):
        """Display video feed (runs in background thread)."""
        logger.info(f"Connecting to video stream: {self.video_url}")
        
        window_name = 'Pepper Camera Feed (Press V or Q to close)'
        
        try:
            stream = urllib.request.urlopen(self.video_url, timeout=config.VIDEO_TIMEOUT)
            bytes_data = b''
            
            logger.info("✓ Video stream connected!")
            
            while self.is_running and not self._stop_requested:
                try:
                    # Read data from stream
                    chunk = stream.read(1024)
                    if not chunk:
                        break
                    
                    bytes_data += chunk
                    
                    # Look for JPEG markers
                    a = bytes_data.find(b'\xff\xd8')  # JPEG start
                    b = bytes_data.find(b'\xff\xd9')  # JPEG end
                    
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        
                        # Decode and display
                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8), 
                            cv2.IMREAD_COLOR
                        )
                        
                        if frame is not None:
                            cv2.imshow(window_name, frame)
                            
                            # Check for key press or window close
                            key = cv2.waitKey(1) & 0xFF
                            
                            # V or Q to close
                            if key in [ord('v'), ord('q'), ord('V'), ord('Q')]:
                                logger.info("Video closed by user (key press)")
                                self.is_running = False
                                break
                            
                            # ESC to close
                            if key == 27:
                                logger.info("Video closed by user (ESC)")
                                self.is_running = False
                                break
                            
                            # Check if window was closed (X button)
                            try:
                                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                                    logger.info("Video closed by user (X button)")
                                    self.is_running = False
                                    break
                            except:
                                # Window doesn't exist anymore
                                self.is_running = False
                                break
                                
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Frame processing error: {e}")
                    break
            
            # Cleanup
            try:
                stream.close()
            except:
                pass
                    
        except urllib.error.URLError as e:
            logger.error(f"Could not connect to video stream: {e}")
            logger.error(f"Make sure video server is running")
        except Exception as e:
            logger.error(f"Video stream error: {e}")
        finally:
            # Ensure cleanup
            try:
                cv2.destroyAllWindows()
            except:
                pass
            self.is_running = False
            logger.info("Video display loop ended")
    
    def is_active(self):
        """Check if video feed is currently running."""
        return self.is_running