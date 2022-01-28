# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from eelbrain import datasets, plot, NDVar
from eelbrain.testing import hide_plots, requires_mne_testing_data


@hide_plots
@requires_mne_testing_data
def test_glassbrain():
    ndvar = datasets.get_mne_stc(True, 'vol-7')

    # source space only
    p = plot.GlassBrain(ndvar.source)
    p.close()

    # single time points
    ndvar_30 = ndvar.sub(time=0.030)
    p = plot.GlassBrain(ndvar_30)
    p.close()
    # without arrows
    p = plot.GlassBrain(ndvar_30, draw_arrows=False)
    p.close()

    # time series
    p = plot.GlassBrain(ndvar)
    p.set_time(.03)
    p.close()

    # masked data
    import numpy as np
    h = ndvar.sub(time=0.030)
    mask = h.norm('space') < 6.15459575929912e-10  # precomputed _fast_abs_percentile(h)
    mask_x = np.repeat(h._ialign(mask), 3, h.get_axis('space'))
    mask = NDVar(mask_x, h.dims)
    y = h.mask(mask)
    p = plot.GlassBrain(y)
    p.close()
