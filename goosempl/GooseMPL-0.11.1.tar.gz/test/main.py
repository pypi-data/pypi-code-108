import unittest

import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt


class Test_ticks(unittest.TestCase):
    """
    Functions generating ticks.
    """

    def test_log_ticks(self):

        ticks, labels = gplt.log_ticks((0, 3))
        self.assertEqual(list(ticks), [1, 10, 100, 1000])
        self.assertEqual(labels, [r"$10^{0}$", r"$10^{1}$", r"$10^{2}$", r"$10^{3}$"])

        ticks, labels = gplt.log_ticks((0, 3), keep=[0, -1])
        self.assertEqual(list(ticks), [1, 10, 100, 1000])
        self.assertEqual(labels, [r"$10^{0}$", "", "", r"$10^{3}$"])

    def test_log_ticks_plot(self):

        fig, ax = plt.subplots()

        ax.set_xlim([1, 1000])
        ax.set_ylim([10, 1000])

        ticks, labels = gplt.log_xticks()
        self.assertEqual(list(ticks), [1, 10, 100, 1000])
        self.assertEqual(labels, [r"$10^{0}$", r"$10^{1}$", r"$10^{2}$", r"$10^{3}$"])

        ticks, labels = gplt.log_yticks()
        self.assertEqual(list(ticks), [10, 100, 1000])
        self.assertEqual(labels, [r"$10^{1}$", r"$10^{2}$", r"$10^{3}$"])

        plt.close(fig)

    def test_log_minorticks(self):

        ticks, labels = gplt.log_minorticks((1, 10))
        self.assertEqual(list(ticks), [2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(labels, ["2", "3", "4", "5", "6", "7", "8", "9"])

    def test_log_minorticks_plot(self):

        fig, ax = plt.subplots()

        ax.set_xlim([0.1, 10])
        ax.set_ylim([0.01, 0.7])

        ticks, labels = gplt.log_minorxticks()
        self.assertEqual(
            list(ticks), [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 2, 3, 4, 5, 6, 7, 8, 9]
        )
        self.assertEqual(
            labels,
            [
                "0.2",
                "0.3",
                "0.4",
                "0.5",
                "0.6",
                "0.7",
                "0.8",
                "0.9",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
            ],
        )

        ticks, labels = gplt.log_minoryticks()
        self.assertTrue(
            np.allclose(
                ticks,
                [
                    0.02,
                    0.03,
                    0.04,
                    0.05,
                    0.06,
                    0.07,
                    0.08,
                    0.09,
                    0.2,
                    0.3,
                    0.4,
                    0.5,
                    0.6,
                    0.7,
                ],
            )
        )
        self.assertEqual(
            labels,
            [
                "0.02",
                "0.03",
                "0.04",
                "0.05",
                "0.06",
                "0.07",
                "0.08",
                "0.09",
                "0.2",
                "0.3",
                "0.4",
                "0.5",
                "0.6",
                "0.7",
            ],
        )

        plt.close(fig)


class Test_fit_powerlaw(unittest.TestCase):
    """
    Fit a powerlaw.
    """

    def test_prefactor_exponent(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * x ** 3.4
        prefactor, exponent, _ = gplt.fit_powerlaw(x, y)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))

    def test_prefactor(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * x ** 3.4
        prefactor, exponent, _ = gplt.fit_powerlaw(x, y, exponent=3.4)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))

    def test_exponent(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * x ** 3.4
        prefactor, exponent, _ = gplt.fit_powerlaw(x, y, prefactor=1.2)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))


class Test_fit_exp(unittest.TestCase):
    """
    Fit an exponential.
    """

    def test_prefactor_exponent(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        prefactor, exponent, _ = gplt.fit_exp(x, y)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))

    def test_prefactor_negative_exponent(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * -3.4)
        prefactor, exponent, _ = gplt.fit_exp(x, y)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, -3.4))

    def test_prefactor(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        prefactor, exponent, _ = gplt.fit_exp(x, y, exponent=3.4)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))

    def test_exponent(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        prefactor, exponent, _ = gplt.fit_exp(x, y, prefactor=1.2)
        self.assertTrue(np.isclose(prefactor, 1.2))
        self.assertTrue(np.isclose(exponent, 3.4))


class Test_fit_linear(unittest.TestCase):
    """
    Fit a linear.
    """

    def test_offset_slope(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        offset, slope, _ = gplt.fit_linear(x, y)
        self.assertTrue(np.isclose(offset, 1.2))
        self.assertTrue(np.isclose(slope, 3.4))

    def test_slope(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        offset, slope, _ = gplt.fit_linear(x, y, slope=3.4)
        self.assertTrue(np.isclose(offset, 1.2))
        self.assertTrue(np.isclose(slope, 3.4))

    def test_offset(self):

        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        offset, slope, _ = gplt.fit_linear(x, y, offset=1.2)
        self.assertTrue(np.isclose(offset, 1.2))
        self.assertTrue(np.isclose(slope, 3.4))


class Test_cdf(unittest.TestCase):
    """
    Cumulative probability density.
    """

    def test_simple(self):

        data = np.array([0, 0, 1, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        xr = np.array([0, 1, 2, 3, 4, 5])
        pr = np.array([2, 1, 1, 2, 3, 4]) / data.size

        p, x = gplt.cdf(data, less_equal=True)

        self.assertTrue(np.allclose(x, xr))
        self.assertTrue(np.allclose(p, np.cumsum(pr)))

        p, x = gplt.cdf(data)

        self.assertTrue(np.allclose(x, xr))
        self.assertTrue(np.allclose(p, np.cumsum([0] + pr.tolist())[:-1]))

        p, x = gplt.ccdf(data)

        self.assertTrue(np.allclose(x, xr))
        self.assertTrue(np.allclose(p, np.cumsum(pr[::-1])[::-1]))

        p, x = gplt.ccdf(data, greater_equal=False)

        self.assertTrue(np.allclose(x, xr))
        self.assertTrue(np.allclose(p, np.cumsum([0] + pr[::-1].tolist())[1::-1]))

        p, x = gplt.cdf(data)
        pc, xc = gplt.ccdf(data)

        self.assertTrue(np.allclose(x, xc))
        self.assertTrue(np.allclose(1 - p, pc))

    def test_random(self):

        data = np.random.random(10000)

        p, x = gplt.cdf(data)

        xp = np.linspace(0, 1, 100)
        pp = np.interp(xp, x, p)

        self.assertTrue(np.allclose(xp, pp, rtol=1e-1, atol=1e-1))

        p, x = gplt.ccdf(data)

        xp = np.linspace(0, 1, 100)
        pp = np.interp(xp, x, p)

        self.assertTrue(np.allclose(1 - xp, pp, rtol=1e-1, atol=1e-1))


class Test_bin(unittest.TestCase):
    """
    Bin data
    """

    def test_simple(self):

        xdata = np.array([1, 1, 3, 3, 3, 5, 5])
        ydata = np.array([2, 4, 1, 2, 3, 2, 4])
        bin_edges = np.array([0, 2, 4, 6])

        data = gplt.bin(xdata, ydata, bin_edges)

        self.assertTrue(np.allclose(data["x"], np.array([1, 3, 5])))
        self.assertTrue(np.allclose(data["y"], np.array([3, 2, 3])))
        self.assertTrue(np.allclose(data["xerr"], np.array([0, 0, 0])))
        self.assertTrue(
            np.allclose(data["yerr"], np.array([np.std([2, 4]), np.std([1, 2, 3]), np.std([2, 4])]))
        )

        median_data = gplt.bin(xdata, ydata, bin_edges, use_median=False)

        for key in data:
            self.assertTrue(np.allclose(data[key], median_data[key]))


class Test_histogram_norm(unittest.TestCase):
    """
    Histogram normalisation.
    """

    def test_density(self):

        data = [0, 0, 0, 1, 1, 2]
        bin_edges = [-0.5, 0.5, 1.5, 2.5]
        p = gplt.histogram_norm(*np.histogram(data, bins=bin_edges))
        q = gplt.histogram_norm(p, bin_edges)
        r, _ = np.histogram(data, bins=bin_edges, density=True)
        self.assertTrue(np.allclose(p, r))
        self.assertTrue(np.allclose(q, r))


class Test_histogram_bin_edges2midpoint(unittest.TestCase):
    """
    Midpoints of bins
    """

    def test_simple(self):
        bin_edges = [-0.5, 0.5, 1.5, 2.5]
        mid = [0, 1, 2]
        self.assertTrue(np.allclose(gplt.histogram_bin_edges2midpoint(bin_edges), mid))


class Test_histogram_bin_edges_integer(unittest.TestCase):
    """
    Bin edges.
    """

    def test_front(self):

        a = [0, 0.5, 1.5, 2.5]
        b = [0, 1.5, 2.5]
        self.assertTrue(np.allclose(gplt.histogram_bin_edges_integer(a), b))

    def test_middle(self):

        a = [0, 1.5, 1.6, 2.5]
        b = [0, 1.6, 2.5]
        self.assertTrue(np.allclose(gplt.histogram_bin_edges_integer(a), b))

    def test_back(self):

        a = [0, 1.5, 2.5, 2.6]
        b = [0, 1.5, 2.6]
        self.assertTrue(np.allclose(gplt.histogram_bin_edges_integer(a), b))


if __name__ == "__main__":

    unittest.main()
