"""Direct probing of coupling coefficients."""

from finesse.detectors.general import Detector
from finesse.detectors.compute.amplitude import (
    KnmDetectorWorkspace,
    knm_detector_scalar_output,
    knm_detector_mode1_output,
    knm_detector_mode2_output,
    knm_detector_matrix_output,
)

from finesse.cymath.homs import field_index


class KnmDetector(Detector):
    """Direct probe of coupling coefficients at a component.

    This detector has several "modes" which depend upon the values
    given for the mode indices `n1`, `m1` and `n2`, `m2`. If:

      * all of `n1`, `m1`, `n2`, `m2` are specified then the detector
        will output a single complex coefficient corresponding to the
        coupling from ``(n1, m1) -> (n2, m2)``,
      * just `n1` and `m1` are specified then it will output a vector
        of complex coefficients corresponding to each coupling from
        ``(n1, m1) -> (n, m)`` for each mode ``(n, m)`` in the model,
      * only `n2` and `m2` are specified then it will output a vector
        of complex coefficients corresponding to each coupling from
        ``(n, m) -> (n2, m2)`` for each mode ``(n, m)`` in the model,
      * none of `n1`, `m1`, `n2`, `m2` are specified then the detector
        outputs the full matrix of complex coupling coefficients.

    .. hint::

        When using this detector in "full-matrix" mode (i.e. by not giving
        the values for any of the mode indices), it can be useful to combine
        the output with the :class:`.KnmMatrix` object to obtain a more
        convenient representation of the scattering matrix.

        An example of this is shown below, where the output of a detector
        of this type is wrapped using :meth:`.KnmMatrix.from_buffer`.

        .. jupyter-execute::

            import finesse
            finesse.configure(plotting=True)
            from finesse.knm.matrix import KnmMatrix

            IFO = finesse.Model()
            IFO.parse('''
            l L0 P=1
            link(L0, ITM)
            m ITM R=0.99 T=0.01 Rc=-2090 xbeta=0.3u
            s LARM ITM.p2 ETM.p1 L=4k
            m ETM R=0.99 T=0.01 Rc=2090

            cav ARM ITM.p2
            modes(x, maxtem=6)

            knmd K_itm_r ITM 22
            ''')

            out = IFO.run()
            # Make a KnmMatrix wrapper around the output from the detector
            k_mat = KnmMatrix.from_buffer(out["K_itm_r"], IFO.homs)
            # Now we can perform operations such as plotting the scattering matrix
            k_mat.plot(cmap="bone");

        See :ref:`arbitrary_scatter_matrices` for some examples on the utility that
        the :class:`.KnmMatrix` object provides.

    Parameters
    ----------
    name : str
        Name of newly created KnmDetector.

    comp : :class:`.Connector`
        A component which can scatter modes.

    coupling : str
        Coupling direction string, e.g. "11" for coupling coefficients on reflection from the front
        surface of a mirror.

    n1, m1, n2, m2: int or None
        From (n1, m1) and To (n2, m2) mode indices of the coupling coefficient(s) to retrieve.

        See above for the options.
    """

    def __init__(self, name, comp, coupling, n1=None, m1=None, n2=None, m2=None):
        Detector.__init__(self, name, label="Coupling coefficient", needs_trace=True)

        self.__comp = comp
        self.__coupling = str(coupling)
        if not self.__coupling.startswith("K"):
            self.__coupling = f"K{self.__coupling}"

        int_or_none = lambda x: None if x is None else int(x)
        self.n1 = int_or_none(n1)
        self.m1 = int_or_none(m1)
        self.n2 = int_or_none(n2)
        self.m2 = int_or_none(m2)

        if any(k < 0 for k in (self.n1, self.m1, self.n2, self.m2) if k is not None):
            raise ValueError("Mode indices cannot be negative.")

        for n, m in (("n1", "m1"), ("n2", "m2")):
            sn = getattr(self, n)
            sm = getattr(self, m)
            if (sn is None and sm is not None) or (sm is None and sn is not None):
                raise ValueError(f"Both of {n}, {m} must either be integers or None.")

        self.__mode1_given = self.n1 is not None
        self.__mode2_given = self.n2 is not None

    def _get_workspace(self, sim):
        # TODO (sjr) Move this block to a separate method which should get called
        #            whenever number of modes in model changes, otherwise
        #            querying self.dtype_shape or self.dtype_size will give
        #            incorrect result until simulation performed. Not a big
        #            problem though, as these are typically never accessed by user.
        if self.__mode1_given and self.__mode2_given:
            shape = ()
        elif self.__mode1_given or self.__mode2_given:
            shape = (sim.model_settings.num_HOMs,)
        else:
            shape = (sim.model_settings.num_HOMs, sim.model_settings.num_HOMs)
        self._update_dtype_shape(shape)

        for n, m in [(self.n1, self.m1), (self.n2, self.m2)]:
            if n is None:
                continue

            index = self._model.mode_index_map.get((n, m))
            if index is None:
                raise ValueError(f"The mode ({n},{m}) is not in the model!")

        ws = KnmDetectorWorkspace(self, sim)
        if self.__mode1_given:
            ws.from_idx = field_index(self.n1, self.m1, sim.model_settings.homs_view)
        if self.__mode2_given:
            ws.to_idx = field_index(self.n2, self.m2, sim.model_settings.homs_view)

        comp_ws = list(filter(lambda x: x.owner == self.__comp, sim.workspaces))
        if not comp_ws:
            raise RuntimeError(
                f"Could not find {self.__comp.name} in simulation workspace"
            )

        ws.knm_matrix = getattr(comp_ws[0], self.__coupling, None)
        if ws.knm_matrix is None:
            raise ValueError(
                f"Connector {self.__comp.name} has no scattering "
                f"matrix coupling {self.__coupling}"
            )

        if self.__mode1_given and self.__mode2_given:
            ws.set_output_fn(knm_detector_scalar_output)
        elif self.__mode1_given:
            ws.set_output_fn(knm_detector_mode1_output)
        elif self.__mode2_given:
            ws.set_output_fn(knm_detector_mode2_output)
        else:
            ws.set_output_fn(knm_detector_matrix_output)

        return ws
