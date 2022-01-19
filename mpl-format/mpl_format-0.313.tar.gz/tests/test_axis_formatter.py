from unittest.case import TestCase

from pandas import Series

from mpl_format.axes import AxesFormatter


class TestAxisFormatter(TestCase):

    def setUp(self) -> None:

        self.data = Series({
            1_000: 3, 2_000: 5, 3_000: 4, 4_000: 6, 5_000: 5
        })
        self.data_pct = Series({
            0.1: 3, 0.2: 5, 0.3: 4, 0.4: 6, 0.5: 5
        })

    def test_set_format_integer_bar(self):

        axf = AxesFormatter()
        self.data.plot.bar(ax=axf.axes)
        axf.x_axis.set_format_integer(categorical=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['1,000', '2,000', '3,000', '4,000', '5,000']
        self.assertListEqual(expected, actual)

    def test_set_format_integer_k_bar(self):

        axf = AxesFormatter()
        self.data.plot.bar(ax=axf.axes)
        axf.x_axis.set_format_integer(categorical=True, kmbt=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['1K', '2K', '3K', '4K', '5K']
        self.assertListEqual(expected, actual)

    def test_set_format_integer_line(self):

        axf = AxesFormatter()
        self.data.plot.line(ax=axf.axes)
        axf.x_axis.set_format_integer()
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['500', '1,000', '1,500', '2,000', '2,500',
                    '3,000', '3,500', '4,000', '4,500', '5,000', '5,500']
        self.assertListEqual(expected, actual)

    def test_set_format_integer_k_line(self):

        axf = AxesFormatter()
        self.data.plot.line(ax=axf.axes)
        axf.x_axis.set_format_integer(kmbt=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['500', '1K', '1.5K', '2K', '2.5K',
                    '3K', '3.5K', '4K', '4.5K', '5K', '5.5K']
        self.assertListEqual(expected, actual)

    def test_set_format_currency_bar(self):

        axf = AxesFormatter()
        self.data.plot.bar(ax=axf.axes)
        axf.x_axis.set_format_currency(categorical=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['$1,000', '$2,000', '$3,000', '$4,000', '$5,000']
        self.assertListEqual(expected, actual)

    def test_set_format_currency_k_bar(self):

        axf = AxesFormatter()
        self.data.plot.bar(ax=axf.axes)
        axf.x_axis.set_format_currency(categorical=True, kmbt=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['$1K', '$2K', '$3K', '$4K', '$5K']
        self.assertListEqual(expected, actual)

    def test_set_format_currency_line(self):

        axf = AxesFormatter()
        self.data.plot.line(ax=axf.axes)
        axf.x_axis.set_format_currency()
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['$500', '$1,000', '$1,500', '$2,000', '$2,500',
                    '$3,000', '$3,500', '$4,000', '$4,500', '$5,000', '$5,500']
        self.assertListEqual(expected, actual)

    def test_set_format_currency_k_line(self):

        axf = AxesFormatter()
        self.data.plot.line(ax=axf.axes)
        axf.x_axis.set_format_currency(kmbt=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['$500', '$1K', '$1.5K', '$2K', '$2.5K',
                    '$3K', '$3.5K', '$4K', '$4.5K', '$5K', '$5.5K']
        self.assertListEqual(expected, actual)

    def test_set_format_percent_bar(self):

        axf = AxesFormatter()
        self.data_pct.plot.bar(ax=axf.axes)
        axf.x_axis.set_format_percent(categorical=True)
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['10%', '20%', '30%', '40%', '50%']
        self.assertListEqual(expected, actual)

    def test_set_format_percent_line(self):

        axf = AxesFormatter()
        self.data_pct.plot.line(ax=axf.axes)
        axf.x_axis.set_format_percent()
        axf.show()
        actual = axf.x_axis.tick_labels.texts
        expected = ['5%', '10%', '15%', '20%', '25%',
                    '30%', '35%', '40%', '45%', '50%', '55%']
        self.assertListEqual(expected, actual)
