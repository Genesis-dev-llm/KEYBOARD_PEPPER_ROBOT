"""
Control Panel - Movement, dances, and robot controls
Right side panel with all control buttons.
"""

import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox, QRadioButton,
    QButtonGroup, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from .audio_streamer import create_audio_streamer
from .voice_commander_hybrid import create_hybrid_voice_commander

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
        
        # Initialize audio streamer
        self.audio_streamer = create_audio_streamer(pepper_conn.session)
        
        # Initialize NATIVE voice commander (uses Pepper's microphones)
        self.voice_commander = create_native_voice_commander(
            pepper_conn, controllers, dances, tablet_ctrl
        )
        
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
    
    def _create_audio_group(self):
        """Create audio control group."""
        group = QGroupBox("🎤 Audio & Voice")
        layout = QVBoxLayout()
        
        # Live mic toggle
        mic_layout = QHBoxLayout()
        
        self.mic_button = QPushButton("🎙️ LIVE MIC")
        self.mic_button.setObjectName("toggleButton")
        self.mic_button.setCheckable(True)
        self.mic_button.setMinimumHeight(50)
        self.mic_button.toggled.connect(self._toggle_mic)
        
        self.mic_indicator = QLabel("⚫ OFF")
        self.mic_indicator.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        mic_layout.addWidget(self.mic_button)
        mic_layout.addWidget(self.mic_indicator)
        
        layout.addLayout(mic_layout)
        
        # Voice commands toggle
        voice_layout = QHBoxLayout()
        
        self.voice_button = QPushButton("🗣️ VOICE COMMANDS")
        self.voice_button.setObjectName("toggleButton")
        self.voice_button.setCheckable(True)
        self.voice_button.setMinimumHeight(50)
        self.voice_button.toggled.connect(self._toggle_voice_commands)
        
        self.voice_indicator = QLabel("⚫ OFF")
        self.voice_indicator.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        voice_layout.addWidget(self.voice_button)
        voice_layout.addWidget(self.voice_indicator)
        
        layout.addLayout(voice_layout)
        
        # Voice commands help
        help_label = QLabel("Say: 'Hi Pepper' or 'my name is [Name]' for handshake\n"
                           "Uses Pepper's built-in microphones (no PC mic needed!)")
        help_label.setStyleSheet("color: #8e8e8e; font-size: 11px; font-style: italic;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("🔊 Volume:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        
        self.volume_label = QLabel("80%")
        self.volume_label.setMinimumWidth(40)
        self.volume_slider.valueChanged.connect(self._update_volume)
        
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        
        layout.addLayout(volume_layout)
        
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
        import threading
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
        """Toggle microphone streaming."""
        if checked:
            success = self.audio_streamer.start_streaming()
            if success:
                self.mic_indicator.setText("🔴 ON")
                self.mic_indicator.setStyleSheet("color: #f87171; font-size: 16px; font-weight: bold;")
                self.status_update_signal.emit("Microphone: ON - Live streaming")
            else:
                self.mic_button.setChecked(False)
                self.mic_indicator.setText("⚠️ ERROR")
                self.mic_indicator.setStyleSheet("color: #fbbf24; font-size: 16px; font-weight: bold;")
                self.status_update_signal.emit("Microphone: Failed to start (install pyaudio)")
        else:
            self.audio_streamer.stop_streaming()
            self.mic_indicator.setText("⚫ OFF")
            self.mic_indicator.setStyleSheet("color: #8e8e8e; font-size: 16px; font-weight: bold;")
            self.status_update_signal.emit("Microphone: OFF")
    
    def _toggle_voice_commands(self, checked):
        """Toggle voice command recognition."""
        if checked:
            success = self.voice_commander.start_listening()
            if success:
                self.voice_indicator.setText("🟢 LISTENING")
                self.voice_indicator.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold;")
                self.status_update_signal.emit("Voice commands: ON - Using Pepper's microphones")
            else:
                self.voice_button.setChecked(False)
                self.voice_indicator.setText("⚠️ ERROR")
                self.voice_indicator.setStyleSheet("color: #fbbf24; font-size: 16px; font-weight: bold;")
                self.status_update_signal.emit("Voice commands: Failed to start")
        else:
            self.voice_commander.stop_listening()
            self.voice_indicator.setText("⚫ OFF")
            self.voice_indicator.setStyleSheet("color: #8e8e8e; font-size: 16px; font-weight: bold;")
            self.status_update_signal.emit("Voice commands: OFF")
    
    def _change_tablet_mode(self, mode_id):
        """Change tablet display mode."""
        self.status_update_signal.emit(f"Tablet: {mode_id}")
        # TODO: Implement tablet mode switching
    
    def _update_volume(self, value):
        """Update audio volume."""
        self.volume_label.setText(f"{value}%")
        self.audio_streamer.set_volume(value / 100.0)
    
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
        if self.mic_button.isChecked():
            self.mic_button.setChecked(False)
        if self.voice_button.isChecked():
            self.voice_button.setChecked(False)
        
        # Cleanup audio
        self.audio_streamer.cleanup()
        
        # Cleanup voice
        self.voice_commander.stop_listening()