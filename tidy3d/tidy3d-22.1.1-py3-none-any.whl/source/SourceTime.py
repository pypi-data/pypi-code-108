import numpy as np

from ..constants import int_, float_, complex_, fp_eps
from ..utils.em import dft_spectrum
import logging

class SourceTime(object):
    """Base class for the time dependence of a source. Available subclasses:

        - :class:`.GaussianPulse`
    """
    def __init__(self):
        """Construct.
        """

        # NB: tind_beg and tind_end are currently not used but in the future 
        # we could allow a starting and stopping time.
        self.tind_beg = 0
        self.tind_end = None


    def _get_spectrum(self, freqs, tmesh=None):
        """Compute the spectrum of the source in the most general case. 
        This uses a brute-fource DFT which may become slow for many 
        frequencies and time points. For evenly spaced frequencies, we could 
        implement a CZT transform in the future. For an arbitrary selection of 
        frequencies, we could also consider interpolating an FFT.
        
        Parameters
        ----------
        freqs : array_like
            Array of frequencies to sample the spectrum at.
        tmesh : array_like
            This function does a numerical computation of the spectrum and so 
            requires a mesh on which the time-dependence is computed and 
            transformed. It can be overriden by methods that use an analytic 
            result, in which case ``tmesh is not needed.

        Returns
        -------
        spectrum : array_like
            Array of same size as ``freqs`` giving the complex-valued spectrum 
            of the source.
        """

        if tmesh is None or len(tmesh)<=1:
            return None

        dt = tmesh[1] - tmesh[0]
        tdep = np.real(self._get_time(tmesh))
        return dft_spectrum(tdep, dt, freqs)

class GaussianPulse(SourceTime):
    """ Source with a Gaussian-envelope time dependence.
    """

    def __init__(self, frequency, fwidth, offset=5., phase=0.):
        """Construct.
        
        Parameters
        ----------
        frequency : float
            (Hertz) Carrier frequency.
        fwidth : float
            (Hertz) Frequency bandwidth.
        offset : float, optional
            Offset of the peak of the Gaussian envelope from the starting time 
            of the simulation, in units of ``twidth = 1/2/pi/fwidth``. 
            The peak of the source amplitude is attained at time 
            ``t = offset/2/pi/fwidth``. 
        phase : float, optional
            (radian) A temporal phase offset of the sinusoidal time dependence.
        """
        super().__init__()
        self.frequency = frequency
        self.fwidth = fwidth
        if fwidth < 0:
            logging.warning("'fwidth' smaller than zero, taking absolute value.")
            self.fwidth = -fwidth
        self.twidth = 1 / 2 / np.pi / fwidth
        self.offset = offset
        # User-defined global phase
        self.phase = phase

    def __repr__(self):
        rep = "GaussianPulse(\n"
        rep += "    frequency  = %1.2e,\n"%self.frequency
        rep += "    fwidth     = %1.2e,\n"%self.fwidth
        rep += "    offset     = %1.2f)"%self.offset

        return rep

    def _get_time(self, tmesh, extra_phase=0):
        """ Compute the time dependence of the source over ``tmesh``, using a 
        first-derivative of a Gaussian for the envelope.

        Return a complex array. The actual source amplitude is the real part.
        """

        # Global phase plus extra phase
        phi = self.phase + extra_phase
        tt0 = tmesh - self.offset * self.twidth
        omega = 2*np.pi*self.frequency
        G = (1j + tt0 / self.twidth**2 / omega) * \
                np.exp(1j*phi - 1j*omega*tmesh - tt0**2/2/self.twidth**2)
                
        # G = np.real(G)

        # Starting and stopping time, currently unused.
        Gnz = np.nonzero(np.abs(G) > 1e-5)[0]
        if Gnz.size > 0:
            self.tind_beg = Gnz[0]
            self.tind_end = Gnz[-1]
        else:
            self.tind_beg = 0
            self.tind_end = 0

        return G

    # def _get_spectrum(self, freqs, tmesh=None):
    #     """For a Gaussian pulse, it should be possible to compute the spectrum 
    #     analytically. However, I keep getting a weird (not just a prefactor) 
    #     mismatch between the formulat and the numerical result. The difference 
    #     depends both on fwidht and offset of the source.
        
    #     Parameters
    #     ----------
    #     freqs : array_like
    #         Array of frequencies to sample the spectrum at.
    #     """

    #     fr  = np.array(freqs) / self.fwidth # normalized frequences
    #     fr0 = self.frequency / self.fwidth  # normalized center frequency
    #     return self.twidth * np.exp(1j*(fr-fr0)*self.offset - 0.5*(fr-fr0)**2)