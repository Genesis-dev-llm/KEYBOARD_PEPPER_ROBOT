"""
Camera Panel - Dual video feed display
Left side panel with Pepper camera + external camera feeds.
"""

import logging
import threading
import time
import cv2
import numpy as np
import urllib.request
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QComboBox, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from .file_handler import FileDropPanel

logger = logging.getLogger(__name__)

class VideoDisplay(QLabel):
    """Widget for displaying video frames."""
    
    def __init__(self, title="Camera"):
        super().__init__()
        
        self.setObjectName("videoLabel")
        self.setMinimumSize(320, 240)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)
        
        # Placeholder
        self.setText(f"{title}\nNo feed")
        self.setStyleSheet("background-color: #000; color: #666; font-size: 18px;")
    
    def update_frame(self, frame):
        """Update with new video frame (numpy array)."""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Create QImage
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit widget while maintaining aspect ratio
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(f"Error updating frame: {e}")
    
    def clear_frame(self):
        """Clear the display."""
        self.clear()
        self.setText("No feed")


class PepperCameraFeed:
    """Manages Pepper's camera feed streaming."""
    
    def __init__(self, ip, port=8080):
        self.ip = ip
        self.port = port
        self.video_url = f"http://{ip}:{port}/video_feed"
        self.is_running = False
        self.thread = None
        self.frame_callback = None
    
    def start(self, callback):
        """Start streaming with frame callback."""
        if self.is_running:
            return False
        
        self.frame_callback = callback
        self.is_running = True
        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop streaming."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _stream_loop(self):
        """Main streaming loop."""
        try:
            stream = urllib.request.urlopen(self.video_url, timeout=5)
            bytes_data = b''
            
            while self.is_running:
                bytes_data += stream.read(1024)
                a = bytes_data.find(b'\xff\xd8')  # JPEG start
                b = bytes_data.find(b'\xff\xd9')  # JPEG end
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    # Decode frame
                    frame = cv2.imdecode(
                        np.frombuffer(jpg, dtype=np.uint8),
                        cv2.IMREAD_COLOR
                    )
                    
                    if frame is not None and self.frame_callback:
                        self.frame_callback(frame)
                        
        except Exception as e:
            logger.error(f"Pepper camera stream error: {e}")
        finally:
            self.is_running = False


class ExternalCameraFeed:
    """Manages external webcam/HoverCam feed."""
    
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.capture = None
        self.is_running = False
        self.thread = None
        self.frame_callback = None
    
    def start(self, callback):
        """Start streaming."""
        if self.is_running:
            return False
        
        try:
            self.capture = cv2.VideoCapture(self.camera_id)
            if not self.capture.isOpened():
                logger.error(f"Cannot open camera {self.camera_id}")
                return False
            
            self.frame_callback = callback
            self.is_running = True
            self.thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.thread.start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start external camera: {e}")
            return False
    
    def stop(self):
        """Stop streaming."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.capture:
            self.capture.release()
            self.capture = None
    
    def _stream_loop(self):
        """Main streaming loop."""
        while self.is_running and self.capture:
            try:
                ret, frame = self.capture.read()
                if ret and self.frame_callback:
                    self.frame_callback(frame)
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                logger.error(f"External camera error: {e}")
                break
        
        self.is_running = False


class CameraPanel(QWidget):
    """Panel for dual camera feeds and file drop."""
    
    status_update_signal = pyqtSignal(str)
    
    def __init__(self, session, robot_ip, tablet_ctrl):
        super().__init__()
        
        self.session = session
        self.robot_ip = robot_ip
        self.tablet = tablet_ctrl
        
        # Camera feeds
        self.pepper_feed = PepperCameraFeed(robot_ip)
        self.external_feed = ExternalCameraFeed(camera_id=0)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # === PEPPER CAMERA ===
        pepper_group = QGroupBox("📹 Pepper Camera")
        pepper_layout = QVBoxLayout()
        
        self.pepper_display = VideoDisplay("Pepper's View")
        pepper_layout.addWidget(self.pepper_display)
        
        # Pepper camera controls
        pepper_controls = QHBoxLayout()
        
        self.pepper_start_btn = QPushButton("▶ Start")
        self.pepper_start_btn.clicked.connect(self._start_pepper_camera)
        
        self.pepper_stop_btn = QPushButton("⏹ Stop")
        self.pepper_stop_btn.clicked.connect(self._stop_pepper_camera)
        self.pepper_stop_btn.setEnabled(False)
        
        pepper_controls.addWidget(self.pepper_start_btn)
        pepper_controls.addWidget(self.pepper_stop_btn)
        
        pepper_layout.addLayout(pepper_controls)
        pepper_group.setLayout(pepper_layout)
        
        # === EXTERNAL CAMERA ===
        external_group = QGroupBox("📷 External Camera")
        external_layout = QVBoxLayout()
        
        self.external_display = VideoDisplay("HoverCam / Webcam")
        external_layout.addWidget(self.external_display)
        
        # External camera controls
        external_controls = QHBoxLayout()
        
        self.camera_selector = QComboBox()
        self.camera_selector.addItems(["Camera 0", "Camera 1", "Camera 2"])
        
        self.external_start_btn = QPushButton("▶ Start")
        self.external_start_btn.clicked.connect(self._start_external_camera)
        
        self.external_stop_btn = QPushButton("⏹ Stop")
        self.external_stop_btn.clicked.connect(self._stop_external_camera)
        self.external_stop_btn.setEnabled(False)
        
        external_controls.addWidget(self.camera_selector)
        external_controls.addWidget(self.external_start_btn)
        external_controls.addWidget(self.external_stop_btn)
        
        external_layout.addLayout(external_controls)
        external_group.setLayout(external_layout)
        
        # === FILE DROP ZONE ===
        self.file_drop_panel = FileDropPanel(self.tablet, self.session)
        self.file_drop_panel.file_displayed.connect(self._on_file_displayed)
        
        # Add all to main layout
        layout.addWidget(pepper_group, 1)
        layout.addWidget(external_group, 1)
        layout.addWidget(self.file_drop_panel, 0)
    
    def _start_pepper_camera(self):
        """Start Pepper camera feed."""
        success = self.pepper_feed.start(self._on_pepper_frame)
        if success:
            self.pepper_start_btn.setEnabled(False)
            self.pepper_stop_btn.setEnabled(True)
            self.status_update_signal.emit("Pepper camera: Started")
        else:
            self.status_update_signal.emit("Pepper camera: Failed to start")
    
    def _stop_pepper_camera(self):
        """Stop Pepper camera feed."""
        self.pepper_feed.stop()
        self.pepper_display.clear_frame()
        self.pepper_start_btn.setEnabled(True)
        self.pepper_stop_btn.setEnabled(False)
        self.status_update_signal.emit("Pepper camera: Stopped")
    
    def _start_external_camera(self):
        """Start external camera feed."""
        camera_id = self.camera_selector.currentIndex()
        self.external_feed.camera_id = camera_id
        
        success = self.external_feed.start(self._on_external_frame)
        if success:
            self.external_start_btn.setEnabled(False)
            self.external_stop_btn.setEnabled(True)
            self.camera_selector.setEnabled(False)
            self.status_update_signal.emit(f"External camera {camera_id}: Started")
        else:
            self.status_update_signal.emit(f"External camera {camera_id}: Failed to start")
    
    def _stop_external_camera(self):
        """Stop external camera feed."""
        self.external_feed.stop()
        self.external_display.clear_frame()
        self.external_start_btn.setEnabled(True)
        self.external_stop_btn.setEnabled(False)
        self.camera_selector.setEnabled(True)
        self.status_update_signal.emit("External camera: Stopped")
    
    def _on_pepper_frame(self, frame):
        """Handle new Pepper camera frame."""
        self.pepper_display.update_frame(frame)
    
    def _on_external_frame(self, frame):
        """Handle new external camera frame."""
        self.external_display.update_frame(frame)
    
    def _on_file_displayed(self, file_path, success):
        """Handle file drop result."""
        if success:
            self.status_update_signal.emit(f"File displayed: {file_path}")
        else:
            self.status_update_signal.emit(f"Failed to display: {file_path}")
    
    def cleanup(self):
        """Cleanup resources."""
        self._stop_pepper_camera()
        self._stop_external_camera()