# done

import psutil
import time

def get_system_health():
    return {
        "uptime_seconds": round(time.time() - psutil.boot_time(), 2),
        "cpu_usage_percent": psutil.cpu_percent(interval=0.5),
        "cpu_freq_mhz": psutil.cpu_freq()._asdict(),
        "cpu_times": psutil.cpu_times()._asdict(),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "used_percent": psutil.virtual_memory().percent
        }
    }
