import numpy as np


def y_at_x(x, x_values, y_values):
    """
    Find values in y_values that belongs to the values in x_values clostest to x.

    Parameters
    ----------
    x : float or list of float
        The values to look for in x_values. If the exact values do not exist,
        the values in x_values clostest to x will be used.
    x_values : ndarray
        The array containing the independent variable.
    y_values : ndarray
        The array containing the dependent variable.

    Returns
    -------
    ndarray
        The values in y_values that are at the indices of the values of
        x_values that are clostest to the values in x.

    """
    y_values = np.asarray(y_values)

    return y_values[closest_index(x, x_values)]

def closest_value(x, x_values):
    """
    Find value in x_values that is closest to x.

    Parameters
    ----------
    x : float
        The values to look for in x_values.
    x_values : ndarray
        The array containing the numbers to look through.

    Returns
    -------
    ndarray
        The value in x_values closest to x.

    """
    x_values = np.asarray(x_values)

    return x_values[closest_index(x, x_values)]

def closest_index(x, x_values):
    """
    Find the index of a value in array x_values that is clostest to x.

    Parameters
    ----------
    x : float or list of float
        A single value or a list of values to look for in x_values.
    x_values : ndarray or list
        The array with the values to compare to x.

    Returns
    -------
    ndarray
        The indices of the values in x_values that are clostest to x.

    """
    x_values = np.asarray(x_values)

    return np.argmin(np.abs(x-x_values[:, np.newaxis]), axis=0)

def segment_xy_values(x_values, segment_borders, y_values=None):
    """
    Segment the x_values and y_values according to segment borders.

    This function is used in the functions piecewise_polynomial_fit and
    piecewise_polynomial.

    Parameters
    ----------
    x_values : ndarray
        A 1D array with the length M holding the independent variable used for
        the fit. Must be sorted for the segmetation, so is sorted ascending if
        it is not already.
    segment_borders : list of int or float
        The values with respect to x_values at which the data is divided into
        segments. An arbitrary number of segment borders may be given, and it
        is recommended to provide a sorted list in order to avoid confusion.
    y_values : ndarray or None, optional
        A 1D array with the length M holding the dependent varibale used for
        the fit. Default is None which means that no y_values are processed.

    Returns
    -------
    x_segments : list of ndarray
        The segments of x_values used for piecewise polynomial calculations.
        All segments overlap by one point.
    y_segments : list of ndarray
        The segments of y_values used for piecewise polynomial calculations.
        All segments overlap by one point. Only if y_values are passed to the
        function.

    """
    x_values = np.asarray(x_values)
    if y_values is not None:
        y_values = np.asarray(y_values)

    if (not np.all(x_values[:-1] <= x_values[1:])):
        sort_index = np.argsort(x_values)
        x_values = x_values[sort_index]
        if y_values is not None:
            y_values = y_values[sort_index]

    # segment_borders are sorted by x values in segment_borders in order to
    # avoid problems during segmentation
    segment_borders = np.sort(segment_borders)

    # ascending_x = x_values[1] > x_values[0]

    # if not ascending_x:
    #     x_values = np.flip(x_values)
    #     if y_values is not None:
    #         y_values = np.flip(y_values)

    # Segmentation indices are the indices of the values in x_values clostest
    # to the values given by segment_borders. At these points, the data is
    # split into segments that are fitted individually. Additionally, the index
    # zero is added for the first data point and the data point number for the
    # last data point.
    segmentation_indices = np.array([0, len(x_values)])
    segmentation_indices = np.insert(segmentation_indices, 1,
                                     closest_index(segment_borders, x_values))
    # segmentation_indices = np.insert(segmentation_indices, 1, np.argmin(
    #     np.abs(x_values[:, np.newaxis]-segment_borders), axis=0))

    # Later on, the right sides of the segments except the last one have to be
    # extended by one relative to the segmentation indices in order to have an
    # overlap of one point between the segments.
    segment_additions = np.zeros(len(segmentation_indices)-1, dtype='int')
    segment_additions[:-1] = 1

    x_segments = []
    if y_values is not None:
        y_segments = []
    for curr_start, curr_end, curr_add in zip(
            segmentation_indices[:-1], segmentation_indices[1:],
            segment_additions):
        x_segments.append(x_values[curr_start:curr_end + curr_add])
        if y_values is not None:
            y_segments.append(y_values[curr_start:curr_end + curr_add])

    # if not ascending_x:
    #     x_segments = [x_seg[::-1] for x_seg in x_segments][::-1]
    #     if y_values is not None:
    #         y_segments = [y_seg[::-1] for y_seg in y_segments][::-1]

    if y_values is not None:
        return (x_segments, y_segments)
    else:
        return x_segments