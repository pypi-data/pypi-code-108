from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from numpy import ndarray
from pandas.core.indexes.numeric import Float64Index
from scipy.optimize import curve_fit

from openqlab.analysis.electromagnetic_wave import ElectromagneticWave
from openqlab.conversion.utils import human_readable
from openqlab.io.data_container import DataContainer
from openqlab.plots.gaussian_beam import beam_profile


class GaussianBeam(ElectromagneticWave):
    """
    Represents a Gaussian beam with a complex gaussian beam parameter q.
    """

    def __init__(self, q: complex, wavelength: float) -> None:
        if wavelength <= 0:
            raise ValueError("Wavelength must be a positiv number")
        super().__init__(wavelength)
        self._q = q

    @classmethod
    def from_waist(cls, w0: float, z0: float, wavelength: float) -> "GaussianBeam":
        """Create Gaussian beam from waist size and position.

        Parameters
        ----------
        w0: float
            Waist size in meters
        z0: float
            Waist position in meters
        wavelength: float
            Wavelength in meters
        """
        return cls(1j * (np.pi * w0 ** 2 / wavelength) - z0, wavelength)

    def propagate(self, d):
        """
        Returns the beam parameter after free-space propagation of d
        """
        return GaussianBeam(self._q + d, self._wavelength)

    def get_profile(
        self, zpoints: Union[Float64Index, ndarray, float]
    ) -> Union[ndarray, Float64Index, float]:
        """
        Returns the beam width at points zpoints along the beam axis.
        """
        quotient = (self._q.real + zpoints) / self._q.imag
        return self.w0 * np.sqrt(1 + quotient ** 2)

    @property
    def wavelength(self) -> Union[float, np.ndarray]:
        return self._wavelength

    @property
    def w0(self) -> Union[float, np.ndarray]:
        """
        Waist size in meters.
        """
        return np.sqrt(self._q.imag * self._wavelength / np.pi)

    @property
    def z0(self) -> Union[float, np.ndarray]:
        """
        The position of the beam waist on the z-axis in meters.
        """
        return -self._q.real  # pylint: disable=invalid-unary-operand-type

    @property
    def zR(self) -> Union[float, np.ndarray]:
        return self._q.imag

    @property
    def R(self) -> float:
        qi = 1 / self._q
        if qi.real == 0:
            return np.infty
        return 1 / (qi.real)

    @property
    def w(self) -> Union[float, np.ndarray]:
        return self.get_profile(0.0)

    @property
    def divergence(self) -> Union[float, np.ndarray]:
        """Beam divergence in radians."""
        return np.arctan(self._wavelength / np.pi / self.w0)

    # TODO enable with useful types
    # def __repr__(self) -> str:
    # return "w0={w0} @ z0={z0}".format(
    # w0=human_readable(self.w0, "m"), z0=human_readable(self.z0, "m")
    # )


def fit_beam_data(
    data: pd.DataFrame,
    wavelength: float,
    bounds: Tuple[List[float], List[float]] = ([0, -np.inf], [np.inf, np.inf]),
    guess_w0: float = 300e-6,
    guess_z0: float = 0.0,
    plot: bool = True,
    print_results: bool = True,
) -> DataContainer:
    """

    Parameters
    ----------
    data
        Data to fit containing the position data in meters as index and the 1/e^2 (13%) radius in meters as columns for different beams.
    wavelength
        Wavelength of the light in m
    bounds
        Lower and upper bounds for the fit parameters in meters in the form ([w0_lower,z0_lower],[w0_upper,z0_upper]).
    guess_w0
        Initial estimate of the beam waist in meters.
    guess_z0
        Initial estimate of the waist position in meters.
    plot
        Create plot after fitting.
    print_results
        Print results in a human readable form.

    Returns
    -------
    Dataframe
        Fit results with errors
    """
    initial_guess = [guess_w0, guess_z0]

    def _fit_function(z, w, z0):
        return GaussianBeam.from_waist(w, z0, wavelength).get_profile(z)

    def _fit_beam(beam_data: pd.Series):
        beam_data = beam_data.dropna()
        popt, pcov = curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
            _fit_function, beam_data.index, beam_data, bounds=bounds, p0=initial_guess
        )
        perr = np.sqrt(np.diag(pcov))
        return pd.Series(
            data=[popt[0], perr[0], popt[1], perr[1]],
            index=["w0", "w0_error", "z0", "z0_error"],
        )

    results = DataContainer(data.apply(_fit_beam))
    results.header["wavelength"] = wavelength
    if plot:
        label_template = "{name}: {w0}m @ {z0}m"
        beams = {
            label_template.format(
                name=name, w0=human_readable(beam["w0"]), z0=human_readable(beam["z0"])
            ): GaussianBeam.from_waist(
                w0=beam["w0"], z0=beam["z0"], wavelength=wavelength
            )
            for name, beam in results.iteritems()
        }
        beam_profile(beams, data=data)
    if print_results:
        for name, result in results.iteritems():
            print(
                u"{name}: ({w0:.1f} ± {w0_e:.1f})µm @ ({z0:.3f} ± {z0_e:.3f})cm".format(
                    name=name,
                    w0=result["w0"] * 1e6,
                    w0_e=result["w0_error"] * 1e6,
                    z0=result["z0"] * 1e2,
                    z0_e=result["z0_error"] * 1e2,
                )
            )
    return results
