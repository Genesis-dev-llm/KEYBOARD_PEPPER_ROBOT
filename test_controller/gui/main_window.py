"""
Main Window for Pepper Control Center
Professional PyQt5 GUI with resizable/movable window.
"""

import sys
import os
import json
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStatusBar, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from .styles import apply_theme
from .camera_panel import CameraPanel
from .control_panel import ControlPanel

logger = logging.getLogger(__name__)

class PepperControlGUI(QMainWindow):
    """Main window for Pepper robot control interface."""
    
    # Signals for inter-component communication
    emergency_stop_signal = pyqtSignal()
    
    def __init__(self, pepper_conn, controllers, dances, tablet_ctrl):
        super().__init__()
        
        # Store references
        self.pepper = pepper_conn
        self.controllers = controllers
        self.dances = dances
        self.tablet = tablet_ctrl
        
        # Configuration file path
        self.config_file = os.path.expanduser('~/.pepper_gui_config.json')
        
        # Initialize UI
        self._init_ui()
        self._load_settings()
        self._setup_status_bar()
        self._setup_connections()
        
        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)  # Update every second
        
        # Start base movement update timer (for continuous movement)
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self._update_movement)
        self.movement_timer.start(50)  # 20Hz for smooth movement
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Window properties
        self.setWindowTitle("🤖 Pepper Control Center")
        self.setMinimumSize(800, 600)
        
        # Default size (will be overridden by saved settings)
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
        
        # Create main splitter (left: cameras, right: controls)
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
        """Create menu bar with File and Help menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Robot Status action
        status_action = file_menu.addAction('🤖 Robot Status')
        status_action.triggered.connect(self._show_robot_status_dialog)
        
        file_menu.addSeparator()
        
        # Quit action
        quit_action = file_menu.addAction('Quit')
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        # Keyboard shortcuts
        shortcuts_action = help_menu.addAction('⌨️ Keyboard Shortcuts')
        shortcuts_action.setShortcut('F1')
        shortcuts_action.triggered.connect(self._show_shortcuts_help)
        
        # About
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self._show_about)
    
    def _show_robot_status_dialog(self):
        """Show robot status dialog (wrapper for control panel method)."""
        if hasattr(self, 'control_panel'):
            self.control_panel._show_robot_status()
        else:
            QMessageBox.warning(self, "Error", "Control panel not initialized")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
<h2>Pepper Control Center</h2>
<p><b>Version 2.0.0</b> - PyQt5 GUI Edition</p>

<p>Professional control interface for SoftBank Robotics Pepper robot</p>

<h3>Features:</h3>
<ul>
<li>Real-time robot control</li>
<li>Dual camera feeds (Pepper + External)</li>
<li>Live audio streaming</li>
<li>Dance animations</li>
<li>Tablet display management</li>
<li>Drag & drop file display</li>
</ul>

<p><i>Built for VR Teleoperation Research</i></p>
<p>© 2025 Pepper VR Team</p>
        """
        QMessageBox.about(self, "About Pepper Control Center", about_text)
    
    def _setup_status_bar(self):
        """Setup the status bar at the bottom."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.connection_label = self._create_status_label("🔴 Disconnected")
        self.battery_label = self._create_status_label("🔋 ---%")
        self.mode_label = self._create_status_label("Mode: --")
        self.tablet_label = self._create_status_label("Tablet: --")
        
        # Add to status bar
        self.status_bar.addPermanentWidget(self.connection_label)
        self.status_bar.addPermanentWidget(self.battery_label)
        self.status_bar.addPermanentWidget(self.mode_label)
        self.status_bar.addPermanentWidget(self.tablet_label)
        
        # Initial update
        self._update_status()
    
    def _create_status_label(self, text):
        """Create a styled status label."""
        from PyQt5.QtWidgets import QLabel
        label = QLabel(text)
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
        return label
    
    def _setup_connections(self):
        """Setup signal/slot connections."""
        # Connect control panel signals
        self.control_panel.status_update_signal.connect(self._handle_status_update)
    
    def _update_status(self):
        """Update status bar information."""
        try:
            # Connection status
            status = self.pepper.get_status()
            if status and status.get('connected'):
                self.connection_label.setText("🟢 Connected")
                self.connection_label.setStyleSheet(self.connection_label.styleSheet() + 
                    "QLabel { color: #4ade80; }")
            else:
                self.connection_label.setText("🔴 Disconnected")
                self.connection_label.setStyleSheet(self.connection_label.styleSheet() + 
                    "QLabel { color: #f87171; }")
            
            # Battery level
            battery = status.get('battery', 0)
            self.battery_label.setText(f"🔋 {battery}%")
            if battery >= 60:
                color = "#4ade80"
            elif battery >= 30:
                color = "#fbbf24"
            else:
                color = "#f87171"
            self.battery_label.setStyleSheet(self.battery_label.styleSheet() + 
                f"QLabel {{ color: {color}; }}")
            
            # Movement mode
            base = self.controllers.get('base')
            if base:
                # Check if actually moving (any velocity non-zero)
                if abs(base.base_x) > 0.01 or abs(base.base_y) > 0.01 or abs(base.base_theta) > 0.01:
                    mode = "MOVING"
                else:
                    mode = "STOPPED"
            else:
                mode = "UNKNOWN"
            self.mode_label.setText(f"Mode: {mode}")
            
            # Tablet mode
            tablet_mode = str(self.tablet.get_current_mode())
            self.tablet_label.setText(f"Tablet: {tablet_mode}")
            
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def _update_movement(self):
        """Update continuous base movement (called at 20Hz)."""
        try:
            base = self.controllers.get('base')
            if base:
                base.move_continuous()
        except Exception as e:
            logger.error(f"Movement update error: {e}")
    
    def _handle_status_update(self, message):
        """Handle status update messages from control panel."""
        self.status_bar.showMessage(message, 3000)  # Show for 3 seconds
    
    def _emergency_stop(self):
        """Handle emergency stop."""
        try:
            self.pepper.emergency_stop()
            self.status_bar.showMessage("🚨 EMERGENCY STOP ACTIVATED", 5000)
            
            # Show dialog
            QMessageBox.warning(
                self,
                "Emergency Stop",
                "Emergency stop activated!\nAll robot movement has been halted.",
                QMessageBox.Ok
            )
        except Exception as e:
            print(f"Error during emergency stop: {e}")
    
    def _load_settings(self):
        """Load window settings from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                
                # Restore window geometry
                if 'window' in settings:
                    w = settings['window']
                    self.resize(w.get('width', 1200), w.get('height', 800))
                    self.move(w.get('x', 100), w.get('y', 100))
                
                # Restore splitter sizes
                if 'splitter' in settings:
                    self.main_splitter.setSizes(settings['splitter'])
                
                print("✓ Loaded GUI settings")
        except Exception as e:
            print(f"Could not load GUI settings: {e}")
    
    def _save_settings(self):
        """Save window settings to config file."""
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
            
            print("✓ Saved GUI settings")
        except Exception as e:
            print(f"Could not save GUI settings: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Confirm exit
        reply = QMessageBox.question(
            self,
            'Exit Confirmation',
            'Are you sure you want to exit?\nThis will stop all robot control.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Save settings first
            self._save_settings()
            
            # Stop timers
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            if hasattr(self, 'movement_timer'):
                self.movement_timer.stop()
            
            # Cleanup panels (this will cleanup audio/camera)
            if hasattr(self, 'control_panel'):
                self.control_panel.cleanup()
            if hasattr(self, 'camera_panel'):
                self.camera_panel.cleanup()
            
            # Accept close
            event.accept()
        else:
            event.ignore()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # F1 - Show help
        if event.key() == Qt.Key_F1:
            self._show_shortcuts_help()
        
        # F11 - Toggle fullscreen
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        
        # Ctrl+Q - Quit
        elif event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            self.close()
        
        # ESC - Emergency stop (when not fullscreen)
        elif event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self._emergency_stop()
        
        else:
            super().keyPressEvent(event)
    
    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog."""
        help_text = """
<h2>Keyboard Shortcuts</h2>

<h3>Window Controls:</h3>
<table>
<tr><td><b>F1</b></td><td>Show this help</td></tr>
<tr><td><b>F11</b></td><td>Toggle fullscreen</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit application</td></tr>
<tr><td><b>ESC</b></td><td>Emergency stop (or exit fullscreen)</td></tr>
</table>

<h3>Robot Controls:</h3>
<p><i>All keyboard controls from the keyboard tester still work!</i></p>
<table>
<tr><td><b>Arrow Keys</b></td><td>Move robot</td></tr>
<tr><td><b>Q/E</b></td><td>Rotate left/right</td></tr>
<tr><td><b>1-4</b></td><td>Trigger dances</td></tr>
<tr><td><b>M</b></td><td>Cycle tablet mode</td></tr>
<tr><td><b>H</b></td><td>Show greeting</td></tr>
<tr><td><b>SPACE</b></td><td>Stop movement</td></tr>
</table>

<p><i>Tip: You can use both GUI buttons and keyboard shortcuts!</i></p>
        """
        
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            help_text
        )


def launch_gui(pepper_conn, controllers, dances, tablet_ctrl):
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Pepper Control Center")
    app.setOrganizationName("PepperVR")
    
    # Apply dark theme
    apply_theme(app)
    
    # Create main window
    window = PepperControlGUI(pepper_conn, controllers, dances, tablet_ctrl)
    window.show()
    
    # Run application (blocks until window closes)
    exit_code = app.exec_()
    
    # Cleanup after GUI closes
    logger.info("GUI closed, cleaning up...")
    try:
        pepper_conn.close()
    except:
        pass
    
    return exit_code