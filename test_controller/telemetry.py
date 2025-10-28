"""
Telemetry System
Records movement data for analysis.
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path

class TelemetryRecorder:
    """Records robot state for analysis."""
    
    def __init__(self, session_name=None):
        self.session_name = session_name or f"session_{int(time.time())}"
        self.log_dir = Path("telemetry") / self.session_name
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.movements = []
        self.dances = []
        self.errors = []
        
        self._recording = False
        self._lock = threading.Lock()
    
    def start_recording(self):
        """Start recording."""
        self._recording = True
        self.start_time = time.time()
        print(f"📊 Telemetry recording started: {self.session_name}")
    
    def stop_recording(self):
        """Stop and save recording."""
        self._recording = False
        self._save_all()
        print(f"✓ Telemetry saved to: {self.log_dir}")
    
    def log_movement(self, movement_type, velocity, duration):
        """Log a movement event."""
        if not self._recording:
            return
        
        with self._lock:
            self.movements.append({
                'timestamp': time.time() - self.start_time,
                'type': movement_type,
                'velocity': velocity,
                'duration': duration
            })
    
    def log_dance(self, dance_name, duration, success, abort_reason=None):
        """Log a dance execution."""
        if not self._recording:
            return
        
        with self._lock:
            self.dances.append({
                'timestamp': time.time() - self.start_time,
                'name': dance_name,
                'duration': duration,
                'success': success,
                'abort_reason': abort_reason
            })
    
    def log_error(self, error_type, message, context=None):
        """Log an error."""
        with self._lock:
            self.errors.append({
                'timestamp': time.time() - self.start_time,
                'type': error_type,
                'message': message,
                'context': context
            })
    
    def _save_all(self):
        """Save all telemetry data."""
        # Movements
        with open(self.log_dir / "movements.json", 'w') as f:
            json.dump(self.movements, f, indent=2)
        
        # Dances
        with open(self.log_dir / "dances.json", 'w') as f:
            json.dump(self.dances, f, indent=2)
        
        # Errors
        with open(self.log_dir / "errors.json", 'w') as f:
            json.dump(self.errors, f, indent=2)
        
        # Summary
        summary = {
            'session_name': self.session_name,
            'duration': time.time() - self.start_time,
            'total_movements': len(self.movements),
            'total_dances': len(self.dances),
            'total_errors': len(self.errors),
            'success_rate': sum(1 for d in self.dances if d['success']) / max(len(self.dances), 1)
        }
        
        with open(self.log_dir / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  Movements: {len(self.movements)}")
        print(f"  Dances: {len(self.dances)}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Duration: {summary['duration']:.1f}s")