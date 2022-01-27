# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 19:12:39 2022

@author: Alexander Southan
"""

import numpy as np

def line_through_box(x_values, y_values, box={'x': [-1, 1], 'y': [-1, 1]}):
    """
    Calculate if a line defined by two points passes through a rectangular box.

    The two points define an endless line in two dimensions and it is
    calculated if this endless line travels through the box. So it is totally
    irrelevant where exactly the two points are.

    Parameters
    ----------
    x_values : list or ndarray
        A list containing two values which are the x coodinates of the two
        data points.
    y_values : list or ndarray
        A list containing two values which are the x coodinates of the two
        data points.
    box : dict, optional
        A dictionary containing the box limits. Must contain the keys 'x' for
        the lower and upper limits on the x coordinate and 'y' for the lower
        and upper limits on the y coordinate, both given as a list or ndarray
        with two entries. The default is {'x': [-1, 1], 'y': [-1, 1]}.

    Returns
    -------
    float
        The distance the line travels through the box.
    list
        The two x coordinates where the line intersects the box walls.
    list
        The two y coordinates where the line intersects the box walls.

    """
    slope = (y_values[1]-y_values[0])/(x_values[1]-x_values[0])
    intercept = y_values[0] - slope*x_values[0]

    if slope != 0:
        intersect_x = np.sort((box['y']-intercept)/slope)
        overlap_x = [max(intersect_x[0], box['x'][0]),
                      min(intersect_x[1], box['x'][1])]
        overlap_x = overlap_x if overlap_x[0] < overlap_x[1] else []
    else:
        if ((y_values[0] > box['y'][0]) &
            (y_values[0] < box['y'][1])):
            overlap_x = box['x']
        else:
            overlap_x = []

    if overlap_x:
        overlap_y = [slope*curr_x+intercept for curr_x in overlap_x]
        score =  np.sqrt((overlap_x[1]-overlap_x[0])**2 +
                         (overlap_y[1]-overlap_y[0])**2)
        return (score, overlap_x, overlap_y)
    else:
        return (0, [], [])


def reflect_line_in_box(start, end, limits):
    """
    Reflect a line defined by two points within a one- to threedimensional box.

    Parameters
    ----------
    start : 2D ndarray
        The start points of the lines to be reflected. Must be a 2D array with
        the shape (n, d) where n is the number of data points and d is the
        dimension (between 1 and 3).
    end : 2D ndarray
        The end points of the lines to be reflected. Must be a 2D array with
        the shape (n, d) where n is the number of data points and d is the
        dimension (between 1 and 3).
    limits : dict
        A dictionary containing the box limits. Cancontain the keys 'x' for
        the lower and upper limits on the x coordinate, 'y' for the lower and
        upper limits on the y coordinate, and 'z' for the lower and upper
        limits on the z coordinate, all given as a list or ndarray with two
        entries. Must cover at least the dimensions given in start and end.


    Returns
    -------
    re_box : list of ndarrays
        The coordinates of the reflection points on the box limits. The list
        contains n elements and each element is a 2D ndarray with the
        coordinates.
    final : ndarray
        The coordinates of the final end points after all reflections. Has the
        same shape like start and end.

    """
    # The datapoints defining the lines to be reflected
    start = np.asarray(start, dtype='float')
    end = np.asarray(end, dtype='float')
    if start.shape == end.shape:
        dimensions = start.shape[1]
    else:
        raise ValueError(
            'Arrays for start and end point must have the same shapes.')

    # characteristics of the datapoints defining the lines to be reflected
    # on the borders of the allowed space
    point_diff = end - start
    direction = np.sign(point_diff).astype('int')

    # characteristics of the box limiting the allowed space
    limits = np.array([limits[ii] for ii in ['x', 'y', 'z'][:dimensions]]).T
    box_diff = np.zeros(dimensions)
    for curr_dim in range(dimensions):
        if np.all(limits[:, curr_dim]):
            box_diff[curr_dim] = np.abs(
                limits[1, curr_dim] - limits[0, curr_dim])
            if box_diff[curr_dim] == 0:
                raise ValueError(
                    'Upper and lower limits for dimension {} are equal. '
                    'They must be different or one or both must be None.'
                    ''.format(curr_dim+1))
        if np.any((start[:, curr_dim] > limits[1, curr_dim]) |
                  (start[:, curr_dim] < limits[0, curr_dim])):
            raise ValueError(
                'At least one of the start points is not within the '
                'limits.')

    # coordinates of the reflection points and the coordinate limit that
    # causes reflection
    reflect = [[[] for _ in range(dimensions)]
               for _ in range(start.shape[0])]
    reflect_type = [[] for _ in range(start.shape[0])]

    # calculate the intersection of the line between the points with the
    # lines of a grid formed by repeating the box limiting the allowed
    # space. This gives the coordinates of reflection points.
    for ii in range(dimensions):
        # if box_diff[ii] > 0:
        n = np.abs(direction[:, ii]) * (1/2*direction[:, ii]+1/2).astype(
            'int')
        grid = limits[0, ii] + n*box_diff[ii]
        for curr_point in range(start.shape[0]):
            while ((grid[curr_point] < end[curr_point, ii]) &
                   (direction[curr_point, ii] == 1) or
                   (grid[curr_point] > end[curr_point, ii]) &
                   (direction[curr_point, ii] == -1)):
                lambd = ((grid[curr_point] - end[curr_point, ii]) /
                         point_diff[curr_point, ii])
                for jj in range(dimensions):
                    if jj != ii:
                        reflect[curr_point][jj].append(
                            end[curr_point, jj] +
                            lambd*point_diff[curr_point, jj])
                    else:
                        reflect[curr_point][ii].append(grid[curr_point])
                reflect_type[curr_point].append(ii)
                n[curr_point] += direction[curr_point, ii]
                grid[curr_point] = (limits[0, ii] +
                                    n[curr_point]*box_diff[ii])

    # sort the reflection coordinates
    sort_idx = [
        np.argsort(reflect[curr_point][0])[::direction[curr_point, 0]]
        for curr_point in range(start.shape[0])]
    reflect = [[np.array(reflect[curr_point][ii])[sort_idx[curr_point]]
                for ii in range(dimensions)]
               for curr_point in range(start.shape[0])]
    reflect_type = [
        np.array(reflect_type[curr_point])[sort_idx[curr_point]]
        for curr_point in range(start.shape[0])]

    # Calculate the reflection points on the box faces
    re_box = [[reflect[curr_point][ii].copy() for ii in range(dimensions)]
              for curr_point in range(start.shape[0])]
    for curr_point in range(start.shape[0]):
        if reflect[curr_point][0].size != 0:
            for ii, r_type in enumerate(reflect_type[curr_point][:-1]):
                re_box[curr_point][r_type][ii+1:] = -(
                    re_box[curr_point][r_type][ii+1:] -
                    re_box[curr_point][r_type][ii]
                    ) + re_box[curr_point][r_type][ii]

    re_box = [np.array(curr_re_box) for curr_re_box in re_box]

    # calculate the final coordinates
    final = np.zeros_like(start)
    for curr_point in range(start.shape[0]):
        if reflect_type[curr_point].size != 0:
            for ii in range(dimensions):
                if any(reflect_type[curr_point] == ii):
                    coords = re_box[curr_point][ii][
                        reflect_type[curr_point] == ii]
                    rest = abs(point_diff[curr_point, ii]) - (
                        (reflect_type[curr_point] == ii).sum()-1
                        )*box_diff[ii] - abs(
                            start[curr_point, ii]-coords[0])
                    if coords[-1] == limits[0, ii]:
                        final[curr_point, ii] = limits[0, ii] + rest
                    else:
                        final[curr_point, ii] = limits[1, ii] - rest
                else:
                    final[curr_point, ii] = end[curr_point, ii]

    return (re_box, final)
