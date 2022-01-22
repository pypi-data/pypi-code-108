import os
import time


class PrettyFloat(float):
    def __repr__(self):
        return '%.2f' % self

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(float(v))) for k, v in list(obj.items()))
    return obj


def write(metrics):
    if not isinstance(metrics, dict):
        raise ValueError('input is not a dictionary!')
    _metrics = pretty_floats(metrics)
    log_file = os.getenv('METRICS_PATH', None)
    if log_file:
        t0=time.time()
        chunk="{}, {}\n".format(t0, _metrics)
        with open(log_file, encoding="utf-8", mode="a") as f:
            f.write(chunk)
