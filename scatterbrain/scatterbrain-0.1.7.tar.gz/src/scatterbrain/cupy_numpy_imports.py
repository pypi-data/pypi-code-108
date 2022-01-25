# flake8: noqa
import os

import fitsio
import numpy as np

try:
    if os.getenv("USE_CUPY") in ["True", "T", "true"]:
        import cupy as xp
        from cupy import sparse

        def load_image_cupy(fname, cutout_size=2048, loc=None):
            return xp.asarray(load_image_numpy(fname, cutout_size=cutout_size, loc=loc))

        def load_image(fname, cutout_size=2048, loc=None):
            return load_image_cupy(fname, cutout_size=cutout_size, loc=loc).astype(
                xp.float32
            )

    else:
        raise ImportError

except ImportError:
    import numpy as xp
    from scipy import sparse

    def load_image(fname, cutout_size=2048, loc=None):
        return load_image_numpy(fname, cutout_size=cutout_size, loc=loc).astype(
            xp.float32
        )


def load_image_numpy(fname, cutout_size=2048, loc=None):
    if loc is None:
        image = np.asarray(fitsio.FITS(fname)[1][:cutout_size, 44 : 44 + cutout_size])
    else:
        if not isinstance(loc, (np.ndarray, list)):
            raise ValueError("Pass a 2x2 location")
        if not np.asarray(loc).shape == (2, 2):
            raise ValueError("Pass a 2x2 location")
        if not (np.asarray(loc) <= 2048).all():
            raise ValueError("Pass a location on the detector")
        if not (np.asarray(loc).dtype == int):
            raise ValueError("Pass integers.")
        image = np.asarray(
            fitsio.FITS(fname)[1][
                loc[0][0] : loc[0][1], 44 + loc[1][0] : 44 + loc[1][1]
            ]
        )
    image[~np.isfinite(image)] = 1e-5
    image[image <= 0] = 1e-5
    return image
