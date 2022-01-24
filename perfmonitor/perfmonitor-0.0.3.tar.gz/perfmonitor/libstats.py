from typing import Tuple
from time import time
import psutil

INIT = False


def get_cpu_stats() -> dict:
    """
    Get CPU percentage stats.
    """
    global INIT

    if not INIT:
        psutil.cpu_percent(interval=0.1)
        psutil.cpu_percent(percpu=True, interval=0.1)

        INIT = True

    n_cores = psutil.cpu_count(logical=True)
    cpu_perc = psutil.cpu_percent(percpu=True, interval=0.0)
    t_cpu_perc = psutil.cpu_percent(interval=0.0)

    return {
        "cpu_percs": {**{i: cpu_perc[i] for i in range(n_cores)}, **{"_Total": t_cpu_perc}},
    }


def get_mem_stats() -> dict:
    """
    Get memory usage/availability stats.
    """
    total_mem, avail_mem, _, _, _ = psutil.virtual_memory()
    total_swap, used_swap, _, _, _, _ = psutil.swap_memory()

    return {
        "byte_avail": avail_mem / (1024 * 1024),
        "mb_tot": total_mem / (1024 * 1024),
        "v_bytes": used_swap / (1024 * 1024),
        "v_bytes_limit": total_swap / (1024 * 1024)
    }


def get_net_stats() -> dict:
    """
    Get network usage stats.
    """
    net_io_counters_total = psutil.net_io_counters()
    net_io_counters_total = {'bytes_sent': net_io_counters_total.bytes_sent,
                             'bytes_recv': net_io_counters_total.bytes_recv}

    if not hasattr(get_net_stats, "old_stats"):
        setattr(get_net_stats, "old_stats", net_io_counters_total)
        setattr(get_net_stats, "old_time", time())

    old_stats = getattr(get_net_stats, "old_stats")
    old_time = getattr(get_net_stats, "old_time")

    refresh_time = time() - old_time
    if refresh_time == 0:
        counter_diff = {'bytes_sent': 0, 'bytes_recv': 0}
    else:
        counter_diff = {'bytes_sent': (net_io_counters_total['bytes_sent'] - old_stats['bytes_sent'])/refresh_time,
                                'bytes_recv': (net_io_counters_total['bytes_recv'] - old_stats['bytes_recv'])/refresh_time}
    
    setattr(get_net_stats, "old_stats", net_io_counters_total)
    setattr(get_net_stats, "old_time", time())
    return {
        "net_io_counters": counter_diff
    }


def get_all_stats() -> Tuple[dict, float]:
    t = time()

    cpu_stats = get_cpu_stats()
    mem_stats = get_mem_stats()
    net_stats = get_net_stats()

    return {**cpu_stats, **mem_stats, **net_stats}, time() - t
