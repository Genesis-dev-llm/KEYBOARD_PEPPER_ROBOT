"""
Camera Panel - Video Feed Display
Left side panel showing Pepper's cameras.

FIXED: This file previously contained ControlPanel code by mistake.
       Now contains actual camera feed display.
"""

import logging
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

logger = logging.getLogger(__name__)

class CameraPanel(QWidget):
    """Panel for displaying camera feeds."""
    
    # Signals
    status_update = pyqtSignal(str)
    
    def __init__(self, session, robot_ip, tablet_ctrl):
        super().__init__()
        
        self.session = session
        self.robot_ip = robot_ip
        self.tablet = tablet_ctrl
        
        # Video device
        self.video_device = None
        self.top_subscriber_id = None
        self.bottom_subscriber_id = None
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_feeds)
        
        # Active camera
        self.active_camera = 0  # 0 = top, 1 = bottom
        
        self._init_ui()
        self._init_cameras()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📹 Camera Feeds")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Camera tabs
        self.tabs = QTabWidget()
        
        # Top camera
        self.top_camera_label = QLabel("Initializing camera...")
        self.top_camera_label.setAlignment(Qt.AlignCenter)
        self.top_camera_label.setObjectName("videoLabel")
        self.top_camera_label.setMinimumSize(640, 480)
        self.top_camera_label.setStyleSheet("""
            QLabel {
                background-color: #000;
                border: 2px solid #3e3e42;
                border-radius: 8px;
            }
        """)
        self.tabs.addTab(self.top_camera_label, "📹 Top Camera")
        
        # Bottom camera
        self.bottom_camera_label = QLabel("Initializing camera...")
        self.bottom_camera_label.setAlignment(Qt.AlignCenter)
        self.bottom_camera_label.setObjectName("videoLabel")
        self.bottom_camera_label.setMinimumSize(640, 480)
        self.bottom_camera_label.setStyleSheet("""
            QLabel {
                background-color: #000;
                border: 2px solid #3e3e42;
                border-radius: 8px;
            }
        """)
        self.tabs.addTab(self.bottom_camera_label, "📹 Bottom Camera")
        
        # Tab change handler
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tabs)
        
        # Controls
        controls_group = QGroupBox("Camera Controls")
        controls_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Restart camera feeds")
        refresh_btn.clicked.connect(self._refresh_cameras)
        controls_layout.addWidget(refresh_btn)
        
        # Snapshot button
        snapshot_btn = QPushButton("📸 Snapshot")
        snapshot_btn.setToolTip("Save current frame")
        snapshot_btn.clicked.connect(self._take_snapshot)
        controls_layout.addWidget(snapshot_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Status label
        self.status_label = QLabel("Camera status: Initializing...")
        self.status_label.setStyleSheet("color: #8e8e8e; font-size: 11px;")
        layout.addWidget(self.status_label)
    
    def _init_cameras(self):
        """Initialize Pepper's cameras."""
        try:
            self.video_device = self.session.service("ALVideoDevice")
            
            # Subscribe to top camera
            self.top_subscriber_id = self.video_device.subscribeCamera(
                "camera_panel_top", 0, 2, 11, 15  # Top, 640x480, RGB, 15fps
            )
            
            # Subscribe to bottom camera
            self.bottom_subscriber_id = self.video_device.subscribeCamera(
                "camera_panel_bottom", 1, 2, 11, 15  # Bottom, 640x480, RGB, 15fps
            )
            
            # Start update timer
            self.update_timer.start(66)  # ~15fps
            
            self.status_label.setText("Camera status: ✓ Connected")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 11px;")
            logger.info("✓ Camera panel initialized (top + bottom)")
            
        except Exception as e:
            logger.error(f"Camera init failed: {e}")
            self.status_label.setText(f"Camera status: ❌ Failed - {e}")
            self.status_label.setStyleSheet("color: #f87171; font-size: 11px;")
            
            # Show error in labels
            self.top_camera_label.setText(f"❌ Camera Error\n\n{str(e)}")
            self.bottom_camera_label.setText(f"❌ Camera Error\n\n{str(e)}")
    
    def _update_feeds(self):
        """Update camera feeds."""
        try:
            if not self.video_device:
                return
            
            # Update top camera
            if self.top_subscriber_id:
                self._update_camera_display(
                    self.top_subscriber_id,
                    self.top_camera_label
                )
            
            # Update bottom camera
            if self.bottom_subscriber_id:
                self._update_camera_display(
                    self.bottom_subscriber_id,
                    self.bottom_camera_label
                )
                
        except Exception as e:
            logger.error(f"Feed update error: {e}")
    
    def _update_camera_display(self, subscriber_id, label):
        """Update a specific camera display."""
        try:
            img_data = self.video_device.getImageRemote(subscriber_id)
            if not img_data:
                return
            
            width, height = img_data[0], img_data[1]
            image_bytes = img_data[6]
            
            # Convert to numpy
            frame = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = frame.reshape((height, width, 3))
            
            # Convert to QPixmap
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Display (scale to fit)
            scaled = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaled)
            
        except Exception as e:
            logger.error(f"Display update error: {e}")
    
    def _on_tab_changed(self, index):
        """Handle tab change."""
        self.active_camera = index
        camera_name = "Top" if index == 0 else "Bottom"
        self.status_update.emit(f"Viewing {camera_name} camera")
    
    def _refresh_cameras(self):
        """Refresh camera connections."""
        self.status_label.setText("Camera status: Refreshing...")
        self.status_label.setStyleSheet("color: #fbbf24; font-size: 11px;")
        
        # Stop timer
        self.update_timer.stop()
        
        # Unsubscribe
        if self.top_subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.top_subscriber_id)
            except:
                pass
        
        if self.bottom_subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.bottom_subscriber_id)
            except:
                pass
        
        # Wait a moment
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, self._init_cameras)
        
        self.status_update.emit("Camera feeds refreshed")
    
    def _take_snapshot(self):
        """Take a snapshot of current camera view."""
        try:
            import os
            from datetime import datetime
            
            # Create snapshots directory
            os.makedirs("snapshots", exist_ok=True)
            
            # Get current label
            if self.active_camera == 0:
                label = self.top_camera_label
                camera_name = "top"
            else:
                label = self.bottom_camera_label
                camera_name = "bottom"
            
            # Get pixmap
            pixmap = label.pixmap()
            if pixmap:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshots/pepper_{camera_name}_{timestamp}.png"
                
                # Save
                pixmap.save(filename)
                
                self.status_label.setText(f"✓ Snapshot saved: {filename}")
                self.status_label.setStyleSheet("color: #4ade80; font-size: 11px;")
                self.status_update.emit(f"Snapshot saved: {filename}")
                logger.info(f"Snapshot saved: {filename}")
            else:
                self.status_label.setText("❌ No image to save")
                self.status_label.setStyleSheet("color: #f87171; font-size: 11px;")
                
        except Exception as e:
            logger.error(f"Snapshot error: {e}")
            self.status_label.setText(f"❌ Snapshot failed: {e}")
            self.status_label.setStyleSheet("color: #f87171; font-size: 11px;")
    
    def cleanup(self):
        """Cleanup camera resources."""
        logger.info("Cleaning up camera panel...")
        
        # Stop timer
        self.update_timer.stop()
        
        # Unsubscribe from cameras
        if self.top_subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.top_subscriber_id)
                logger.info("✓ Top camera unsubscribed")
            except Exception as e:
                logger.error(f"Error unsubscribing top camera: {e}")
        
        if self.bottom_subscriber_id and self.video_device:
            try:
                self.video_device.unsubscribe(self.bottom_subscriber_id)
                logger.info("✓ Bottom camera unsubscribed")
            except Exception as e:
                logger.error(f"Error unsubscribing bottom camera: {e}")
        
        logger.info("✓ Camera panel cleaned up")