from typing import List


def ziegler_nichols_method(critical_gain: float, cycle_time: float) -> List[float]:
    """Calculate PID values using the Ziegler-Nichols method.

    Returns:
        [P, I, D]
    """
    p = 0.6 * critical_gain
    i = 1.2 * critical_gain / cycle_time
    d = 0.075 * critical_gain * cycle_time
    return [p, i, d]
