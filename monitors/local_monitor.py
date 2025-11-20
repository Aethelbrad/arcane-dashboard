"""
Local System Monitor
Collects system metrics from the local machine using psutil
"""

import psutil
from datetime import datetime


class LocalMonitor:
    """Monitor local system metrics"""
    
    def __init__(self):
        self.name = "Local System"
        
    def get_cpu_percent(self, interval=1):
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=interval)
    
    def get_memory_info(self):
        """Get memory usage information"""
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'used_gb': mem.used / (1024**3),
            'total_gb': mem.total / (1024**3),
            'available_gb': mem.available / (1024**3)
        }
    
    def get_disk_info(self):
        """Get disk usage information for root partition"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'used_gb': disk.used / (1024**3),
            'total_gb': disk.total / (1024**3),
            'free_gb': disk.free / (1024**3)
        }
    
    def get_network_io(self):
        """Get network I/O statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent_mb': net.bytes_sent / (1024**2),
            'bytes_recv_mb': net.bytes_recv / (1024**2),
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    def get_all_metrics(self):
        """Get all system metrics at once"""
        timestamp = datetime.now()
        
        return {
            'timestamp': timestamp,
            'cpu_percent': self.get_cpu_percent(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_io(),
            'system_name': self.name
        }
    
    def get_system_info(self):
        """Get static system information"""
        return {
            'hostname': psutil.os.uname().nodename,
            'system': psutil.os.uname().sysname,
            'cpu_count': psutil.cpu_count(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time())
        }
