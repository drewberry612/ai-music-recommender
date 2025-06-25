import logging
import os
import asyncio
import json
from health import get_system_health

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")

        # Console handler, remove after testing
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler
        fh = logging.FileHandler(os.path.join(LOG_DIR, filename))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

query_logger = setup_logger("query_logger", "query.log")
health_logger = setup_logger("health_logger", "health.log")

async def periodic_health_logger(interval_seconds: int = 300):
    while True:
        try:
            health_data = get_system_health()
            health_logger.info(f"System health: {json.dumps(health_data)}")
        except Exception as e:
            health_logger.error(f"Error while logging system health: {e}")
        await asyncio.sleep(interval_seconds)
