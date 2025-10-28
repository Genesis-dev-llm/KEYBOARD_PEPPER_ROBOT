# 🤖 Pepper Robot Control System

**Version 2.0** - Complete VR Teleoperation Framework

A comprehensive control system for SoftBank Robotics Pepper robot with GUI, keyboard controls, dances, and tablet display features.

---

## ✨ Features

### 🎮 Dual Control Modes
- **GUI Mode** (default) - Professional PyQt5 interface with live camera feeds
- **Keyboard Mode** - Terminal-based control with immediate response

### 🤖 Movement Control
- **Base Movement**: Forward/backward, strafe left/right, rotation
- **Head Control**: Pan and tilt with limits
- **Arm Control**: Shoulders, elbows, wrists with smooth interpolation
- **Hand Control**: Open/close grippers
- **Speed Control**: Adjustable speeds + turbo mode

### 💃 Dance Animations
1. **Wave** - Friendly greeting gesture
2. **Special Dance** - Anatomically accurate twerk with squats
3. **Robot Dance** - Mechanical choppy movements
4. **Moonwalk** - Michael Jackson style with crotch grab → spin → moonwalk

### 📱 Tablet Display System
- **STATUS Mode**: Shows current action with preset images
- **CUSTOM IMAGE Mode**: Display user-uploaded images
- **PEPPER CAM Mode**: Mirror Pepper's camera on tablet
- **HOVERCAM Mode**: Display external USB camera feed

### 📹 Video Streaming
- Flask-based HTTP server streams Pepper + HoverCam feeds
- Real-time MJPEG streaming at 10 FPS
- Snapshot endpoints for still frames

---

## 📋 Requirements

### System Requirements
- **Python**: 3.6+
- **OS**: Windows, macOS, or Linux
- **Network**: Pepper and PC on same network

### Python Dependencies

**Core (required):**
```bash
qi==3.1.5
websockets==13.0
Flask==3.1.2
Flask-Cors==6.0.1
numpy==1.26.4
opencv-python==4.12.0.88
pynput==1.7.6
```

**GUI (optional, for GUI mode):**
```bash
PyQt5==5.15.10
Pillow==10.1.0
```

**Audio (optional, Phase 4):**
```bash
pyaudio==0.2.14
SpeechRecognition==3.10.0
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd pepper-control

# Install dependencies
pip install -r requirements.txt

# Optional: Install GUI
pip install -r requirements_gui.txt
```

### 2. Connect to Pepper

```bash
# GUI mode (default)
python test_keyboard_control.py 192.168.1.100

# Keyboard-only mode
python test_keyboard_control.py 192.168.1.100 --no-gui

# Using IP flag
python test_keyboard_control.py --ip 192.168.1.100
```

### 3. First Time Setup

The IP address is saved to `.pepper_ip` file for convenience.

---

## ⌨️ Keyboard Controls

### Movement
| Key | Action |
|-----|--------|
| `↑` | Move forward |
| `↓` | Move backward |
| `←` | Strafe left |
| `→` | Strafe right |
| `Q` | Rotate left |
| `E` | Rotate right |
| `Space` | **STOP** |

### Head Control
| Key | Action |
|-----|--------|
| `W` | Head up |
| `S` | Head down |
| `A` | Head left |
| `D` | Head right |
| `R` | Reset head |

### Arms (Shoulders)
| Key | Action |
|-----|--------|
| `U` | Left shoulder up |
| `J` | Left shoulder down |
| `I` | Right shoulder up |
| `K` | Right shoulder down |
| `O` | Left arm out |
| `L` | Right arm out |

### Arms (Elbows)
| Key | Action |
|-----|--------|
| `7` | Left elbow bend |
| `9` | Left elbow straighten |
| `8` | Right elbow bend |
| `0` | Right elbow straighten |

### Wrists
| Key | Action |
|-----|--------|
| `,` | Left wrist CCW |
| `.` | Left wrist CW |
| `;` | Right wrist CCW |
| `'` | Right wrist CW |

### Hands (use Shift)
| Key | Action |
|-----|--------|
| `<` (Shift+,) | Left hand open |
| `>` (Shift+.) | Left hand close |
| `(` (Shift+9) | Right hand open |
| `)` (Shift+0) | Right hand close |

### Dances
| Key | Dance |
|-----|-------|
| `1` | 👋 Wave |
| `2` | 💃 Special |
| `3` | 🤖 Robot |
| `4` | 🌙 Moonwalk |

### Speed & Modes
| Key | Action |
|-----|--------|
| `+` or `=` | Increase speed |
| `-` or `_` | Decrease speed |
| `X` | Toggle turbo mode (1.5x) |
| `T` | Toggle continuous/incremental mode |

### Tablet & Video
| Key | Action |
|-----|--------|
| `M` | Cycle tablet display mode |
| `H` | Show greeting |
| `V` | Toggle video feed |

### System
| Key | Action |
|-----|--------|
| `P` | Print status |
| `Z` | Reset position |
| `ESC` | **Emergency stop & quit** |

---

## 🖥️ GUI Mode

### Features
- Live camera feeds (Pepper + HoverCam)
- Visual control buttons
- Image manager with drag & drop
- Real-time status display
- Battery monitoring

### GUI Keyboard Shortcuts
All keyboard controls work in GUI mode! Plus:
- `F1` - Show help
- `F11` - Toggle fullscreen
- `Ctrl+Q` - Quit
- `Ctrl+I` - Robot status

### Panels

**Left Panel - Cameras:**
- Camera Feeds tab - Live video display
- Images tab - Preset image management
- Files tab - Drag & drop files to tablet

**Right Panel - Controls:**
- Movement controls with hold-to-move
- Dance buttons
- Tablet mode selector
- Emergency stop

---

## 📱 Tablet Display System

### Setting Up Images

1. **Create directory structure:**
```bash
mkdir -p assets/tablet_images/custom
```

2. **Add preset images** (optional):
```
assets/tablet_images/
├── standby.png       # Default idle screen
├── wave.png          # During wave dance
├── special.png       # During special dance
├── robot.png         # During robot dance
├── moonwalk.png      # During moonwalk
├── moving_forward.png
└── moving_back.png
```

3. **Custom images:**
- Use GUI's Image Manager
- Drag & drop any image
- Click to display on tablet

### Safe Fallbacks
If images are missing, the system shows text/emoji instead (no crashes!).

### Display Modes
- **STATUS**: Shows current action + battery
- **CUSTOM_IMAGE**: Your uploaded image
- **PEPPER_CAM**: Pepper's camera mirror
- **HOVERCAM**: External USB camera

Press `M` to cycle modes.

---

## 🎭 Dance System

### Available Dances

**1. Wave (Key: 1)**
- Simple friendly greeting
- Raises right arm and waves
- Duration: ~3 seconds

**2. Special Dance (Key: 2)**
- Anatomically accurate twerk
- Includes squat, hip isolation, arm flair
- Duration: ~20 seconds
- 6 phases with progressive intensity

**3. Robot Dance (Key: 3)**
- Mechanical choppy movements
- Sharp angles, staccato motion
- Duration: ~15 seconds

**4. Moonwalk (Key: 4)**
- Full Michael Jackson sequence
- Crotch grab → Hip thrust → Spin → Moonwalk
- Duration: ~25 seconds
- Includes balance checks

### Safety Features
- Joint angle clamping
- Balance validation
- Emergency abort (ESC)
- One dance at a time
- Graceful failure handling

---

## 🔧 Configuration

Edit `test_controller/config.py` to customize:

```python
# Speed settings
BASE_LINEAR_SPEED_DEFAULT = 0.4    # m/s
BASE_ANGULAR_SPEED_DEFAULT = 0.6   # rad/s
BODY_SPEED_DEFAULT = 0.3

# Turbo multiplier
TURBO_MULTIPLIER = 1.5

# Dance parameters
SPECIAL_DANCE_CYCLES = 8
MOONWALK_GLIDE_DISTANCE = -0.2
```

### Motion Safety
```python
ENABLE_FOOT_CONTACT_PROTECTION = True      # Always enabled
ENABLE_EXTERNAL_COLLISION_PROTECTION = True
ENABLE_SMART_STIFFNESS = True
```

---

## 📹 Video Streaming

### Starting Video Server

The video server starts automatically. It serves:
- Pepper's camera feed: `http://YOUR_PC_IP:8080/pepper_feed`
- HoverCam feed: `http://YOUR_PC_IP:8080/hover_feed`
- Snapshots: `/pepper_snapshot`, `/hover_snapshot`
- Images: `/image/<filename>`

### Health Check
```bash
curl http://localhost:8080/health
```

### Troubleshooting
If camera feeds don't work:
1. Check PC IP address is detected correctly
2. Verify firewall allows port 8080
3. Check HoverCam is connected (USB)
4. Restart video server

---

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connection
ping 192.168.1.100

# Check if Pepper is on
# Check same network
# Verify IP address

# Try manual connection
python test_keyboard_control.py --ip 192.168.1.100
```

### GUI Won't Launch
```bash
# Check dependencies
python diagnostic_gui_check.py

# Test PyQt5
python gui_test_simple.py

# Install missing packages
pip install -r requirements_gui.txt
```

### Movement is Sluggish
1. Check `config.py` - smoothing factor should be low
2. Verify 50Hz update rate
3. Check network latency
4. Try turbo mode (X key)

### Dances Not Working
1. Check robot has full stiffness
2. Verify standing posture
3. Check battery level (>30%)
4. Look for error messages in console

### Tablet Display Issues
1. Check PC IP address in logs
2. Verify video server is running
3. Check image file paths
4. Try cycling modes (M key)

---

## 📁 Project Structure

```
pepper-control/
├── test_keyboard_control.py    # Main launcher
├── test_controller/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── input_handler.py        # Keyboard input
│   ├── video_server.py         # Flask video server
│   ├── controllers/
│   │   ├── pepper_connection.py
│   │   ├── base_controller.py
│   │   ├── body_controller.py
│   │   └── video_controller.py
│   ├── dances/
│   │   ├── base_dance.py
│   │   ├── wave_dance.py
│   │   ├── special_dance.py
│   │   ├── robot_dance.py
│   │   └── moonwalk_dance.py
│   ├── tablet/
│   │   ├── tablet_controller.py
│   │   ├── display_modes.py
│   │   └── html_templates.py
│   └── gui/
│       ├── main_window.py
│       ├── camera_panel.py
│       ├── control_panel.py
│       ├── image_manager.py
│       ├── file_handler.py
│       └── styles.py
├── assets/
│   └── tablet_images/
│       ├── standby.png
│       └── custom/
├── requirements.txt
├── requirements_gui.txt
└── README.md
```

---

## 🔬 Advanced Features

### Custom Dances
Create your own dance by extending `BaseDance`:

```python
from test_controller.dances import BaseDance

class MyDance(BaseDance):
    def perform(self):
        # Your dance logic
        self.safe_set_angles_smooth("RShoulderPitch", -1.0, 0.3)
        self.safe_wait(0.5)
        # ...
```

### Custom Tablet Displays
Create custom HTML templates in `html_templates.py`:

```python
def get_my_custom_html():
    return """
    <!DOCTYPE html>
    <html>
    <!-- Your HTML -->
    </html>
    """
```

---

## 📊 Performance Tips

1. **Optimize Network**: Use wired connection if possible
2. **Reduce Video Quality**: Lower FPS in config
3. **Disable Unused Features**: Comment out video server if not needed
4. **Battery Management**: Keep Pepper charged above 30%
5. **Collision Protection**: Keep enabled for safety

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create feature branch
3. Test thoroughly with real Pepper robot
4. Submit pull request

---

## 📄 License

[Your License Here]

---

## 🙏 Credits

- Built for VR Teleoperation Research
- Uses SoftBank Robotics NAOqi SDK
- PyQt5 for GUI
- Flask for video streaming

---

## 📞 Support

For issues or questions:
- Check troubleshooting section
- Run diagnostic scripts
- Check logs in console
- Review configuration

---

## 🗺️ Roadmap

### Phase 3 (Current)
- ✅ Smooth movement
- ✅ Perfect dances
- ✅ Tablet display system

### Phase 4 (Planned)
- ⏳ Voice commands
- ⏳ Audio streaming
- ⏳ Advanced NLP

### Phase 5 (Future)
- 📅 VR integration
- 📅 Cloud recording
- 📅 Multi-robot control

---

**Happy Controlling! 🤖✨**