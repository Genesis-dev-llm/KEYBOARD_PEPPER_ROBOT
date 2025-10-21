"""
Control Panel - Movement, dances, and robot controls
FIXED: Import corrections, proper cleanup, error handling
"""

import threading
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

# FIXED: Added missing import
logger = logging.getLogger(__name__)

class ControlPanel(QWidget):
    """Panel for robot control buttons and settings."""
    
    # Signals
    emergency_stop_signal = pyqtSignal()
    status_update_signal = pyqtSignal(str)
    
    def __init__(self, controllers, dances, tablet_ctrl, pepper_conn):
        super().__init__()
        
        self.controllers = controllers
        self.dances = dances
        self.tablet = tablet_ctrl
        self.pepper = pepper_conn
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        # Make panel scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        
        # === MOVEMENT CONTROLS ===
        layout.addWidget(self._create_movement_group())
        
        # === DANCE CONTROLS ===
        layout.addWidget(self._create_dance_group())
        
        # === EMERGENCY STOP ===
        layout.addWidget(self._create_emergency_button())
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_movement_group(self):
        """Create movement control group."""
        group = QGroupBox("🎮 Movement")
        layout = QVBoxLayout()
        
        # Arrow pad
        arrow_layout = QGridLayout()
        
        up_btn = QPushButton("↑")
        up_btn.setFixedSize(60, 50)
        up_btn.pressed.connect(lambda: self._move('forward'))
        up_btn.released.connect(lambda: self._stop_move())
        
        down_btn = QPushButton("↓")
        down_btn.setFixedSize(60, 50)
        down_btn.pressed.connect(lambda: self._move('back'))
        down_btn.released.connect(lambda: self._stop_move())
        
        left_btn = QPushButton("←")
        left_btn.setFixedSize(60, 50)
        left_btn.pressed.connect(lambda: self._move('left'))
        left_btn.released.connect(lambda: self._stop_move())
        
        right_btn = QPushButton("→")
        right_btn.setFixedSize(60, 50)
        right_btn.pressed.connect(lambda: self._move('right'))
        right_btn.released.connect(lambda: self._stop_move())
        
        center_label = QLabel("●")
        center_label.setAlignment(Qt.AlignCenter)
        center_label.setStyleSheet("font-size: 20px; color: #0e639c;")
        
        arrow_layout.addWidget(up_btn, 0, 1)
        arrow_layout.addWidget(left_btn, 1, 0)
        arrow_layout.addWidget(center_label, 1, 1)
        arrow_layout.addWidget(right_btn, 1, 2)
        arrow_layout.addWidget(down_btn, 2, 1)
        
        layout.addLayout(arrow_layout)
        
        # Rotation buttons
        rotate_layout = QHBoxLayout()
        
        rotate_left_btn = QPushButton("Rotate L")
        rotate_left_btn.pressed.connect(lambda: self._move('rotate_left'))
        rotate_left_btn.released.connect(lambda: self._stop_move())
        
        rotate_right_btn = QPushButton("Rotate R")
        rotate_right_btn.pressed.connect(lambda: self._move('rotate_right'))
        rotate_right_btn.released.connect(lambda: self._stop_move())
        
        rotate_layout.addWidget(rotate_left_btn)
        rotate_layout.addWidget(rotate_right_btn)
        
        layout.addLayout(rotate_layout)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(50)
        self.speed_slider.setValue(30)
        self.speed_slider.valueChanged.connect(self._update_speed)
        
        self.speed_label = QLabel("0.3")
        self.speed_label.setMinimumWidth(40)
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        
        layout.addLayout(speed_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_dance_group(self):
        """Create dance control group."""
        group = QGroupBox("💃 Dances")
        layout = QGridLayout()
        
        dances = [
            ("👋\nWave", "wave"),
            ("💃\nSpecial", "special"),
            ("🤖\nRobot", "robot"),
            ("🌙\nMoonwalk", "moonwalk")
        ]
        
        for i, (text, dance_id) in enumerate(dances):
            btn = QPushButton(text)
            btn.setObjectName("danceButton")
            btn.setMinimumHeight(70)
            btn.clicked.connect(lambda checked, d=dance_id: self._trigger_dance(d))
            layout.addWidget(btn, i // 2, i % 2)
        
        group.setLayout(layout)
        return group
    
    def _create_emergency_button(self):
        """Create emergency stop button."""
        btn = QPushButton("🚨 EMERGENCY STOP")
        btn.setObjectName("emergencyButton")
        btn.setMinimumHeight(70)
        btn.clicked.connect(self.emergency_stop_signal.emit)
        return btn
    
    # ========================================================================
    # SLOT METHODS
    # ========================================================================
    
    def _move(self, direction):
        """Handle movement button press."""
        base = self.controllers.get('base')
        if not base:
            self.status_update_signal.emit("Error: Base controller not found")
            return
        
        try:
            if direction == 'forward':
                base.set_continuous_velocity('x', 1.0)
                self.tablet.set_action("Moving Forward", "")
            elif direction == 'back':
                base.set_continuous_velocity('x', -1.0)
                self.tablet.set_action("Moving Backward", "")
            elif direction == 'left':
                base.set_continuous_velocity('y', 1.0)
                self.tablet.set_action("Strafing Left", "")
            elif direction == 'right':
                base.set_continuous_velocity('y', -1.0)
                self.tablet.set_action("Strafing Right", "")
            elif direction == 'rotate_left':
                base.set_continuous_velocity('theta', 1.0)
                self.tablet.set_action("Rotating Left", "")
            elif direction == 'rotate_right':
                base.set_continuous_velocity('theta', -1.0)
                self.tablet.set_action("Rotating Right", "")
            
            self.status_update_signal.emit(f"Moving: {direction}")
        except Exception as e:
            logger.error(f"Movement error: {e}")
            self.status_update_signal.emit(f"Movement error: {e}")
    
    def _stop_move(self):
        """Stop movement."""
        base = self.controllers.get('base')
        if base:
            try:
                base.stop()
                self.tablet.set_action("Ready", "Waiting for input...")
                self.status_update_signal.emit("Movement stopped")
            except Exception as e:
                logger.error(f"Stop error: {e}")
    
    def _update_speed(self, value):
        """Update movement speed."""
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}")
        
        base = self.controllers.get('base')
        if base:
            base.linear_speed = speed
            self.status_update_signal.emit(f"Speed: {speed:.1f}")
    
    def _trigger_dance(self, dance_id):
        """Trigger a dance animation."""
        self.status_update_signal.emit(f"Dance: {dance_id}")
        self.tablet.set_action(dance_id.capitalize(), "Starting...")
        
        # Execute dance in separate thread to avoid blocking
        thread = threading.Thread(target=self._execute_dance, args=(dance_id,))
        thread.daemon = True
        thread.start()
    
    def _execute_dance(self, dance_id):
        """Execute dance (runs in thread)."""
        try:
            if dance_id in self.dances:
                self.dances[dance_id].perform()
                self.tablet.set_action("Ready", f"{dance_id.capitalize()} complete")
                self.status_update_signal.emit(f"Dance complete: {dance_id}")
            else:
                logger.error(f"Dance not found: {dance_id}")
                self.status_update_signal.emit(f"Error: Dance '{dance_id}' not found")
        except Exception as e:
            logger.error(f"Dance error: {e}")
            self.status_update_signal.emit(f"Dance failed: {e}")
            self.tablet.set_action("Ready", "Dance failed")
    
    def cleanup(self):
        """Cleanup resources."""
        # Stop any ongoing operations
        self._stop_move()
        logger.info("Control panel cleanup complete")