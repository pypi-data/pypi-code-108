import datetime

from .utils import extract_time


def if_stale(run):
    """judge whether run is stale, runs happens long time ago or its duration is short

    :return: True if stale
    :rtype: bool
    """
    duration, run2now = extract_time(run)
    time_thred = [[0, 10], [7, 60], [3, 180], [1, 600]]
    for thr_d, thr_s in time_thred:
        if run2now > datetime.timedelta(days=thr_d) and duration < datetime.timedelta(
            seconds=thr_s
        ):
            return True
    return False


def if_notag(run):
    duration, run2now = extract_time(run)
    if "stable" in run.tags or "delete" in run.tags:
        return True
    if duration > datetime.timedelta(days=2):
        return False
    if run2now > datetime.timedelta(days=3) and len(run.tags) == 0:
        return True
    return False
