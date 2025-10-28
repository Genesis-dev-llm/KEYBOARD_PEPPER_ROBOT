"""
MODULE: test_controller/gui/main_window.py
Main Window for Pepper Control Center - COMPLETE VERSION WITH KEYBOARD SHORTCUTS

FEATURES:
- Keyboard shortcuts work in GUI (arrow keys, WASD, 1-4, etc.)
- F1 for help, Space to stop, ESC for emergency
- All keyboard controls from terminal mode work in GUI!
- Resizable/movable window
- Battery warnings
- Status bar
- Settings save/load
"""

import sys
import os
import json
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStatusBar, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QKeyEvent

from .styles import apply_theme
from .camera_panel import CameraPanel
from .control_panel import ControlPanel

logger = logging.getLogger(__name__)

class PepperControlGUI(QMainWindow):
    """Main window for Pepper robot control interface - WITH KEYBOARD SHORTCUTS."""
    
    # Signals
    emergency_stop_signal = pyqtSignal()
    
    def __init__(self, pepper_conn, controllers, dances, tablet_ctrl):
        super().__init__()
        
        # Store references
        self.pepper = pepper_conn
        self.controllers = controllers
        self.dances = dances
        self.tablet = tablet_ctrl
        
        # Configuration
        self.config_file = os.path.expanduser('~/.pepper_gui_config.json')
        
        # Battery warning state
        self._battery_warning_shown = False
        self._battery_critical_shown = False
        self._low_battery_threshold = 30
        self._critical_battery_threshold = 15
        
        # Keyboard state tracking
        self._keys_pressed = set()
        
        # Initialize UI
        self._init_ui()
        self._load_settings()
        self._setup_status_bar()
        self._setup_connections()
        
        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)
        
        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)
        
        # Start base movement update timer
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self._update_movement)
        self.movement_timer.start(50)
        
        logger.info("✓ GUI initialized with keyboard shortcuts enabled")
        logger.info("  Press F1 for help, Arrow keys to move, Space to stop")
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🤖 Pepper Control Center")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Camera feeds
        self.camera_panel = CameraPanel(
            self.pepper.session,
            self.pepper.ip,
            self.tablet
        )
        
        # Right panel - Controls
        self.control_panel = ControlPanel(
            self.controllers,
            self.dances,
            self.tablet,
            self.pepper
        )
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.camera_panel)
        self.main_splitter.addWidget(self.control_panel)
        
        # Initial sizes (60% cameras, 40% controls)
        self.main_splitter.setSizes([720, 480])
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Connect emergency stop
        self.control_panel.emergency_stop_signal.connect(self._emergency_stop)
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        settings_action = file_menu.addAction('⚙️ Settings')
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self._show_settings)
        
        file_menu.addSeparator()
        
        status_action = file_menu.addAction('🤖 Robot Status')
        status_action.setShortcut('Ctrl+I')
        status_action.triggered.connect(self._show_robot_status_dialog)
        
        file_menu.addSeparator()
        
        quit_action = file_menu.addAction('Quit')
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        shortcuts_action = help_menu.addAction('⌨️ Keyboard Shortcuts')
        shortcuts_action.setShortcut('F1')
        shortcuts_action.triggered.connect(self._show_shortcuts_help)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self._show_about)
    
    # ========================================================================
    # KEYBOARD SHORTCUTS
    # ========================================================================
    
    def eventFilter(self, obj, event):
        """Filter events to capture keyboard shortcuts."""
        if event.type() == QEvent.KeyPress:
            return self._handle_key_press(event)
        elif event.type() == QEvent.KeyRelease:
            return self._handle_key_release(event)
        
        return super().eventFilter(obj, event)
    
    def _handle_key_press(self, event: QKeyEvent):
        """Handle key press events."""
        key = event.key()
        self._keys_pressed.add(key)
        
        base = self.controllers.get('base')
        body = self.controllers.get('body')
        
        # Movement (Arrow Keys)
        if key == Qt.Key_Up:
            if base:
                base.set_continuous_velocity('x', 1.0)
                self.status_bar.showMessage("Moving Forward", 100)
            return True
        
        elif key == Qt.Key_Down:
            if base:
                base.set_continuous_velocity('x', -1.0)
                self.status_bar.showMessage("Moving Backward", 100)
            return True
        
        elif key == Qt.Key_Left:
            if base:
                base.set_continuous_velocity('y', 1.0)
                self.status_bar.showMessage("Strafing Left", 100)
            return True
        
        elif key == Qt.Key_Right:
            if base:
                base.set_continuous_velocity('y', -1.0)
                self.status_bar.showMessage("Strafing Right", 100)
            return True
        
        # Rotation (Q/E)
        elif key == Qt.Key_Q:
            if base:
                base.set_continuous_velocity('theta', 1.0)
                self.status_bar.showMessage("Rotating Left", 100)
            return True
        
        elif key == Qt.Key_E:
            if base:
                base.set_continuous_velocity('theta', -1.0)
                self.status_bar.showMessage("Rotating Right", 100)
            return True
        
        # Head (WASD)
        elif key == Qt.Key_W:
            if body:
                body.move_head('up')
                self.status_bar.showMessage("Head Up", 1000)
            return True
        
        elif key == Qt.Key_S:
            if body:
                body.move_head('down')
                self.status_bar.showMessage("Head Down", 1000)
            return True
        
        elif key == Qt.Key_A:
            if body:
                body.move_head('left')
                self.status_bar.showMessage("Head Left", 1000)
            return True
        
        elif key == Qt.Key_D:
            if body:
                body.move_head('right')
                self.status_bar.showMessage("Head Right", 1000)
            return True
        
        elif key == Qt.Key_R:
            if body:
                body.reset_head()
                self.status_bar.showMessage("Head Reset", 1000)
            return True
        
        # Dances (1-4)
        elif key == Qt.Key_1:
            self._trigger_dance_from_key('wave')
            return True
        
        elif key == Qt.Key_2:
            self._trigger_dance_from_key('special')
            return True
        
        elif key == Qt.Key_3:
            self._trigger_dance_from_key('robot')
            return True
        
        elif key == Qt.Key_4:
            self._trigger_dance_from_key('moonwalk')
            return True
        
        # Stop (Space)
        elif key == Qt.Key_Space:
            if base:
                base.stop()
                self.status_bar.showMessage("⏹ STOPPED", 2000)
            return True
        
        # Speed Control (+/-)
        elif key in [Qt.Key_Plus, Qt.Key_Equal]:
            if base:
                speed = base.increase_speed()
                self.status_bar.showMessage(f"⬆️ Speed: {speed:.2f} m/s", 2000)
            return True
        
        elif key in [Qt.Key_Minus, Qt.Key_Underscore]:
            if base:
                speed = base.decrease_speed()
                self.status_bar.showMessage(f"⬇️ Speed: {speed:.2f} m/s", 2000)
            return True
        
        # Turbo (X)
        elif key == Qt.Key_X:
            if base:
                turbo = base.toggle_turbo()
                status = "ENABLED 🚀" if turbo else "DISABLED"
                self.status_bar.showMessage(f"Turbo: {status}", 2000)
            return True
        
        # Help (F1)
        elif key == Qt.Key_F1:
            self._show_shortcuts_help()
            return True
        
        # Fullscreen (F11)
        elif key == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return True
        
        # Emergency Stop (ESC)
        elif key == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self._emergency_stop()
            return True
        
        return False
    
    def _handle_key_release(self, event: QKeyEvent):
        """Handle key release events."""
        key = event.key()
        self._keys_pressed.discard(key)
        
        base = self.controllers.get('base')
        
        # Stop movement when keys released
        if key in [Qt.Key_Up, Qt.Key_Down]:
            if base:
                base.set_continuous_velocity('x', 0.0)
            return True
        
        elif key in [Qt.Key_Left, Qt.Key_Right]:
            if base:
                base.set_continuous_velocity('y', 0.0)
            return True
        
        elif key in [Qt.Key_Q, Qt.Key_E]:
            if base:
                base.set_continuous_velocity('theta', 0.0)
            return True
        
        return False
    
    def _trigger_dance_from_key(self, dance_id):
        """Trigger dance from keyboard shortcut."""
        self.control_panel._trigger_dance(dance_id)
        self.status_bar.showMessage(f"💃 Dance: {dance_id.title()}", 2000)
    
    # ========================================================================
    # DIALOGS
    # ========================================================================
    
    def _show_settings(self):
        """Show settings dialog."""
        try:
            from .settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            if dialog.exec_():
                logger.info("Settings saved")
        except ImportError:
            QMessageBox.warning(self, "Not Available", "Settings dialog not available")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open settings:\n{e}")
    
    def _show_robot_status_dialog(self):
        """Show robot status dialog."""
        try:
            status = self.pepper.get_status()
            
            if status and status.get('connected'):
                battery = status.get('battery', 'Unknown')
                stiffness = status.get('stiffness', 'Unknown')
                
                message = f"""
<h3>Robot Status</h3>
<table cellpadding="5">
<tr><td><b>Connection:</b></td><td style="color: #4ade80;">✓ Connected</td></tr>
<tr><td><b>Battery:</b></td><td>{battery}%</td></tr>
<tr><td><b>Stiffness:</b></td><td>{stiffness}</td></tr>
</table>
                """
            else:
                message = "<h3>Robot Status</h3><p style='color: #f87171;'>✗ Not Connected</p>"
            
            QMessageBox.information(self, "Robot Status", message)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not get status:\n{e}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
<h2>🤖 Pepper Control Center</h2>
<p><b>Version 2.0.1</b> - With Keyboard Shortcuts</p>

<h3>⌨️ Keyboard Shortcuts:</h3>
<p>• Arrow keys - Move robot<br>
• WASD - Control head<br>
• Q/E - Rotate<br>
• Space - Stop<br>
• 1-4 - Dances<br>
• F1 - Help<br>
• ESC - Emergency stop</p>

<p><i>Built for VR Teleoperation Research</i></p>
<p><b>© 2025 Pepper VR Team</b></p>
        """
        QMessageBox.about(self, "About", about_text)
    
    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog."""
        help_text = """
<h2>⌨️ Keyboard Shortcuts</h2>

<h3>Movement:</h3>
<table cellpadding="5">
<tr><td><b>↑ ↓ ← →</b></td><td>Move robot</td></tr>
<tr><td><b>Q / E</b></td><td>Rotate left / right</td></tr>
<tr><td><b>SPACE</b></td><td>Stop all movement</td></tr>
</table>

<h3>Head Control:</h3>
<table cellpadding="5">
<tr><td><b>W / S</b></td><td>Head up/down</td></tr>
<tr><td><b>A / D</b></td><td>Head left/right</td></tr>
<tr><td><b>R</b></td><td>Reset head</td></tr>
</table>

<h3>Speed:</h3>
<table cellpadding="5">
<tr><td><b>+ / =</b></td><td>Increase speed</td></tr>
<tr><td><b>- / _</b></td><td>Decrease speed</td></tr>
<tr><td><b>X</b></td><td>Toggle turbo</td></tr>
</table>

<h3>Dances:</h3>
<table cellpadding="5">
<tr><td><b>1</b></td><td>Wave 👋</td></tr>
<tr><td><b>2</b></td><td>Special 💃</td></tr>
<tr><td><b>3</b></td><td>Robot 🤖</td></tr>
<tr><td><b>4</b></td><td>Moonwalk 🌙</td></tr>
</table>

<h3>System:</h3>
<table cellpadding="5">
<tr><td><b>F1</b></td><td>Show this help</td></tr>
<tr><td><b>F11</b></td><td>Toggle fullscreen</td></tr>
<tr><td><b>ESC</b></td><td>Emergency stop</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit</td></tr>
</table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)
    
    # ========================================================================
    # STATUS BAR
    # ========================================================================
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        from PyQt5.QtWidgets import QLabel
        
        self.connection_label = QLabel("🔴 Disconnected")
        self.battery_label = QLabel("🔋 ---%")
        self.mode_label = QLabel("Mode: --")
        self.tablet_label = QLabel("Tablet: --")
        
        for label in [self.connection_label, self.battery_label, self.mode_label, self.tablet_label]:
            label.setStyleSheet("""
                QLabel {
                    padding: 5px 10px;
                    margin: 2px;
                    background-color: #2d2d30;
                    border-radius: 4px;
                    color: #e0e0e0;
                    font-size: 12px;
                }
            """)
            self.status_bar.addPermanentWidget(label)
        
        self._update_status()
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.control_panel.status_update_signal.connect(self._handle_status_update)
    
    def _update_status(self):
        """Update status bar information."""
        try:
            status = self.pepper.get_status()
            
            # Connection
            if status and status.get('connected'):
                self.connection_label.setText("🟢 Connected")
            else:
                self.connection_label.setText("🔴 Disconnected")
            
            # Battery
            battery = status.get('battery', 0)
            self.battery_label.setText(f"🔋 {battery}%")
            
            # Battery warnings
            if battery < self._critical_battery_threshold and not self._battery_critical_shown:
                self._battery_critical_shown = True
                QMessageBox.critical(self, "Critical Battery", f"Battery: {battery}%!\n\nCharge immediately!")
            elif battery < self._low_battery_threshold and not self._battery_warning_shown:
                self._battery_warning_shown = True
                QMessageBox.warning(self, "Low Battery", f"Battery: {battery}%\n\nCharge soon.")
            
            if battery >= self._low_battery_threshold:
                self._battery_warning_shown = False
            if battery >= self._critical_battery_threshold:
                self._battery_critical_shown = False
            
            # Update control panel battery display
            self.control_panel.update_battery(battery)
            
            # Mode
            base = self.controllers.get('base')
            if base and base.is_moving():
                mode = "MOVING"
            else:
                mode = "STOPPED"
            self.mode_label.setText(f"Mode: {mode}")
            
            # Tablet
            tablet_mode = str(self.tablet.get_current_mode())
            self.tablet_label.setText(f"Tablet: {tablet_mode}")
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    def _update_movement(self):
        """Update continuous base movement (20Hz)."""
        try:
            base = self.controllers.get('base')
            if base:
                base.move_continuous()
        except Exception as e:
            logger.error(f"Movement update error: {e}")
    
    def _handle_status_update(self, message):
        """Handle status messages from control panel."""
        self.status_bar.showMessage(message, 3000)
    
    def _emergency_stop(self):
        """Emergency stop."""
        try:
            self.pepper.emergency_stop()
            self.status_bar.showMessage("🚨 EMERGENCY STOP", 5000)
            QMessageBox.warning(self, "Emergency Stop", "Emergency stop activated!")
        except Exception as e:
            logger.error(f"Emergency stop error: {e}")
    
    # ========================================================================
    # SETTINGS
    # ========================================================================
    
    def _load_settings(self):
        """Load window settings."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                
                if 'window' in settings:
                    w = settings['window']
                    self.resize(w.get('width', 1200), w.get('height', 800))
                    self.move(w.get('x', 100), w.get('y', 100))
                
                if 'splitter' in settings:
                    self.main_splitter.setSizes(settings['splitter'])
                
                logger.info("✓ Loaded GUI settings")
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
    
    def _save_settings(self):
        """Save window settings."""
        try:
            settings = {
                'window': {
                    'width': self.width(),
                    'height': self.height(),
                    'x': self.x(),
                    'y': self.y()
                },
                'splitter': self.main_splitter.sizes()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info("✓ Saved GUI settings")
        except Exception as e:
            logger.warning(f"Could not save settings: {e}")
    
    def closeEvent(self, event):
        """Handle window close."""
        reply = QMessageBox.question(
            self,
            'Exit Confirmation',
            'Exit and stop robot control?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._save_settings()
            
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            if hasattr(self, 'movement_timer'):
                self.movement_timer.stop()
            
            if hasattr(self, 'control_panel'):
                self.control_panel.cleanup()
            if hasattr(self, 'camera_panel'):
                self.camera_panel.cleanup()
            
            event.accept()
        else:
            event.ignore()
    
    def keyPressEvent(self, event):
        """Fallback key press handler."""
        # eventFilter handles most keys, this is just backup
        super().keyPressEvent(event)


def launch_gui(pepper_conn, controllers, dances, tablet_ctrl):
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    
    app.setApplicationName("Pepper Control Center")
    app.setOrganizationName("PepperVR")
    
    apply_theme(app)
    
    window = PepperControlGUI(pepper_conn, controllers, dances, tablet_ctrl)
    window.show()
    
    exit_code = app.exec_()
    
    logger.info("GUI closed, cleaning up...")
    try:
        pepper_conn.close()
    except:
        pass
    
    return exit_code