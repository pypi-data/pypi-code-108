from __future__ import absolute_import, division, print_function

import numpy as np


def lincongrid1d(data, new_shp):
    """

    Parameters
    ----------
    data :

    new_shp :


    Returns
    -------

    """
    ind = np.arange(new_shp) * data.size / new_shp
    ind_f = np.floor(ind).astype(int)
    delta = ind - ind_f
    data_ = data.flatten()
    inds = np.where(ind_f < (data.size - 1))
    res = np.zeros(new_shp, dtype=data.dtype)
    res[inds] = (
        data_[ind_f[inds]] * (1 - delta[inds])
        + delta[inds] * data_[ind_f[inds] + 1]
    )
    inds = np.where(ind_f >= (data.size - 1))
    res[inds] = data_[ind_f[inds]] + (
        (data_[ind_f[inds]] - data_[ind_f[inds] - 1]) * delta[inds]
    )
    return res


def lincongrid2d(data, new_shp):
    """

    Parameters
    ----------
    data :

    new_shp :


    Returns
    -------

    """
    if (len(data.shape) != len(new_shp)) or (len(new_shp) != 2):
        raise NameError("Incompatible dimensions to lincongrid2d")

    # Handle case where first dimension is one
    if data.shape[0] == 1:
        d1 = lincongrid1d(data, new_shp[1]).reshape(1, new_shp[1])
        # We do not expand trivial dimensions
        return d1
    if data.shape[1] == 1:
        d1 = lincongrid1d(data, new_shp[0]).reshape(new_shp[0], 1)

    # Interpolate first over the first dimension
    ind = np.arange(new_shp[0]) * data.shape[0] / new_shp[0]
    ind_f = np.floor(ind).astype(int)
    delta = ind - ind_f
    inds = np.where(ind_f < (data.shape[0] - 1))[0]
    d1 = np.zeros((new_shp[0], data.shape[1]), dtype=data.dtype)
    delta_ = delta[inds].reshape((inds.size, 1))
    d1[inds, :] = (
        data[ind_f[inds], :] * (1 - delta_) + delta_ * data[ind_f[inds] + 1, :]
    )
    inds = np.where(ind_f >= (data.shape[0] - 1))[0]
    delta_ = delta[inds].reshape((inds.size, 1))
    d1[inds, :] = data[ind_f[inds], :] + (
        (data[ind_f[inds], :] - data[ind_f[inds] - 1, :]) * delta_
    )
    # Interpolate first over the first dimension
    ind = np.arange(new_shp[1]) * data.shape[1] / new_shp[1]
    ind_f = np.floor(ind).astype(int)
    delta = ind - ind_f
    inds = np.where(ind_f < (data.shape[1] - 1))[0]
    d2 = np.zeros((new_shp[0], new_shp[1]), dtype=data.dtype)
    delta_ = delta[inds].reshape((1, inds.size))
    d2[:, inds] = (
        d1[:, ind_f[inds]] * (1 - delta_) + delta_ * d1[:, ind_f[inds] + 1]
    )
    inds = np.where(ind_f >= (data.shape[1] - 1))[0]
    delta_ = delta[inds].reshape(1, (inds.size))
    d2[:, inds] = d1[:, ind_f[inds]] + (
        (d1[:, ind_f[inds]] - d1[:, ind_f[inds] - 1]) * delta_
    )
    return d2


def lincongrid(data, new_shp):
    """Resizes 1 or 2 dimensionsal array to new shape
        performing a bilineal interpolation

    Parameters
    ----------
    data :
        input np.array
    data :
        output shape (same dimensions as input)

        :out: resized array
    new_shp :


    Returns
    -------

    """
    if len(data.shape) == 1:
        return lincongrid1d(data, new_shp)
    elif len(data.shape) == 2:
        return lincongrid2d(data, new_shp)
    else:
        print("Unsuported number of dimensions")
        raise NameError("lincongrid failed")


def linresample(data, samples_, axis=0, extrapolate=False, circular=False):
    """Resamples data to new samples

    Parameters
    ----------
    data :
        ndarray
    samples :
        new samples (1D vector)
    axis :
        axis to be resampled (Default value = 0)
    extrapolate :
        extend if required repeating first or last sample (Default value = False)
    samples_ :

    circular :
         (Default value = False)

    Returns
    -------

    """
    smp = np.array(samples_)  # Just to make sure
    if circular:
        ind_f = np.floor(smp).astype(int)
        delta = smp - ind_f
        # Now a hack to account for the case that the last sample is the last input
        # index
        ind_c = np.mod(ind_f + 1, data.shape[axis])
        ind_f = np.mod(ind_f, data.shape[axis])

    else:
        if not extrapolate:
            if (smp.min() < 0) or (smp.max() > (data.shape[axis] - 1)):
                print("Output samples out of bound")
                raise NameError("linresample failed")
        else:
            smp = np.where(smp > 0, smp, 0)
            smp = np.where(
                smp <= data.shape[axis] - 1, smp, data.shape[axis] - 1
            )
        ind_f = np.floor(smp).astype(int)
        delta = smp - ind_f
        # Now a hack to account for the case that the last sample is the last input
        # index
        ind_c = np.where(delta > 0, ind_f + 1, ind_f)
    delta_nshp = np.ones(len(data.shape), dtype=np.int32)
    delta_nshp[axis] = delta.size
    delta = delta.reshape(delta_nshp.tolist())
    if axis == 0:
        out = data[ind_f] * (1 - delta) + data[ind_c] * delta
    elif axis == 1:
        out = data[:, ind_f] * (1 - delta) + data[:, ind_c] * delta
    elif axis == 2:
        out = data[:, :, ind_f] * (1 - delta) + data[:, :, ind_c] * delta
    elif axis == 3:
        out = data[:, :, :, ind_f] * (1 - delta) + data[:, :, :, ind_c] * delta
    elif axis == 4:
        out = (
            data[:, :, :, :, ind_f] * (1 - delta)
            + data[:, :, :, :, ind_c] * delta
        )
    elif axis == 5:
        out = (
            data[:, :, :, :, :, ind_f] * (1 - delta)
            + data[:, :, :, :, :, ind_c] * delta
        )
    else:
        print("Only resampling up fifth axis is supported")
        raise NameError("linresample failed")
    return out


def interp_rat(rat, samples):
    """Read and interpolate samples from rat

    Parameters
    ----------
    rat :
        rat object
    samples :
        a tuple with the new axes. The tuple should have the
        same number of elements as we have dimensions

    Returns
    -------

    """
    if len(rat.shape) != len(samples):
        print("Invalid axes")
        raise NameError("interp_rat failed")
    rat_block = ()
    for dim in range(len(samples)):
        t_block = (
            int(np.floor(samples[dim].min()).astype(int)),
            int(np.ceil(samples[dim].max()).astype(int) + 1),
        )
        rat_block = rat_block + t_block
    data = rat.read(block=rat_block)
    for dim in range(len(samples)):
        data = linresample(
            data, samples[dim] - np.floor(samples[dim].min()), axis=dim
        )

    return data


def basemap_interp(
    datain, xin, yin, xout, yout, interpolation="NearestNeighbour"
):

    """Interpolates a 2D array onto a new grid (only works for linear grids),
       with the Lat/Lon inputs of the old and new grid. Can perfom nearest
       neighbour interpolation or bilinear interpolation (of order 1)'

       This is an extract from the basemap module (truncated)

    Parameters
    ----------
    datain :

    xin :

    yin :

    xout :

    yout :

    interpolation :
         (Default value = "NearestNeighbour")

    Returns
    -------

    """

    # Mesh Coordinates so that they are both 2D arrays
    xout, yout = np.meshgrid(xout, yout)

    # compute grid coordinates of output grid.
    delx = xin[1:] - xin[0:-1]
    dely = yin[1:] - yin[0:-1]

    xcoords = (len(xin) - 1) * (xout - xin[0]) / (xin[-1] - xin[0])
    ycoords = (len(yin) - 1) * (yout - yin[0]) / (yin[-1] - yin[0])

    xcoords = np.clip(xcoords, 0, len(xin) - 1)
    ycoords = np.clip(ycoords, 0, len(yin) - 1)

    # Interpolate to output grid using nearest neighbour
    if interpolation == "NearestNeighbour":
        xcoordsi = np.around(xcoords).astype(np.int32)
        ycoordsi = np.around(ycoords).astype(np.int32)
        dataout = datain[ycoordsi, xcoordsi]

    # Interpolate to output grid using bilinear interpolation.
    elif interpolation == "Bilinear":
        xi = xcoords.astype(np.int32)
        yi = ycoords.astype(np.int32)
        xip1 = xi + 1
        yip1 = yi + 1
        xip1 = np.clip(xip1, 0, len(xin) - 1)
        yip1 = np.clip(yip1, 0, len(yin) - 1)
        delx = xcoords - xi.astype(np.float32)
        dely = ycoords - yi.astype(np.float32)
        dataout = (
            (1.0 - delx) * (1.0 - dely) * datain[yi, xi]
            + delx * dely * datain[yip1, xip1]
            + (1.0 - delx) * dely * datain[yip1, xi]
            + delx * (1.0 - dely) * datain[yi, xip1]
        )

    return dataout
