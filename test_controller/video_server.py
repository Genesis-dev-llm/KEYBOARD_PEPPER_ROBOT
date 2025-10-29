"""
Video Streaming Server - COMPLETE & DEBUGGED
Minimal, optional video server with all routes properly defined.

FIXES APPLIED:
- Completed _generate_pepper_stream function
- Added all image serving routes
- Fixed duplicate route definitions
- Added proper error handling
"""

import logging
import threading
import time
import os
import cv2
import numpy as np
from flask import Flask, Response, jsonify, send_file
from flask_cors import CORS

logger = logging.getLogger(__name__)

# GLOBAL FLAG - Set to False to disable video completely
VIDEO_ENABLED = True

class VideoStreamingServer:
    """Minimal video server - can be disabled."""
    
    def __init__(self, pepper_session, hovercam_id=0):
        if not VIDEO_ENABLED:
            logger.info("Video server DISABLED by configuration")
            self.enabled = False
            return
        
        self.enabled = True
        self.session = pepper_session
        self.hovercam_id = hovercam_id
        
        # Services
        self.video_device = None
        self.subscriber_id = None
        self.hovercam = None
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Server state
        self.is_running = False
        self.server_thread = None
        
        # Frame buffers
        self._pepper_frame = None
        self._hover_frame = None
        self._frame_lock = threading.Lock()
        
        # FPS throttle
        self._last_frame_time = 0
        self._min_frame_interval = 0.1  # 10 FPS max
    
    def _initialize(self):
        """Initialize cameras - LAZY (only when started)."""
        if not self.enabled:
            return
        
        try:
            # Pepper camera - LOWER RESOLUTION for speed
            self.video_device = self.session.service("ALVideoDevice")
            self.subscriber_id = self.video_device.subscribeCamera(
                "video_server", 
                0,    # Top camera
                1,    # 320x240 (was 2=640x480)
                11,   # RGB
                5     # 5fps (was 10fps)
            )
            logger.info("✓ Pepper camera: 320x240@5fps (low-res mode)")
            
            # HoverCam - only try once
            try:
                cap = cv2.VideoCapture(self.hovercam_id)
                if cap.isOpened():
                    # Test read
                    ret, _ = cap.read()
                    if ret:
                        self.hovercam = cap
                        logger.info(f"✓ HoverCam on device {self.hovercam_id}")
                    else:
                        cap.release()
                else:
                    cap.release()
            except Exception as e:
                logger.debug(f"HoverCam init error: {e}")
            
            if not self.hovercam:
                logger.info("HoverCam not detected (optional)")
                
        except Exception as e:
            logger.error(f"Camera init error: {e}")
    
    def _setup_routes(self):
        """Setup all Flask routes."""
        if not self.enabled:
            return
        
        @self.app.route('/health')
        def health():
            """Health check."""
            return jsonify({
                'status': 'ok',
                'pepper_camera': self.subscriber_id is not None,
                'hovercam': self.hovercam is not None
            })
        
        @self.app.route('/pepper_feed')
        def pepper_feed():
            """Pepper camera MJPEG stream."""
            return Response(
                self._generate_pepper_stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/hover_feed')
        def hover_feed():
            """HoverCam MJPEG stream."""
            return Response(
                self._generate_hover_stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/pepper_snapshot')
        def pepper_snapshot():
            """Single frame from Pepper."""
            with self._frame_lock:
                if self._pepper_frame is not None:
                    _, buffer = cv2.imencode('.jpg', self._pepper_frame)
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
            return "No frame available", 404
        
        @self.app.route('/hover_snapshot')
        def hover_snapshot():
            """Single frame from HoverCam."""
            with self._frame_lock:
                if self._hover_frame is not None:
                    _, buffer = cv2.imencode('.jpg', self._hover_frame)
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
            return "No frame available", 404
        
        @self.app.route('/image/<path:filename>')
        def serve_image(filename):
            """Serve preset or custom tablet images."""
            # Try preset directory first
            preset_dir = "assets/tablet_images"
            filepath = os.path.join(preset_dir, filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, mimetype=self._get_mimetype(filename))
            
            # Try custom directory
            custom_dir = os.path.join(preset_dir, "custom")
            filepath = os.path.join(custom_dir, filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, mimetype=self._get_mimetype(filename))
            
            logger.warning(f"Image not found: {filename}")
            return "Image not found", 404
        
        @self.app.route('/custom_image/<path:filename>')
        def serve_custom_image(filename):
            """Serve custom user-uploaded images."""
            custom_dir = "assets/tablet_images/custom"
            filepath = os.path.join(custom_dir, filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, mimetype=self._get_mimetype(filename))
            
            return "Image not found", 404
    
    def _get_mimetype(self, filename):
        """Get MIME type from filename."""
        ext = filename.lower().split('.')[-1]
        mimetypes = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'bmp': 'image/bmp'
        }
        return mimetypes.get(ext, 'application/octet-stream')
    
    def _generate_pepper_stream(self):
        """Generate MJPEG stream from Pepper - WITH FPS THROTTLE."""
        logger.debug("Pepper stream generator started")
        
        while self.is_running:
            try:
                # Throttle FPS
                current_time = time.time()
                if current_time - self._last_frame_time < self._min_frame_interval:
                    time.sleep(0.05)
                    continue
                
                self._last_frame_time = current_time
                
                if self.video_device and self.subscriber_id:
                    # Get frame from Pepper
                    img_data = self.video_device.getImageRemote(self.subscriber_id)
                    
                    if img_data and len(img_data) > 6:
                        width, height = img_data[0], img_data[1]
                        image_bytes = img_data[6]
                        
                        # Convert to numpy array
                        frame = np.frombuffer(image_bytes, dtype=np.uint8)
                        frame = frame.reshape((height, width, 3))
                        
                        # Store latest frame
                        with self._frame_lock:
                            self._pepper_frame = frame.copy()
                        
                        # Encode as JPEG (lower quality for speed)
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                        frame_bytes = buffer.tobytes()
                        
                        # Yield as MJPEG frame
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Pepper stream error: {e}")
                time.sleep(1)
    
    def _generate_hover_stream(self):
        """Generate MJPEG stream from HoverCam."""
        logger.debug("HoverCam stream generator started")
        
        while self.is_running:
            try:
                if self.hovercam and self.hovercam.isOpened():
                    ret, frame = self.hovercam.read()
                    
                    if ret and frame is not None:
                        # Store latest frame
                        with self._frame_lock:
                            self._hover_frame = frame.copy()
                        
                        # Encode as JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                        frame_bytes = buffer.tobytes()
                        
                        # Yield as MJPEG frame
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                logger.error(f"HoverCam stream error: {e}")
                time.sleep(1)
    
    def start(self, host='0.0.0.0', port=8080):
        """Start server - ONLY if explicitly called."""
        if not self.enabled:
            logger.info("Video server disabled - skipping")
            return
        
        if self.is_running:
            logger.warning("Video server already running")
            return
        
        # Initialize cameras
        self._initialize()
        
        # Setup routes
        self._setup_routes()
        
        self.is_running = True
        
        def run_server():
            try:
                logger.info(f"🎥 Video server starting on {host}:{port}")
                logger.info(f"   Pepper: http://{host}:{port}/pepper_feed")
                logger.info(f"   Hover:  http://{host}:{port}/hover_feed")
                
                # Suppress Flask logs
                import logging as flask_logging
                flask_log = flask_logging.getLogger('werkzeug')
                flask_log.setLevel(flask_logging.ERROR)
                
                self.app.run(host=host, port=port, threaded=True, debug=False)
                
            except Exception as e:
                logger.error(f"Video server error: {e}")
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        time.sleep(1.5)
        logger.info("✓ Video server ready")
    
    def stop(self):
        """Stop server and cleanup."""
        if not self.enabled:
            return
        
        logger.info("Stopping video server...")
        self.is_running = False
        
        # Cleanup Pepper camera
        if self.subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.subscriber_id)
                logger.debug("✓ Pepper camera unsubscribed")
            except Exception as e:
                logger.warning(f"Error unsubscribing camera: {e}")
        
        # Cleanup HoverCam
        if self.hovercam:
            try:
                self.hovercam.release()
                logger.debug("✓ HoverCam released")
            except Exception as e:
                logger.warning(f"Error releasing HoverCam: {e}")
        
        logger.info("✓ Video server stopped")
    
    def get_pepper_url(self, host_ip):
        """Get Pepper feed URL."""
        return f"http://{host_ip}:8080/pepper_feed" if self.enabled else None
    
    def get_hover_url(self, host_ip):
        """Get HoverCam feed URL."""
        return f"http://{host_ip}:8080/hover_feed" if self.enabled else None


class DummyVideoServer:
    """Dummy server when video is disabled."""
    
    def __init__(self):
        self.enabled = False
        self.is_running = False
    
    def start(self, host='0.0.0.0', port=8080):
        logger.info("Video server disabled (dummy mode)")
    
    def stop(self):
        pass
    
    def get_pepper_url(self, host_ip):
        return None
    
    def get_hover_url(self, host_ip):
        return None


def create_video_server(pepper_session, hovercam_id=0, start=False):
    """
    Create video server.
    
    Args:
        pepper_session: NAOqi session
        hovercam_id: USB camera device ID
        start: If True, start immediately
    
    Returns:
        VideoStreamingServer or DummyVideoServer
    """
    if not VIDEO_ENABLED:
        logger.info("Video globally disabled")
        return DummyVideoServer()
    
    server = VideoStreamingServer(pepper_session, hovercam_id)
    
    if start:
        server.start()
    
    return server