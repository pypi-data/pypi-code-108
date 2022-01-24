
from typing import List, Sequence

from shyft.time_series import (
    DtsClient,
    Calendar, UtcPeriod,
    TimeAxis, TimeSeries, TsVector, DoubleVector, UtcTimeVector,
    point_interpretation_policy, POINT_AVERAGE_VALUE,
)


def selector_ts(
        ts: TimeSeries,
        period: UtcPeriod,
        average_dt: int,
        threshold_tss: Sequence[TimeSeries],
        tss: Sequence[TimeSeries],
        mask_point_fx: point_interpretation_policy,
        client: DtsClient, calendar: Calendar
) -> TimeSeries:
    """Select values from different time-series based on values from a single
    time-series when compared to a set of threshold time-series.

    Args:
        ts: TimeSeries to base selections on.
        period: Period to select values in.
        average_dt: Time step to use for the internal masking series. An average of
            the input ts together with the threshold time-series in threshold_tss is
            used to generate the masks.
        threshold_tss: Threshold time-series. Should be one less than the number of
            time-series to choose from.
        tss: TimeSeries to choose values from.
        mask_point_fx: Point interpretation to use for the mask time-series. If equal
            to POINT_INSTANT_VALUE the boundaries between different selection
            regions is smoothed. If equal to POINT_AVERAGE_VALUE the boundaries are
            sharp.
        client: DtsClient use for computations and data retrieval.
        calendar: Calendar used to interpret time.

    Returns:
        A TimeSeries that is the selection of values from tss.
    """
    if not len(threshold_tss) == len(tss) - 1:
        raise RuntimeError('the number of thresholds should be one less '
                                                'than the number of time-series')

    # setup averaging for mask
    tsv = TsVector()
    # ----------
    n = calendar.diff_units(period.start, period.end, average_dt)
    if n * average_dt < period.end - period.start:
        n += 1
    ta_avg = TimeAxis(period.start, average_dt, n)
    tsv.append(ts.average(ta_avg))
    # ----------
    tsv: TsVector = client.evaluate(tsv, period)
    # ----------
    avg_ts = tsv[0]
    del tsv

    # compute mask
    masks: List[DoubleVector] = []
    for avg_p, avg_v in zip(avg_ts.get_time_axis(), avg_ts.values):
        added_mask = False
        for i in range(len(tss)):
            if i == len(masks):
                masks.append(DoubleVector())
            if not added_mask:
                # determine period threshold
                if i == 0:
                    min_threshold = -1_000_000_000
                    max_threshold = threshold_tss[0](avg_p.start)
                elif i == len(tss) - 1:
                    min_threshold = threshold_tss[-1](avg_p.start)
                    max_threshold = 1_000_000_000
                else:
                    min_threshold = threshold_tss[i - 1](avg_p.start)
                    max_threshold = threshold_tss[i](avg_p.start)
                # set mask value
                if min_threshold <= avg_v < max_threshold:
                    added_mask = True
                    masks[i].append(1.0)
                else:
                    masks[i].append(0.0)
            else:
                masks[i].append(0.0)

    # construct final ts
    computed_ts = None
    for i, ts_expr in enumerate(tss):
        if computed_ts is not None:
            computed_ts += ts_expr * TimeSeries(ta_avg, masks[i], mask_point_fx)
        else:
            computed_ts = ts_expr * TimeSeries(ta_avg, masks[i], mask_point_fx)

    return computed_ts


def fixed_tsv(
        period: UtcPeriod,
        fixed_values: Sequence[float]
) -> TsVector:
    """Create a TsVector with TimeSeries with fixed values spanning the given period.

    Args:
        period: Time period the generated TimeSeries should span.
        fixed_values: A sequence of numbers to generate constant TimeSeries for.

    Returns:
        A TsVector with one TimeSeries for each value in fixed_values, all spanning period.
    """
    tsv = TsVector()
    for fv in fixed_values:
        tsv.append(TimeSeries(
            TimeAxis(UtcTimeVector([period.start, period.end])),
            [fv], POINT_AVERAGE_VALUE
        ))
    return tsv


def windowed_percentiles_tsv(
        ts: TimeSeries,
        period: UtcPeriod,
        average_dt: int,
        percentile_dt: int,
        percentiles: Sequence[int],
        client: DtsClient, calendar: Calendar
) -> TsVector:
    """Compute percentiles for a time-series in a gliding window fashion.

     The input time-series is partitioned and averaged using ``ts.partition_by`` such
     that each value is included in percentile computations spanning percentile_dt time
     from the value occurrence.

    Args:
        ts: TimeSeries to compute percentile time-series for.
        period: Period to generate percentile time-series for.
        average_dt: Period to average values by when partitioning the input time-series.
            This is the time-step of the time-series in the output TsVector.
        percentile_dt: Time span for a value to contribute to percentile computations.
        percentiles: Percentiles to compute. Values should be in the range ``0..100``.
        client: DtsClient to use for performing the partitioning.
        calendar: Calendar to to for interpreting time and partitioning the input
            time-series.

    Returns:
        A TsVector with one TimeSeries for each value in percentiles, all spanning period.
    """
    periods = int(percentile_dt//average_dt)

    n_avg = calendar.diff_units(period.start, period.end, average_dt)
    if n_avg*average_dt < period.end - period.start:
        n_avg += 1

    tsv = client.evaluate(
        ts.average(TimeAxis(period.start, average_dt, n_avg))
          .partition_by(calendar, period.start, average_dt, periods, period.start)
          .time_shift(periods*average_dt),
        period
    )

    return tsv.percentiles(TimeAxis(period.start, average_dt, n_avg), percentiles)


def period_percentiles_tsv(
        ts: TimeSeries,
        period: UtcPeriod,
        average_dt: int,
        percentile_period: UtcPeriod,
        percentiles: Sequence[int],
        client: DtsClient, calendar: Calendar
) -> TsVector:
    """Compute percentiles from a part of a time-series and generate a TsVector of
    percentile time-series spanning a possibly different time period.

    Args:
        ts: TimeSeries to compute percentile time-series for.
        period: Time period the output time-series should span.
        average_dt: Period to average values by when partitioning the input time-series.
        percentile_period: Period from ts to compute percentiles for.
        percentiles: Percentiles to compute. Values should be in the range ``0..100``.
        client: DtsClient to use for performing the partitioning.
        calendar: Calendar to to for interpreting time and partitioning the input
            time-series.

    Returns:
        A TsVector with one TimeSeries for each value in percentiles, all spanning period.
    """
    periods = int((percentile_period.end - percentile_period.start)//average_dt)

    n_avg = calendar.diff_units(period.start, period.end, average_dt)
    if n_avg*average_dt < period.end - period.start:
        n_avg += 1

    tsv = client.evaluate(
        ts.average(TimeAxis(period.start, average_dt, n_avg))
          .partition_by(calendar, period.start, average_dt, periods, period.start),
        period
    )
    tsv_p = tsv.percentiles(TimeAxis(period.start, average_dt, 1), percentiles)

    tsv = TsVector()
    ta = TimeAxis(period.start, period.end - period.start, 1)
    for ts_p in tsv_p:
        tsv.append(TimeSeries(ta, [ts_p.values[0]], POINT_AVERAGE_VALUE))

    return tsv
