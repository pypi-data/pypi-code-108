import numpy as np

from .Monitor import TimeMonitor, FreqMonitor, ModeMonitor
from ..constants import int_, float_, complex_, fp_eps, C_0
from ..mode import ModePlane, Mode
from ..utils.log import log_and_raise, MonitorError

class MonitorData(object):
    """Class used internally to store data related to a Monitor added in a 
    specific Simulation.
    """

    def __init__(self, monitor):

        # Reference to the monitor that the data corresponds to
        self.monitor = monitor

        # To be set by Simulation
        self.name = None

        # Everything below is set after a run of store_data() or load_fields()
        self.data = False # To be set to True after data is loaded

        # Raw E and H data as returned by the solver
        self._E = np.empty((3, 0, 0, 0, 0), dtype=float_)
        self._H = np.empty((3, 0, 0, 0, 0), dtype=float_)
        # Total flux as returned by the solver
        self._flux = np.empty((0, 1), dtype=float_)
        # Poynting flux density if computed after a solve
        self._S = np.empty((3, 0, 0, 0, 0), dtype=float_)
        # Permittivity if stored
        self.eps = np.empty((3, 0, 0, 0, 0), dtype=float_)

        # Mesh defining the positions of the Yee grid cell centers
        self.xmesh = np.empty((0, ), dtype=float_)
        self.ymesh = np.empty((0, ), dtype=float_)
        self.zmesh = np.empty((0, ), dtype=float_)

        # Mesh defining the positions of the Yee grid cell beggining points
        self.xmesh_b = np.empty((0, ), dtype=float_)
        self.ymesh_b = np.empty((0, ), dtype=float_)
        self.zmesh_b = np.empty((0, ), dtype=float_)

        # Mesh in time, for a TimeMonitor. Set when added to a Simulation.
        self.tmesh = np.empty((0, ), dtype=float_)
        self.tind_beg = 0
        self.tind_end = 0
        self.tind_step = 1
        self.Nt = 0

        # Frequencies, for a FreqMonitor
        self.freqs = np.empty((0, ), dtype=float_)
        if isinstance(monitor, FreqMonitor):
            self.freqs = np.array(monitor.freqs, dtype=float_)
            self.Nf = self.freqs.size

        # Indexes defining the span of the Monitor in the simulation grid in 
        # which it is embedded.
        self.mnt_inds = np.empty((0, 3), dtype=int_)
        self.inds_beg = np.zeros((3, ), dtype=int_)
        self.inds_end = np.zeros((3, ), dtype=int_)

        # Source normalization, which may be set later for FreqMonitors
        self.set_source_norm(None)

        # For 2D monitors
        self.norm_ind = None
        self.normal = None

        # Expansion coefficients for a ModeMonitor, loaded after solver run
        self._mode_amps = np.zeros((2, 0, 0), dtype=float_)
        if isinstance(monitor, ModeMonitor):
            self.Nmodes = monitor.Nmodes
            self.target_neff = None
            self.pml_layers = (0, 0)
            self.bend_radius = None
            self.bend_axis = None
            self.angle_theta = monitor.angle_theta
            self.angle_phi = monitor.angle_phi
            self._mode_amps = np.zeros((2, self.Nf, self.Nmodes), dtype=float_)

    @property
    def E(self):
        """ (V/micron) Electric field, if it was requested and after the data
        has been loaded.
        """
        return self._E

    @property
    def H(self):
        """ (A/micron) Magnetic field, if it was requested and after the data
        has been loaded.
        """
        return self._H

    @property
    def S(self):
        """ (W/micron\\ :sup:`2`) Poynting vector (power flux density) if it
        has been computed with :meth:`Simulation.poynting`.
        """
        return self._S

    @property
    def flux(self):
        """ (W) Power flux through a 2D surface monitor, if it was requested
        and after the data has been loaded.
        """
        return self._flux

    @property
    def modes(self):
        """ (:class:`Mode`) For a :class:`ModeMonitor`, a list of 
        length ``Nf`` (number of frequencies in monitor) of lists of length 
        ``Nmodes`` (number of stored modes) of :class:`Mode` objects.
        These store the ``E`` and ``H`` fields of each mode as well as the 
        real and imaginary part of the effective index, ``neff`` and ``keff``. 
        The fields are
        oriented in the mode plane axes, such that they are arrays of shape
        (3, Np1, Np2) where ``Np1`` and ``Np2`` are the two in-plane
        directions. The three components are also oriented in-plane as
        ``(parallel_1, parallel_2, normal)``.
        """
        return self.mode_plane.modes

    @property
    def mode_amps(self):
        """ (:math:`\\sqrt{W}`) Power amplitude expansion coefficients for
        mode monitors.
        """
        return self._mode_amps

    def _set_normal(self):
        """Get normal direction for a 2D monitor. Raise an error if not a 
        2D monitor. """

        if not (isinstance(self.monitor, ModeMonitor) or
            'flux' in self.monitor.store):
            return

        self.norm_ind = np.nonzero(self.monitor.size < fp_eps)[0]
        if self.norm_ind.size !=1:
            log_and_raise(
                f"Exactly one element of the 'size' of Monitor {self.name} "
                "must be zero.", 
                MonitorError
            )
            
        self.norm_ind = int(self.norm_ind)

        if isinstance(self.monitor, ModeMonitor):
            self.mode_plane = ModePlane(self.monitor.span, self.norm_ind)

    def _set_tmesh(self, tmesh):
        """Set the time mesh of the monitor. During the solver run, the H 
        field values are interpolated to be on the ``tmesh`` as defined here.
        """

        if tmesh.size == 0:
            self.tmesh = tmesh
            self.Nt = 0
            self.tind_beg = 0
            self.tind_end = 0
            return
 
        # Step to compare to in order to handle t_start = t_stop
        if np.array(tmesh).size < 2:
            dt = 1e-20
        else:
            dt = tmesh[1] - tmesh[0]

        if self.monitor.t_step is not None:
            self.tind_step = max(1, int(self.monitor.t_step/dt))

        # If t_stop is None, record until the end
        t_stop = self.monitor.t_stop
        if self.monitor.t_stop is None:
            t_stop = tmesh[-1]
            self.tind_end = tmesh.size
        else:
            tend = np.nonzero(tmesh <= self.monitor.t_stop)[0]
            if tend.size > 0:
                self.tind_end = tend[-1] + 1
            else:
                self.tind_end = 0

        # If equal (within dt), record one time step
        if np.abs(self.monitor.t_start - t_stop) < dt:
            self.tind_beg = np.max([self.tind_end - 1, 0])
        else:
            tbeg = np.nonzero(tmesh[0:self.tind_end] >= 
                                self.monitor.t_start)[0]
            if tbeg.size > 0:
                self.tind_beg = tbeg[0]
            else:
                self.tind_beg = self.tind_end

        self.tmesh = tmesh[self.tind_beg:self.tind_end:self.tind_step]
        self.Nt = self.tmesh.size


    def set_source_norm(self, source, tmesh=None):
        """Normalize the stored fields.
        
        Parameters
        ----------
        source : Source or None
            A :class:`.Source` object from whose spectrum the fields are 
            normalized.
        tmesh : array_like
            The time mesh of the simulation.
        """

        if isinstance(self.monitor, TimeMonitor):
            self.source_norm = np.ones((1, ), dtype=float_)
        elif source is None:
            self.source_norm = np.ones((len(self.freqs), ), dtype=complex_)
        else:
            spectrum = source.source_time._get_spectrum(self.freqs, tmesh)
            if spectrum is not None:
                # Field is pi/2 delayed from generating current.
                self.source_norm = np.array(1j / spectrum)
                # Need to add back the original external phase of the source
                self.source_norm *= np.exp(1j * source.source_time.phase)