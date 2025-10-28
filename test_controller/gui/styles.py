"""
MODULE: test_controller/gui/styles.py
Qt Stylesheet - ENHANCED Professional Dark Theme

IMPROVEMENTS:
- Better button hover/pressed states
- Smooth transitions
- Better contrast
- Cleaner look
"""

DARK_THEME = """
/* ========================================================================
   MAIN WINDOW
   ======================================================================== */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* ========================================================================
   STATUS BAR
   ======================================================================== */
QStatusBar {
    background-color: #2d2d30;
    color: #e0e0e0;
    border-top: 1px solid #3e3e42;
    padding: 5px;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

/* ========================================================================
   PANELS & FRAMES
   ======================================================================== */
QFrame {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    padding: 10px;
}

QGroupBox {
    background-color: #252526;
    border: 2px solid #3e3e42;
    border-radius: 8px;
    margin-top: 10px;
    padding: 15px;
    font-weight: bold;
    font-size: 14px;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    background-color: #2d2d30;
    border-radius: 4px;
}

/* ========================================================================
   BUTTONS - IMPROVED
   ======================================================================== */
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #005a9e;
    padding-top: 12px;  /* Push down effect */
    padding-bottom: 8px;
}

QPushButton:disabled {
    background-color: #3e3e42;
    color: #6e6e6e;
}

/* Dance Buttons (with emojis) */
QPushButton#danceButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #7c3aed, stop:1 #5a1ea6);
    font-size: 16px;
    min-width: 80px;
    min-height: 50px;
}

QPushButton#danceButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #8b5cf6, stop:1 #6d28d9);
}

QPushButton#danceButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #6d28d9, stop:1 #5a1ea6);
}

/* Emergency Stop Button */
QPushButton#emergencyButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #dc2626, stop:1 #991b1b);
    font-size: 16px;
    min-height: 60px;
    font-weight: bold;
    border: 2px solid #7f1d1d;
}

QPushButton#emergencyButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #ef4444, stop:1 #b91c1c);
}

QPushButton#emergencyButton:pressed {
    background: #7f1d1d;
}

/* Toggle Buttons (Checkable) */
QPushButton:checkable {
    background-color: #3e3e42;
}

QPushButton:checked {
    background-color: #0e639c;
    border: 2px solid #1177bb;
}

/* ========================================================================
   SLIDERS - IMPROVED
   ======================================================================== */
QSlider::groove:horizontal {
    background: #3e3e42;
    height: 10px;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #1177bb, stop:1 #0e639c);
    width: 20px;
    height: 20px;
    margin: -5px 0;
    border-radius: 10px;
    border: 2px solid #0e639c;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #1e88e5, stop:1 #1177bb);
}

QSlider::handle:horizontal:pressed {
    background: #0e639c;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #0e639c, stop:1 #1177bb);
    border-radius: 5px;
}

/* ========================================================================
   RADIO BUTTONS
   ======================================================================== */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
    font-size: 13px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #6e6e6e;
    background-color: #2d2d30;
}

QRadioButton::indicator:checked {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                               fx:0.5, fy:0.5,
                               stop:0 #0e639c, stop:1 #0e639c);
    border: 2px solid #1177bb;
}

QRadioButton::indicator:hover {
    border: 2px solid #1177bb;
}

/* ========================================================================
   LABELS
   ======================================================================== */
QLabel {
    color: #e0e0e0;
    font-size: 13px;
    background: transparent;
    border: none;
}

QLabel#headerLabel {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#statusLabel {
    font-size: 12px;
    padding: 5px;
    border-radius: 4px;
}

/* ========================================================================
   PROGRESS BARS - IMPROVED
   ======================================================================== */
QProgressBar {
    border: 2px solid #3e3e42;
    border-radius: 5px;
    background-color: #2d2d30;
    text-align: center;
    color: #e0e0e0;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #0e639c, stop:1 #1177bb);
    border-radius: 3px;
}

/* Battery colors */
QProgressBar#batteryGood::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #10b981, stop:1 #34d399);
}

QProgressBar#batteryMedium::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #f59e0b, stop:1 #fbbf24);
}

QProgressBar#batteryLow::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #dc2626, stop:1 #ef4444);
}

/* ========================================================================
   SCROLLBARS
   ======================================================================== */
QScrollBar:vertical {
    background: #2d2d30;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #6e6e6e;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #8e8e8e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #2d2d30;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #6e6e6e;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #8e8e8e;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========================================================================
   SPLITTER
   ======================================================================== */
QSplitter::handle {
    background-color: #3e3e42;
    width: 3px;
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #0e639c;
}

/* ========================================================================
   VIDEO DISPLAY
   ======================================================================== */
QLabel#videoLabel {
    background-color: #000000;
    border: 2px solid #3e3e42;
    border-radius: 8px;
}

/* ========================================================================
   DRAG & DROP ZONE
   ======================================================================== */
QLabel#dropZone {
    background-color: #2d2d30;
    border: 3px dashed #6e6e6e;
    border-radius: 10px;
    color: #8e8e8e;
    font-size: 14px;
    padding: 30px;
}

QLabel#dropZone[dragActive="true"] {
    border: 3px dashed #0e639c;
    background-color: #1e3a5f;
    color: #ffffff;
}

/* ========================================================================
   TOOLTIPS
   ======================================================================== */
QToolTip {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #6e6e6e;
    border-radius: 4px;
    padding: 5px;
    font-size: 12px;
}

/* ========================================================================
   SCROLL AREA
   ======================================================================== */
QScrollArea {
    background-color: #1e1e1e;
    border: none;
}

/* ========================================================================
   MENU BAR
   ======================================================================== */
QMenuBar {
    background-color: #2d2d30;
    color: #e0e0e0;
    border-bottom: 1px solid #3e3e42;
}

QMenuBar::item {
    padding: 5px 10px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: #0e639c;
}

QMenu {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3e3e42;
}

QMenu::item {
    padding: 5px 30px 5px 20px;
}

QMenu::item:selected {
    background-color: #0e639c;
}

/* ========================================================================
   SPIN BOXES
   ======================================================================== */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 2px solid #3e3e42;
    border-radius: 4px;
    padding: 5px;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #0e639c;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #3e3e42;
    border-radius: 2px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #0e639c;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #3e3e42;
    border-radius: 2px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #0e639c;
}

/* ========================================================================
   CHECK BOXES
   ======================================================================== */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid #6e6e6e;
    background-color: #2d2d30;
}

QCheckBox::indicator:checked {
    background-color: #0e639c;
    border: 2px solid #1177bb;
}

QCheckBox::indicator:hover {
    border: 2px solid #1177bb;
}

/* ========================================================================
   TAB WIDGET
   ======================================================================== */
QTabWidget::pane {
    border: 1px solid #3e3e42;
    background-color: #252526;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #8e8e8e;
    padding: 8px 16px;
    border: 1px solid #3e3e42;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #252526;
    color: #e0e0e0;
    border-bottom: 2px solid #0e639c;
}

QTabBar::tab:hover {
    background-color: #3e3e42;
}
"""

def apply_theme(app):
    """Apply the dark theme to the application."""
    app.setStyleSheet(DARK_THEME)