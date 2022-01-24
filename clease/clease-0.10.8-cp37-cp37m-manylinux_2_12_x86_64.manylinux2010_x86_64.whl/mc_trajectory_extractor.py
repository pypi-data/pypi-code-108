import logging
import numpy as np
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


class MCTrajectoryExtractor:
    """
    Class that extracts structures that are related by two atoms swap from
    a list of atoms
    """

    def is_related_by_swap(self, atoms1, atoms2):
        """
        Check if the second atom can be obtained by swapping two
        atoms
        """
        # pylint: disable=no-self-use
        if len(atoms1) != len(atoms2):
            return False

        differ1 = []
        differ2 = []
        for n1, n2 in zip(atoms1.numbers, atoms2.numbers):
            if n1 != n2:
                differ1.append(n1)
                differ2.append(n2)

        if len(differ1) != 2:
            return False

        return sorted(differ1) == sorted(differ2)

    def find_swaps(self, all_atoms):
        """
        Extract paths links all entries that are connected by swaps
        """
        swaps = []
        for i, atoms1 in enumerate(all_atoms):
            for j, atoms2 in enumerate(all_atoms[i + 1:]):
                if self.is_related_by_swap(atoms1, atoms2):
                    swaps.append((i, i + j + 1))
        return swaps

    def swap_energy_deviations(self, swaps, e_pred, e_ref):
        """
        Calculate the energy deviation between the energy difference in e_ref
        and the energy difference in e_pred

        Parameters:

        swaps: list
            List of tuples with swaps (e.g. [(0, 3), (2, 8)]). Can be obtained
            from find_swaps

        e_pred: list
            List of energies prediced for all energy calculations. Note that
            this should be total energies (not normalised per atom)

        e_ref: list
            List of energies from for instance DFT. Should be total energy, not
            normalised per atom.
        """
        # pylint: disable=no-self-use
        dev = []
        for s in swaps:
            dE_pred = e_pred[s[0]] - e_pred[s[1]]
            dE_ref = e_ref[s[0]] - e_ref[s[1]]
            dev.append(dE_pred - dE_ref)
        return dev

    def gaussian(self, x, mu, var):
        """
        Return the gaussian distribution

        Parameters:

        x: np.ndarray
            Values at which to evaluate the gaussian

        mu: float
            Expecteation value

        var: float
            Variance
        """
        # pylint: disable=no-self-use
        return np.exp(-(x - mu)**2 / (2 * var)) / np.sqrt(2 * np.pi * var)

    def plot_swap_deviation(self, dev):
        """
        Creates a plot with the distribution of the deviations
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        hist, bins = np.histogram(np.array(dev), bins='auto')
        dx = bins[1] - bins[0]
        ax.plot(bins[1:] - 0.5 * dx, hist / np.trapz(hist, dx=dx), 'o', mfc='none', color='grey')
        ax.set_xlabel("Energy deviation (eV)")
        ax.set_ylabel("Probability Density")
        mu = np.mean(dev)
        var = np.var(dev)
        logger.info("Mean dev. %.4f eV", mu)
        logger.info("Standard deviation %.4f eV", np.sqrt(var))

        rng = bins[-1] - bins[0]
        x = np.linspace(bins[0] - 0.2 * rng, bins[-1] + 0.2 * rng, 100)
        y = self.gaussian(x, mu, var)
        ax.plot(x, y, color="#3c362b")
        x = np.linspace(mu - np.sqrt(var), mu + np.sqrt(var), 100)
        y = self.gaussian(x, mu, var)
        ax.fill_between(x, y, color="#8c361f", alpha=0.3)

        x = np.linspace(mu + np.sqrt(var), mu + 2 * np.sqrt(var), 100)
        y = self.gaussian(x, mu, var)
        ax.fill_between(x, y, color="#5b4930", alpha=0.3)

        x = np.linspace(mu - 2 * np.sqrt(var), mu - np.sqrt(var), 100)
        y = self.gaussian(x, mu, var)
        ax.fill_between(x, y, color="#5b4930", alpha=0.3)
        return fig
