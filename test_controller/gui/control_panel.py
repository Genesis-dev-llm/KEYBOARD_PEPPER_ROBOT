"""
Control Panel - Movement, dances, and robot controls
Right side panel with all control buttons.

FIXED VERSION - Corrected imports and voice commander initialization
"""

import logging
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox, QRadioButton,
    QButtonGroup, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from .audio_streamer import create_audio_streamer
from .voice_commander_hybrid import create_hybrid_voice_commander

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
        
        # Initialize audio streamer (DISABLED - Phase 4A)
        # self.audio_streamer = create_audio_streamer(pepper_conn.session)
        self.audio_streamer = None  # Placeholder
        
        # Initialize HYBRID voice commander (DISABLED - Phase 4A)
        # self.voice_commander = create_hybrid_voice_commander(
        #     pepper_conn, controllers, dances, tablet_ctrl
        # )
        self.voice_commander = None  # Placeholder
        
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
        
        # === AUDIO CONTROLS ===
        layout.addWidget(self._create_audio_group())
        
        # === TABLET MODE ===
        layout.addWidget(self._create_tablet_group())
        
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
        up_btn.setToolTip("Move Forward (Arrow Up)")
        up_btn.pressed.connect(lambda: self._move('forward'))
        up_btn.released.connect(lambda: self._stop_move())
        
        down_btn = QPushButton("↓")
        down_btn.setFixedSize(60, 50)
        down_btn.setToolTip("Move Backward (Arrow Down)")
        down_btn.pressed.connect(lambda: self._move('back'))
        down_btn.released.connect(lambda: self._stop_move())
        
        left_btn = QPushButton("←")
        left_btn.setFixedSize(60, 50)
        left_btn.setToolTip("Strafe Left (Arrow Left)")
        left_btn.pressed.connect(lambda: self._move('left'))
        left_btn.released.connect(lambda: self._stop_move())
        
        right_btn = QPushButton("→")
        right_btn.setFixedSize(60, 50)
        right_btn.setToolTip("Strafe Right (Arrow Right)")
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
        rotate_left_btn.setToolTip("Rotate Left (Q key)")
        rotate_left_btn.pressed.connect(lambda: self._move('rotate_left'))
        rotate_left_btn.released.connect(lambda: self._stop_move())
        
        rotate_right_btn = QPushButton("Rotate R")
        rotate_right_btn.setToolTip("Rotate Right (E key)")
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
        self.speed_slider.setToolTip("Adjust movement speed (or use +/- keys)")
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
            ("👋\nWave", "wave", "Simple friendly wave (Key: 1)"),
            ("💃\nSpecial", "special", "Energetic dance with squats (Key: 2)"),
            ("🤖\nRobot", "robot", "Mechanical choppy movements (Key: 3)"),
            ("🌙\nMoonwalk", "moonwalk", "Michael Jackson style (Key: 4)")
        ]
        
        for i, (text, dance_id, tooltip) in enumerate(dances):
            btn = QPushButton(text)
            btn.setObjectName("danceButton")
            btn.setMinimumHeight(70)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, d=dance_id: self._trigger_dance(d))
            layout.addWidget(btn, i // 2, i % 2)
        
        group.setLayout(layout)
        return group
    
    def _create_audio_group(self):
        """Create audio control group (PLACEHOLDERS - Phase 4A)."""
        group = QGroupBox("🎤 Audio & Voice - Coming Soon")
        layout = QVBoxLayout()
        
        # Placeholder message
        placeholder = QLabel(
            "Audio features will include:\n\n"
            "• Live microphone streaming\n"
            "• Voice commands\n"
            "• Volume control\n\n"
            "Coming in future update!"
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #8e8e8e;
                font-size: 12px;
                padding: 30px;
                background: #2d2d30;
                border: 2px dashed #6e6e6e;
                border-radius: 10px;
            }
        """)
        placeholder.setMinimumHeight(150)
        
        layout.addWidget(placeholder)
        
        group.setLayout(layout)
        return group
    
    def _create_tablet_group(self):
        """Create tablet mode control group."""
        group = QGroupBox("📱 Tablet Display")
        layout = QVBoxLayout()
        
        self.tablet_buttons = QButtonGroup()
        
        modes = [
            ("Status", "status"),
            ("Camera - Pepper", "camera_pepper"),
            ("Camera - HoverCam", "camera_hover"),
            ("Greeting", "greeting")
        ]
        
        for text, mode_id in modes:
            radio = QRadioButton(text)
            radio.toggled.connect(lambda checked, m=mode_id: self._change_tablet_mode(m) if checked else None)
            self.tablet_buttons.addButton(radio)
            layout.addWidget(radio)
        
        # Set default
        self.tablet_buttons.buttons()[0].setChecked(True)
        
        # Additional buttons
        button_layout = QHBoxLayout()
        
        status_btn = QPushButton("📊 Show Status")
        status_btn.clicked.connect(lambda: self._show_robot_status())
        
        greeting_btn = QPushButton("👋 Greeting")
        greeting_btn.clicked.connect(lambda: self.tablet.show_greeting())
        
        button_layout.addWidget(status_btn)
        button_layout.addWidget(greeting_btn)
        
        layout.addLayout(button_layout)
        
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
    
    def _stop_move(self):
        """Stop movement."""
        base = self.controllers.get('base')
        if base:
            base.stop()
            self.tablet.set_action("Ready", "Waiting for input...")
            self.status_update_signal.emit("Movement stopped")
    
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
    
    def _toggle_mic(self, checked):
        """Toggle microphone streaming (PLACEHOLDER)."""
        QMessageBox.information(
            self,
            "Feature Coming Soon",
            "Live microphone streaming will be available in a future update!"
        )
        if hasattr(self, 'mic_button'):
            self.mic_button.setChecked(False)
    
    def _toggle_voice_commands(self, checked):
        """Toggle voice command recognition (PLACEHOLDER)."""
        QMessageBox.information(
            self,
            "Feature Coming Soon",
            "Voice commands will be available in a future update!"
        )
        if hasattr(self, 'voice_button'):
            self.voice_button.setChecked(False)
    
    def _update_volume(self, value):
        """Update audio volume (PLACEHOLDER)."""
        # Do nothing - placeholder
        pass
    
    def _show_robot_status(self):
        """Show robot status dialog."""
        try:
            status = self.pepper.get_status()
            if status:
                message = f"Battery: {status.get('battery', 'Unknown')}%\n"
                message += f"Stiffness: {status.get('stiffness', 'Unknown')}\n"
                message += f"Connected: {status.get('connected', False)}"
            else:
                message = "Could not retrieve robot status.\nRobot may not be connected."
            
            QMessageBox.information(self, "Robot Status", message)
        except Exception as e:
            logger.error(f"Status dialog error: {e}")
            QMessageBox.warning(self, "Error", f"Could not get status:\n{e}")
    
    def cleanup(self):
        """Cleanup resources."""
        # Stop any ongoing operations
        self._stop_move()
        
        # Audio features disabled in Phase 4A
        # if self.mic_button.isChecked():
        #     self.mic_button.setChecked(False)
        # if self.voice_button.isChecked():
        #     self.voice_button.setChecked(False)
        
        # Cleanup audio (disabled)
        # self.audio_streamer.cleanup()
        
        # Cleanup voice (disabled)
        # self.voice_commander.stop_listening()
        
        logger.info("✓ Control panel cleaned up")