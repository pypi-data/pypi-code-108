from typing import Dict


def convert_window_size_to_ms(window_size: Dict) -> int:
    ms: float = 0
    days = window_size.get("days")
    hours = window_size.get("hours")
    minutes = window_size.get("minutes")
    if days:
        ms += int(days) * 24 * 3600 * 1e3
    if hours:
        ms += int(hours) * 3600 * 1e3
    if minutes:
        ms += int(minutes) * 60 * 1e3
    converted: int = int(ms)
    return converted


def window_size_update(config: Dict):
    window_size = config["schedule"].get("windowSize")
    if window_size:
        converted_window_size = convert_window_size_to_ms(window_size)
        config["schedule"]["windowSize"] = converted_window_size
