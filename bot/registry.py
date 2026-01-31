from bot.config import IP_MONITORING
from bot.monitor import PingMonitor

monitors = [
    PingMonitor(name, cfg["host"])
    for name, cfg in IP_MONITORING.items()
]
