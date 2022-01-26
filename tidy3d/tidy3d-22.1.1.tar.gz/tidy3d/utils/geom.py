import numpy as np

from .misc import listify
from .log import log_and_raise


def inside_box_mesh(span, mesh):
    """Finds which points defined by ``mesh`` are inside a Box ``span``.

    Parameters
    ----------
    span : np.ndarray of shape (3, 2)
        Defines (xmin, xmax), (ymin, ymax), (zmin, zmax) of the box.
    mesh : tuple
        3-tuple defining the x, y, and z points on the Cartesian grid.

    Returns
    -------
    indsx, indsy, indsz: tuple
        Tuples defining the (start, stop) index of the mesh inside the box.
    """

    # Check if min and max values are in order
    for dim in range(3):
        if span[dim, 1] < span[dim, 0]:
            log_and_raise(
                "Incorrect box span (max value smaller than " "min value).",
                ValueError,
            )

    # Initialize indexes for no part of the mesh inside the box
    indsx, indsy, indsz = ((0, 0), (0, 0), (0, 0))

    # Check if any of the mesh arrays has zero length
    if np.any([m.size == 0 for m in mesh]):
        return indsx, indsy, indsz

    indx = np.nonzero((span[0, 0] < mesh[0]) * (mesh[0] < span[0, 1]))[0]
    indy = np.nonzero((span[1, 0] < mesh[1]) * (mesh[1] < span[1, 1]))[0]
    indz = np.nonzero((span[2, 0] < mesh[2]) * (mesh[2] < span[2, 1]))[0]

    # For each dimension handle non-empty set of indexes; else return (0, 0)
    if indx.size > 0:
        indsx = (indx[0], indx[-1] + 1)
    if indy.size > 0:
        indsy = (indy[0], indy[-1] + 1)
    if indz.size > 0:
        indsz = (indz[0], indz[-1] + 1)

    return (indsx, indsy, indsz)


def inside_box(span, mesh):
    """Elementwise indicator function for the points defined by ``mesh``
    which are inside a Box ``span``.

    Parameters
    ----------
    span : np.ndarray of shape (3, 2)
        Defines (xmin, xmax), (ymin, ymax), (zmin, zmax) of the box.
    mesh : tuple
        3-tuple defining the xgrid, ygrid and zgrid.

    Returns
    -------
    mask : np.ndarray
        A 3D array of shape (mesh[0].size, mesh[1].size, mesh[2].size)
        that is 1 inside the box and 0 outside.
    """

    # Initialize empty mask
    mask = np.zeros((mesh[0].size, mesh[1].size, mesh[2].size))

    indsx, indsy, indsz = inside_box_mesh(span, mesh)
    mask[indsx[0] : indsx[1], indsy[0] : indsy[1], indsz[0] : indsz[1]] = 1.0

    return mask


def inside_box_coords(span, coords, include_zero_size=True):
    """Finds which points defined by ``coords`` are inside a Box ``span``.
    If ``include_zero_size==False``, this is equivalent to calling
    ``inside_box_mesh`` with the mesh defined by the centers of the ``coords``.
    When ``include_zero_size==True`` (default), this function allows to place
    the zero-size Box inside the correct cell where the box center lies.
    This is often needed for sources and monitors that are smaller than 3D.

    Parameters
    ----------
    span : np.ndarray of shape (3, 2)
        Defines (xmin, xmax), (ymin, ymax), (zmin, zmax) of the box.
    coords : tuple
        3-tuple defining the coordinate boundaries, such that the mesh centers
        are given by ``(coords[:-1] + coords[1:])/2``.
    include_zero_size : bool, optional
        Description

    Returns
    -------
    indsx, indsy, indsz : tuple
        Tuples defining the (start, stop) index of the mesh inside the box.
    """

    # Check if any of the coords arrays has length less than two
    for dim in range(3):
        if coords[dim].size < 2:
            return ((0, 0), (0, 0), (0, 0))

    mesh = [(c[:-1] + c[1:]) / 2 for c in coords]
    ind1, ind2, ind3 = inside_box_mesh(span, mesh)

    inds_all = list(inside_box_mesh(span, mesh))
    if include_zero_size == True:
        for dim, inds in enumerate(inds_all):
            if (inds[1] == inds[0] == 0) and (span[dim, 1] - span[dim, 0] == 0):
                ind = np.nonzero(
                    (span[dim, 0] >= coords[dim][:-1]) * (span[dim, 0] < coords[dim][1:])
                )[0]
                if ind.size > 0:
                    inds_all[dim] = (ind[0], ind[0] + 1)

    return tuple(inds_all)


def intersect_box(span1, span2):
    """Return a span of a box that is the intersection between two spans.
    If there's no intersection along dimension d, the returned span[d, 1] 
    values are smaller than the returned span[d, 0] values.
    """
    span = np.zeros((3, 2))
    for d in range(3):
        span[d, 0] = max(span1[d, 0], span2[d, 0])
        span[d, 1] = min(span1[d, 1], span2[d, 1])

    return span


def cs2span(center, size):
    """Get shape (3, 2) span from center and size, each (3, ) arrays."""
    return np.vstack(
        (
            np.array(center) - np.array(size) / 2,
            np.array(center) + np.array(size) / 2,
        )
    ).T


def span2cs(span):
    """Get center, size: each arrays of shape (3,), from a shape (3, 2) array
    span.
    """
    center = np.array([(span[d, 1] + span[d, 0]) / 2 for d in range(3)])
    size = np.array([(span[d, 1] - span[d, 0]) for d in range(3)])
    return center, size


def axes_handed(axes):
    """Return +1 if the axes indexes in the list ``axes`` form a right-handed
    coordinate system, and -1 if they form a left-handed one.
    """

    if listify(axes) in [[0, 1, 2], [1, 2, 0], [2, 0, 1]]:
        return 1
    elif listify(axes) in [[0, 2, 1], [1, 0, 2], [2, 1, 0]]:
        return -1
    else:
        log_and_raise("Unrecognized list of axes indexes.", ValueError)


def rotate3D(x, y, z, angle_x, angle_y, angle_z):
    """3D rotation around x, y, and/or z axes. The order is first around z,
    then around y, then around x.
    """

    shape_in = x.shape
    assert y.shape == z.shape == shape_in

    xf, yf, zf = [a.flatten() for a in [x, y, z]]
    Rx = np.array(
        [
            [1, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x)],
            [0, np.sin(angle_x), np.cos(angle_x)],
        ]
    )
    Ry = np.array(
        [
            [np.cos(angle_y), 0, np.sin(angle_y)],
            [0, 1, 0],
            [-np.sin(angle_y), 0, np.cos(angle_y)],
        ]
    )
    Rz = np.array(
        [
            [np.cos(angle_z), -np.sin(angle_z), 0],
            [np.sin(angle_z), np.cos(angle_z), 0],
            [0, 0, 1],
        ]
    )

    out = np.stack((xf, yf, zf), axis=0)
    out = Rx.dot(Ry.dot(Rz.dot(out)))

    return (o.reshape(shape_in) for o in out)
