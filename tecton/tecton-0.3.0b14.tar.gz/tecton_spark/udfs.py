import datetime
from typing import List
from typing import Optional

from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType
from pyspark.sql.types import TimestampType

from tecton_spark.errors import TectonValidationError
from tecton_spark.time_utils import align_time_downwards
from tecton_spark.time_utils import assert_valid_time_string
from tecton_spark.time_utils import strict_pytimeparse
from tecton_spark.time_utils import WINDOW_UNBOUNDED_PRECEDING


def _tecton_sliding_window_impl(
    timestamp: datetime.datetime,
    window_size: str,
    slide_interval: str,
    feature_start: datetime.datetime,
    feature_end: datetime.datetime,
) -> List[datetime.datetime]:
    window_size_td, slide_interval_td = _validate_sliding_window_duration(window_size, slide_interval)

    aligned_feature_start = align_time_downwards(feature_start, slide_interval_td)
    earliest_possible_window_start = align_time_downwards(timestamp, slide_interval_td)
    window_end_cursor = max(aligned_feature_start, earliest_possible_window_start) + slide_interval_td
    windows = []
    # confirm windows are aligned
    while window_end_cursor <= feature_end:
        ts_after_window_start = window_size_td is None or timestamp >= window_end_cursor - window_size_td
        ts_before_window_end = timestamp < window_end_cursor
        if ts_after_window_start and ts_before_window_end:
            windows.append(window_end_cursor - datetime.timedelta(microseconds=1))
            window_end_cursor = window_end_cursor + slide_interval_td
        else:
            break
    return windows


def _validate_and_parse_time(duration: str, field_name: str, allow_unbounded: bool) -> Optional[datetime.timedelta]:
    if allow_unbounded and duration.lower() == WINDOW_UNBOUNDED_PRECEDING:
        duration_td = None
    else:
        # called for nice error message
        assert_valid_time_string(duration, allow_unbounded=allow_unbounded)
        duration_td = datetime.timedelta(seconds=strict_pytimeparse(duration))
    if duration_td is not None and duration_td.total_seconds() <= 0:
        raise TectonValidationError(f"Duration {duration} provided for field {field_name} must be positive.")
    return duration_td


def _validate_sliding_window_duration(
    window_size: str, slide_interval: str
) -> (Optional[datetime.timedelta], datetime.timedelta):
    slide_interval_td = _validate_and_parse_time(slide_interval, "slide_interval", allow_unbounded=False)
    window_size_td = _validate_and_parse_time(window_size, "window_size", allow_unbounded=True)
    if window_size_td is not None:
        # note this also confirms window >= slide since a>0, b>0, a % b = 0 implies a >= b
        if window_size_td.total_seconds() % slide_interval_td.total_seconds() != 0:
            raise TectonValidationError(
                f"Window size {window_size} must be a multiple of slide interval {slide_interval}"
            )
    return window_size_td, slide_interval_td


tecton_sliding_window_udf = udf(_tecton_sliding_window_impl, ArrayType(TimestampType()))
