"""
Video Streaming Server - FIXED VERSION
Serves camera feeds (Pepper + HoverCam) over HTTP using Flask.
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

class VideoStreamingServer:
    """HTTP server that streams camera feeds."""
    
    def __init__(self, pepper_session, hovercam_id=0):
        self.session = pepper_session
        self.hovercam_id = hovercam_id
        
        # Services
        self.video_device = None
        self.subscriber_id = None
        
        # HoverCam
        self.hovercam = None
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Server control
        self.is_running = False
        self.server_thread = None
        
        # Frame buffers
        self._pepper_frame = None
        self._hover_frame = None
        self._frame_lock = threading.Lock()
        
        # Setup routes
        self._setup_routes()
        
        # Initialize cameras
        self._initialize()
    
    def _initialize(self):
        """Initialize Pepper's camera and HoverCam."""
        try:
            # Pepper's camera
            self.video_device = self.session.service("ALVideoDevice")
            self.subscriber_id = self.video_device.subscribeCamera(
                "video_server", 0, 2, 11, 10  # Top camera, 640x480, RGB, 10fps
            )
            logger.info("✓ Pepper's camera initialized for streaming")
            
            # HoverCam (USB)
            for cam_id in range(5):
                try:
                    cap = cv2.VideoCapture(cam_id)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            self.hovercam = cap
                            self.hovercam_id = cam_id
                            logger.info(f"✓ HoverCam detected on device {cam_id}")
                            break
                        else:
                            cap.release()
                except:
                    continue
            
            if not self.hovercam:
                logger.warning("⚠ HoverCam not detected (USB camera)")
                
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
    
    def _setup_routes(self):
        """Setup Flask routes - FIXED duplicate route."""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'ok',
                'pepper_camera': self.subscriber_id is not None,
                'hovercam': self.hovercam is not None
            })
        
        @self.app.route('/pepper_feed')
        def pepper_feed():
            return Response(
                self._generate_pepper_stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/hover_feed')
        def hover_feed():
            return Response(
                self._generate_hover_stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/pepper_snapshot')
        def pepper_snapshot():
            with self._frame_lock:
                if self._pepper_frame is not None:
                    _, buffer = cv2.imencode('.jpg', self._pepper_frame)
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
            return "No frame available", 404
        
        @self.app.route('/hover_snapshot')
        def hover_snapshot():
            with self._frame_lock:
                if self._hover_frame is not None:
                    _, buffer = cv2.imencode('.jpg', self._hover_frame)
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
            return "No frame available", 404
        
        # FIXED: Single route for preset images
        @self.app.route('/image/<path:filename>')
        def serve_image(filename):
            """Serve tablet images (preset or custom)."""
            # Try preset directory first
            preset_dir = "assets/tablet_images"
            filepath = os.path.join(preset_dir, filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, mimetype=self._get_mimetype(filename))
            
            # Try custom directory
            custom_dir = "assets/tablet_images/custom"
            filepath = os.path.join(custom_dir, filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, mimetype=self._get_mimetype(filename))
            
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
        if filename.endswith('.png'):
            return 'image/png'
        elif filename.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif filename.endswith('.gif'):
            return 'image/gif'
        else:
            return 'application/octet-stream'
    
    def _generate_pepper_stream(self):
        """Generate MJPEG stream from Pepper's camera."""
        while self.is_running:
            try:
                if self.video_device and self.subscriber_id:
                    img_data = self.video_device.getImageRemote(self.subscriber_id)
                    
                    if img_data:
                        width, height = img_data[0], img_data[1]
                        image_bytes = img_data[6]
                        
                        # Convert to numpy array
                        frame = np.frombuffer(image_bytes, dtype=np.uint8)
                        frame = frame.reshape((height, width, 3))
                        
                        # Store latest frame
                        with self._frame_lock:
                            self._pepper_frame = frame.copy()
                        
                        # Encode as JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frame_bytes = buffer.tobytes()
                        
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                logger.error(f"Pepper stream error: {e}")
                time.sleep(1)
    
    def _generate_hover_stream(self):
        """Generate MJPEG stream from HoverCam."""
        while self.is_running:
            try:
                if self.hovercam and self.hovercam.isOpened():
                    ret, frame = self.hovercam.read()
                    
                    if ret:
                        with self._frame_lock:
                            self._hover_frame = frame.copy()
                        
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frame_bytes = buffer.tobytes()
                        
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                logger.error(f"HoverCam stream error: {e}")
                time.sleep(1)
    
    def start(self, host='0.0.0.0', port=8080):
        """Start the Flask server in a background thread."""
        if self.is_running:
            logger.warning("Video server already running")
            return
        
        self.is_running = True
        
        def run_server():
            try:
                logger.info(f"🎥 Starting video server on http://{host}:{port}")
                
                # Suppress Flask logging
                import logging as flask_logging
                flask_log = flask_logging.getLogger('werkzeug')
                flask_log.setLevel(flask_logging.ERROR)
                
                self.app.run(host=host, port=port, threaded=True, debug=False)
                
            except Exception as e:
                logger.error(f"Video server error: {e}")
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        time.sleep(2)
        logger.info("✓ Video streaming server ready")
    
    def stop(self):
        """Stop the video server."""
        logger.info("Stopping video server...")
        self.is_running = False
        
        if self.subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.subscriber_id)
            except:
                pass
        
        if self.hovercam:
            try:
                self.hovercam.release()
            except:
                pass
        
        logger.info("✓ Video server stopped")
    
    def get_pepper_url(self, host_ip):
        return f"http://{host_ip}:8080/pepper_feed"
    
    def get_hover_url(self, host_ip):
        return f"http://{host_ip}:8080/hover_feed"


def create_video_server(pepper_session, hovercam_id=0):
    """Factory function to create video server."""
    return VideoStreamingServer(pepper_session, hovercam_id)