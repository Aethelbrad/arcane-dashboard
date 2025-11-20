"""
System Monitoring Dashboard
A real-time system monitoring tool built with Streamlit
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import time
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitors.local_monitor import LocalMonitor
from utils.alerts import AlertManager

# Page configuration
st.set_page_config(
    page_title="System Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Souls aesthetic with muted pastels
st.markdown("""
<style>
    /* Color palette */
    :root {
        --bg-primary: #1a1a2e;
        --bg-secondary: #16213e;
        --bg-tertiary: #0f3460;
        --accent-purple: #533483;
        --critical-red: #e94560;
        --warning-orange: #f39c6b;
        --success-teal: #a8dadc;
        --text-beige: #c8b6a6;
        --text-muted: #8a8a8a;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-right: 1px solid var(--accent-purple);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: var(--text-beige);
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Headers */
    h1 {
        color: var(--text-beige) !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    h2, h3 {
        color: var(--success-teal) !important;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--accent-purple), var(--bg-tertiary));
        color: var(--text-beige);
        border: 1px solid var(--accent-purple);
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--bg-tertiary), var(--accent-purple));
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    /* Sliders */
    .stSlider [data-baseweb="slider"] {
        background: var(--bg-tertiary);
    }
    
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--success-teal);
        box-shadow: 0 2px 6px rgba(168, 218, 220, 0.4);
    }
    
    /* Dividers */
    hr {
        border-color: var(--accent-purple);
        opacity: 0.3;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
    }
    
    /* Text */
    p, label, span {
        color: var(--text-beige);
    }
    
    /* Checkbox */
    [data-testid="stCheckbox"] label {
        color: var(--text-beige) !important;
    }
    
    /* Make plots blend better */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Load configuration
@st.cache_resource
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize session state
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []
    st.session_state.start_time = datetime.now()

if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager(config['thresholds'])

if 'monitor' not in st.session_state:
    st.session_state.monitor = LocalMonitor()

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Refresh settings
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider(
        "Refresh interval (seconds)", 
        min_value=1, 
        max_value=30, 
        value=config['settings']['refresh_interval']
    )
    
    st.divider()
    
    # Threshold configuration
    st.subheader("Alert Thresholds")
    
    cpu_warning = st.slider("CPU Warning (%)", 0, 100, config['thresholds']['cpu_warning'])
    cpu_critical = st.slider("CPU Critical (%)", 0, 100, config['thresholds']['cpu_critical'])
    
    mem_warning = st.slider("Memory Warning (%)", 0, 100, config['thresholds']['memory_warning'])
    mem_critical = st.slider("Memory Critical (%)", 0, 100, config['thresholds']['memory_critical'])
    
    disk_warning = st.slider("Disk Warning (%)", 0, 100, config['thresholds']['disk_warning'])
    disk_critical = st.slider("Disk Critical (%)", 0, 100, config['thresholds']['disk_critical'])
    
    # Update thresholds
    st.session_state.alert_manager.thresholds = {
        'cpu_warning': cpu_warning,
        'cpu_critical': cpu_critical,
        'memory_warning': mem_warning,
        'memory_critical': mem_critical,
        'disk_warning': disk_warning,
        'disk_critical': disk_critical
    }
    
    st.divider()
    
    if st.button("Clear History"):
        st.session_state.metrics_history = []
        st.session_state.alert_manager.clear_history()
        st.rerun()

# Main content
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>⚔️ SYSTEM MONITORING DASHBOARD ⚔️</h1>", unsafe_allow_html=True)

# Get current metrics
monitor = st.session_state.monitor
current_metrics = monitor.get_all_metrics()

# Add to history
st.session_state.metrics_history.append(current_metrics)

# Keep only recent history
max_points = config['settings']['history_points']
if len(st.session_state.metrics_history) > max_points:
    st.session_state.metrics_history = st.session_state.metrics_history[-max_points:]

# Check for alerts
alerts = st.session_state.alert_manager.check_metrics(current_metrics)

# Display alerts
if alerts:
    for alert in alerts:
        if alert.severity == 'critical':
            st.error(f"🚨 {alert.message}")
        else:
            st.warning(f"⚠️ {alert.message}")

# System info
sys_info = monitor.get_system_info()
uptime = datetime.now() - sys_info['boot_time']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "System", 
        sys_info['hostname'],
        delta=None
    )

with col2:
    st.metric(
        "CPU Cores", 
        sys_info['cpu_count'],
        delta=None
    )

with col3:
    st.metric(
        "Uptime", 
        f"{uptime.days}d {uptime.seconds//3600}h",
        delta=None
    )

with col4:
    st.metric(
        "Monitoring Duration", 
        f"{(datetime.now() - st.session_state.start_time).seconds}s",
        delta=None
    )

st.divider()

# Current status cards
st.subheader("Current Status")

col1, col2, col3 = st.columns(3)

with col1:
    cpu_color = "🟢" if current_metrics['cpu_percent'] < cpu_warning else ("🟡" if current_metrics['cpu_percent'] < cpu_critical else "🔴")
    st.metric(
        f"{cpu_color} CPU Usage",
        f"{current_metrics['cpu_percent']:.1f}%",
        delta=None
    )

with col2:
    mem_pct = current_metrics['memory']['percent']
    mem_color = "🟢" if mem_pct < mem_warning else ("🟡" if mem_pct < mem_critical else "🔴")
    st.metric(
        f"{mem_color} Memory Usage",
        f"{mem_pct:.1f}%",
        delta=f"{current_metrics['memory']['used_gb']:.1f}/{current_metrics['memory']['total_gb']:.1f} GB"
    )

with col3:
    disk_pct = current_metrics['disk']['percent']
    disk_color = "🟢" if disk_pct < disk_warning else ("🟡" if disk_pct < disk_critical else "🔴")
    st.metric(
        f"{disk_color} Disk Usage",
        f"{disk_pct:.1f}%",
        delta=f"{current_metrics['disk']['used_gb']:.1f}/{current_metrics['disk']['total_gb']:.1f} GB"
    )

st.divider()

# Historical charts
if len(st.session_state.metrics_history) > 1:
    st.subheader("Historical Metrics")
    
    history = st.session_state.metrics_history
    timestamps = [m['timestamp'] for m in history]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network I/O'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # CPU chart
    cpu_data = [m['cpu_percent'] for m in history]
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=cpu_data, name="CPU %", 
            line=dict(color='#a8dadc', width=3),
            fill='tozeroy',
            fillcolor='rgba(168, 218, 220, 0.2)'
        ),
        row=1, col=1
    )
    fig.add_hline(y=cpu_warning, line_dash="dash", line_color="#f39c6b", line_width=2, row=1, col=1)
    fig.add_hline(y=cpu_critical, line_dash="dash", line_color="#e94560", line_width=2, row=1, col=1)
    
    # Memory chart
    mem_data = [m['memory']['percent'] for m in history]
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=mem_data, name="Memory %", 
            line=dict(color='#533483', width=3),
            fill='tozeroy',
            fillcolor='rgba(83, 52, 131, 0.2)'
        ),
        row=1, col=2
    )
    fig.add_hline(y=mem_warning, line_dash="dash", line_color="#f39c6b", line_width=2, row=1, col=2)
    fig.add_hline(y=mem_critical, line_dash="dash", line_color="#e94560", line_width=2, row=1, col=2)
    
    # Disk chart
    disk_data = [m['disk']['percent'] for m in history]
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=disk_data, name="Disk %", 
            line=dict(color='#c8b6a6', width=3),
            fill='tozeroy',
            fillcolor='rgba(200, 182, 166, 0.2)'
        ),
        row=2, col=1
    )
    fig.add_hline(y=disk_warning, line_dash="dash", line_color="#f39c6b", line_width=2, row=2, col=1)
    fig.add_hline(y=disk_critical, line_dash="dash", line_color="#e94560", line_width=2, row=2, col=1)
    
    # Network chart
    net_sent = [m['network']['bytes_sent_mb'] for m in history]
    net_recv = [m['network']['bytes_recv_mb'] for m in history]
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=net_sent, name="Sent (MB)", 
            line=dict(color='#e94560', width=2.5)
        ),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=net_recv, name="Received (MB)", 
            line=dict(color='#a8dadc', width=2.5)
        ),
        row=2, col=2, secondary_y=True
    )
    
    # Update layout
    fig.update_xaxes(title_text="Time", row=2, col=1, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    fig.update_xaxes(title_text="Time", row=2, col=2, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    fig.update_yaxes(title_text="Percentage", row=1, col=1, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    fig.update_yaxes(title_text="Percentage", row=1, col=2, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    fig.update_yaxes(title_text="Percentage", row=2, col=1, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    fig.update_yaxes(title_text="MB", row=2, col=2, gridcolor='rgba(83, 52, 131, 0.2)', color='#c8b6a6')
    
    # Update all subplot titles
    for annotation in fig.layout.annotations:
        annotation.font.color = '#a8dadc'
        annotation.font.size = 14
    
    fig.update_layout(
        height=600, 
        showlegend=True,
        plot_bgcolor='rgba(22, 33, 62, 0.4)',
        paper_bgcolor='rgba(26, 26, 46, 0)',
        font=dict(color='#c8b6a6', family='system-ui'),
        legend=dict(
            bgcolor='rgba(22, 33, 62, 0.6)',
            bordercolor='#533483',
            borderwidth=1,
            font=dict(color='#c8b6a6')
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Recent alerts
st.divider()
st.subheader("Recent Alerts")

recent_alerts = st.session_state.alert_manager.get_recent_alerts(count=10)
if recent_alerts:
    for alert in reversed(recent_alerts):
        alert_time = alert.timestamp.strftime("%H:%M:%S")
        if alert.severity == 'critical':
            st.error(f"🚨 [{alert_time}] {alert.message}")
        else:
            st.warning(f"⚠️ [{alert_time}] {alert.message}")
else:
    st.info("No alerts generated yet. System is running normally.")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()