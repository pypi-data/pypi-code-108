import numpy as np
from foldedleastsquares import DefaultTransitTemplateGenerator


class LcbuilderHelper:
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def calculate_period_grid(time, min_period, max_period, oversampling, star_info, transits_min_count,
                              max_oversampling=15):
        time_span_curve = time[-1] - time[0]
        dif = time[1:] - time[:-1]
        jumps = np.where(dif > 1)[0]
        jumps = np.append(jumps, len(time))
        previous_jump_index = 0
        time_span_all_sectors = 0
        empty_days = 0
        for jumpIndex in jumps[0:-1]:
            empty_days = empty_days + time[jumpIndex + 1] - time[jumpIndex - 1]
        if oversampling is None:
            oversampling = int(1 / ((time_span_curve - empty_days) / time_span_curve))
            oversampling = oversampling if oversampling < max_oversampling else max_oversampling
            oversampling = oversampling if oversampling > 3 else 3
        for jumpIndex in jumps:
            time_chunk = time[previous_jump_index + 1:jumpIndex]  # ignoring first measurement as could be the last from the previous chunk
            time_span_all_sectors = time_span_all_sectors + (time_chunk[-1] - time_chunk[0])
            previous_jump_index = jumpIndex
        return DefaultTransitTemplateGenerator() \
            .period_grid(star_info.radius, star_info.mass, time_span_curve, min_period,
                         max_period, oversampling, transits_min_count, time_span_all_sectors)
