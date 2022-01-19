import matplotlib.pyplot as plt
from unittest.case import TestCase

from mpl_format.figures.figure_formatter import FigureFormatter


class TestFigureFormatter(TestCase):

    def test_init_with_figure_gives_correct_axes_shape(self):

        fig, axes = plt.subplots(nrows=3, ncols=2)
        ff = FigureFormatter(fig)
        self.assertEqual(ff.axes.shape, axes.shape)
