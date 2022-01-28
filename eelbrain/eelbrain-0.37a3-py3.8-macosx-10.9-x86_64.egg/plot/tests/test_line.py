from eelbrain import datasets, plot
from eelbrain.testing import hide_plots


@hide_plots
def test_linestack():
    "Test plot.LineStack()"
    ds = datasets.get_uts()
    p = plot.LineStack(ds[:10, 'uts'])
    ax = p.figure.axes[0]
    assert ax.get_xlim() == (-0.2, .79)
    p.set_xlim(.1, .4)
    assert ax.get_xlim() == (.1, .4)
    p.close()
