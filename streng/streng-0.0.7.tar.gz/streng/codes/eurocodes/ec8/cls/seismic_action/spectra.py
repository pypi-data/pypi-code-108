import numpy as np
from dataclasses import dataclass

from ...raw.ch3.seismic_action import spectra as spec_raw


@dataclass
class SpectraEc8:
    """Eurocode 8 response spectra

    .. note::
        If αgR values are given in g, displacements and velocities should be multiplied with 9.81

    .. uml::

        class SpectraEc8 {
        .. attributes ..
        + αgR (float)
        + γI (float)
        + ground_type (str)
        + spectrum_type (int)
        + η (float)
        + q (float)
        + β (float)
        .. properties ..
        + dg()
        + getAllSpectra0to4()
        .. methods ..
        + Se(T) (float)
        + SDe(T) (float)
        + Sd(T) (float)
        }

    Attributes:
        αgR (float): reference peak ground acceleration on type A ground
        γI (float): importance factor
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2
        η (float): value of the damping correction factor
        q (float): behaviour factor
        β (float): lower bound factor for the horizontal design spectrum. Recommended value for β is 0.2

    """
    αgR: float
    γI: float
    ground_type: str
    spectrum_type: int
    η: float = 1.0
    q: float = 1.0
    β: float = 0.2

    def __post_init__(self):
        self.αg = self.γI * self.αgR
        self.S = spec_raw.S(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TB = spec_raw.TB(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TC = spec_raw.TC(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TD = spec_raw.TD(ground_type=self.ground_type, spectrum_type=self.spectrum_type)

    def Se(self, T):
        """
        Args:
            T(float): Period

        Returns:
            float: The elastic acceleration response spectrum

        """
        return spec_raw.Se(T, self.αg, self.S, self.TB, self.TC, self.TD, self.η)

    def SDe(self, T):
        """
        Args:
            T(float): Period

        Returns:
            float: The elastic displacement response spectrum

        """
        return spec_raw.SDe(T, self.Se(T))

    @property
    def dg(self):
        """float: Design ground displacement"""
        return spec_raw.dg(self.αg, self.S, self.TC, self.TD)

    def Sd(self, T):
        """
        Args:
            T(float): Period

        Returns:
            float: Design spectrum for elastic analyses

        """
        return spec_raw.Sd(T, self.αg, self.S, self.TB, self.TC, self.TD, self.q, self.β)

    @property
    def getAllSpectra0to4(self):
        """ dict: A dictionary of numpy arrays with spectral values in the range 0-4sec"""
        _T_range = np.linspace(0.01, 4, 400)

        _Se = self.Se(_T_range)
        _SDe = self.SDe(_T_range)
        _Sv = _Se / (2 * np.pi / _T_range)
        _Sd = self.Sd(_T_range)

        _T_range = np.append(0., _T_range)
        _Se = np.append(self.αg * self.S, _Se)
        _SDe = np.append(0., _SDe)
        _Sv = np.append(0., _Sv)
        _Sd = np.append(self.αg * self.S * 2.0 / 3.0, _Sd)

        _data = {'T': _T_range,
                 'Se': _Se,
                 'Sv': _Sv,
                 'SDe': _SDe,
                 'Sd': _Sd}

        return _data

