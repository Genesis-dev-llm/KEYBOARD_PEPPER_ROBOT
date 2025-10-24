"""
Settings Dialog - Phase 4B
Allow users to save/load preferences for speeds, modes, etc.
"""

import json
import os
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for user preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config_file = os.path.expanduser("~/.pepper_gui_settings.json")
        self.settings = self._load_settings()
        
        self._init_ui()
        self._load_values()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: Movement Settings
        tabs.addTab(self._create_movement_tab(), "🎮 Movement")
        
        # Tab 2: Robot Settings
        tabs.addTab(self._create_robot_tab(), "🤖 Robot")
        
        # Tab 3: Interface Settings
        tabs.addTab(self._create_interface_tab(), "🖥️ Interface")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_and_close)
        save_btn.setDefault(True)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_movement_tab(self):
        """Create movement settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Speed Settings
        speed_group = QGroupBox("Speed Settings")
        speed_layout = QVBoxLayout()
        
        # Base speed
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("Base Linear Speed (m/s):"))
        self.base_speed_spin = QDoubleSpinBox()
        self.base_speed_spin.setRange(0.1, 1.0)
        self.base_speed_spin.setSingleStep(0.1)
        self.base_speed_spin.setDecimals(1)
        self.base_speed_spin.setToolTip("Default: 0.5 m/s")
        base_layout.addWidget(self.base_speed_spin)
        speed_layout.addLayout(base_layout)
        
        # Angular speed
        angular_layout = QHBoxLayout()
        angular_layout.addWidget(QLabel("Base Angular Speed (rad/s):"))
        self.angular_speed_spin = QDoubleSpinBox()
        self.angular_speed_spin.setRange(0.1, 1.5)
        self.angular_speed_spin.setSingleStep(0.1)
        self.angular_speed_spin.setDecimals(1)
        self.angular_speed_spin.setToolTip("Default: 0.7 rad/s")
        angular_layout.addWidget(self.angular_speed_spin)
        speed_layout.addLayout(angular_layout)
        
        # Body speed
        body_layout = QHBoxLayout()
        body_layout.addWidget(QLabel("Body Movement Speed:"))
        self.body_speed_spin = QDoubleSpinBox()
        self.body_speed_spin.setRange(0.1, 1.0)
        self.body_speed_spin.setSingleStep(0.1)
        self.body_speed_spin.setDecimals(1)
        self.body_speed_spin.setToolTip("Default: 0.3")
        body_layout.addWidget(self.body_speed_spin)
        speed_layout.addLayout(body_layout)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # Mode Settings
        mode_group = QGroupBox("Default Mode")
        mode_layout = QVBoxLayout()
        
        self.continuous_mode_check = QCheckBox("Start in Continuous Mode")
        self.continuous_mode_check.setToolTip("If unchecked, starts in Incremental mode")
        mode_layout.addWidget(self.continuous_mode_check)
        
        self.turbo_enabled_check = QCheckBox("Enable Turbo Mode by Default")
        self.turbo_enabled_check.setToolTip("1.5x speed multiplier")
        mode_layout.addWidget(self.turbo_enabled_check)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        layout.addStretch()
        return widget
    
    def _create_robot_tab(self):
        """Create robot settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Connection Settings
        conn_group = QGroupBox("Connection")
        conn_layout = QVBoxLayout()
        
        self.auto_connect_check = QCheckBox("Auto-connect on startup")
        self.auto_connect_check.setToolTip("Automatically connect to last used IP")
        conn_layout.addWidget(self.auto_connect_check)
        
        self.save_ip_check = QCheckBox("Remember last IP address")
        self.save_ip_check.setToolTip("Save IP to .pepper_ip file")
        conn_layout.addWidget(self.save_ip_check)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Safety Settings
        safety_group = QGroupBox("Safety")
        safety_layout = QVBoxLayout()
        
        # Battery warning threshold
        battery_layout = QHBoxLayout()
        battery_layout.addWidget(QLabel("Low Battery Warning (%):"))
        self.battery_warning_spin = QSpinBox()
        self.battery_warning_spin.setRange(10, 50)
        self.battery_warning_spin.setSingleStep(5)
        self.battery_warning_spin.setToolTip("Show warning when battery below this %")
        battery_layout.addWidget(self.battery_warning_spin)
        safety_layout.addLayout(battery_layout)
        
        self.confirm_dances_check = QCheckBox("Confirm before starting dances")
        self.confirm_dances_check.setToolTip("Ask for confirmation before dance animations")
        safety_layout.addWidget(self.confirm_dances_check)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        layout.addStretch()
        return widget
    
    def _create_interface_tab(self):
        """Create interface settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Display Settings
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout()
        
        self.show_tooltips_check = QCheckBox("Show tooltips on hover")
        self.show_tooltips_check.setToolTip("Display helpful hints when hovering over buttons")
        display_layout.addWidget(self.show_tooltips_check)
        
        self.show_status_messages_check = QCheckBox("Show status messages")
        self.show_status_messages_check.setToolTip("Display status updates in status bar")
        display_layout.addWidget(self.show_status_messages_check)
        
        self.save_window_state_check = QCheckBox("Remember window size/position")
        self.save_window_state_check.setToolTip("Restore window geometry on startup")
        display_layout.addWidget(self.save_window_state_check)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Startup Settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        
        self.launch_gui_check = QCheckBox("Always launch GUI (ignore --no-gui)")
        self.launch_gui_check.setToolTip("Force GUI mode even with --no-gui flag")
        startup_layout.addWidget(self.launch_gui_check)
        
        self.run_diagnostics_check = QCheckBox("Run movement diagnostics on startup")
        self.run_diagnostics_check.setToolTip("Test movement capabilities at startup")
        startup_layout.addWidget(self.run_diagnostics_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        layout.addStretch()
        return widget
    
    def _load_settings(self):
        """Load settings from file."""
        default_settings = {
            'movement': {
                'base_linear_speed': 0.5,
                'base_angular_speed': 0.7,
                'body_speed': 0.3,
                'continuous_mode': True,
                'turbo_enabled': False
            },
            'robot': {
                'auto_connect': False,
                'save_ip': True,
                'battery_warning': 30,
                'confirm_dances': False
            },
            'interface': {
                'show_tooltips': True,
                'show_status_messages': True,
                'save_window_state': True,
                'launch_gui': True,
                'run_diagnostics': False
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings added)
                    for category in default_settings:
                        if category in loaded:
                            default_settings[category].update(loaded[category])
                    logger.info("✓ Settings loaded")
                    return default_settings
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        
        return default_settings
    
    def _load_values(self):
        """Load values into UI widgets."""
        # Movement tab
        self.base_speed_spin.setValue(self.settings['movement']['base_linear_speed'])
        self.angular_speed_spin.setValue(self.settings['movement']['base_angular_speed'])
        self.body_speed_spin.setValue(self.settings['movement']['body_speed'])
        self.continuous_mode_check.setChecked(self.settings['movement']['continuous_mode'])
        self.turbo_enabled_check.setChecked(self.settings['movement']['turbo_enabled'])
        
        # Robot tab
        self.auto_connect_check.setChecked(self.settings['robot']['auto_connect'])
        self.save_ip_check.setChecked(self.settings['robot']['save_ip'])
        self.battery_warning_spin.setValue(self.settings['robot']['battery_warning'])
        self.confirm_dances_check.setChecked(self.settings['robot']['confirm_dances'])
        
        # Interface tab
        self.show_tooltips_check.setChecked(self.settings['interface']['show_tooltips'])
        self.show_status_messages_check.setChecked(self.settings['interface']['show_status_messages'])
        self.save_window_state_check.setChecked(self.settings['interface']['save_window_state'])
        self.launch_gui_check.setChecked(self.settings['interface']['launch_gui'])
        self.run_diagnostics_check.setChecked(self.settings['interface']['run_diagnostics'])
    
    def _save_settings(self):
        """Save current values to settings."""
        # Movement
        self.settings['movement']['base_linear_speed'] = self.base_speed_spin.value()
        self.settings['movement']['base_angular_speed'] = self.angular_speed_spin.value()
        self.settings['movement']['body_speed'] = self.body_speed_spin.value()
        self.settings['movement']['continuous_mode'] = self.continuous_mode_check.isChecked()
        self.settings['movement']['turbo_enabled'] = self.turbo_enabled_check.isChecked()
        
        # Robot
        self.settings['robot']['auto_connect'] = self.auto_connect_check.isChecked()
        self.settings['robot']['save_ip'] = self.save_ip_check.isChecked()
        self.settings['robot']['battery_warning'] = self.battery_warning_spin.value()
        self.settings['robot']['confirm_dances'] = self.confirm_dances_check.isChecked()
        
        # Interface
        self.settings['interface']['show_tooltips'] = self.show_tooltips_check.isChecked()
        self.settings['interface']['show_status_messages'] = self.show_status_messages_check.isChecked()
        self.settings['interface']['save_window_state'] = self.save_window_state_check.isChecked()
        self.settings['interface']['launch_gui'] = self.launch_gui_check.isChecked()
        self.settings['interface']['run_diagnostics'] = self.run_diagnostics_check.isChecked()
        
        # Write to file
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("✓ Settings saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def _save_and_close(self):
        """Save settings and close dialog."""
        if self._save_settings():
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved!\n\nSome changes may require restart to take effect."
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                "Failed to save settings. Check logs for details."
            )
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all settings to defaults?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.settings = self._load_settings.__func__(self)  # Get fresh defaults
            self._load_values()
            logger.info("Settings reset to defaults")
    
    def get_settings(self):
        """Get current settings dict."""
        return self.settings