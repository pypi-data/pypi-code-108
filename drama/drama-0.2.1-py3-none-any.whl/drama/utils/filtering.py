"""Some filtering functions."""
import numpy as np
from scipy import signal
from drama.utils.misc import optimize_fftsize

def smooth1d(data, window_len=11, window="flat", axis=0):
    """

    Parameters
    ----------
    data :

    window_len :
         (Default value = 11)
    window :
         (Default value = "flat")
    axis :
         (Default value = 0)

    Returns
    -------

    """
    if window == "flat":
        shp = np.array(data.shape).astype(np.int)
        # shp[axis] += int(window_len)
        out = np.zeros(shp, dtype=data.dtype)
        wlh1 = int(window_len / 2)
        wlh2 = window_len - wlh1
        wl = int(window_len)
        normf = np.zeros(shp[axis])

        for ind in range(window_len):
            # print(ind)
            i1 = int(ind - wlh1)
            i2 = i1 + shp[axis]
            if i1 <= 0:
                o1 = -i1
                i1 = 0
                o2 = shp[axis]
            else:
                i2 = shp[axis]
                o1 = 0
                o2 = shp[axis] - i1
            # print((i1, i2, o1, o2))

            normf[o1:o2] += 1
            if data.ndim == 1 or axis == 0:
                out[o1:o2] += data[i1:i2]
            elif axis == 1:
                out[:, o1:o2] += data[:, i1:i2]
            elif axis == 2:
                out[:, :, o1:o2] += data[:, :, i1:i2]
        shpn = np.ones_like(shp)
        shpn[axis] = shp[axis]
        out /= normf.reshape(shpn)
        # print(normf)
        return out
    else:
        raise ValueError("1d Smoothing with non flat window not yet supported")


def smooth(data, window_len=11, window="flat", axis=None, force_fft=False):
    """Smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        Works with 1-D and 2-D arrays.

    Parameters
    ----------
    data :
        Input data
    window_len :
        Dimension of the smoothing window; should be an odd integer (Default value = 11)
    window :
        Type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'.
        Flat window will produce a moving average smoothing. (Default value = "flat")
    axis :
        if set, then it smoothes only over that axis (Default value = None)
    force_fft :
        force use of fftconvolve to overide use of direct implementation for flat windows (Default value = False)

    Returns
    -------
    type
        the smoothed signal

    """

    if data.ndim > 2:
        raise ValueError("Arrays with ndim > 2 not supported")

    if (window_len < 3 and window != "flat") or window_len < 2:
        return data

    if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError("Window type not supported")

    if window == "flat" and ((axis is not None) or (data.ndim == 1)):
        if axis is None:
            axis_ = 0
        else:
            axis_ = axis
        return smooth1d(data, window_len, axis=axis_)

    # Calculate Kernel
    if window == "flat":
        w = np.ones(window_len)
    else:
        w = eval("np." + window + "(window_len)")

    # Smooth
    if data.ndim > 1:
        if axis is None:
            w = np.sqrt(np.outer(w, w))
        elif axis == 0:
            w = w.reshape((w.size, 1))
        else:
            w = w.reshape((1, w.size))

    y = signal.fftconvolve(data, w / w.sum(), mode="same")

    return y


def gaussian_window(x, y ,w_u, w_v=None, theta_r=0):
    """Calculates a Gaussian window"""
    if w_v is None:
        w_v = w_u
    s_u = w_u / 2
    s_v = w_v / 2
    rot = np.array([[np.cos(theta_r), np.sin(theta_r)] , [-np.sin(theta_r), np.cos(theta_r)]])
    u = rot[0, 0] * x + rot[0,1] * y
    v = rot[1, 0] * x + rot[1,1] * y
    return 1/(2 * np.pi * s_u * s_v) * np.exp(-u**2 / (2 * s_u**2)) * np.exp(-v**2 / (2 * s_v**2))


class GradientFilter(object):
    """Implements gradient estimators for noisy data.

    Parameters
    ----------
    dx :
        sampling in the x (axis=1) dimension
    dy :
        sampling in the y (axis=0) dimension
    res_x :
        output resolution in x-dimension
    res_y :
        output resolution in x-dimension
    edge_data:
        True if data is at the leading edge of the grid

    """

    def __init__(self, dx, dy, res_x, res_y, type='gaussian', edge_data=False):
        self.dx = dx
        self.dy = dy
        self.res_x = res_x
        self.res_y = res_y
        nptsx = optimize_fftsize(int(res_x / dx * 5), 2)
        nptsy = optimize_fftsize(int(res_y / dy * 5), 2)
        if not edge_data:
            nptsx = nptsx + 1
            nptsy = nptsy + 1
        x = - (np.arange(nptsx) * dx - nptsx * dx/2 + dx/2).reshape((1, nptsx))
        y = - (np.arange(nptsy) * dy - nptsy * dy/2 + dy/2).reshape((nptsy, 1))
        self.win = gaussian_window(x, y, self.res_x, self.res_y)
        self.gradx_irf = self.win * x / np.sum(self.win * x**2)
        self.grady_irf = self.win * y / np.sum(self.win * y**2)

    def gradient(self, data):
        grad_x = signal.fftconvolve(data, self.gradx_irf, mode="same")
        grad_y = signal.fftconvolve(data, self.grady_irf, mode="same")
        return grad_x, grad_y
# %%
if __name__ == '__main__':
    from matplotlib import pyplot as plt
    dx = 1
    nptsx = 3
    x = - (np.arange(nptsx) * dx - nptsx * dx/2 + dx/2).reshape((1, nptsx))
    x
    gf = GradientFilter(250, 250, 2000, 800)
    plt.figure()
    plt.imshow(gf.gradx_irf, aspect='auto', origin='lower')
    plt.colorbar()
    data = np.linspace(0, 100, 1000).reshape((1, 1000)) + np.zeros((1000, 1000))
    data = data + np.random.randn(*data.shape)
    ddatadx, ddatady = gf.gradient(data)
    print(np.median(ddatadx))
    print(100/1000/250)
    print(ddatadx[500, 500])
