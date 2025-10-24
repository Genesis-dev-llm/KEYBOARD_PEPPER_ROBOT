"""
Image Manager - Phase 2
GUI widget for managing tablet images (drag-drop + presets).
"""

import os
import shutil
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

logger = logging.getLogger(__name__)

class ImageThumbnail(QLabel):
    """Clickable image thumbnail."""
    
    clicked = pyqtSignal(str)  # Emits image path when clicked
    
    def __init__(self, image_path, name):
        super().__init__()
        
        self.image_path = image_path
        self.image_name = name
        
        # Load and scale image with error handling
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(scaled)
            else:
                # Corrupt or invalid image
                self.setText("❌\nInvalid")
                logger.warning(f"Could not load image: {image_path}")
        except Exception as e:
            # Any error loading image
            self.setText("❌\nError")
            logger.error(f"Error loading thumbnail {image_path}: {e}")
        
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(140, 140)
        self.setObjectName("imageThumbnail")
        self.setToolTip(name)
        
        # Style
        self.setStyleSheet("""
            QLabel#imageThumbnail {
                border: 2px solid #3e3e42;
                border-radius: 8px;
                padding: 5px;
                background: #2d2d30;
            }
            QLabel#imageThumbnail:hover {
                border: 2px solid #0e639c;
                background: #1e3a5f;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)


class ImageDropZone(QLabel):
    """Drag and drop zone for images."""
    
    image_dropped = pyqtSignal(str)  # Emits file path
    
    def __init__(self):
        super().__init__()
        
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(150)
        self.setObjectName("imageDropZone")
        
        self.setText(
            "📁 Drag & Drop Images Here\n\n"
            "Supported: PNG, JPG, JPEG, GIF\n\n"
            "Images will be saved to custom gallery"
        )
        
        self.setStyleSheet("""
            QLabel#imageDropZone {
                border: 3px dashed #6e6e6e;
                border-radius: 10px;
                background: #2d2d30;
                color: #8e8e8e;
                font-size: 14px;
                padding: 20px;
            }
            QLabel#imageDropZone[dragActive="true"] {
                border: 3px dashed #0e639c;
                background: #1e3a5f;
                color: #ffffff;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            # Check if it's an image
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                event.acceptProposedAction()
                self.setProperty("dragActive", "true")
                self.style().unpolish(self)
                self.style().polish(self)
                return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def dropEvent(self, event: QDropEvent):
        """Handle image drop."""
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            if os.path.exists(file_path):
                self.image_dropped.emit(file_path)
                event.acceptProposedAction()


class ImageManager(QWidget):
    """
    Image gallery manager widget.
    Shows preset images + custom uploaded images.
    """
    
    image_selected = pyqtSignal(str)  # Emits path when user selects image
    
    def __init__(self):
        super().__init__()
        
        # Paths
        self.preset_dir = "assets/tablet_images"
        self.custom_dir = os.path.join(self.preset_dir, "custom")
        
        # Create directories if they don't exist
        os.makedirs(self.preset_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
        
        self._init_ui()
        self._load_images()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🖼️ Tablet Image Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Drop zone
        self.drop_zone = ImageDropZone()
        self.drop_zone.image_dropped.connect(self._on_image_dropped)
        layout.addWidget(self.drop_zone)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8e8e8e; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Preset images section
        preset_label = QLabel("📌 Preset Images (for dances/states)")
        preset_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(preset_label)
        
        self.preset_scroll = QScrollArea()
        self.preset_scroll.setWidgetResizable(True)
        self.preset_scroll.setMaximumHeight(180)
        self.preset_container = QWidget()
        self.preset_layout = QGridLayout(self.preset_container)
        self.preset_scroll.setWidget(self.preset_container)
        layout.addWidget(self.preset_scroll)
        
        # Custom images section
        custom_label = QLabel("📁 Custom Images (your uploads)")
        custom_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(custom_label)
        
        self.custom_scroll = QScrollArea()
        self.custom_scroll.setWidgetResizable(True)
        self.custom_scroll.setMaximumHeight(180)
        self.custom_container = QWidget()
        self.custom_layout = QGridLayout(self.custom_container)
        self.custom_scroll.setWidget(self.custom_container)
        layout.addWidget(self.custom_scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_images)
        
        clear_btn = QPushButton("🗑️ Clear Custom")
        clear_btn.clicked.connect(self._clear_custom_images)
        
        help_btn = QPushButton("❓ Help")
        help_btn.clicked.connect(self._show_help)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(help_btn)
        
        layout.addLayout(button_layout)
    
    def _load_images(self):
        """Load all images (preset + custom)."""
        # Clear existing
        self._clear_layout(self.preset_layout)
        self._clear_layout(self.custom_layout)
        
        # Load preset images
        preset_count = self._load_images_from_dir(self.preset_dir, self.preset_layout, exclude_custom=True)
        
        # Load custom images
        custom_count = self._load_images_from_dir(self.custom_dir, self.custom_layout)
        
        self.status_label.setText(f"Loaded: {preset_count} preset, {custom_count} custom")
        logger.info(f"Loaded {preset_count} preset images, {custom_count} custom images")
    
    def _load_images_from_dir(self, directory, grid_layout, exclude_custom=False):
        """Load images from directory into grid."""
        if not os.path.exists(directory):
            return 0
        
        count = 0
        row, col = 0, 0
        
        for filename in sorted(os.listdir(directory)):
            # Skip custom folder when loading presets
            if exclude_custom and filename == 'custom':
                continue
            
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filepath = os.path.join(directory, filename)
                
                # Create thumbnail
                thumb = ImageThumbnail(filepath, filename)
                thumb.clicked.connect(self._on_image_clicked)
                
                grid_layout.addWidget(thumb, row, col)
                
                col += 1
                if col >= 4:  # 4 columns
                    col = 0
                    row += 1
                
                count += 1
        
        if count == 0:
            placeholder = QLabel("No images found\n\nAdd images to:\n" + directory)
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #6e6e6e; font-style: italic;")
            grid_layout.addWidget(placeholder, 0, 0, 1, 4)
        
        return count
    
    def _clear_layout(self, layout):
        """Clear all widgets from layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _on_image_dropped(self, source_path):
        """Handle dropped image."""
        try:
            # Generate unique filename
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.custom_dir, filename)
            
            # Handle duplicates
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(self.custom_dir, filename)
                    counter += 1
            
            # Copy image
            shutil.copy2(source_path, dest_path)
            
            self.status_label.setText(f"✓ Added: {filename}")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 11px;")
            logger.info(f"Image added: {filename}")
            
            # Reload gallery
            self._load_images()
            
        except Exception as e:
            self.status_label.setText(f"✗ Error: {e}")
            self.status_label.setStyleSheet("color: #f87171; font-size: 11px;")
            logger.error(f"Error adding image: {e}")
    
    def _on_image_clicked(self, image_path):
        """Handle image selection."""
        logger.info(f"Image selected: {os.path.basename(image_path)}")
        self.status_label.setText(f"Selected: {os.path.basename(image_path)}")
        self.status_label.setStyleSheet("color: #0e639c; font-size: 11px;")
        
        # Emit signal
        self.image_selected.emit(image_path)
    
    def _clear_custom_images(self):
        """Clear all custom images."""
        reply = QMessageBox.question(
            self,
            'Clear Custom Images',
            'Delete all custom images?\n\nThis cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                for filename in os.listdir(self.custom_dir):
                    filepath = os.path.join(self.custom_dir, filename)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                
                self.status_label.setText("✓ Custom images cleared")
                self._load_images()
                logger.info("Custom images cleared")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear images:\n{e}")
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
<h2>Image Manager Help</h2>

<h3>Preset Images:</h3>
<p>Place images in <b>assets/tablet_images/</b> with these names:</p>
<ul>
<li><b>standby.png</b> - Default idle screen</li>
<li><b>wave.png</b> - During wave dance</li>
<li><b>special.png</b> - During special dance</li>
<li><b>robot.png</b> - During robot dance</li>
<li><b>moonwalk.png</b> - During moonwalk</li>
<li><b>moving_forward.png</b> - When moving forward (optional)</li>
<li><b>moving_back.png</b> - When moving backward (optional)</li>
</ul>

<h3>Custom Images:</h3>
<p>Drag & drop any image to add to custom gallery.</p>
<p>Click any image to display on Pepper's tablet.</p>

<h3>Safe Fallback:</h3>
<p>If images don't exist, text will be shown instead (no crash!).</p>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def get_preset_image(self, name):
        """
        Get path to preset image (with fallback).
        Returns None if doesn't exist.
        """
        path = os.path.join(self.preset_dir, f"{name}.png")
        if os.path.exists(path):
            return path
        
        # Try jpg
        path = os.path.join(self.preset_dir, f"{name}.jpg")
        if os.path.exists(path):
            return path
        
        return None