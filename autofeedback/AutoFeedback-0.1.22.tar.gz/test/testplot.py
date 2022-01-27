import unittest
import AutoFeedback.plotchecks as pc
from AutoFeedback.plotclass import line
import matplotlib.pyplot as plt


class tmod:
    plt.plot([0, 1, 2], [0, 1, 4], 'r-', label='quadratic')
    plt.plot([0.5, 1.5], [1.5, 2.5], 'bD', label='linear')
    plt.legend()
    plt.axis([-1, 1, -2, 2])
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('z')
    fighand = plt.gca()
    line_data, patch_data, axes_data, labels, legend_data = \
        pc._extract_plot_elements(
            fighand, lines=True, axislabels=True, axes=True, legend=True)
    l1, l2 = line_data[0], line_data[1]


line1 = line([0, 1, 2], [0, 1, 4], linestyle=['-', 'solid'],
             colour=['r', 'red', (1.0, 0.0, 0.0, 1)],
             label='quadratic')

line2 = line([0.5, 1.5], [1.5, 2.5], marker=['D', 'd'],
             colour=['b', 'blue', (0.0, 0.0, 1.0, 1)],
             label='linear')

axislabels = ["x", "y", "z"]
axeslimits = [-1, 1, -2, 2]


class ExtractTests(unittest.TestCase):
    def test_legend_extract(self):
        assert (tmod.legend_data == ['quadratic', 'linear'])

    def test_axes_extract(self):
        assert (tmod.axes_data == axeslimits)

    def test_label_extract(self):
        assert (tmod.labels == axislabels)

    def test_line1_extract(self):
        x, y = zip(*tmod.l1.get_xydata())
        assert (x == (0., 1., 2.) and y == (0., 1., 4.))

    def test_line2_extract(self):
        x, y = zip(*tmod.l2.get_xydata())
        assert (x == (0.5, 1.5) and y == (1.5, 2.5))


class UnitTests(unittest.TestCase):
    def test_reorder(self):
        a = [pc._reorder([line2, line1], tmod.line_data)[i] for i in [1, 0]]
        b = [pc._reorder([line1, line2], tmod.line_data)[i] for i in [0, 1]]
        assert (a == b)

    def test_check_axes(self):
        assert (pc._check_axes([0, 1], [0, 1])
                and not pc._check_axes([0, 1], [1, 2]))

    def test_check_legend(self):
        assert (pc._check_legend(['this'], ['this'])
                and not pc._check_legend(['this'], ['that']))

    def test_check_empty_legend(self):
        assert (not pc._check_legend([], []))

    def test_check_linedata(self):
        assert (pc._check_linedata(tmod.l1, line1) and not
                pc._check_linedata(tmod.l1, line2))

    def test_check_colour(self):
        assert (pc._check_colour(tmod.l1, line1.colour) and not
                pc._check_colour(tmod.l2, line1.colour))

    def test_check_marker(self):
        assert (pc._check_marker(tmod.l2, line2.marker) and not
                pc._check_marker(tmod.l1, line2.marker))

    def test_check_linestyle(self):
        assert (pc._check_linestyle(tmod.l1, line1.linestyle) and not
                pc._check_linestyle(tmod.l2, line1.linestyle))

    def test_e_string(self):
        assert (pc._e_string('dataset', 'label')) == 'dataset("label")'


class SystemTests(unittest.TestCase):
    def test_check_plot(self):
        assert(pc.check_plot([line1, line2], expaxes=axeslimits,
                             explabels=axislabels,
                             explegend=True, modname='tmod'))

    def test_invert_order(self):
        assert(pc.check_plot([line2, line1], expaxes=axeslimits,
                             explabels=axislabels,
                             explegend=True, modname='tmod'))

    def test_partial(self):
        assert(pc.check_plot([line2], check_partial=True, expaxes=axeslimits,
                             explabels=axislabels,
                             explegend=True, modname='tmod'))
