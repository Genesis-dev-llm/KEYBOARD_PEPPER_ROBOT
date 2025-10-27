#!/usr/bin/env python
"""
Simple GUI Test
Opens a test window to verify PyQt5 works.
Doesn't require Pepper connection.

Usage:
    python gui_test_simple.py
"""

import sys

print("\n🧪 Testing PyQt5 GUI...")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    print("✓ PyQt5 imported successfully")
except ImportError as e:
    print(f"❌ Cannot import PyQt5: {e}")
    print("\nInstall with: pip install PyQt5")
    sys.exit(1)

class TestWindow(QMainWindow):
    """Simple test window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🤖 Pepper GUI Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("✅ GUI IS WORKING!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4ade80;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "If you can see this window, PyQt5 is working!\n\n"
            "This means the GUI dependencies are installed correctly.\n\n"
            "Next step: Launch the full Pepper GUI with:\n"
            "python launch_gui.py 192.168.1.100"
        )
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 20px;
            }
        """)
        layout.addWidget(message)
        
        # Close button
        close_btn = QPushButton("Close Window")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        layout.addWidget(close_btn)
        
        layout.addStretch()

def main():
    """Run test."""
    try:
        app = QApplication(sys.argv)
        print("✓ QApplication created")
        
        window = TestWindow()
        print("✓ Test window created")
        
        window.show()
        print("✓ Window shown")
        print("\n🎉 SUCCESS! If you see a window, PyQt5 works!\n")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()