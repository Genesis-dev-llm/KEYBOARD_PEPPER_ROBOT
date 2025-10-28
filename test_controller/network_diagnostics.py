"""
Network Diagnostics
Tests connection quality to Pepper.
"""

import time
import socket
import logging
import statistics

logger = logging.getLogger(__name__)

class NetworkDiagnostics:
    """Network quality checker."""
    
    @staticmethod
    def ping_test(ip, port=9559, count=10):
        """Test latency to Pepper."""
        print(f"\n📡 Testing connection to {ip}:{port}...")
        latencies = []
        
        for i in range(count):
            try:
                start = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((ip, port))
                latency = (time.time() - start) * 1000  # ms
                sock.close()
                latencies.append(latency)
                print(f"  Ping {i+1}/{count}: {latency:.1f}ms")
            except Exception as e:
                latencies.append(None)
                print(f"  Ping {i+1}/{count}: FAILED")
            
            time.sleep(0.1)
        
        # Calculate stats
        valid = [l for l in latencies if l is not None]
        
        if not valid:
            logger.error("❌ All pings failed - check connection!")
            return None
        
        result = {
            'success_rate': len(valid) / count * 100,
            'min': min(valid),
            'max': max(valid),
            'avg': statistics.mean(valid),
            'std': statistics.stdev(valid) if len(valid) > 1 else 0
        }
        
        print("\n📊 Results:")
        print(f"  Success Rate: {result['success_rate']:.1f}%")
        print(f"  Latency: {result['avg']:.1f}ms ± {result['std']:.1f}ms")
        print(f"  Range: {result['min']:.1f}ms - {result['max']:.1f}ms")
        
        # Warnings
        if result['avg'] > 50:
            logger.warning("⚠️  High latency detected (>50ms) - may affect responsiveness")
        if result['avg'] > 100:
            logger.error("❌ Very high latency (>100ms) - control will be sluggish")
        if result['success_rate'] < 90:
            logger.warning("⚠️  Packet loss detected - connection unstable")
        if result['success_rate'] < 70:
            logger.error("❌ High packet loss - connection very unstable")
        
        return result
    
    @staticmethod
    def quick_check(ip):
        """Quick connection check."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, 9559))
            sock.close()
            return True
        except:
            return False