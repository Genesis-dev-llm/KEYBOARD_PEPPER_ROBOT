"""
Professional HTML/CSS Templates for Pepper's Tablet - Phase 2
High-quality, modern UI designs with image support.
"""

def get_status_display_html(action, action_detail, battery, mode, image_url=None):
    """
    Generate HTML for status + action display.
    Can show preset image or fallback to icon/text.
    """
    
    # Battery color based on level
    if battery >= 60:
        battery_color = "#4ade80"  # Green
    elif battery >= 30:
        battery_color = "#fbbf24"  # Yellow
    else:
        battery_color = "#f87171"  # Red
    
    # Mode text
    mode_text = "CONTINUOUS" if mode else "INCREMENTAL"
    
    # Action icon mapping (fallback if no image)
    action_icons = {
        "Ready": "🤖",
        "Standby": "😴",
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
        "Low Battery": "🔋"
    }
    
    icon = action_icons.get(action, "🤖")
    
    # Content: image or icon/text
    if image_url:
        content = f'''
        <div class="image-container">
            <img src="{image_url}" alt="{action}" class="status-image">
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
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }}
            
            .header {{
                position: absolute;
                top: 20px;
                left: 20px;
                font-size: 24px;
                font-weight: 600;
                opacity: 0.9;
            }}
            
            .action-card {{
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 60px 80px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: fadeIn 0.5s ease-in-out;
                max-width: 90%;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .image-container {{
                margin-bottom: 20px;
            }}
            
            .status-image {{
                max-width: 400px;
                max-height: 400px;
                border-radius: 20px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                animation: pulse 2s infinite;
            }}
            
            .action-icon {{
                font-size: 120px;
                margin-bottom: 20px;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
            }}
            
            .action-text {{
                font-size: 56px;
                font-weight: bold;
                margin-bottom: 15px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .action-detail {{
                font-size: 32px;
                opacity: 0.9;
                font-weight: 300;
            }}
            
            .status-bar {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 24px;
            }}
            
            .battery {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .battery-bar {{
                width: 150px;
                height: 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .battery-fill {{
                height: 100%;
                background: {battery_color};
                width: {battery}%;
                transition: width 0.3s ease;
            }}
            
            .mode-badge {{
                background: rgba(255, 255, 255, 0.2);
                padding: 8px 16px;
                border-radius: 12px;
                font-size: 20px;
                font-weight: 600;
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
                <span>🔋 {battery}%</span>
                <div class="battery-bar">
                    <div class="battery-fill"></div>
                </div>
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
                gap: 20px;
            }}
            
            .main-image {{
                max-width: 100%;
                max-height: 80vh;
                object-fit: contain;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1);
            }}
            
            .caption {{
                font-size: 28px;
                font-weight: 600;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="image-container">
            <img src="{image_url}" alt="Custom Image" class="main-image">
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
                padding: 20px 30px;
                font-size: 28px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            
            .camera-container {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                background: #1a1a1a;
            }}
            
            .camera-feed {{
                max-width: 100%;
                max-height: 100%;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
            
            .live-indicator {{
                position: absolute;
                top: 80px;
                left: 30px;
                background: rgba(239, 68, 68, 0.9);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 20px;
                font-weight: 700;
                animation: blink 2s infinite;
            }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            📹 {camera_name.upper()}
        </div>
        
        <div class="camera-container">
            <img class="camera-feed" src="{camera_url}" alt="Live Feed">
        </div>
        
        <div class="live-indicator">● LIVE</div>
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
                padding: 60px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 30px;
                max-width: 80%;
            }}
            
            .error-icon {{
                font-size: 100px;
                margin-bottom: 20px;
            }}
            
            .error-title {{
                font-size: 48px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            
            .error-message {{
                font-size: 28px;
                opacity: 0.9;
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