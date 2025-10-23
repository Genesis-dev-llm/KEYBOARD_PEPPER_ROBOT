"""
Camera Panel - Display video feeds
Shows Pepper's camera and HoverCam (USB) feeds.
"""

import os
import logging
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np

from .file_handler import FileDropPanel

logger = logging.getLogger(__name__)

class CameraPanel(QWidget):
    """Panel for displaying camera feeds."""
    
    def __init__(self, session, robot_ip, tablet_ctrl):
        super().__init__()
        
        self.session = session
        self.robot_ip = robot_ip
        self.tablet = tablet_ctrl
        
        # Camera captures
        self.pepper_video = None
        self.hovercam = None
        self.pepper_subscriber_id = None
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frames)
        
        self._init_ui()
        self._init_cameras()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # === PEPPER'S CAMERA ===
        pepper_group = QGroupBox("📹 Pepper's Camera")
        pepper_layout = QVBoxLayout()
        
        self.pepper_label = QLabel()
        self.pepper_label.setObjectName("videoLabel")
        self.pepper_label.setMinimumSize(400, 300)
        self.pepper_label.setAlignment(Qt.AlignCenter)
        self.pepper_label.setText("Initializing Pepper's camera...")
        self.pepper_label.setStyleSheet("color: #8e8e8e;")
        
        pepper_layout.addWidget(self.pepper_label)
        pepper_group.setLayout(pepper_layout)
        layout.addWidget(pepper_group)
        
        # === HOVERCAM ===
        hover_group = QGroupBox("📷 HoverCam (External)")
        hover_layout = QVBoxLayout()
        
        self.hover_label = QLabel()
        self.hover_label.setObjectName("videoLabel")
        self.hover_label.setMinimumSize(400, 300)
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setText("Initializing HoverCam...")
        self.hover_label.setStyleSheet("color: #8e8e8e;")
        
        hover_layout.addWidget(self.hover_label)
        hover_group.setLayout(hover_layout)
        layout.addWidget(hover_group)
        
        # === CONTROL BUTTONS ===
        button_layout = QHBoxLayout()
        
        self.switch_button = QPushButton("📷 Switch to Tablet")
        self.switch_button.setToolTip("Send HoverCam feed to Pepper's tablet")
        self.switch_button.clicked.connect(self._switch_camera_source)
        
        self.snapshot_button = QPushButton("📸 Snapshot")
        self.snapshot_button.setToolTip("Save current frame")
        self.snapshot_button.clicked.connect(self._take_snapshot)
        
        button_layout.addWidget(self.switch_button)
        button_layout.addWidget(self.snapshot_button)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("color: #8e8e8e; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # === DRAG & DROP ZONE ===
        drop_group = QGroupBox("📄 Tablet Display - Drag & Drop")
        drop_layout = QVBoxLayout()
        
        self.file_drop_panel = FileDropPanel(self.tablet, self.session)
        self.file_drop_panel.file_displayed.connect(self._on_file_displayed)
        
        drop_layout.addWidget(self.file_drop_panel)
        drop_group.setLayout(drop_layout)
        layout.addWidget(drop_group)
        
        layout.addStretch()
    
    def _init_cameras(self):
        """Initialize camera connections."""
        try:
            # Initialize Pepper's camera
            self.pepper_video = self.session.service("ALVideoDevice")
            self.pepper_subscriber_id = self.pepper_video.subscribeCamera(
                "gui_feed", 0, 2, 11, 15  # Top camera, 640x480, RGB, 15fps
            )
            self.status_label.setText("Status: ✓ Pepper's camera connected")
            
            # Initialize HoverCam (USB camera)
            self._detect_hovercam()
            
            # Start update timer
            self.timer.start(33)  # ~30 FPS
            
        except Exception as e:
            self.status_label.setText(f"Status: ⚠ Camera init error: {e}")
            print(f"Camera initialization error: {e}")
    
    def _detect_hovercam(self):
        """Detect and connect to HoverCam."""
        # Try common camera indices
        for cam_id in range(5):
            try:
                cap = cv2.VideoCapture(cam_id)
                if cap.isOpened():
                    # Test read
                    ret, frame = cap.read()
                    if ret:
                        self.hovercam = cap
                        self.status_label.setText(f"Status: ✓ HoverCam found (device {cam_id})")
                        print(f"✓ HoverCam detected on device {cam_id}")
                        return
                    else:
                        cap.release()
            except:
                continue
        
        self.hover_label.setText("HoverCam not detected\n\nPlug in USB camera and restart")
        print("⚠ HoverCam not detected")
    
    def _update_frames(self):
        """Update video frames."""
        # Update Pepper's camera
        if self.pepper_video and self.pepper_subscriber_id:
            try:
                img_data = self.pepper_video.getImageRemote(self.pepper_subscriber_id)
                if img_data:
                    width, height, image_bytes = img_data[0], img_data[1], img_data[6]
                    frame = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))
                    self._display_frame(frame, self.pepper_label)
            except Exception as e:
                print(f"Error getting Pepper frame: {e}")
        
        # Update HoverCam
        if self.hovercam and self.hovercam.isOpened():
            ret, frame = self.hovercam.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._display_frame(frame_rgb, self.hover_label)
    
    def _display_frame(self, frame, label):
        """Display a frame in a QLabel."""
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error displaying frame: {e}")
    
    def _switch_camera_source(self):
        """Switch which camera feed goes to tablet."""
        # Toggle between Pepper's camera and HoverCam on tablet
        if not hasattr(self, 'showing_hover_on_tablet'):
            self.showing_hover_on_tablet = False
        
        self.showing_hover_on_tablet = not self.showing_hover_on_tablet
        
        try:
            if self.showing_hover_on_tablet:
                # Show HoverCam on tablet (via tablet controller)
                self.tablet.current_mode = self.tablet.current_mode  # Keep current mode
                self.tablet.refresh_display()
                
                self.switch_button.setText("📷 Show Pepper Cam")
                self.status_label.setText("Status: Tablet showing HoverCam (feature in development)")
                logger.info("Switched tablet to HoverCam view")
            else:
                # Show Pepper's camera on tablet
                self.tablet.refresh_display()
                
                self.switch_button.setText("📷 Switch to Tablet")
                self.status_label.setText("Status: Tablet showing Pepper's camera")
                logger.info("Switched tablet to Pepper's camera")
        except Exception as e:
            logger.error(f"Camera switch error: {e}")
            self.status_label.setText(f"✗ Switch failed: {e}")
    
    def _take_snapshot(self):
        """Save current frame as image."""
        try:
            from PIL import Image
        except ImportError:
            self.status_label.setText("✗ PIL not installed (pip install Pillow)")
            logger.error("Pillow not installed")
            return
        
        # Create snapshots directory
        snapshot_dir = os.path.expanduser("~/pepper_snapshots")
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Get current frame from Pepper's camera
        if self.pepper_video and self.pepper_subscriber_id:
            try:
                img_data = self.pepper_video.getImageRemote(self.pepper_subscriber_id)
                if img_data:
                    width, height, image_bytes = img_data[0], img_data[1], img_data[6]
                    frame = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))
                    
                    # Generate filename with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"pepper_snapshot_{timestamp}.png"
                    filepath = os.path.join(snapshot_dir, filename)
                    
                    # Save using PIL
                    img = Image.fromarray(frame)
                    img.save(filepath)
                    
                    self.status_label.setText(f"✓ Saved: {filename}")
                    self.status_label.setStyleSheet("color: #4ade80; font-size: 11px;")
                    logger.info(f"Snapshot saved: {filepath}")
                    
                    # Show notification
                    QMessageBox.information(
                        self,
                        "Snapshot Saved",
                        f"Image saved to:\n{filepath}"
                    )
                    return
            except Exception as e:
                logger.error(f"Snapshot error: {e}")
        
        self.status_label.setText("✗ Snapshot failed")
        self.status_label.setStyleSheet("color: #f87171; font-size: 11px;")
    
    def _on_file_displayed(self, file_path, success):
        """Handle file display result."""
        if success:
            self.status_label.setText(f"✓ File displayed on tablet")
        else:
            self.status_label.setText(f"✗ Failed to display file")
    
    def cleanup(self):
        """Cleanup camera resources."""
        self.timer.stop()
        
        if self.pepper_subscriber_id and self.pepper_video:
            try:
                self.pepper_video.unsubscribe(self.pepper_subscriber_id)
            except:
                pass
        
        if self.hovercam:
            self.hovercam.release()