import numpy as np
import json
import h5py
import logging

from .utils import listify, list2str, UniqueNames, cs2span, log_and_raise
from .utils.geom import inside_box_coords
from .utils.log import Tidy3DError, DivergenceError, MonitorError, SourceError, StructureError
from .utils.check import check_3D_lists, check_poles, check_material, check_structure
from .constants import int_, float_, complex_, fp_eps, C_0, pec_viz, pmc_viz

from .grid import Grid, SubGrid
from .structure import Structure, Box
from .material import Medium
from . import PEC, PMC

from .source import Source, Field2DSource, ModeSource, SourceData
from .monitor import Monitor, TimeMonitor, FreqMonitor, ModeMonitor, MonitorData

from .json_ops import write_parameters, write_structures, write_sources, write_monitors

class Simulation(object):
    """
    Main class for building a simulation model.
    """
    from .utils.check import _check_size, _check_monitor_size, _check_outside
    from .source._simulation import _compute_modes_source, _src_data, set_mode, spectrum
    from .monitor._simulation import _compute_modes_monitor, _mnt_data, _load_fields
    from .monitor._simulation import data, poynting, flux, decompose, set_monitor_modes
    from .json_ops import _read_simulation
    from .viz import _fmonitors_png, _structure_png
    from .viz import viz_eps_2D, viz_mat_2D, viz_field_2D, viz_modes
    from .viz import viz_source, viz_source_spectrum, viz_source_time

    def __init__(
        self,
        size=(0., 0., 0.),
        center=(0., 0., 0.),
        resolution=None,
        mesh_step=None,
        coords=None,
        structures=None,
        sources=None,
        monitors=None,
        symmetries=(0, 0, 0),
        pml_layers=(0, 0, 0),
        run_time=0.,
        courant=0.9,
        shutoff=1e-5,
        subpixel=True,
    ):
        """Construct.

        Parameters
        ----------
        center : array_like, optional
            (micron) 3D vector defining the center of the simulation domain.
        size : array_like, optional
            (micron) 3D vector defining the size of the simulation domain.
        resolution : float or array_like, optional
            (1/micron) Number of grid points per micron, or a 3D vector 
            defining the number of grid points per mircon in x, y, and z.
        mesh_step : float or array_like, optional
            (micron) Step size in all directions, or a 3D vector defining the 
            step size in x, y, and z seprately. If provided, ``mesh_step`` 
            overrides the ``resolution`` parameter, otherwise 
            ``mesh_step = 1/resolution``.
        coords : List[array_like], optional
            (micron) If provided, overrides ``center``, ``size``, and
            ``mesh_step``/``resolution``. A list of three arrays defining the
            beginning and end points of the discretization grid to be used in
            the three dimensions. For a given dimension, if ``Nd`` is the size
            of ``coords[d]``, this then defines ``Nd - 1`` Yee grid cells,
            and the simulation span in that dimension is from ``coords[d][0]``
            to ``coords[d][-1]``.
        structures : Structure or List[Structure], optional
            Empty list (default) means vacuum. 
        sources : Source or List[Source], optional
            Source(s) to be added to the simulation.
        monitors : Monitor or List[Monitor], optional
            Monitor(s) to be added to the simulation.
        symmetries : array_like, optional
            Array of three integers defining reflection symmetry across a 
            plane bisecting the simulation domain normal to the x-, y-, and 
            z-axis, respectively. Each element can be ``0`` (no symmetry), 
            ``1`` (even, i.e. 'PMC' symmetry) or ``-1`` (odd, i.e. 'PEC' 
            symmetry). Note that the vectorial nature of the fields must be 
            taken into account to correctly determine the symmetry value.
        pml_layers : array_like, optional
            Array of three elements defining the PML boundaries on both 
            sides of the simulation domain along x, y, and z, respectively. 
            Default is ``0`` on all sides, in which case periodic boundary 
            conditions are applied. If element is an integer, defines the 
            number of PML layers using the ``'standard'`` profile. If element
            is a string, it defines the profile, one of ``'standard'``, 
            ``'stable'`` or ``'absorber'``, which come with a default number 
            of layers. ``'absorber'`` is a simple adiabatically tapered 
            absorbing material. Finally, each element can also be a dictionary
            of the form ``{'profile': 'standard', 'Nlayers': 20}``,
            defining a custom combination of profile and number of layers.
        run_time : float, optional
            (second) Total electromagnetic evolution time.
        shutoff : float, optional
            The simulation will automatically shut down if the ratio of the 
            integrated E-field intensity at the current time step over the
            maximum integrated intensity at a previous time step becomes lower
            than the ``shutoff`` factor. Set to ``0`` to disable this feature.
        courant : float, optional
            Courant stability factor, must be smaller than 1, or more 
            generally smaller than the smallest refractive index in the 
            simulation.
        subpixel : boolean, optional
            Whether to enable subpixel permittivity averaging.
        """

        check_3D_lists(center=listify(center), size=listify(size),
                            symmetries=listify(symmetries),
                            pml_layers=listify(pml_layers))

        logging.info("Initializing simulation...")

        # Set spatial mesh step, if coords not provided
        if coords is None:
            if mesh_step is None:
                if resolution is None:
                    log_and_raise("'mesh_step', 'resolution' or 'coords' must be set.", ValueError)
                mesh_step = 1/np.array(resolution)
            else:
                if resolution is not None:
                    logging.info("Note: parameter 'mesh_step' overrides 'resolution'.")
        else:
            if np.any([item is not None for item in [mesh_step, resolution, center, size]]):
                logging.info("Note: parameter 'coords' overrides 'center', 'size', 'mesh_step' and "
                    "'resolution'.")

        # Materials and indexing populated when adding ``Structure`` objects.
        self._mat_inds = [] # material index of each structure
        self._materials = [] # list of materials included in the simulation
        self._structures = []

        # List containing SourceData for all sources, and a dictionary 
        # used to get SourceData from id(source), e.g. src_data = 
        # self._source_ids[id(source)]
        self._source_data = []
        self._source_ids = {}

        # List containing MonitorData for all monitors, and a dictionary 
        # used to get MonitorData from id(monitor)
        self._monitor_data = []
        self._monitor_ids = {}

        # Variables used to store unique names for all objects
        self._str_names = UniqueNames("struct")
        self._mat_names = UniqueNames("mat")
        self._mnt_names = UniqueNames("monitor")
        self._src_names = UniqueNames("source")

        # Structures and material indexing for symmetry boxes
        self._structures_sym = [] # PEC/PMC boxes added for symmetry

        # Parse PML input
        self._add_pml(pml_layers)

        # Set simulation grid and size inside the PML and including the PML
        self.grid = Grid()
        if coords is not None:
            self.coords = [np.array(c) for c in coords]
            self.grid.load_coords(self.coords, symmetries)
        else:
            self.coords = None
            self.grid.init_uniform(mesh_step, cs2span(center, size), symmetries)

        # Simulation size based on grid
        self.span_in = np.copy(self.grid.span)
        self.size_in = self.span_in[:, 1] - self.span_in[:, 0]
        self.center = (self.span_in[:, 0] + self.span_in[:, 1])/2

        zero_dims = np.nonzero(self.size_in == 0)[0]
        if zero_dims.size > 0:
            log_and_raise(
                f"Simulation domain size is zero along dimension(s) {zero_dims}!", Tidy3DError)

        # Add the PML to the grid
        Npml = self.Npml
        self.grid.pad(Npml[0, 0], Npml[0, 1], Npml[1, 0], Npml[1, 1], Npml[2, 0], Npml[2, 1])
        self.span = np.copy(self.grid.span)
        self.size = self.span[:, 1] - self.span[:, 0]

        self.subpixel = subpixel

        logging.info(
            f"Mesh step (micron): {list2str(self.grid.mesh_step, '%1.2e')}.\n"
            f"Simulation domain in number of grid points: {list2str(self.grid.Nxyz, '%d')}."
        )

        # Grid including symmetries, if any
        span_inds = np.stack((np.zeros((3,)), self.grid.Nxyz), axis=1).astype(int_)
        pec_pad = np.array([sym == 1 for sym in symmetries]).astype(int_)
        self.Npml_sym = np.copy(self.Npml)
        for d, sym in enumerate(symmetries):
            if sym != 0:
                span_inds[d, 0] = self.grid.Nxyz[d] // 2
                self.Npml_sym[d, 0] = 0
        self.grid_sym = SubGrid(self.grid, span_inds)
        self.grid_sym.pad(pec_pad[0], pec_pad[0], pec_pad[1], pec_pad[1], pec_pad[2], pec_pad[2])

        # Print new size, if there are any symmetries
        if np.any(np.array(symmetries) != 0):
            logging.info(f"Grid points after symmetries: {list2str(self.grid_sym.Nxyz, '%d')}.")

        # Total number of points in computational domain (after symmetries)
        self.Np = np.prod(self.grid_sym.Nxyz, dtype=np.int64)
        logging.info(f"Total number of computational grid points: {self.Np:.2e}.")

        # Set up run time
        self.set_time(run_time, courant)
        logging.info(f"Total number of time steps: {self.Nt}.")
        if self.Nt <= 0:
            logging.warning(
                f"run_time = {self.run_time:.2e} smaller than a single "
                f"simulation time step dt = {self.dt:.2e}.",
            )
        self.shutoff = shutoff

        # Check the simulation size
        self._check_size()

        # Simulation frequency range, updated based on sources
        self.freq_range = [0., 0]

        # Add structures, sources, monitors, symmetries
        self._add_symmetries(symmetries)
        if sources:
            [self._add_source(source) for source in listify(sources)]
        if monitors:
            [self._add_monitor(monitor) for monitor in listify(monitors)]
        if structures:
            [self._add_structure(struct) for struct in listify(structures)]

        # JSON file from which the simulation is loaded
        self.fjson = None

    def __repr__(self):
        rep = "Tidy3D Simulation:\n"
        rep += "center      = %s\n" % list2str(self.center, "%1.4f")
        rep += "size        = %s\n" % list2str(self.size_in, "%1.4f")
        rep += "size w. pml = %s\n" % list2str(self.size, "%1.4f")
        rep += "mesh_step   = %s\n" % list2str(self.grid.mesh_step, "%1.4f")
        rep += "run_time    = %1.2e\n"%self.run_time
        rep += "symmetries  = %s\n" % list2str(self.symmetries, "%d")
        rep += "pml Nlayers = %s\n\n" % list2str(self.Npml[:, 1], "%d")

        rep += "Number of grid points in x, y, z: %s\n" % list2str(
                    self.grid.Nxyz, "%d")
        rep += "    after symmeries             : %s\n"%list2str(
                    self.grid_sym.Nxyz, "%d")
        rep += "Total number of grid points: %d\n" % np.prod(self.grid.Nxyz)
        rep += "    after symmetries:        %d\n" % self.Np

        rep += "Number of time steps       : %d\n" % self.Nt
        rep += "Number of structures       : %d\n"%len(self._structures)
        rep += "Number of sources          : %d\n"%len(self.sources)
        rep += "Number of monitors         : %d\n"%len(self.monitors)

        return rep

    @property
    def materials(self):
        """ List containing all materials included in the simulation."""
        return self._materials

    @property
    def mat_inds(self):
        """ List containing the material index in :attr:`.materials` of every 
        structure in :attr:`.structures`. """
        return self._mat_inds

    @property
    def structures(self, sym=None):
        """ List containing all :class:`Structure` objects. """
        return self._structures

    @structures.setter
    def structures(self, new_struct):
        raise RuntimeError("Structures can be added upon Simulation init.")

    @property
    def sources(self):
        """ List containing all :class:`Source` objects. """
        return [src_data.source for src_data in self._source_data]

    @sources.setter
    def sources(self, new_sources):
        raise RuntimeError("Sources can be added upon Simulation init.")

    @property
    def monitors(self):
        """ List containing all :class:`.Monitor` objects. """
        return [mnt_data.monitor for mnt_data in self._monitor_data]

    @monitors.setter
    def monitors(self, new_monitors):
        raise RuntimeError("Monitors can be added upon Simulation init.")

    def _add_structure(self, structure):
        """ Adds a Structure object to the list of structures and to the 
        permittivity array. """

        if not isinstance(structure, Structure):
            t = type(structure)
            log_and_raise(
                f"Object of type {t} cannot be added as a structure.",
                StructureError
            )

        self._structures.append(structure)
        self._str_names.append(structure.name)
        check_structure(self, -1)

        try:
            mind = self.materials.index(structure.material)
            self._mat_inds.append(mind)
        except ValueError:
            if len(self.materials) < 200:
                mat = structure.material
                self._materials.append(mat)
                self._mat_names.append(mat.name)
                self._mat_inds.append(len(self.materials)-1)
                check_material(mat, self._mat_names[-1], self.freq_range)
            else:
                log_and_raise(
                    "Maximum 200 distinct materials allowed.",
                    Tidy3DError
                )

    def _add(self, objects):
        """Add a list of objects, which can contain structures, sources, and 
        monitors.
        """

        for obj in listify(objects):
            if isinstance(obj, Structure):
                self._add_structure(obj)
            elif isinstance(obj, Source):
                self._add_source(obj)
            elif isinstance(obj, Monitor):
                self._add_monitor(obj)

    def _add_source(self, source):
        """ Adds a Source object to the list of sources.
        """

        if not isinstance(source, Source):
            t = type(source)
            log_and_raise(
                f"Object of type {t} cannot be added as a source.",
                SourceError
            )

        if id(source) in self._source_ids.keys():
            logging.warning("Source already in Simulation, skipping.")
            return

        src_data = SourceData(source)
        src_data.name = self._src_names.append(source.name)
        self._check_outside(source, src_data.name)
        src_data._mesh_norm(self.grid)

        if isinstance(source, Field2DSource):
            freq = source.source_time.frequency
            src_data.mode_plane._set_sim(self, freq)

        self._source_data.append(src_data)
        self._source_ids[id(source)] = src_data
        self._update_freq_range()

    def _add_monitor(self, monitor):
        """ Adds a time or frequency domain Monitor object to the 
        corresponding list of monitors.
        """

        if not isinstance(monitor, Monitor):
            t = type(monitor)
            log_and_raise(
                f"Object of type {t} cannot be added as a monitor.",
                MonitorError
            )

        if id(monitor) in self._monitor_ids.keys():
            logging.warning("Monitor already in Simulation, skipping.")
            return

        mnt_data = MonitorData(monitor)
        mnt_data.name = self._mnt_names.append(monitor.name)
        self._check_outside(monitor, mnt_data.name)
        mnt_data._set_normal()
        self._monitor_data.append(mnt_data)
        self._monitor_ids[id(monitor)] = mnt_data

        if isinstance(monitor, TimeMonitor):
            mnt_data._set_tmesh(self.tmesh)

        if isinstance(monitor, ModeMonitor):   
            mnt_data.mode_plane._set_sim(self, mnt_data.freqs)

        memGB = self._check_monitor_size(monitor)
        logging.info(
            f"Estimated data size (GB) of monitor {mnt_data.name}: "
            f"{memGB:.4f}."
        )

    def _add_symmetries(self, symmetries):
        """ Add all symmetries as PEC or PMC boxes.
        """
        self.symmetries = listify(symmetries)
        for dim, sym in enumerate(symmetries):
            if sym not in [0, -1, 1]:
                log_and_raise(
                    "Reflection symmetry values can be 0 (no symmetry), "
                    "1, or -1.",
                    Tidy3DError
                )
            elif sym==1 or sym==-1:
                sym_cent = np.copy(self.center)
                sym_size = np.copy(self.size)
                sym_cent[dim] -= self.size[dim]/2
                sym_size[dim] = sym_size[dim] - fp_eps
                sym_mat = PEC if sym==-1 else PMC
                sym_pre = 'pec' if sym==-1 else 'pmc'
                self._structures_sym.append(Box(center=sym_cent,
                                                size=sym_size,
                                                material=sym_mat,
                                                name=sym_pre + '_sym%d'%dim))

    def _add_pml(self, pml_layers):
        """ Add the PML layers input to simulation. It is rephrased in 
        dictionary form for each of the three directions.
        """
        pml_layers = listify(pml_layers)
        self.pml_layers = []

        for pml in pml_layers:
            if isinstance(pml, dict):
                try:
                    Nlayers = int(pml['Nlayers'])
                    profile = pml['profile']
                    assert profile in ['standard', 'stable', 'absorber']
                    # extend = bool(pml['extend'])
                except (ValueError, KeyError, AssertionError):
                    log_and_raise("Error in pml_layers input.", Tidy3DError)
            else:
                extend = True
                try:
                    # input is a string defining the profile
                    assert pml in ['standard', 'stable', 'absorber', None]
                    profile = pml
                    if profile == 'standard':
                        Nlayers = 12
                    elif profile == 'stable':
                        Nlayers = 40
                    elif profile == 'absorber':
                        Nlayers = 40
                    elif profile is None:
                        profile = 'standard'
                        Nlayers = 0
                except AssertionError:
                    try:
                        # input is a number defining the number of layers
                        Nlayers = int(pml)
                        profile = 'standard'
                    except ValueError:
                        log_and_raise("Error in pml_layers input.", Tidy3DError)

            pml_dict = {
                'profile': profile,
                'Nlayers': Nlayers,
                # 'extend': extend
            }
            self.pml_layers.append(pml_dict)

        Nl = [pml['Nlayers'] for pml in self.pml_layers]
        self.Npml = np.vstack((Nl, Nl)).astype(int_).T


    def _update_freq_range(self):
        """Update the global frequency range of the simulation based on the
        spectrum of all sources.
        """

        if len(self.sources)==0:
            return

        fmins, fmaxs = [], []
        for source in self.sources:
            src_time = source.source_time
            # five sigma -/+ interval
            fmins.append(src_time.frequency - 4 * src_time.fwidth)
            fmaxs.append(src_time.frequency + 4 * src_time.fwidth)

        self.freq_range = [np.amin(fmins), np.amax(fmaxs)]
        # Negative frequencies mean 0 frequency
        self.freq_range[0] = max(self.freq_range[0], 0)


    def _get_eps(self, mesh, edges='in', pec_val=pec_viz, pmc_val=pmc_viz,
            freq=None, syms=True, component='average'):
        """Compute the permittivity over a given mesh. For large simulations, 
        this could be computationally heavy, so preferably use only over small 
        meshes (e.g. 2D cuts). 
        
        Parameters
        ----------
        mesh : tuple
            Three 1D arrays defining the mesh in x, y, z.
        edges : {'in', 'out', 'average'}
            When an edge of a structure sits exactly on a mesh point, it is 
            counted as in, out, or an average value of in and out is taken.
        pec_val : float
            Value to use for PEC material.
        pmc_val : float
            Value to use for PMC material.
        freq : float or None, optional
            (Hz) frequency at which to query the permittivity. If 
            ``None``, the instantaneous :math:`\\epsilon_\\infty` is returned.
        syms : bool, optional
            If ``True``, PEC/PMC boxes are overlaid as defined by the 
            simulation symmetries.
        
        Returns
        -------
        eps : np.ndarray
            Array of size (mesh[0].size, mesh[1].size, mesh[2].size) defining 
            the (complex) relative permittivity at each point.
        """

        Nx, Ny, Nz = [mesh[i].size for i in range(3)]
        eps = np.ones((Nx, Ny, Nz), dtype=complex_)

        strs = self.structures
        if syms==True:
            strs = strs + self._structures_sym

        # Apply all structures
        for struct in strs:
            eps_val = struct._get_eps_val(pec_val, pmc_val, freq, component)
            struct._set_val(mesh, eps, eps_val, edges=edges)

        # return eps array after filling in all structures
        return eps

    def _get_mat(self, mesh, edges='in', pec_val=pec_viz, pmc_val=pmc_viz,
                    syms=True):
        """Get the material index over a given mesh. For large simulations, 
        this could be computationally heavy, so preferably use only over small 
        meshes (e.g. 2D cuts). 
        
        Parameters
        ----------
        mesh : tuple
            Three 1D arrays defining the mesh in x, y, z.
        edges : {'in', 'out', 'average'}
            When an edge of a structure sits exactly on a mesh point, it is 
            counted as in, out, or an average value of in and out is taken.
        pec_val : float
            Value to use for PEC material.
        pmc_val : float
            Value to use for PMC material.
        syms : bool, optional
            If ``True``, PEC/PMC boxes are overlaid as defined by the 
            simulation symmetries.
        
        Returns
        -------
        mat_inds : np.ndarray
            Array of size (mesh[0].size, mesh[1].size, mesh[2].size) defining 
            the index in the list of materials of the material at each point.
        """

        Nx, Ny, Nz = [mesh[i].size for i in range(3)]
        # Denote vacuum as -1
        mat_inds = -np.ones((Nx, Ny, Nz), dtype=int_)

        strs = self.structures
        if syms==True:
            strs = strs + self._structures_sym

        # Apply all structures
        for (istruct, struct) in enumerate(strs):
            
            # Use the get_eps function to check if PEC/PMC
            mat_ind = struct._get_eps_val(pec_val, pmc_val)
            if mat_ind not in [pec_val, pmc_val]:
                mat_ind = self.mat_inds[istruct]
            
            struct._set_val(mesh, mat_inds, mat_ind, edges=edges)

        # return material index array after filling in all structures
        return mat_inds

    def epsilon(self, monitor=None, center=(0., 0., 0.), size=(0., 0., 0.),
                pec_val=pec_viz, pmc_val=pmc_viz, frequency=None, syms=True):
        """Compute the complex relative permittivity inside a volume. The 
        permittivity is returned at the Yee grid centers isnide the volume.
        For large simulations, this could be computationally heavy over the
        full simulation volume, so this function is ideally used over a
        sub-domain, e.g. a 2D cut. The volume ``size`` can be ``0`` in any
        dimension, in which case the single Yee grid center closest to the
        volume ``center`` in that dimension is taken.
        
        Parameters
        ----------
        monitor : None or Monitor, optional
            If provided, overrides ``center`` and ``size``, and the monitor 
            volume is used.
        center : array_like, optional
            (micron) 3D vector defining the center of the queried volume.
        size : array_like, optional
            (micron) 3D vector defining the size of the queried volume.
        pec_val : float
            Value to use for PEC material.
        pmc_val : float
            Value to use for PMC material.
        frequency : float or None, optional
            (Hz) frequency at which to query the permittivity. If 
            ``None``, the instantaneous :math:`\\epsilon_\\infty` is returned.
        syms : bool, optional
            If ``True``, PEC/PMC boxes are overlaid as defined by the 
            simulation symmetries, with values defined by ``pec_val`` and 
            ``pmc_val``.
        
        Returns
        -------
        epsilon : np.ndarray
            Array defining the (complex) relative permittivity at the center 
            of each Yee cell inside the volume. For anisotropic materials,
            the components are averaged.
        mesh : tuple of np.ndarray
            Three arrays defining the Cartesian grid of x, y, and z positions
            where the permittivity array is returned, such that
            ``epsilon.shape == (mesh[0].size, mesh[1].size, mesh[2].size)``.
        """

        if monitor is not None:
            span = monitor.span
        else:
            span = cs2span(center, size)

        minds = inside_box_coords(span, self.grid.coords)
        mesh = (
            self.grid.mesh[0][minds[0][0]:minds[0][1]],
            self.grid.mesh[1][minds[1][0]:minds[1][1]],
            self.grid.mesh[2][minds[2][0]:minds[2][1]],
        )

        eps = self._get_eps(mesh, pec_val=pec_val, pmc_val=pmc_val,
                    freq=frequency, syms=syms)

        return eps, mesh


    def set_time(self, run_time=None, courant=None):
        """Change the value of the run time of the simulation and the time 
        step determined by the courant stability factor.
        
        Parameters
        ----------
        run_time : None or float
            (second) If a float, the new ``run_time`` of the simulation. 
        courant : None or float, optional
            If a float, the new courant factor to be used.
        """

        if run_time is not None:
            self.run_time = run_time

        if courant is not None:
            self.courant = courant
            self._set_time_step(courant)
            for (mat, mat_name) in zip(self.materials, self._mat_names):
                check_poles(mat, mat_name, self.dt)

        # Raise an error if number of time steps is crazy large
        if self.run_time/self.dt > 1e9:
            log_and_raise(
                f"Too many time steps, {self.run_time/self.dt:1.2e}.",
                Tidy3DError
            )

        if run_time is not None or courant is not None:
            self.tmesh = np.arange(0, self.run_time, self.dt)
            self.Nt = np.array(self.tmesh.size)


    def _set_time_step(self, stability_factor=0.9):
        """Set the time step based on the generalized Courant stability
        Delta T < 1 / C_0 / sqrt(1 / dx^2 + 1/dy^2 + 1/dz^2)
        dt = courant_condition * stability_factor, so stability factor
        should be < 1.
        """

        dL_sum = np.sum([1 / self.grid.mesh_step[ir] ** 2 for ir in range(3)])
        dL_avg = 1 / np.sqrt(dL_sum)
        courant_stability = dL_avg / C_0
        self.dt = float_(courant_stability * stability_factor)


    def compute_modes(self, mode_object, Nmodes, target_neff=None,
            pml_layers=(0, 0), bend_radius=None, bend_axis=None):
        """Compute the eigenmodes of the 2D cross-section of a 
        :class:`.ModeSource` or :class:`.ModeMonitor` object, assuming 
        translational invariance in the third dimension. The eigenmodes are 
        computed at the central frequency of the :class:`.ModeSource` or for
        every frequency in the list of frequencies of the
        :class:`.ModeMonitor`. In-plane, PEC boundaries are assumed, such that
        the mode shold decay at the boundaries to be accurate. PML boundaries
        can also be added to ensure decay. Use :meth:`.viz_modes` to 
        visuzlize the computed eigenmodes.
        
        Parameters
        ----------
        mode_object : ModeSource or ModeMonitor
            The object defining the 2D plane in which to compute the modes.
        Nmodes : int
            Number of eigenmodes to compute.
        target_neff : None or float, optional
            Look for modes with effective index closest to ``target_neff``.
        pml_layers : tuple, optional
            Number of PML layers to be added in each direction. These are added
            to the **interior** of the mode plane, i.e. its size is not
            extended.
        bend_radius : float or None, optional
            (micron) A curvature radius for simulation of waveguide bends.
        bend_axis : ``'x'``, ``'y'``, ``'z'`` or None, optional
            The axis normal to the plane in which the bend lies. This must be
            provided if ``bend_radius`` is not none, and it must be orthogonal
            to the axis normal to the mode plane.

        Note
        ----
        Adding PML layers could make the decay at the boundaries cleaner, but
        could also introduce spurious modes.
        """

        if isinstance(mode_object, ModeMonitor):
            try:
                self._compute_modes_monitor(mode_object, Nmodes, target_neff,
                    pml_layers, bend_radius, bend_axis)
            except Tidy3DError as e:
                mnt_data = self._mnt_data(mode_object)
                log_and_raise(
                    f"Unable to compute modes of monitor '{mnt_data.name}'. {e}",
                    MonitorError
                )

        elif isinstance(mode_object, ModeSource):
            try:
                self._compute_modes_source(mode_object, Nmodes, target_neff,
                    pml_layers, bend_radius, bend_axis)
            except Tidy3DError as e:
                src_data = self._src_data(mode_object)
                log_and_raise(
                    f"Unable to compute modes of source '{src_data.name}'. {e}",
                    SourceError
                )

    def export(self):
        """Return a dictionary with all simulation parameters and objects.
        """
        js = {}
        js["parameters"] = write_parameters(self)
        js["sources"] = write_sources(self)
        js["monitors"] = write_monitors(self)
        js["materials"], js["structures"] = write_structures(self)

        return js

    def export_json(self, fjson):
        """Export the simulation specification to a JSON file.
        
        Parameters
        ----------
        fjson : str
            JSON file name.
        """

        self.fjson = fjson
        with open(fjson, 'w') as json_file:
            json.dump(self.export(), json_file, indent=4)

    @classmethod
    def import_json(cls, fjson):
        """Import a simulation specification from a JSON file.
        
        Parameters
        ----------
        fjson : str
            JSON file name.
        """
        
        with open(fjson, 'r') as json_file:
            js = json.load(json_file)

        sim = cls._read_simulation(js)
        sim.fjson = fjson

        return sim

    def load_results(self, dfile, ind_src_norm=0):
        """Load all monitor data recorded from a Tidy3D run.
        The data from each monitor can then be queried using 
        :meth:`.data`.
        
        Parameters
        ----------
        dfile : str
            Path to the file containing the simulation results.
        ind_src_norm : int or None, optional
            Index of which source to be used for normalization of frequency 
            monitors. If ``None`` or larger than the number of monitors in the 
            simulation, the raw field data is loaded.
        """

        mfile = h5py.File(dfile, "r")

        if "diverged" in mfile.keys():
            if mfile["diverged"][0] == 1:
                logging.warning(mfile["diverged_msg"][0].decode('utf-8'))

        if ind_src_norm is not None:
            if len(self.sources) <= ind_src_norm:
                logging.warning(
                    "Source normalization index larger than number of sources "
                    "in the simulation; no normalization applied."
                )
            else:
                logging.info(
                    "Applying source normalization to all frequency "
                    f"monitors using source index {ind_src_norm}."
                )

        try:
            for (im, mnt_data) in enumerate(self._monitor_data):
                # Set source normalization
                if isinstance(mnt_data.monitor, FreqMonitor):
                    if (ind_src_norm is None or 
                            len(self.sources) <= ind_src_norm):
                        mnt_data.set_source_norm(None)
                    else:
                        mnt_data.set_source_norm(self.sources[ind_src_norm], self.tmesh)

                # Load field data
                mname = mnt_data.name
                self._load_fields(im, mfile[mname])

        except Exception as e:
            log_and_raise(f"Error when loading data. {e}", Tidy3DError)
        finally:
            mfile.close()