import numpy as np
import logging

from .utils import listify, log_and_raise
from .utils.log import Tidy3DError
from .constants import int_, float_, EPSILON_0, C_0, pec_viz, pmc_viz

class Medium(object):
    """
    Base class for a custom defined material.
    """

    def __init__(self, name=None, **kwargs):
        """Define a material. Various input artuments are possible which
        define either frequency-independent material parameters, or a
        dispersive, frequency-dependent model.

        Parameters
        ----------
        epsilon : float or array_like, optional
            Real part of the dimensionless relative permittivity. For 
            anisotropic materials an array of three elements giving the
            main diagonal values of the permittivity tensor can be provided.
        sigma : float or array_like, optional
            (S/micron) Electric conductivity, s.t.
            ``Im(eps(omega)) = sigma/omega``, where ``eps(omega)`` is the
            complex permittivity at frequency omega. For anisotropic materials
            an array of three elements giving the main diagonal values of the 
            conductivity tensor can be provided.
        n : float, optional
            Real part of refractive index.
        k : float, optional
            Imaginary part of refractive index, where
            ``epsilon = (n + 1i*k)**2``.
        wl : float, optional
            (micron) Wavelength corresponding to n and k values.
        freq : float, optional
            (Hz) Frequency corresponding to n and k values.

        Note
        ----
        Only the following combinations of arguments are supported:

         * ``Medium(epsilon)``
         * ``Medium(epsilon, sigma)``
         * ``Medium(n)``
         * ``Medium(n, k, wl)``
         * ``Medium(n, k, freq)``

        """

        self.name = None if name is None else str(name)
        # If set, frequency_range defines a tuple (f_lower, f_upper) in Hz of 
        # the frequency range of validity of this material model.
        self.frequency_range = None
        # poles filled by a DispersionModel if used
        self.poles = []

        if "epsilon" in kwargs:
            eps_real = kwargs.pop("epsilon")
            sigma = kwargs.pop("sigma", 0.)

            if kwargs:
                log_and_raise(
                    f"Invalid keyword arguments specified with epsilon and sigma: "
                    f"{list(kwargs.keys())}.",
                    ValueError,
                )

        elif "n" in kwargs:
            n = kwargs.pop("n")
            lam = None
            freq = None
            k = 0

            if "k" in kwargs:
                k = kwargs.pop("k")
                if "wl" in kwargs:
                    lam = kwargs.pop("wl")
                if "freq" in kwargs:
                    freq = kwargs.pop("freq")
                if lam is None and freq is None:
                    log_and_raise("wl or freq required when specifying k.", ValueError)
                if lam is not None and freq is not None:
                    log_and_raise("Only wl or freq may be specified", ValueError)

            if kwargs:
                log_and_raise(
                    f"Invalid keyword arguments specified with n and sigma: {list(kwargs.keys())}.",
                    ValueError,
                )

            if freq is not None:
                lam = C_0 / freq
            if lam is not None:
                freq = C_0 / lam

            eps_real = n * n - k * k
            sigma = 0
            if k != 0:
                sigma = 2 * np.pi * freq * (2 * n * k) * EPSILON_0

        else:
            log_and_raise("Either epsilon or n must be specified.", ValueError)

        # Make both epsilon and sigma arrays of size 3
        self.eps = self._eps_input(eps_real, "epsilon")
        self.sigma = self._eps_input(sigma, "sigma")

        self._check_stability()

    def _check_stability(self):

        if len(self.poles) > 0:
            # Dispersive material; can add checks
            return

        if np.any((0 < self.eps) * (self.eps < 1)):
            logging.warning(
                "Permittivity smaller than one could result "
                "in numerical instability. Use Courant stability factor "
                "value lower than the smallest refractive index value."
            )

        elif np.any(self.eps) <= 0:
            err_msg = (
                "Permittivity smaller than zero can result in "
                "numerical instability and should be included as a "
                "dispersive model."
            )

            if np.any(self.eps) < -100:
                err_msg += "For large negative values consider using PEC instead."

            log_and_raise(err_msg, Tidy3DError)

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

        if self.eps is None:
            return None

        if freqs is None:
            return self._eps_component(self.eps[None, :], component)
        else:
            w = 2*np.pi*np.array(freqs)
            w = w.reshape((w.size, 1))
            eps_im = self.sigma[None, :] / w / EPSILON_0
            return self._eps_component(self.eps[None, :] + 1j * eps_im, component)


    @staticmethod
    def _eps_component(eps, component):
        """Return requested 'component' for the array 'eps' of shape (Nf, 3).
        """
        val_dict = {'xx': 0, 'yy': 1, 'zz': 2}

        if component == "average":
            return np.mean(eps, axis=1)
        elif component in val_dict.keys():
            return eps[:, val_dict[component]]
        else:
            log_and_raise(f"Unrecognized component {component}.", ValueError)


    @staticmethod
    def _eps_input(value, name):
        """Convert 'value' to a size-3 array to be used as anisotropic 
        permittivity/conductivity, or raise an error if not possible.
        """
        if isinstance(value, int) or isinstance(value, float):
            value = value * np.ones((3,))
        try:
            value = np.array(value)
            if value.size==1:
                value = np.tile(value, (3,))
            assert value.size == 3
        except:
            log_and_raise(f"Wrong '{name}' in permittivity specification.", ValueError)

        return value


class PEC(object):
    """Perfect electric conductor. All tangential electric fields vanish."""

    def __init__(self, name="PEC"):
        """Construct.

        Parameters
        ----------
        name : str, optional
            Custom name of the material.
        """
        self.name = name
        self.dispmod = None
        self.frequency_range = None
        self.poles = []

    def epsilon(self, freqs):
        """Used for viz purposes only.
        """

        if freqs is None:
            shape = (1, )
        elif np.array(freqs).size <= 1:
            shape = (1, )
        else:
            shape = freqs.shape

        return pec_viz * np.ones(shape)


class PMC(object):
    """Perfect magnetic conductor. All tangential magnetic fields vanish."""

    def __init__(self, name="PMC"):
        """Construct.

        Parameters
        ----------
        name : str, optional
            Custom name of the material.
        """
        self.name = name
        self.dispmod = None
        self.frequency_range = None
        self.poles = []

    def epsilon(self, freqs):
        """Used for viz purposes only.
        """

        if freqs is None:
            shape = (1, )
        elif np.array(freqs).size <= 1:
            shape = (1, )
        else:
            shape = freqs.shape

        return pmc_viz * np.ones(shape)

