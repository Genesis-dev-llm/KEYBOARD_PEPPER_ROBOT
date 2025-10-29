"""
Camera Panel - Complete Implementation
Displays camera feeds and allows image upload.
"""

import logging
import threading
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from .file_handler import FileDropPanel
from .image_manager import ImageManager

logger = logging.getLogger(__name__)

class CameraPanel(QWidget):
    """Panel for displaying camera feeds and managing images."""
    
    # Signals
    image_selected = pyqtSignal(str)  # Emits when user selects image for display
    
    def __init__(self, session, robot_ip, tablet_ctrl):
        super().__init__()
        
        self.session = session
        self.robot_ip = robot_ip
        self.tablet = tablet_ctrl
        
        # Camera feed state
        self._pepper_feed_active = False
        self._hover_feed_active = False
        
        # Video URLs
        self._pepper_url = f"http://{robot_ip}:8080/pepper_feed"
        self._hover_url = f"http://{robot_ip}:8080/hover_feed"
        
        # Frame update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_feeds)
        self.update_timer.setInterval(100)  # 10 FPS
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: Camera Feeds
        tabs.addTab(self._create_camera_tab(), "📹 Camera Feeds")
        
        # Tab 2: Image Manager
        self.image_manager = ImageManager()
        self.image_manager.image_selected.connect(self._on_image_selected)
        tabs.addTab(self.image_manager, "🖼️ Images")
        
        # Tab 3: File Drop
        self.file_drop = FileDropPanel(self.tablet, self.session)
        self.file_drop.file_displayed.connect(self._on_file_displayed)
        tabs.addTab(self.file_drop, "📄 Files")
        
        layout.addWidget(tabs)
    
    def _create_camera_tab(self):
        """Create camera feeds tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Pepper Camera
        pepper_group = QGroupBox("📷 Pepper's Camera")
        pepper_layout = QVBoxLayout()
        
        self.pepper_label = QLabel("Camera feed inactive")
        self.pepper_label.setAlignment(Qt.AlignCenter)
        self.pepper_label.setMinimumSize(320, 240)
        self.pepper_label.setStyleSheet("""
            QLabel {
                background-color: #000;
                border: 2px solid #3e3e42;
                border-radius: 8px;
                color: #8e8e8e;
                font-size: 14px;
            }
        """)
        self.pepper_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pepper_layout.addWidget(self.pepper_label)
        
        # Pepper controls
        pepper_controls = QHBoxLayout()
        
        self.pepper_start_btn = QPushButton("▶ Start Feed")
        self.pepper_start_btn.clicked.connect(self._toggle_pepper_feed)
        
        pepper_tablet_btn = QPushButton("📱 Show on Tablet")
        pepper_tablet_btn.clicked.connect(lambda: self._show_on_tablet('pepper'))
        
        pepper_controls.addWidget(self.pepper_start_btn)
        pepper_controls.addWidget(pepper_tablet_btn)
        
        pepper_layout.addLayout(pepper_controls)
        pepper_group.setLayout(pepper_layout)
        layout.addWidget(pepper_group)
        
        # HoverCam
        hover_group = QGroupBox("🎥 HoverCam (USB)")
        hover_layout = QVBoxLayout()
        
        self.hover_label = QLabel("Camera feed inactive")
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setMinimumSize(320, 240)
        self.hover_label.setStyleSheet("""
            QLabel {
                background-color: #000;
                border: 2px solid #3e3e42;
                border-radius: 8px;
                color: #8e8e8e;
                font-size: 14px;
            }
        """)
        self.hover_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hover_layout.addWidget(self.hover_label)
        
        # HoverCam controls
        hover_controls = QHBoxLayout()
        
        self.hover_start_btn = QPushButton("▶ Start Feed")
        self.hover_start_btn.clicked.connect(self._toggle_hover_feed)
        
        hover_tablet_btn = QPushButton("📱 Show on Tablet")
        hover_tablet_btn.clicked.connect(lambda: self._show_on_tablet('hover'))
        
        hover_controls.addWidget(self.hover_start_btn)
        hover_controls.addWidget(hover_tablet_btn)
        
        hover_layout.addLayout(hover_controls)
        hover_group.setLayout(hover_layout)
        layout.addWidget(hover_group)
        
        layout.addStretch()
        
        return widget
    
    def _toggle_pepper_feed(self):
        """Toggle Pepper camera feed."""
        if self._pepper_feed_active:
            self._stop_pepper_feed()
        else:
            self._start_pepper_feed()
    
    def _toggle_hover_feed(self):
        """Toggle HoverCam feed."""
        if self._hover_feed_active:
            self._stop_hover_feed()
        else:
            self._start_hover_feed()
    
    def _start_pepper_feed(self):
        """Start Pepper camera feed."""
        self._pepper_feed_active = True
        self.pepper_start_btn.setText("⏹ Stop Feed")
        self.pepper_label.setText("Connecting...")
        
        if not self.update_timer.isActive():
            self.update_timer.start()
        
        logger.info("Pepper camera feed started")
    
    def _stop_pepper_feed(self):
        """Stop Pepper camera feed."""
        self._pepper_feed_active = False
        self.pepper_start_btn.setText("▶ Start Feed")
        self.pepper_label.clear()
        self.pepper_label.setText("Camera feed stopped")
        
        if not self._hover_feed_active and self.update_timer.isActive():
            self.update_timer.stop()
        
        logger.info("Pepper camera feed stopped")
    
    def _start_hover_feed(self):
        """Start HoverCam feed."""
        self._hover_feed_active = True
        self.hover_start_btn.setText("⏹ Stop Feed")
        self.hover_label.setText("Connecting...")
        
        if not self.update_timer.isActive():
            self.update_timer.start()
        
        logger.info("HoverCam feed started")
    
    def _stop_hover_feed(self):
        """Stop HoverCam feed."""
        self._hover_feed_active = False
        self.hover_start_btn.setText("▶ Start Feed")
        self.hover_label.clear()
        self.hover_label.setText("Camera feed stopped")
        
        if not self._pepper_feed_active and self.update_timer.isActive():
            self.update_timer.stop()
        
        logger.info("HoverCam feed stopped")
    
    def _update_feeds(self):
        """Update camera feeds (called by timer)."""
        if self._pepper_feed_active:
            self._update_pepper_frame()
        
        if self._hover_feed_active:
            self._update_hover_frame()
    
    def _update_pepper_frame(self):
        """Fetch and display Pepper camera frame."""
        try:
            import urllib.request
            
            # Get snapshot
            url = f"http://{self.robot_ip}:8080/pepper_snapshot"
            req = urllib.request.urlopen(url, timeout=1)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale to fit label
                pixmap = QPixmap.fromImage(q_img)
                scaled = pixmap.scaled(
                    self.pepper_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.pepper_label.setPixmap(scaled)
            
        except Exception as e:
            logger.debug(f"Pepper frame update error: {e}")
            if self._pepper_feed_active:
                self.pepper_label.setText("Connection lost\nRetrying...")
    
    def _update_hover_frame(self):
        """Fetch and display HoverCam frame."""
        try:
            import urllib.request
            
            url = f"http://{self.robot_ip}:8080/hover_snapshot"
            req = urllib.request.urlopen(url, timeout=1)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_img)
                scaled = pixmap.scaled(
                    self.hover_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.hover_label.setPixmap(scaled)
            
        except Exception as e:
            logger.debug(f"HoverCam frame update error: {e}")
            if self._hover_feed_active:
                self.hover_label.setText("Connection lost\nRetrying...")
    
    def _show_on_tablet(self, camera):
        """Display camera feed on Pepper's tablet."""
        from ..tablet.display_modes import DisplayMode
        
        if camera == 'pepper':
            self.tablet.set_mode(DisplayMode.PEPPER_CAM)
            logger.info("Showing Pepper camera on tablet")
        elif camera == 'hover':
            self.tablet.set_mode(DisplayMode.HOVERCAM)
            logger.info("Showing HoverCam on tablet")
    
    def _on_image_selected(self, image_path):
        """Handle image selection from image manager."""
        logger.info(f"Image selected: {image_path}")
        self.tablet.set_custom_image(image_path)
        self.image_selected.emit(image_path)
    
    def _on_file_displayed(self, file_path, success):
        """Handle file display result."""
        if success:
            logger.info(f"File displayed: {file_path}")
        else:
            logger.error(f"Failed to display file: {file_path}")
    
    def cleanup(self):
        """Cleanup resources."""
        if self.update_timer.isActive():
            self.update_timer.stop()
        
        self._stop_pepper_feed()
        self._stop_hover_feed()
        
        logger.info("✓ Camera panel cleaned up")