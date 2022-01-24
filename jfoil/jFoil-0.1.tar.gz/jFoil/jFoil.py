import numpy as np
import matplotlib.pyplot as plt


class jFoil:
    """ Joukowsky foil creator.

    Parameters:

    a - Radius of the pre-transformation cilinder. Approximately 1/4 of the final chord length.

    relThickness - Proportional to the thickness of the airfoil. Must be between 0 and 1. For airfoils, it is generally close to 0.9.

    beta - Curvature of the foil in degrees.

    [n] - number of samples that make the foil. Default 100. """

    def __init__(self, a, relThickness, beta, n=100):
        if relThickness < 0 or relThickness > 1:
            raise ValueError(
                "Bad value of airfoil thickness (relative thickness must be between 0 and 1)")

        self.a = a
        self.relThickness = relThickness
        self.beta = np.deg2rad(beta)

        self._theta = np.linspace(0, 2*np.pi, n)
        self.cilinder = self.a * (np.exp(1j*self._theta) - self.relThickness +
                                  np.exp(1j*self.beta))

        self.foil = _joukowskyTransform(
            self.cilinder, self.a * self.relThickness)

    def plotFoil(self, title='', grid=False):
        """  plotFoil """
        plt.plot(np.real(self.foil), np.imag(self.foil))
        plt.title(title)
        plt.axis("scaled")
        if grid:
            plt.grid()
        plt.show()

    def saveFoil(self, filename='foil.csv'):
        """ saveFoil """
        np.savetxt(filename, self.foil, fmt='%f;%f', header='x;y', comments='')

    def _plotCurrent(self, alpha=0, n=100):
        """ (WIP) plotCurrent """
        xlim, ylim = 3, 3
        alpha = np.deg2rad(alpha)

        velocity = 1
        circulation = 4 * np.pi * self.a * velocity * np.sin(alpha + self.beta)

        x, y = np.mgrid[-xlim:xlim:1j*n, -ylim:ylim:1j*n]

        z = x + 1j*y + self.a * self.relThickness - \
            self.a * np.exp(1j*self.beta)

        z *= np.abs(z) >= self.a

        f = _uniformCurrent(z, velocity, alpha) + \
            _dipole(z, velocity, self.a) - _rotor(z, circulation)

        psi = np.imag(f)

        plt.contour(x, y, psi, levels=50)
        plt.axis("scaled")
        plt.show()

    def plotCl(self, minAlpha=-5, maxAlpha=5, n=50):
        """ plotcL """
        minAlpha = np.deg2rad(minAlpha)
        maxAlpha = np.deg2rad(maxAlpha)

        alpha = np.linspace(minAlpha, maxAlpha, n)
        cL = 2*np.pi * np.sin(alpha + self.beta)

        plt.plot(np.rad2deg(alpha), cL)
        plt.xlabel("alpha (°)")
        plt.ylabel("cL")
        plt.grid()
        plt.show()


def _joukowskyTransform(z, b):
    return z + b**2 / z


def _uniformCurrent(z, uInf, alpha):
    return uInf * z * np.exp(1j*alpha)


def _dipole(z, uInf, a):
    return uInf * a**2 / z


def _rotor(z, circulation):
    return -1j / 2*np.pi * circulation * np.log(z)
