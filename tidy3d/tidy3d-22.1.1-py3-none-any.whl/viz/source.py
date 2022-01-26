import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def viz_source_spectrum(self, source, ax=None, Nfreqs=1000, flims=None):
    """Plot the frequency dependence of a source.
    
    Parameters
    ----------
    source : Source
        Source object to plot.
    ax : Matplotlib axis object, optional
        If None, a new figure is created.
    Nfreqs : int
        Number of frequencies to interpolate the spectrum over.
    flims : List[float], optional
        Frequency limits (fmin, fmax) to plot within.
    
    Returns
    -------
    Matplotlib axis object
    """

    if ax is None:
        fig, ax = plt.subplots(1)

    if flims is None:
        stime = source.source_time
        flims = (stime.frequency - 4*stime.fwidth, stime.frequency + 4*stime.fwidth)

    # # Compute from FFT if tmesh and tdep are known
    # Nt = tdep.size
    # dt = tmesh[1] - tmesh[0]
    # df = 1/Nt/dt
    # fmesh = np.arange(0, Nt)*df
    # spectrum = 1/np.sqrt(2*np.pi)*np.fft.ifft(tdep)/df

    # Compute directly from source time method
    fmesh = np.linspace(flims[0], flims[1], Nfreqs)
    spectrum = self.spectrum(source, fmesh)
    spectrum /= np.amax(np.abs(spectrum))
    pl = ax.plot(fmesh, np.abs(spectrum))

    ax.set_ylim([0, 1.1])
    ax.set_xlim(flims)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Amplitude [a.u.]")
    ax.set_title("Spectrum")

    return ax

def viz_source_time(self, source, ax=None):
    """Plot the time dependence of a source.
    
    Parameters
    ----------
    source : Source
        Source object to plot.
    ax : Matplotlib axis object, optional
        If None, a new figure is created.

    Returns
    -------
    Matplotlib axis object
    """

    tmesh = self.tmesh
    tdep = np.real(source.source_time._get_time(tmesh))
    tdep /= np.amax(np.abs(tdep))

    if ax is None:
        fig, ax = plt.subplots(1)

    pl = ax.plot(tmesh, tdep)
    ax.set_xlim([tmesh[0], tmesh[-1]])
    ax.set_ylim([-1.1, 1.1])
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude [a.u.]")
    ax.set_title("Time dependence");

    return ax

def viz_source(self, source, axs=None):
    """Plot both the time and frequency dependence of a source.
    
    Parameters
    ----------
    source : Source
        Source object to plot.
    axs : List[Matplotlib axis object], optional
        If None, a new figure is created.

    Returns
    -------
    Matplotlib axis object
    """
    
    if axs is None:
        fig, axs = plt.subplots(1, 2, figsize=(10, 3))

    self.viz_source_time(source, ax=axs[0])
    self.viz_source_spectrum(source, ax=axs[1])

    return axs