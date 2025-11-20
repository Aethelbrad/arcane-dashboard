"""
Alert System
Checks metrics against thresholds and generates alerts
"""

from datetime import datetime
from typing import List, Dict


class Alert:
    def __init__(self, severity, metric, value, threshold, message):
        self.severity = severity  # 'warning' or 'critical'
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.message = message
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"[{self.severity.upper()}] {self.message}"


class AlertManager:
    def __init__(self, thresholds):
        self.thresholds = thresholds
        self.alert_history = []
        self.max_history = 100
    
    def check_metrics(self, metrics: Dict) -> List[Alert]:
        """Check metrics against thresholds and return alerts"""
        alerts = []
        
        # Check CPU
        cpu = metrics.get('cpu_percent', 0)
        if cpu >= self.thresholds['cpu_critical']:
            alert = Alert(
                'critical', 'CPU', cpu, self.thresholds['cpu_critical'],
                f"CPU usage critical: {cpu:.1f}%"
            )
            alerts.append(alert)
        elif cpu >= self.thresholds['cpu_warning']:
            alert = Alert(
                'warning', 'CPU', cpu, self.thresholds['cpu_warning'],
                f"CPU usage high: {cpu:.1f}%"
            )
            alerts.append(alert)
        
        # Check Memory
        memory = metrics.get('memory', {}).get('percent', 0)
        if memory >= self.thresholds['memory_critical']:
            alert = Alert(
                'critical', 'Memory', memory, self.thresholds['memory_critical'],
                f"Memory usage critical: {memory:.1f}%"
            )
            alerts.append(alert)
        elif memory >= self.thresholds['memory_warning']:
            alert = Alert(
                'warning', 'Memory', memory, self.thresholds['memory_warning'],
                f"Memory usage high: {memory:.1f}%"
            )
            alerts.append(alert)
        
        # Check Disk
        disk = metrics.get('disk', {}).get('percent', 0)
        if disk >= self.thresholds['disk_critical']:
            alert = Alert(
                'critical', 'Disk', disk, self.thresholds['disk_critical'],
                f"Disk usage critical: {disk:.1f}%"
            )
            alerts.append(alert)
        elif disk >= self.thresholds['disk_warning']:
            alert = Alert(
                'warning', 'Disk', disk, self.thresholds['disk_warning'],
                f"Disk usage high: {disk:.1f}%"
            )
            alerts.append(alert)
        
        # Add to history
        for alert in alerts:
            self.alert_history.append(alert)
        
        # Trim history if needed
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        return alerts
    
    def get_recent_alerts(self, count=10):
        return self.alert_history[-count:]
    
    def clear_history(self):
        self.alert_history = []
