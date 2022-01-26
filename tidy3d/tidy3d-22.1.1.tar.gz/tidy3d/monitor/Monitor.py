import numpy as np

from ..utils import inside_box_coords, cs2span, listify, list2str
from ..utils.log import log_and_raise, MonitorError
from ..utils.check import check_3D_lists
from ..constants import int_, float_, fp_eps, xyz_list, xyz_dict, C_0

class Monitor(object):
    """Base class for defining field monitors.
    """
    def __init__(self, center, size, name=None):
        """Base constructor. Available subclasses:

        - :class:`.TimeMonitor`
        - :class:`.FreqMonitor`
        - :class:`.ModeMonitor`
        """
        check_3D_lists(center=listify(center), size=listify(size))
        self.center = np.array(center)
        self.size = np.array(size)
        """ Slightly offset the span such that if the monitor is zero-size 
        along a certain direction, and is placed exactly on a grid coordinate,
        it will deterministically be placed to the right of the coordinate."""
        self.span = cs2span(self.center, self.size)
        zero_span = self.span[:, 1] - self.span[:, 0] < fp_eps
        self.span[zero_span, :] += fp_eps
        self.name = None if name is None else str(name)

        # Data requested to be written to the final monitor file
        self.store = []
        # Data that will be needed in the post-processing
        self.store_run = []


    def _inside(self, coords):
        """ Get a mask equal to one if a point is inside the monitor region, 
        and zero if outside.
        
        Parameters
        ----------
        coords : 3-tuple
            Defines the x, y, and z coords. 
        """
        mask = np.zeros(tuple(c.size - 1 for c in coords))
        indsx, indsy, indsz = inside_box_coords(self.span, coords)
        mask[indsx[0]:indsx[1], indsy[0]:indsy[1], indsz[0]:indsz[1]] = 1.0

        return mask

    def _inside_inds(self, coords):
        """ Get indexes of the points inside the monitor region.
        
        Parameters
        ----------
        coords : 3-tuple
            Defines the x, y, and z coords. 
        
        Returns
        -------
        np.ndarray
            An array of shape (Np, 3), where Np is the total number of coords 
            points in the monitor region.
        """
        inds = inside_box_coords(self.span, coords)
        indsm = np.meshgrid(np.arange(inds[0][0], inds[0][1]), 
                            np.arange(inds[1][0], inds[1][1]),
                            np.arange(inds[2][0], inds[2][1]),
                            indexing='ij')
        if indsm[0].size==0: 
            return np.zeros((0, 3), dtype=int_)

        return np.stack([inds.ravel() for inds in indsm], axis=1).astype(int_)


class TimeMonitor(Monitor):
    """Monitor recording the time-domain fields within a 3D region.
    """

    def __init__(self, center, size, t_start=0, t_stop=None, t_step=None,
                    store=('E', 'H'), name=None):
        """Construct.
        
        Parameters
        ----------
        center : array_like
            (micron) x, y, and z position of the center of the Monitor.
        size : array_like
            (micron) Size in x, y, and z.
        t_start : float, optional
            (second) Starting time of field recording.
        t_stop : float, optional
            (second) Stopping time of field recording. If ``None``, record 
            until the end of the simulation.
        t_step : None, optional
            (second) : Time interval at which to record the fields. If
            ``None``, the fields at every time step are recorded. If a float,
            it is snapped to an integer multiple of the simulation time step.
        store : list, optional
            List of attributes to be recorded. Valid entries are 
            ``'E'``, ``'H'`` and ``'flux'``. If ``'flux'`` is requested, the 
            monitor must be a 2D surface.
        name : str, optional
            Custom name of the monitor.
        
        Note
        ----
        Time monitors can result in very large amounts of data if defined over 
        a large spatial region. Recommended usage is either recording the full 
        time evolution of a single point in space, or using ``t_start`` and 
        ``t_stop`` to record just a few time steps of a larger region. 
        """

        super().__init__(center, size, name)
        for f in listify(store):
            if f.lower() in ['e', 'h', 'flux']:
                self.store.append(f.lower())
                self.store_run.append(f.lower())
            else:
                log_and_raise(f"Unrecognized store value '{f}'.", MonitorError)

        self.t_start = t_start
        self.t_stop = t_stop
        self.t_step = t_step

    def __repr__(self):
        rep = "Tidy3D TimeMonitor: {\n"
        rep += "name     = %s\n"%self.name
        rep += "center   = %s\n" % list2str(self.center, "%1.4f")
        rep += "size     = %s\n" % list2str(self.size, "%1.4f")
        rep += "t_start  = %1.2e,\n"%self.t_start
        if self.t_stop is None:
            rep += "t_stop   = None\n"
        else:
            rep += "t_stop   = %1.2e,\n"%self.t_stop
        if self.t_step is None:
            rep += "t_step   = None\n"
        else:
            rep += "t_step   = %1.2e,\n"%self.t_step
        rep += f"Store: {self.store}\n"
        rep += "}\n"

        return rep

class FreqMonitor(Monitor):
    """Monitor recording a discrete Fourier transform of the fields within a 
    3D region, for a given list of frequencies.
    """
    
    def __init__(self, center, size, freqs, store=('E', 'H'), interpolate=True, name=None):
        """ Construct.

        Parameters
        ----------
        center : array_like
            (micron) x, y, and z position of the center of the Monitor.
        size : array_like
            (micron) Size in x, y, and z.
        freqs : float or array_like
            Frequencies at which the fields are sampled.
        store : list, optional
            List of attributes to be recorded. Valid entries are 
            ``'E'``, ``'H'``, ``'flux'``, and ``'eps'``. If ``'flux'`` is 
            requested, the monitor must be a 2D surface, and ``interpolate``
            must be ``True``.
        interpolate : bool, optional
            If ``True``, the fields are returned at the centers of the Yee
            lattice, and all fields and components are at the same position.
            If ``False``, the raw fields, where each component lies on its
            assigned Yee lattice location, are returned.
        name : str, optional
            Custom name of the monitor.
        """

        super().__init__(center, size, name)
        for f in listify(store):
            if f.lower() in ['e', 'h', 'flux', 'eps']:
                self.store.append(f.lower())
                self.store_run.append(f.lower())
            else:
                log_and_raise(f"Unrecognized store value '{f}'.", MonitorError)

        self.freqs = listify(freqs)
        if len(self.freqs) == 0:
            log_and_raise(
                "Monitor 'freqs' must be a non-empty list.", MonitorError
            )
        if interpolate == False and 'flux' in store:
            log_and_raise("flux can only be stored during the simulation run if the monitor "
                "interpolate setting is True.", MonitorError)

        self.lambdas = C_0 / (np.array(freqs) + fp_eps)
        self.interpolate = interpolate

    def __repr__(self):
        rep = "Tidy3D FreqMonitor: {\n"
        rep += "name     = %s\n"%self.name
        rep += "center   = %s\n" % list2str(self.center, "%1.4f")
        rep += "size     = %s\n" % list2str(self.size, "%1.4f")
        rep += "freqs    = %s\n" % list2str(self.freqs, "%1.2e")
        rep += f"Store: {self.store}\n"
        rep += "}\n"

        return rep

class ModeMonitor(FreqMonitor):
    """ :class:`.FreqMonitor` subclass defining a 2D plane in which the 
    recorded frequency-domain fields can be decomposed into propagating 
    eigenmodes.
    """
    
    def __init__(self, center, size, freqs, angle_theta=0., angle_phi=0., Nmodes=1,
            store=['E', 'H', 'modes', 'mode_amps'], name=None):
        """Construct.
        
        Parameters
        ----------
        center : array_like
            (micron) 3D vector defining the center of the 2D plane.
        size : array_like
            (micron) 3D vector defining the size of the 2D plane. Exactly one 
            of the values must be ``0``, defining the normal direction.
        freqs : float or list of float
            Frequencies at which the fields are sampled.
        angle_theta : float, optional
            (radian) Polar angle of propagation from the normal axis.
        angle_phi : float, optional
            (radian) Azimuth angle of propagation in the plane orthogonal to the normal axis.
        Nmodes : int
            Compute the decomposition into the first ``Nmodes`` modes in
            order of decreasing effective index.
        store : List of attributes to be recorded. Valid entries are 
            ``'modes'``, ``'mode_amps'``, ``'E'``, ``'H'``, and ``'flux'``.
        name : str, optional
            Custom name of the monitor.
        """

        super().__init__(center, size, freqs, store=(), name=name)
        # The E and H fields are always needed in order to do the 
        # mode decomposition in the post processing.
        self.store_run = ['e', 'h']
        for f in listify(store):
            if f.lower() in ['e', 'h', 'flux', 'modes', 'mode_amps']:
                self.store.append(f.lower())
                if f.lower() == 'flux':
                    self.store_run.append(f.lower())
            else:
                log_and_raise(f"Unrecognized store value '{f}'.", MonitorError)


        if angle_theta < 0 or angle_theta >= np.pi / 2:
            log_and_raise("'angle_theta' must be between 0 and pi/2.", MonitorError)

        self.Nmodes = Nmodes
        self.angle_theta = angle_theta
        self.angle_phi = angle_phi

    def __repr__(self):
        rep = "Tidy3D ModeMonitor: {\n"
        rep += "name     = %s\n"%self.name
        rep += "center   = %s\n" % list2str(self.center, "%1.4f")
        rep += "size     = %s\n" % list2str(self.size, "%1.4f")
        rep += "freqs    = %s\n" % list2str(self.freqs, "%1.2e")
        rep += "Nmodes   = %d\n" % self.Nmodes
        rep += "}\n"

        return rep