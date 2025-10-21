"""
Standalone Video Stream Tester
Test Pepper's camera feed directly in a window without Unity/VR
"""

import cv2
import numpy as np
import urllib.request
import argparse
import sys
import time

def test_video_stream(server_ip, port=8080):
    """
    Test video stream from Pepper by displaying it in an OpenCV window.
    
    Args:
        server_ip: IP address of the PC running the Python server
        port: Video stream port (default 8080)
    """
    
    stream_url = f"http://{server_ip}:{port}/video_feed"
    health_url = f"http://{server_ip}:{port}/health"
    
    print("=" * 70)
    print("🎥 PEPPER VIDEO STREAM TESTER")
    print("=" * 70)
    print(f"\nStream URL: {stream_url}")
    print(f"Health URL: {health_url}")
    print()
    
    # First, check if the server is running
    print("Checking if video server is accessible...")
    try:
        response = urllib.request.urlopen(health_url, timeout=5)
        health_data = response.read().decode('utf-8')
        print(f"✓ Server is running: {health_data}")
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        print()
        print("SOLUTION:")
        print(f"  1. Make sure Python server is running:")
        print(f"     python Python/main.py --ip <PEPPER_IP>")
        print()
        print(f"  2. Wait for this message in the logs:")
        print(f"     'Starting video streaming server on http://0.0.0.0:{port}/video_feed'")
        print()
        print(f"  3. Then run this tester again:")
        print(f"     python test_video_stream.py {server_ip}")
        return False
    
    print()
    print("Connecting to video stream...")
    print("Press 'Q' or ESC to quit")
    print("Press 'S' to save a screenshot")
    print()
    
    try:
        # Open the stream
        stream = urllib.request.urlopen(stream_url, timeout=10)
        bytes_data = b''
        frame_count = 0
        start_time = time.time()
        
        print("✓ Video stream connected!")
        print()
        
        while True:
            # Read stream data
            bytes_data += stream.read(1024)
            
            # Find JPEG frame boundaries
            a = bytes_data.find(b'\xff\xd8')  # JPEG start
            b = bytes_data.find(b'\xff\xd9')  # JPEG end
            
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                
                # Decode JPEG to image
                frame = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8),
                    cv2.IMREAD_COLOR
                )
                
                if frame is not None:
                    frame_count += 1
                    
                    # Calculate FPS
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    # Add FPS overlay
                    cv2.putText(
                        frame, 
                        f"FPS: {fps:.1f} | Frame: {frame_count}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    
                    # Display frame
                    cv2.imshow("Pepper Camera Feed (Press Q to quit, S to save)", frame)
                    
                    # Handle key presses
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q') or key == ord('Q') or key == 27:  # Q or ESC
                        print("\nClosing video stream...")
                        break
                    elif key == ord('s') or key == ord('S'):
                        # Save screenshot
                        filename = f"pepper_screenshot_{int(time.time())}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"✓ Screenshot saved: {filename}")
                    
                    # Check if window was closed
                    if cv2.getWindowProperty("Pepper Camera Feed (Press Q to quit, S to save)", cv2.WND_PROP_VISIBLE) < 1:
                        break
        
        print(f"\n✓ Video test complete!")
        print(f"  Total frames: {frame_count}")
        print(f"  Average FPS: {fps:.1f}")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        cv2.destroyAllWindows()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test Pepper's video stream in a window",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_video_stream.py 192.168.1.129
  python test_video_stream.py --ip 192.168.1.129 --port 8080

Prerequisites:
  1. Python server must be running:
     python Python/main.py --ip <PEPPER_IP>
  
  2. Wait for video server to start (check logs)
  
  3. Then run this tester
        """
    )
    
    parser.add_argument(
        'ip',
        nargs='?',
        type=str,
        help="IP address of the PC running the Python server (YOUR PC, not Pepper's!)"
    )
    
    parser.add_argument(
        '--ip',
        dest='ip_flag',
        type=str,
        help="IP address (alternative syntax)"
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help="Video streaming port (default: 8080)"
    )
    
    args = parser.parse_args()
    
    # Get IP
    server_ip = args.ip or args.ip_flag
    
    if not server_ip:
        print("Error: Server IP required!")
        print()
        print("Usage:")
        print("  python test_video_stream.py 192.168.1.129")
        print()
        print("This is YOUR PC's IP (where Python server is running),")
        print("NOT Pepper's IP!")
        sys.exit(1)
    
    # Run test
    success = test_video_stream(server_ip, args.port)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


# ============================================================================
# ALTERNATIVE: Simple Browser Test
# ============================================================================

"""
You can also test the video feed directly in a web browser:

1. Start the Python server:
   python Python/main.py --ip <PEPPER_IP>

2. Open your browser and go to:
   http://YOUR_PC_IP:8080/video_feed

   For example:
   http://192.168.1.129:8080/video_feed

3. You should see the live camera feed from Pepper!

To check if the server is running:
   http://YOUR_PC_IP:8080/health

This should show: {"status": "ok", "camera_id": 0}
"""