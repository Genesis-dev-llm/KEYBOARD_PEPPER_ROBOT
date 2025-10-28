"""
Movement Recorder
Record and replay movement sequences.
"""

import json
import time
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MovementRecorder:
    """Records joint trajectories for playback."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        self.recording = []
        self.is_recording = False
        self.start_time = None
        self._record_thread = None
        
        # Create recordings directory
        self.recordings_dir = Path("recordings")
        self.recordings_dir.mkdir(exist_ok=True)
    
    def start_recording(self):
        """Start recording joint angles."""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        self.recording = []
        self.is_recording = True
        self.start_time = time.time()
        
        logger.info("🔴 Recording started")
        
        def record_loop():
            while self.is_recording:
                try:
                    timestamp = time.time() - self.start_time
                    
                    # Get all body joint angles
                    joint_names = self.motion.getBodyNames("Body")
                    angles = self.motion.getAngles(joint_names, True)
                    
                    self.recording.append({
                        'time': timestamp,
                        'joints': joint_names,
                        'angles': angles
                    })
                    
                    time.sleep(0.05)  # 20Hz recording
                    
                except Exception as e:
                    logger.error(f"Recording error: {e}")
                    break
        
        self._record_thread = threading.Thread(target=record_loop, daemon=True)
        self._record_thread.start()
    
    def stop_recording(self):
        """Stop recording."""
        if not self.is_recording:
            return []
        
        self.is_recording = False
        
        if self._record_thread:
            self._record_thread.join(timeout=2)
        
        duration = self.recording[-1]['time'] if self.recording else 0
        logger.info(f"⏹️  Recording stopped: {len(self.recording)} frames, {duration:.1f}s")
        
        return self.recording.copy()
    
    def save_recording(self, name=None):
        """Save recording to file."""
        if not self.recording:
            logger.warning("No recording to save")
            return None
        
        if name is None:
            name = f"recording_{int(time.time())}"
        
        filename = self.recordings_dir / f"{name}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'name': name,
                'duration': self.recording[-1]['time'],
                'frame_count': len(self.recording),
                'fps': len(self.recording) / self.recording[-1]['time'],
                'frames': self.recording
            }, f, indent=2)
        
        logger.info(f"✓ Recording saved: {filename}")
        return filename
    
    def load_recording(self, filename):
        """Load recording from file."""
        filepath = Path(filename)
        
        if not filepath.exists():
            # Try in recordings directory
            filepath = self.recordings_dir / filename
            if not filepath.suffix:
                filepath = filepath.with_suffix('.json')
        
        if not filepath.exists():
            logger.error(f"Recording not found: {filename}")
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        logger.info(f"✓ Loaded: {data['name']} ({data['frame_count']} frames, {data['duration']:.1f}s)")
        return data['frames']
    
    def playback(self, recording=None, speed=1.0):
        """Play back recorded movement."""
        if recording is None:
            recording = self.recording
        
        if not recording:
            logger.warning("No recording to play")
            return
        
        logger.info(f"▶️  Playing back recording (speed: {speed}x)...")
        
        try:
            start_time = time.time()
            
            for i, frame in enumerate(recording):
                # Wait until correct time
                target_time = frame['time'] / speed
                elapsed = time.time() - start_time
                wait_time = target_time - elapsed
                
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Set joint angles
                self.motion.setAngles(frame['joints'], frame['angles'], 0.5)
                
                # Progress
                if i % 20 == 0:
                    progress = (i / len(recording)) * 100
                    logger.debug(f"Playback: {progress:.0f}%")
            
            logger.info("✓ Playback complete")
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
    
    def list_recordings(self):
        """List all saved recordings."""
        recordings = list(self.recordings_dir.glob("*.json"))
        
        if not recordings:
            print("No recordings found")
            return []
        
        print("\n📼 Available Recordings:")
        for rec in recordings:
            try:
                with open(rec, 'r') as f:
                    data = json.load(f)
                print(f"  • {rec.stem}: {data['duration']:.1f}s, {data['frame_count']} frames")
            except:
                print(f"  • {rec.stem}: (corrupted)")
        
        return [r.stem for r in recordings]