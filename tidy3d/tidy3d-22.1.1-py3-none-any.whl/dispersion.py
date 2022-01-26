import math
import numpy as np
from .constants import C_0, HBAR, complex_
from .utils.log import log_and_raise
from .utils.em import eps_pole_residue
from .material import Medium

class DispersionModel(Medium):
    """Base class for a model of material dispersion.
    """

    def __init__(self, eps_inf=1.0, poles=None, name=None):
        """Initialize a medium with dispersion defined by the pole-residue 
        model,

        .. math::
            
            \\epsilon(\\omega) = \\epsilon_\\infty - \\sum_p 
            \\left[\\frac{c_p}{j \\omega + a_p} +
            \\frac{c_p^*}{j \\omega + a_p^*}\\right]
        
        Parameters
        ----------
        eps_inf : float or array_like
            The relative permittivity at infinite frequency, usually 1. It can
            be anisotropic if defined as an array of three elements.
        poles : list of the form [(:math:`a_0, c_0`), ...], optional
            (Hz) A list of the (a, c) coefficients. Added isotropically to 
            all three components.
        """
        super().__init__(name, epsilon=eps_inf)

        if poles is None:
            self.poles = []
        else:
            self.poles = [(pole[0], pole[1]) for pole in poles]


    def epsilon(self, freqs=None, component="average"):
        """Evaluate the (complex) relative permittivity of the medium.

        Parameters
        ----------
        freqs : array_like or None, optional
            (Hz) Array of frequencies at which to query the permittivity. If
            ``None``, the instantaneous :math:`\\epsilon_\\infty` is returned.
        component : str, optional
            One of {'average', 'xx', 'yy', 'zz'}, denoting which component of
            the permittivity to be returned.

        Returns
        -------
        array_like
            The permittivity values, same shape as ``freqs``.
        """
        if freqs is None:
            return self._eps_component(self.eps[None, :], component)

        pole_term = eps_pole_residue(self.poles, freqs)
        eps = np.tile(self.eps.astype(complex_), (pole_term.size, 1))
        eps += pole_term.reshape((pole_term.size, 1))

        return self._eps_component(eps, component)


class Sellmeier(DispersionModel):
    """Sellmeier dispersion refractive index model.
    """

    def __init__(self, coeffs, name=None):
        """ Define a material with Sellmeier dispersion.
        
        Parameters
        ----------
        coeffs : list, of the form [(:math:`B_0, C_0`), ...]
            The dispersion formula is:

            .. math::
            
                n^2 - 1 = \\sum_p \\frac{B_p \\lambda^2}{\\lambda^2 - C_p}

            where :math:`\\lambda` is in microns.
        """
        eps_inf = 1
        poles = []
        for BC in coeffs:
            # C enters with units of microns**2, B is unitless
            # If we let c = alpha*1j, a = beta*1j, then
            # B = 2*alpha/beta, C = (2*pi*c0/beta)**2
            beta = 2*np.pi*C_0 / np.sqrt(BC[1]) # This has units of rad/s
            alpha = -0.5*beta*BC[0]
            a = 1j*beta
            c = 1j*alpha
            poles.append((a, c))

        super().__init__(eps_inf, poles, name)

    @classmethod
    def from_dn(cls, wl, n, dn_dwl, name=None):
        """ Create a 1-pole Sellmeier model from dispersion data.

        Parameters
        ----------
        wl : float
            (micron) The center wavelength.
        n : float
            The refractive index at the center wavelength.
        dn_dwl : float
            (1/micron) Refractive index dispersion; derivative of
            refractive index with respect to wavelength.
        """

        if dn_dwl > 0:
            log_and_raise("dn_dwl must be smaller than zero.", NotImplementedError)

        nm1 = n - 1
        ld = wl*dn_dwl
        B = nm1*nm1 / (nm1 - 0.5*ld)
        C = -wl*wl*ld / (2*nm1 - ld)
        coeffs = [(B, C)]
        return cls(coeffs, name);

class Lorentz(DispersionModel):
    """Lorentz dispersion permittivity model.
    """

    def __init__(self, eps_inf, coeffs, name=None):
        """ Define a material with Lorentz dispersion.
        
        Parameters
        ----------
        eps_inf: float
            The relative permittivity at infinite frequency, usually 1.
        coeffs : list, of the form [(:math:`\\Delta\\epsilon_0, f_0, \\delta_0`), ...]
            The dispersion formula is:
            
            .. math::

                \\epsilon(f) = \\epsilon_\\infty + \\sum_p 
                \\frac{\\Delta\\epsilon_p f_p^2}{f_p^2 - 2jf\\delta_p - f^2}

            where :math:`f, f_p, \\delta_p` are in Hz.
        """

        poles = []
        for c in coeffs:
            w = 2*math.pi*c[1]
            d = 2*math.pi*c[2]
            if d > w:
                r = np.sqrt(d*d-w*w)
                a0 = -d+r
                c0 = c[0]*w*w/4/r
                a1 = -d-r
                c1 = -c0
                poles.append((a0,c0))
                poles.append((a1,c1))
            else:
                r = np.sqrt(w*w - d*d)
                a = -d - 1j*r
                c = 0.5j*c[0]*w*w / r
                poles.append((a, c))

        super().__init__(eps_inf, poles, name)

class Drude(DispersionModel):
    """Drude dispersion permittivity model.
    """

    def __init__(self, eps_inf, coeffs, name=None):
        """ Define a material with Drude dispersion.
        
        Parameters
        ----------
        eps_inf: float
            The relative permittivity at infinite frequency, usually 1.
        coeffs : list, of the form [(:math:`f_i, \\delta_i`), ...]
            The dispersion formula is:
            
            .. math::

                \\epsilon(f) = \\epsilon_\\infty - \\sum_i
                \\frac{ f_i^2}{jf\\delta_i + f^2}

            where :math:`f, f_p, \\delta_p` are in Hz.
        """

        poles = []
        for c in coeffs:
            w = 2*math.pi*c[0]
            d = 2*math.pi*c[1]

            a0 = 0
            c0 = w*w/2/d
            a1 = -d
            c1 = -c0
            poles.append((a0,c0))
            poles.append((a1,c1))

        super().__init__(eps_inf, poles, name)

class Debye(DispersionModel):
    """Debye dispersion permittivity model.
    """
    
    def __init__(self, eps_inf, coeffs, name=None):
        """ Define a material with Debye dispersion.
        
        Parameters
        ----------
        eps_inf: float
            The relative permittivity at infinite frequency, usually 1.  
        coeffs : list, of the form [(:math:`\\Delta\\epsilon_0, \\tau_0`), ...]
            The dispersion formula is:
            
            .. math::

                \\epsilon(f) = \\epsilon_\\infty + \\sum_p 
                \\frac{\\Delta\\epsilon_p}{1 - jf\\tau_p}
            
            where :math:`f` is in Hz, and :math:`\\tau_p` is in s.
        """

        poles = []
        for c in coeffs:
            a = -2*math.pi / c[1]
            c = -0.5*c[0]*a
            poles.append((a, c))

        super().__init__(eps_inf, poles, name)