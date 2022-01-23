import numpy

from vortex.marker import ActiveLines, InactiveLines, SegmentBoundary, VolumeBoundary

def active_intervals_binary(markers, last_sample=None, initial_active=False, initial_reversed=False):
    active_intervals = []

    prior_marker = None
    active = initial_active
    reversed = initial_reversed
    for marker in markers:
        if marker[1] == b'S':
            reversed = marker[4] == b'R'
        elif not active and marker[1] == b'A':
            # inactive to active transition
            prior_marker = marker
            active = True

        elif active and marker[1] == b'I':
            # active to inactive transition
            if prior_marker is None:
                active_intervals.append((0, marker[0] - 1, False))
            else:
                active_intervals.append((prior_marker[0], marker[0] - 1, reversed))
            active = False

    # final interval
    if active:
        if prior_marker is None:
            active_intervals.append((0, last_sample, reversed))
        else:
            active_intervals.append((prior_marker[0], last_sample, reversed))

    return active_intervals

def active_intervals(markers, last_sample=None, initial_active=False, initial_reversed=False):
    active_intervals = []

    prior_marker = None
    active = initial_active
    reversed = initial_reversed
    for marker in markers:
        if isinstance(marker, SegmentBoundary):
            reversed = marker.reversed
        elif not active and isinstance(marker, ActiveLines):
            # inactive to active transition
            prior_marker = marker
            active = True

        elif active and isinstance(marker, InactiveLines):
            # active to inactive transition
            if prior_marker is None:
                active_intervals.append((0, marker.sample - 1, False))
            else:
                active_intervals.append((prior_marker.sample, marker.sample - 1, reversed))
            active = False

    # final interval
    if active:
        if prior_marker is None:
            active_intervals.append((0, last_sample, reversed))
        else:
            active_intervals.append((prior_marker.sample, last_sample, reversed))

    return active_intervals

def partition_segments_by_activity(markers, waveforms, initial_active=False, base_sample=0):
    active = initial_active
    prior_marker = None

    def _extract(marker):
        nonlocal prior_marker
        if prior_marker is None:
            start = 0
        else:
            start = prior_marker.sample - base_sample
        prior_marker = marker

        if marker is None:
            end = len(waveforms) + 1
        else:
            end = marker.sample - base_sample

        if start != end:
            return waveforms[start:end]
        else:
            return None

    active_segments = []
    inactive_segments = []
    for marker in markers:
        if not active and isinstance(marker, ActiveLines):
            # inactive to active transition
            segment = _extract(marker)
            if segment is not None:
                inactive_segments.append(segment)
            active = True

        elif active and isinstance(marker, InactiveLines):
            # active to inactive transition
            segment = _extract(marker)
            if segment is not None:
                active_segments.append(segment)
            active = False

    # final segment
    segment = _extract(None)
    if segment is not None:
        if active:
            active_segments.append(segment)
        else:
            inactive_segments.append(segment)

    return (active_segments, inactive_segments)

def plot_annotated_waveforms_time(dt, qs, markers, initial_active=False):
    from matplotlib import pyplot, transforms

    fig, axes = pyplot.subplots(3, sharex=True, constrained_layout=True)
    (qa, qda, qdda) = axes
    # ref: https://stackoverflow.com/questions/63153629/matplotlib-text-use-data-coords-for-x-axis-coords-for-y
    trans = transforms.blended_transform_factory(qa.transData, qa.transAxes)

    ts = dt * numpy.arange(0, len(qs))

    qa.plot(ts, qs, '-+')

    qds = numpy.diff(qs, 1, axis=0) / dt
    qda.plot(ts[1:], qds, '-+')

    qdds = numpy.diff(qs, 2, axis=0) / dt**2
    qdda.plot(ts[2:], qdds, '-+')

    # annotations
    for marker in markers:
        if isinstance(marker, SegmentBoundary):
            for ax in axes:
                ax.axvline(dt * marker.sample, color='g', linestyle=':')
            qa.text(dt * marker.sample, 1, f'{marker.sequence}:{marker.index_in_volume}', ha='center', va='bottom', transform=trans)
        elif isinstance(marker, VolumeBoundary):
            for ax in axes:
                ax.axvline(dt * marker.sample, color='r', linestyle=':' if marker.reversed == 'R' else '-', linewidth=3)

    # shade active intervals
    for (a, b, r) in active_intervals(markers, last_sample=len(qs) - 1):
        for ax in axes:
            ax.axvspan(dt * a, dt * b, color='r' if r else 'g', alpha=0.25)

    # styling
    for ax in axes:
        ax.grid(True)

    # qa.set_title('Position')
    qa.set_ylabel('q (au)')
    qa.set_xlim(0, dt * (len(qs) - 1))

    # qda.set_title('Velocity')
    qda.set_ylabel('dq/dt (au/s)')
    qda.set_xlim(0, dt * (len(qs) - 1))

    # qdda.set_title('Acceleration')
    qdda.set_xlabel('t (s)')
    qdda.set_ylabel('dq^2/dt^2 (au/s^2)')
    qdda.set_xlim(0, dt * (len(qs) - 1))

    return (fig, axes)

def plot_annotated_waveforms_space(qs, markers, **kwargs):
    from matplotlib import pyplot
    from matplotlib.cm import viridis

    initial_active = kwargs.get('initial_actve', False)

    colorize = kwargs.get('colorize', True)
    scan_line = kwargs.get('scan_line', 'k-')
    active_marker = kwargs.get('active_marker', '+')
    inactive_marker = kwargs.get('inactive_marker', 'k+')

    axes = kwargs.get('axes', None)
    if axes is None:
        fig, axes = pyplot.subplots(1)
    else:
        fig = axes.get_figure()

    if scan_line is not None:
        axes.plot(qs[:, 0], qs[:, 1], scan_line)

    (active, inactive) = partition_segments_by_activity(markers, qs, initial_active=initial_active)

    if inactive_marker is not None:
        inactive = numpy.row_stack(inactive)
        axes.plot(inactive[:, 0], inactive[:, 1], inactive_marker)

    if active_marker is not None:
        active = numpy.row_stack(active)
        if colorize:
            axes.scatter(active[:, 0], active[:, 1], c=viridis(numpy.linspace(0, 1, len(active))), marker=active_marker, zorder=10)
        else:
            axes.plot(active[:, 0], active[:, 1], active_marker)

    axes.set_xlabel('x (au)')
    axes.set_ylabel('y (au)')
    axes.axis('equal')

    return (fig, axes)
