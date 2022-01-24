import numpy as np
import scipy.interpolate
from .translation import DetectorTranslationAlongBeam
from ..misc.filters import correct_spikes
from ..resources.logger import LoggerOrPrint

def estimate_flat_distortion(
    flat, image, tile_size=100, interpolation_kind="linear", padding_mode="edge", correction_spike_threshold=None, logger=None
):
    """
    Estimate the wavefront distortion on a flat image, from another image.

    Parameters
    ----------
    flat: np.array
        The flat-field image to be corrected
    image: np.ndarray
        The image to correlate the flat against.
    tile_size: int
        The wavefront corrections are calculated by correlating the
        image to the flat, region by region. The regions are tiles of size tile_size
    interpolation_kind: "linear" or "cubic"
        The interpolation method used for interpolation
    padding_mode: string
        Padding mode. Must be valid for np.pad
        when wavefront correction is applied, the corrections are first found for the tiles,
        which gives the shift at the center of each tiled. Then, to interpolate the corrections,
        at the positions f every pixel, on must add also the border of the extremal tiles.
        This is done by padding with a width of 1, and using the mode given 'padding_mode'.
    correction_spike_threshold: float, optional
        By default it is None and no spike correction is performed on the shifts grid which is found by correlation.
        If set to a float, a spike removal will be applied using such threshold

    Returns
    --------
    coordinates: np.ndarray
        An array having dimensions (flat.shape[0], flat.shape[1], 2)
        where each coordinates[i,j] contains the coordinates of the position
        in the  image "flat" which correlates to the pixel (i,j) in the  image "im2".
    """
    logger = LoggerOrPrint(logger)
    starts_r = np.array(range(0, image.shape[0] - tile_size, tile_size))
    starts_c = np.array(range(0, image.shape[1] - tile_size, tile_size))
    cor1 = np.zeros([len(starts_r), len(starts_c)], np.float32)
    cor2 = np.zeros([len(starts_r), len(starts_c)], np.float32)

    shift_finder = DetectorTranslationAlongBeam()
    for ir, r in enumerate(starts_r):
        for ic, c in enumerate(starts_c):
            try:
                coeff_v, coeff_h, shifts_vh_per_img = shift_finder.find_shift(
                    np.array([image[r : r + tile_size, c : c + tile_size], flat[r : r + tile_size, c : c + tile_size]]),
                    np.array([0, 1]),
                    return_shifts=True,
                    low_pass=(1.0, 0.3),
                    high_pass=(tile_size, tile_size * 0.3),
                )
                cor1[ir, ic], cor2[ir, ic] = shifts_vh_per_img[1]

            except ValueError as e:
                if "positions are outside" in str(e):
                    logger.debug(str(e))
                    cor1[ir, ic], cor2[ir, ic] = (0, 0)
                else:
                    raise

    cor1[np.isnan(cor1)] = 0
    cor2[np.isnan(cor2)] = 0

    if correction_spike_threshold is not None:
        cor1 = correct_spikes(cor1, correction_spike_threshold)
        cor2 = correct_spikes(cor2, correction_spike_threshold)

    # TODO implement the previous spikes correction in CCDCorrection - median_clip
    # spikes_corrector = CCDCorrection(cor1.shape, median_clip_thresh=3, abs_diff=True, preserve_borders=True)
    # cor1 = spikes_corrector.median_clip_correction(cor1)
    # cor2 = spikes_corrector.median_clip_correction(cor2)

    cor1 = np.pad(cor1, ((1, 1), (1, 1)), mode=padding_mode)
    cor2 = np.pad(cor2, ((1, 1), (1, 1)), mode=padding_mode)

    hp = np.concatenate([[0.0], starts_c + tile_size * 0.5, [image.shape[1]]])
    vp = np.concatenate([[0.0], starts_r + tile_size * 0.5, [image.shape[0]]])

    h_ticks = np.arange(image.shape[1]).astype(np.float32)
    v_ticks = np.arange(image.shape[0]).astype(np.float32)

    foo = scipy.interpolate.interp2d(hp, vp, cor1, kind=interpolation_kind)
    cor1 = foo(h_ticks, v_ticks)

    foo = scipy.interpolate.interp2d(hp, vp, cor2, kind=interpolation_kind)
    cor2 = foo(h_ticks, v_ticks)

    hh = np.arange(image.shape[1]).astype(np.float32)
    vv = np.arange(image.shape[0]).astype(np.float32)
    unshifted_v, unshifted_h = np.meshgrid(vv, hh, indexing="ij")

    shifted_v = unshifted_v - cor1
    shifted_h = unshifted_h - cor2

    coordinates = np.transpose(np.array([shifted_v, shifted_h]), axes=[1, 2, 0])

    return coordinates
