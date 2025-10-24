# Assets Directory Structure - Phase 2

This folder contains images displayed on Pepper's tablet.

## 📁 Directory Structure

```
assets/
├── tablet_images/          # Preset images for dances/states
│   ├── standby.png        # Default idle screen (REQUIRED)
│   ├── wave.png           # During wave dance
│   ├── special.png        # During special dance
│   ├── robot.png          # During robot dance
│   ├── moonwalk.png       # During moonwalk
│   ├── moving_forward.png # When moving forward (optional)
│   ├── moving_back.png    # When moving backward (optional)
│   └── custom/            # User uploaded images (drag & drop)
│       ├── image1.png
│       └── image2.jpg
└── greetings/             # Greeting images (optional)
    └── hello.png
```

---

## 🎨 Image Requirements

### **Recommended Specifications:**
- **Format:** PNG (transparent background) or JPG
- **Resolution:** 1280x800 or 1920x1200
- **Aspect Ratio:** 16:10 (matches Pepper's tablet)
- **File Size:** < 2MB per image

### **Supported Formats:**
- ✅ PNG (.png)
- ✅ JPG/JPEG (.jpg, .jpeg)
- ✅ GIF (.gif) - static only, no animation

---

## 📋 Preset Image Names

These names are automatically mapped to robot actions:

| Filename | When Displayed | Priority |
|----------|----------------|----------|
| `standby.png` | Idle/Ready state | **HIGH** |
| `wave.png` | Wave dance (key 1) | Medium |
| `special.png` | Special dance (key 2) | Medium |
| `robot.png` | Robot dance (key 3) | Medium |
| `moonwalk.png` | Moonwalk dance (key 4) | Medium |
| `moving_forward.png` | Moving forward | Low |
| `moving_back.png` | Moving backward | Low |

---

## ⚠️ **IMPORTANT: Safe Fallbacks**

**If images are missing, the system will NOT crash!**

- Missing images → Text/emoji fallback automatically shown
- System checks for `.png` first, then `.jpg`
- Custom folder is created automatically on first run

---

## 🚀 Quick Start

### **Option 1: Use Preset Images**

1. Create folder: `assets/tablet_images/`
2. Add images with exact names above
3. Restart the controller
4. Images will automatically show during actions!

### **Option 2: Use Custom Images (GUI)**

1. Launch GUI mode: `python test_keyboard_control.py --gui`
2. Find "Image Manager" panel
3. Drag & drop any image
4. Click thumbnail to display on tablet

---

## 🎯 Recommended Workflow

### **For Dances:**
1. Find/create fun images for each dance
2. Name them exactly: `wave.png`, `special.png`, etc.
3. Place in `assets/tablet_images/`
4. Test by pressing dance keys (1-4)

### **For Custom Display:**
1. Use GUI's Image Manager
2. Drag & drop any image you want
3. Click to show on Pepper's tablet
4. Switch modes with M key or GUI

---

## 🖼️ Image Ideas

### **Standby (standby.png):**
- Pepper logo
- "Ready!" text
- Robot emoji 🤖
- Company logo

### **Wave (wave.png):**
- Waving hand emoji 👋
- "Hello!" text
- Friendly greeting graphic

### **Special Dance (special.png):**
- Dancing emoji 💃
- Party graphics 🎉
- Colorful patterns

### **Robot Dance (robot.png):**
- Robot emoji 🤖
- Matrix-style graphics
- Retro robot art

### **Moonwalk (moonwalk.png):**
- Moon emoji 🌙
- Michael Jackson silhouette
- "Smooth Criminal" reference

---

## 🔧 Troubleshooting

### **Images not showing?**

1. **Check filename spelling** - Must match exactly!
2. **Check file format** - PNG or JPG only
3. **Check file location** - Must be in `assets/tablet_images/`
4. **Restart controller** - Images loaded at startup

### **Images look distorted?**

- Use 16:10 aspect ratio (1280x800 or 1920x1200)
- Don't use images smaller than 640x400

### **Custom images not saving?**

- Check folder permissions
- Ensure `assets/tablet_images/custom/` exists
- Check disk space

---

## 📊 File Size Guidelines

| Image Type | Max Size | Notes |
|------------|----------|-------|
| Preset | 2MB | Loaded frequently |
| Custom | 5MB | Loaded once when selected |
| High-res | 10MB | May cause lag on tablet |

---

## 🎨 Where to Find Images

### **Free Stock Photos:**
- [Unsplash](https://unsplash.com)
- [Pexels](https://pexels.com)
- [Pixabay](https://pixabay.com)

### **Icons & Graphics:**
- [Flaticon](https://flaticon.com)
- [Noun Project](https://thenounproject.com)

### **AI Generated:**
- [DALL-E](https://openai.com/dall-e-2)
- [Midjourney](https://midjourney.com)
- [Stable Diffusion](https://stablediffusion.com)

---

## 💡 Pro Tips

1. **Use transparent PNGs** for professional look
2. **Add text overlays** in image editing software
3. **Keep file sizes small** for faster loading
4. **Test on Pepper first** before committing to design
5. **Create theme sets** (e.g., all purple, all retro, etc.)

---

## 🔄 Auto-Generated Folders

The system creates these automatically:
- `assets/`
- `assets/tablet_images/`
- `assets/tablet_images/custom/`
- `assets/greetings/`

**No need to create manually!**

---

## ✅ Checklist for Full Setup

- [ ] Create `assets/tablet_images/` folder
- [ ] Add `standby.png` (most important!)
- [ ] Add dance images (optional)
- [ ] Test in STATUS mode (press M to cycle)
- [ ] Try custom image upload in GUI
- [ ] Check camera feeds work (PEPPER_CAM, HOVERCAM)

---

## 📝 Example: Minimal Setup

```bash
mkdir -p assets/tablet_images/custom

# Add just one image (standby)
# Download or create standby.png
# Place in assets/tablet_images/

# Run controller
python test_keyboard_control.py 192.168.1.100
```

**That's it!** Everything else is optional.

---

Need help? Check the main README or ask in the project issues!