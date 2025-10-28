"""
MODULE: test_controller/gui/control_panel.py
Control Panel - IMPROVED VERSION

IMPROVEMENTS:
- Better button states (pressed/released visual feedback)
- Hold-to-move for arrow buttons
- Instant response
- Better status messages
- Cleaned up placeholders
"""

import logging
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox, QRadioButton,
    QButtonGroup, QScrollArea, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class ControlPanel(QWidget):
    """Panel for robot control buttons and settings - IMPROVED."""
    
    # Signals
    emergency_stop_signal = pyqtSignal()
    status_update_signal = pyqtSignal(str)
    
    def __init__(self, controllers, dances, tablet_ctrl, pepper_conn):
        super().__init__()
        
        self.controllers = controllers
        self.dances = dances
        self.tablet = tablet_ctrl
        self.pepper = pepper_conn
        
        # Movement button tracking (for hold-to-move)
        self._movement_active = {
            'forward': False,
            'back': False,
            'left': False,
            'right': False,
            'rotate_left': False,
            'rotate_right': False
        }
        
        # Movement update timer (for hold-to-move)
        self._movement_timer = QTimer()
        self._movement_timer.timeout.connect(self._update_held_movement)
        self._movement_timer.start(50)  # 20Hz
        
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
        
        # === STATUS DISPLAY ===
        layout.addWidget(self._create_status_display())
        
        # === MOVEMENT CONTROLS ===
        layout.addWidget(self._create_movement_group())
        
        # === DANCE CONTROLS ===
        layout.addWidget(self._create_dance_group())
        
        # === TABLET MODE ===
        layout.addWidget(self._create_tablet_group())
        
        # === EMERGENCY STOP ===
        layout.addWidget(self._create_emergency_button())
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_status_display(self):
        """Create status display at top."""
        group = QGroupBox("📊 Robot Status")
        layout = QVBoxLayout()
        
        # Battery progress bar
        battery_layout = QHBoxLayout()
        battery_layout.addWidget(QLabel("Battery:"))
        
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(50)
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat("%p%")
        battery_layout.addWidget(self.battery_bar)
        
        layout.addLayout(battery_layout)
        
        # Current action label
        self.action_label = QLabel("Ready - Waiting for input")
        self.action_label.setAlignment(Qt.AlignCenter)
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background: #2d2d30;
                border-radius: 5px;
                color: #4ade80;
            }
        """)
        layout.addWidget(self.action_label)
        
        # Speed indicator
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_label = QLabel("0.4 m/s")
        self.speed_label.setStyleSheet("font-weight: bold;")
        speed_layout.addWidget(self.speed_label)
        speed_layout.addStretch()
        layout.addLayout(speed_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_movement_group(self):
        """Create movement control group - IMPROVED with hold-to-move."""
        group = QGroupBox("🎮 Movement Controls")
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Hold buttons to move continuously")
        instructions.setStyleSheet("color: #8e8e8e; font-size: 11px; font-style: italic;")
        layout.addWidget(instructions)
        
        # Arrow pad with hold-to-move
        arrow_layout = QGridLayout()
        
        # Forward button
        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedSize(60, 50)
        self.up_btn.setToolTip("Move Forward (Hold)")
        self.up_btn.pressed.connect(lambda: self._start_movement('forward'))
        self.up_btn.released.connect(lambda: self._stop_movement('forward'))
        
        # Back button
        self.down_btn = QPushButton("↓")
        self.down_btn.setFixedSize(60, 50)
        self.down_btn.setToolTip("Move Backward (Hold)")
        self.down_btn.pressed.connect(lambda: self._start_movement('back'))
        self.down_btn.released.connect(lambda: self._stop_movement('back'))
        
        # Left button
        self.left_btn = QPushButton("←")
        self.left_btn.setFixedSize(60, 50)
        self.left_btn.setToolTip("Strafe Left (Hold)")
        self.left_btn.pressed.connect(lambda: self._start_movement('left'))
        self.left_btn.released.connect(lambda: self._stop_movement('left'))
        
        # Right button
        self.right_btn = QPushButton("→")
        self.right_btn.setFixedSize(60, 50)
        self.right_btn.setToolTip("Strafe Right (Hold)")
        self.right_btn.pressed.connect(lambda: self._start_movement('right'))
        self.right_btn.released.connect(lambda: self._stop_movement('right'))
        
        # Center stop button
        stop_btn = QPushButton("⏹")
        stop_btn.setFixedSize(60, 50)
        stop_btn.setToolTip("STOP (Space)")
        stop_btn.clicked.connect(self._stop_all_movement)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        
        arrow_layout.addWidget(self.up_btn, 0, 1)
        arrow_layout.addWidget(self.left_btn, 1, 0)
        arrow_layout.addWidget(stop_btn, 1, 1)
        arrow_layout.addWidget(self.right_btn, 1, 2)
        arrow_layout.addWidget(self.down_btn, 2, 1)
        
        layout.addLayout(arrow_layout)
        
        # Rotation buttons
        rotate_layout = QHBoxLayout()
        
        self.rotate_left_btn = QPushButton("↶ Rotate L")
        self.rotate_left_btn.setToolTip("Rotate Left (Hold)")
        self.rotate_left_btn.pressed.connect(lambda: self._start_movement('rotate_left'))
        self.rotate_left_btn.released.connect(lambda: self._stop_movement('rotate_left'))
        
        self.rotate_right_btn = QPushButton("Rotate R ↷")
        self.rotate_right_btn.setToolTip("Rotate Right (Hold)")
        self.rotate_right_btn.pressed.connect(lambda: self._start_movement('rotate_right'))
        self.rotate_right_btn.released.connect(lambda: self._stop_movement('rotate_right'))
        
        rotate_layout.addWidget(self.rotate_left_btn)
        rotate_layout.addWidget(self.rotate_right_btn)
        
        layout.addLayout(rotate_layout)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(40)
        self.speed_slider.setToolTip("Adjust movement speed")
        self.speed_slider.valueChanged.connect(self._update_speed)
        
        self.speed_value_label = QLabel("0.4")
        self.speed_value_label.setMinimumWidth(40)
        self.speed_value_label.setStyleSheet("font-weight: bold;")
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)
        
        layout.addLayout(speed_layout)
        
        # Quick buttons
        quick_layout = QHBoxLayout()
        
        turbo_btn = QPushButton("🚀 Turbo")
        turbo_btn.setCheckable(True)
        turbo_btn.setToolTip("Toggle turbo mode (1.5x speed)")
        turbo_btn.toggled.connect(self._toggle_turbo)
        
        reset_btn = QPushButton("🔄 Reset Position")
        reset_btn.setToolTip("Reset accumulated position to origin")
        reset_btn.clicked.connect(self._reset_position)
        
        quick_layout.addWidget(turbo_btn)
        quick_layout.addWidget(reset_btn)
        
        layout.addLayout(quick_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_dance_group(self):
        """Create dance control group."""
        group = QGroupBox("💃 Dance Animations")
        layout = QGridLayout()
        
        dances = [
            ("👋\nWave", "wave", "Simple friendly wave"),
            ("💃\nSpecial", "special", "Energetic dance with squats"),
            ("🤖\nRobot", "robot", "Mechanical choppy movements"),
            ("🌙\nMoonwalk", "moonwalk", "Michael Jackson style")
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
    
    def _create_tablet_group(self):
        """Create tablet mode control group."""
        group = QGroupBox("📱 Tablet Display")
        layout = QVBoxLayout()
        
        self.tablet_buttons = QButtonGroup()
        
        modes = [
            ("📊 Status", "status"),
            ("📷 Pepper Camera", "camera_pepper"),
            ("🎥 HoverCam", "camera_hover"),
            ("👋 Greeting", "greeting")
        ]
        
        for text, mode_id in modes:
            radio = QRadioButton(text)
            radio.toggled.connect(lambda checked, m=mode_id: self._change_tablet_mode(m) if checked else None)
            self.tablet_buttons.addButton(radio)
            layout.addWidget(radio)
        
        # Set default
        self.tablet_buttons.buttons()[0].setChecked(True)
        
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
    # MOVEMENT METHODS - HOLD TO MOVE
    # ========================================================================
    
    def _start_movement(self, direction):
        """Start movement in direction (called when button pressed)."""
        self._movement_active[direction] = True
        self._update_button_state(direction, True)
        self.action_label.setText(f"Moving: {direction.replace('_', ' ').title()}")
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background: #2d2d30;
                border-radius: 5px;
                color: #fbbf24;
            }
        """)
    
    def _stop_movement(self, direction):
        """Stop movement in direction (called when button released)."""
        self._movement_active[direction] = False
        self._update_button_state(direction, False)
        
        # If no movements active, stop
        if not any(self._movement_active.values()):
            base = self.controllers.get('base')
            if base:
                base.stop()
            self.action_label.setText("Ready - Waiting for input")
            self.action_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    background: #2d2d30;
                    border-radius: 5px;
                    color: #4ade80;
                }
            """)
    
    def _update_held_movement(self):
        """Update movement for held buttons (called by timer at 20Hz)."""
        base = self.controllers.get('base')
        if not base:
            return
        
        # Set velocities based on active movements
        if self._movement_active['forward']:
            base.set_continuous_velocity('x', 1.0)
        elif self._movement_active['back']:
            base.set_continuous_velocity('x', -1.0)
        else:
            base.set_continuous_velocity('x', 0.0)
        
        if self._movement_active['left']:
            base.set_continuous_velocity('y', 1.0)
        elif self._movement_active['right']:
            base.set_continuous_velocity('y', -1.0)
        else:
            base.set_continuous_velocity('y', 0.0)
        
        if self._movement_active['rotate_left']:
            base.set_continuous_velocity('theta', 1.0)
        elif self._movement_active['rotate_right']:
            base.set_continuous_velocity('theta', -1.0)
        else:
            base.set_continuous_velocity('theta', 0.0)
        
        # Update base movement
        base.move_continuous()
    
    def _update_button_state(self, direction, pressed):
        """Update button visual state."""
        button_map = {
            'forward': self.up_btn,
            'back': self.down_btn,
            'left': self.left_btn,
            'right': self.right_btn,
            'rotate_left': self.rotate_left_btn,
            'rotate_right': self.rotate_right_btn
        }
        
        btn = button_map.get(direction)
        if btn:
            if pressed:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1177bb;
                        border: 2px solid #0e639c;
                    }
                """)
            else:
                btn.setStyleSheet("")  # Reset to default
    
    def _stop_all_movement(self):
        """Stop all movement immediately."""
        # Reset all active flags
        for key in self._movement_active:
            self._movement_active[key] = False
            self._update_button_state(key, False)
        
        # Stop base
        base = self.controllers.get('base')
        if base:
            base.stop()
        
        self.action_label.setText("⏹ STOPPED")
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background: #2d2d30;
                border-radius: 5px;
                color: #f87171;
            }
        """)
        
        # Reset to ready after 1 second
        QTimer.singleShot(1000, lambda: self.action_label.setText("Ready - Waiting for input"))
    
    # ========================================================================
    # OTHER METHODS
    # ========================================================================
    
    def _update_speed(self, value):
        """Update movement speed."""
        speed = value / 100.0
        self.speed_value_label.setText(f"{speed:.2f}")
        self.speed_label.setText(f"{speed:.2f} m/s")
        
        base = self.controllers.get('base')
        if base:
            base.linear_speed = speed
            base.angular_speed = speed * 1.5  # Angular a bit faster
        
        self.status_update_signal.emit(f"Speed: {speed:.2f} m/s")
    
    def _toggle_turbo(self, checked):
        """Toggle turbo mode."""
        base = self.controllers.get('base')
        if base:
            base.toggle_turbo()
        
        status = "ENABLED 🚀" if checked else "DISABLED"
        self.status_update_signal.emit(f"Turbo mode: {status}")
    
    def _reset_position(self):
        """Reset accumulated position."""
        base = self.controllers.get('base')
        if base:
            base.reset_position()
        self.status_update_signal.emit("Position reset to origin")
    
    def _trigger_dance(self, dance_id):
        """Trigger a dance animation."""
        self.status_update_signal.emit(f"Dance: {dance_id}")
        self.action_label.setText(f"Dancing: {dance_id.title()}")
        
        # Execute dance in separate thread
        thread = threading.Thread(target=self._execute_dance, args=(dance_id,))
        thread.daemon = True
        thread.start()
    
    def _execute_dance(self, dance_id):
        """Execute dance (runs in thread)."""
        try:
            if dance_id in self.dances:
                self.dances[dance_id].perform()
                self.status_update_signal.emit(f"Dance complete: {dance_id}")
        except Exception as e:
            logger.error(f"Dance error: {e}")
            self.status_update_signal.emit(f"Dance failed: {e}")
    
    def _change_tablet_mode(self, mode_id):
        """Change tablet display mode."""
        # Implementation depends on tablet controller
        self.status_update_signal.emit(f"Tablet mode: {mode_id}")
    
    def update_battery(self, level):
        """Update battery display."""
        self.battery_bar.setValue(level)
        
        # Change color based on level
        if level >= 60:
            self.battery_bar.setObjectName("batteryGood")
        elif level >= 30:
            self.battery_bar.setObjectName("batteryMedium")
        else:
            self.battery_bar.setObjectName("batteryLow")
        
        self.battery_bar.style().unpolish(self.battery_bar)
        self.battery_bar.style().polish(self.battery_bar)
    
    def cleanup(self):
        """Cleanup resources."""
        # Stop movement timer
        self._movement_timer.stop()
        
        # Stop all movement
        self._stop_all_movement()
        
        logger.info("✓ Control panel cleaned up")