import psutil
import schedule
from .storage import get_logger


def run_samplers():
    logger = get_logger()

    def collect():
        metrics = {}

        memory = psutil.virtual_memory()
        metrics["memory"] = {"used": memory.used, "available": memory.available}

        total_cpu = psutil.cpu_percent()
        metrics["cpu"] = {"load": total_cpu}

        logger.debug(metrics)

    schedule.every(10).seconds.do(collect)
