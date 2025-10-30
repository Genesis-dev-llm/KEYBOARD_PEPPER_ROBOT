"""
Professional HTML/CSS Templates for Pepper's Tablet - ENHANCED
High-quality, modern UI designs with better visuals and animations.

IMPROVEMENTS:
- Smoother animations
- Better color schemes
- More responsive layouts
- Fallback handling
- Better error messages
"""

def get_status_display_html(action, action_detail, battery, mode, image_url=None):
    """
    Generate HTML for status + action display.
    Enhanced with better visuals and animations.
    """
    
    # Battery color based on level
    if battery >= 60:
        battery_color = "#10b981"  # Green
        battery_gradient = "linear-gradient(90deg, #10b981 0%, #34d399 100%)"
    elif battery >= 30:
        battery_color = "#f59e0b"  # Yellow/Orange
        battery_gradient = "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)"
    else:
        battery_color = "#ef4444"  # Red
        battery_gradient = "linear-gradient(90deg, #ef4444 0%, #dc2626 100%)"
    
    # Mode text and color
    if mode:
        mode_text = "CONTINUOUS"
        mode_color = "#10b981"
    else:
        mode_text = "INCREMENTAL"
        mode_color = "#3b82f6"
    
    # Action icon mapping (enhanced emojis)
    action_icons = {
        "Ready": "🤖",
        "Standby": "⏸️",
        "Moving Forward": "⬆️",
        "Moving Backward": "⬇️",
        "Strafing Left": "⬅️",
        "Strafing Right": "➡️",
        "Rotating Left": "↶",
        "Rotating Right": "↷",
        "Wave": "👋",
        "Special Dance": "💃",
        "Special": "💃",
        "Robot Dance": "🤖",
        "Robot": "🤖",
        "Moonwalk": "🌙",
        "Looking Around": "👀",
        "Moving Arms": "💪",
        "Hello": "👋",
        "Emergency Stop": "🚨",
        "Stopped": "⏹️",
        "Low Battery": "🔋",
        "Dancing": "🕺"
    }
    
    icon = action_icons.get(action, "🤖")
    
    # Content: image or icon/text
    if image_url:
        content = f'''
        <div class="image-container">
            <img src="{image_url}" alt="{action}" class="status-image" onerror="this.style.display='none'; document.getElementById('fallback-icon').style.display='flex';">
        </div>
        <div id="fallback-icon" style="display:none; flex-direction: column; align-items: center;">
            <div class="action-icon">{icon}</div>
        </div>
        <div class="action-text">{action.upper()}</div>
        <div class="action-detail">{action_detail}</div>
        '''
    else:
        content = f'''
        <div class="action-icon">{icon}</div>
        <div class="action-text">{action.upper()}</div>
        <div class="action-detail">{action_detail}</div>
        '''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                position: relative;
            }}
            
            /* Animated background gradient */
            body::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.8) 0%, 
                    rgba(118, 75, 162, 0.8) 100%);
                animation: gradientShift 10s ease infinite;
                z-index: 0;
            }}
            
            @keyframes gradientShift {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.8; }}
            }}
            
            .header {{
                position: absolute;
                top: 20px;
                left: 20px;
                font-size: 28px;
                font-weight: 700;
                opacity: 0.95;
                z-index: 10;
                text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
            }}
            
            .action-card {{
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(30px);
                -webkit-backdrop-filter: blur(30px);
                border-radius: 40px;
                padding: 60px 80px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: fadeInUp 0.6s ease-out;
                max-width: 90%;
                z-index: 5;
                position: relative;
            }}
            
            @keyframes fadeInUp {{
                from {{ 
                    opacity: 0; 
                    transform: translateY(30px);
                }}
                to {{ 
                    opacity: 1; 
                    transform: translateY(0);
                }}
            }}
            
            .image-container {{
                margin-bottom: 25px;
                animation: slideIn 0.8s ease-out;
            }}
            
            @keyframes slideIn {{
                from {{ 
                    opacity: 0;
                    transform: scale(0.8);
                }}
                to {{ 
                    opacity: 1;
                    transform: scale(1);
                }}
            }}
            
            .status-image {{
                max-width: 450px;
                max-height: 450px;
                border-radius: 25px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
                animation: pulse 2s ease-in-out infinite;
            }}
            
            .action-icon {{
                font-size: 140px;
                margin-bottom: 25px;
                animation: bounce 2s ease-in-out infinite;
                filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .action-text {{
                font-size: 64px;
                font-weight: 800;
                margin-bottom: 18px;
                text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
                letter-spacing: 1px;
            }}
            
            .action-detail {{
                font-size: 36px;
                opacity: 0.95;
                font-weight: 400;
                line-height: 1.4;
            }}
            
            .status-bar {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                padding: 25px 35px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 26px;
                z-index: 10;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .battery {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .battery-icon {{
                font-size: 32px;
                animation: batteryPulse 2s ease-in-out infinite;
            }}
            
            @keyframes batteryPulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .battery-bar {{
                width: 160px;
                height: 24px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                overflow: hidden;
                border: 2px solid rgba(255, 255, 255, 0.3);
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            .battery-fill {{
                height: 100%;
                background: {battery_gradient};
                width: {battery}%;
                transition: width 0.5s ease;
                box-shadow: 0 0 10px {battery_color};
            }}
            
            .battery-text {{
                font-weight: 700;
                min-width: 70px;
                text-align: right;
            }}
            
            .mode-badge {{
                background: rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 22px;
                font-weight: 700;
                border: 2px solid {mode_color};
                color: {mode_color};
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="header">🤖 PEPPER</div>
        
        <div class="action-card">
            {content}
        </div>
        
        <div class="status-bar">
            <div class="battery">
                <span class="battery-icon">🔋</span>
                <div class="battery-bar">
                    <div class="battery-fill"></div>
                </div>
                <span class="battery-text">{battery}%</span>
            </div>
            <div class="mode-badge">{mode_text}</div>
        </div>
    </body>
    </html>
    """
    
    return html


def get_custom_image_html(image_url, caption=""):
    """Generate HTML for custom static image display."""
    
    caption_html = f'<div class="caption">{caption}</div>' if caption else ''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: #000;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }}
            
            .image-container {{
                max-width: 95%;
                max-height: 90vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 25px;
                animation: fadeIn 0.6s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: scale(0.95); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
            
            .main-image {{
                max-width: 100%;
                max-height: 80vh;
                object-fit: contain;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(255, 255, 255, 0.15);
            }}
            
            .caption {{
                font-size: 32px;
                font-weight: 700;
                text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7);
                animation: slideUp 0.8s ease-out 0.3s both;
            }}
            
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="image-container">
            <img src="{image_url}" alt="Custom Image" class="main-image" 
                 onerror="this.style.display='none'; document.body.innerHTML='<div style=\\'text-align:center; padding:50px;\\'><h1>❌</h1><p>Image not found</p></div>';">
            {caption_html}
        </div>
    </body>
    </html>
    """
    
    return html


def get_camera_feed_html(camera_url, camera_name="Camera"):
    """Generate HTML for live camera feed display."""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: #000;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 22px 35px;
                font-size: 32px;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 18px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                z-index: 10;
            }}
            
            .camera-container {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 25px;
                background: #1a1a1a;
                position: relative;
            }}
            
            .camera-feed {{
                max-width: 100%;
                max-height: 100%;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
                border: 3px solid rgba(255, 255, 255, 0.15);
            }}
            
            .live-indicator {{
                position: absolute;
                top: 90px;
                left: 35px;
                background: rgba(239, 68, 68, 0.95);
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 24px;
                font-weight: 800;
                animation: blink 2s ease-in-out infinite;
                box-shadow: 0 4px 16px rgba(239, 68, 68, 0.5);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
            
            .live-dot {{
                width: 12px;
                height: 12px;
                background: white;
                border-radius: 50%;
                animation: pulse 1s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.3); }}
            }}
            
            .error-message {{
                text-align: center;
                padding: 50px;
                font-size: 24px;
                color: #ef4444;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            📹 {camera_name.upper()}
        </div>
        
        <div class="camera-container">
            <img class="camera-feed" src="{camera_url}" alt="Live Feed"
                 onerror="this.style.display='none'; document.querySelector('.camera-container').innerHTML='<div class=\\'error-message\\'><h2>❌ Connection Lost</h2><p>Camera feed unavailable</p></div>';">
        </div>
        
        <div class="live-indicator">
            <div class="live-dot"></div>
            LIVE
        </div>
    </body>
    </html>
    """
    
    return html


def get_blank_screen_html():
    """Generate HTML for blank screen."""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: #000;
                height: 100vh;
                overflow: hidden;
            }
        </style>
    </head>
    <body>
    </body>
    </html>
    """
    
    return html


def get_error_html(error_message):
    """Generate HTML for error display."""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }}
            
            .error-container {{
                text-align: center;
                padding: 70px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(15px);
                border-radius: 35px;
                max-width: 85%;
                animation: shake 0.5s ease-out;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }}
            
            @keyframes shake {{
                0%, 100% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-10px); }}
                75% {{ transform: translateX(10px); }}
            }}
            
            .error-icon {{
                font-size: 120px;
                margin-bottom: 25px;
                animation: bounce 1s ease-in-out infinite;
            }}
            
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-15px); }}
            }}
            
            .error-title {{
                font-size: 56px;
                font-weight: 800;
                margin-bottom: 25px;
                text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
            }}
            
            .error-message {{
                font-size: 32px;
                opacity: 0.95;
                line-height: 1.5;
                font-weight: 400;
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-icon">⚠️</div>
            <div class="error-title">ERROR</div>
            <div class="error-message">{error_message}</div>
        </div>
    </body>
    </html>
    """
    
    return html