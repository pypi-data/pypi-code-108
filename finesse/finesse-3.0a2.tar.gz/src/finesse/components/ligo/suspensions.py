from finesse.components import Connector, NodeType, NodeDirection
from finesse.components.general import DOFDefinition
from finesse.components.mechanical import (
    MIMOTFWorkspace,
    get_mechanical_port,
)
from finesse.components.workspace import ConnectorWorkspace
import importlib.resources as pkg_resources
import numpy as np
from finesse.utilities.misc import reduce_getattr

TRIPLE_DATA = (
    None  # Global for storing the triple pendulum data so we don't keep reloading it
)

QUAD_DATA = (
    None  # Global for storing the triple pendulum data so we don't keep reloading it
)


def node_2_ligo_node(io, node, name_map={}):
    """Maps a Finesse node to a LIGO suspension model degree of freedom string, i.e.
    in.gnd.disp.L."""
    if node.name.startswith("F_"):
        _type = "drive"
        dof = node.name[2:]
    else:
        _type = "disp"
        dof = node.name
    mapp = {"z": "L", "yaw": "Y", "pitch": "P"}
    return "{io}.{port}.{_type}.{dof}".format(
        io=io,
        port=name_map.get(node.port.name, node.port.name),
        _type=_type,
        dof=mapp[dof.lower()],
    )


def quad_scipy_statespace():
    from scipy.signal import StateSpace
    import bz2
    import pickle
    from . import data

    # Load some data in and process it
    ss = pickle.loads(
        bz2.decompress(pkg_resources.read_binary(data, "quad_damped_ss.pbz2"))
    )

    SS = StateSpace(ss["A"], ss["B"], ss["C"], ss["D"])
    SS.input_names = ss["inputs"]
    SS.output_names = ss["outputs"]
    return SS


class LIGOQuadSuspension(Connector):
    """A mechanics element that represents a LIGO Quad suspension.

    LIGO Quad
    generate_Quad_Model_Production.m
    SVN REV 10312
    https://redoubt.ligo-wa.caltech.edu/svn/sus/trunk/QUAD/Common/MatlabTools

    The Matlab code above was run to generate the state space model which
    was exported to Python. The Python Controls toolbox was then used
    to generate the transfer-function coefficients and stored in a Pickled
    file which this object accesses.

    The component being suspended must have a mechanical port with
    nodes z, pitch, and yaw and forces F_z, F_pitch, and F_yaw.

    This mechanics element provides access to the ground (`gnd` port)
    and penultimate (`pum` port) mass stages for injecting in
    displacement noise or feedback signals for controlling the test
    (`tst` port) mass.

    >>> from scipy.io import loadmat
    >>> import bz2
    >>> import pickle
    >>>
    >>> SS = loadmat('/Users/ddb/quad_ss.mat')
    >>>
    >>> A = SS['ss'][0][0][0]
    >>> B = SS['ss'][0][0][1]
    >>> C = SS['ss'][0][0][2]
    >>> D = SS['ss'][0][0][3]
    >>> inputs = {_[0]: i for i, _ in enumerate(SS['ss'][0][0][15].squeeze())}
    >>> outputs = {_[0]: i for i, _ in enumerate(SS['ss'][0][0][18].squeeze())}
    >>>
    >>> tfs = control.ss2tf(A, B, C, D)
    >>>
    >>> with bz2.BZ2File("/Users/ddb/git/finesse3/src/finesse/components/ligo/data/quad_damped_ss.pbz2", 'w') as f:
    >>>     pickle.dump({
    >>>         "A": A,
    >>>         "B": B,
    >>>         "C": C,
    >>>         "D": D,
    >>>         "inputs": inputs,
    >>>         "outputs": outputs
    >>>     }, f, protocol=3)
    """

    def __init__(self, name, connect_to):
        super().__init__(name)

        mech_port = get_mechanical_port(connect_to)
        # Add motion and force nodes to mech port.
        # Here we duplicate the already created mechanical
        # nodes in some other connector element
        self._add_port("tst", NodeType.MECHANICAL)
        self.tst._add_node("z", None, mech_port.z)
        self.tst._add_node("yaw", None, mech_port.yaw)
        self.tst._add_node("pitch", None, mech_port.pitch)
        self.tst._add_node("F_z", None, mech_port.F_z)
        self.tst._add_node("F_yaw", None, mech_port.F_yaw)
        self.tst._add_node("F_pitch", None, mech_port.F_pitch)
        # Suspension point ground port
        self._add_port("gnd", NodeType.MECHANICAL)
        self.gnd._add_node("z", NodeDirection.BIDIRECTIONAL)
        self.gnd._add_node("yaw", NodeDirection.BIDIRECTIONAL)
        self.gnd._add_node("pitch", NodeDirection.BIDIRECTIONAL)
        # Penultimate mass port
        self._add_port("pum", NodeType.MECHANICAL)
        self.pum._add_node("F_z", NodeDirection.BIDIRECTIONAL)
        self.pum._add_node("F_yaw", NodeDirection.BIDIRECTIONAL)
        self.pum._add_node("F_pitch", NodeDirection.BIDIRECTIONAL)
        # Intermediate mass port
        self._add_port("uim", NodeType.MECHANICAL)
        self.uim._add_node("F_z", NodeDirection.BIDIRECTIONAL)
        self.uim._add_node("F_yaw", NodeDirection.BIDIRECTIONAL)
        self.uim._add_node("F_pitch", NodeDirection.BIDIRECTIONAL)

        global QUAD_DATA
        if QUAD_DATA is None:
            import bz2
            import control
            import pickle
            from . import data

            # Load some data in and process it
            ss = pickle.loads(
                bz2.decompress(pkg_resources.read_binary(data, "quad_damped_ss.pbz2"))
            )
            tfs = control.ss2tf(
                ss["A"],
                ss["B"],
                ss["C"],
                ss["D"],
            )
            QUAD_DATA = (
                tfs,
                ss["inputs"],
                ss["outputs"],
                control.ss(ss["A"], ss["B"], ss["C"], ss["D"]),
            )

        self.tfs, self.inputs, self.outputs, self._ss = QUAD_DATA

        # Add in connections for GND/UIM/PUM coupling into TST
        for i in self.gnd.nodes + self.pum.nodes + self.uim.nodes:
            for o in self.tst.nodes:
                # Sus model computes how PUM/GND couple
                # into TST displacement
                if not o.name.startswith("F_"):
                    self._register_node_coupling(
                        f"{i.full_name}__{o.full_name}".replace(".", "_"), i, o
                    )
        # Add in TST drives to TST displacements
        # coupling and cross-coupling
        for i in self.tst.nodes:
            if i.name.startswith("F_"):  # drives only
                for o in self.tst.nodes:
                    if not o.name.startswith("F_"):  # disp only
                        self._register_node_coupling(
                            f"{i.full_name}__{o.full_name}".replace(".", "_"), i, o
                        )

        # Define typical degrees of freedom for this component
        import types

        self.dofs = types.SimpleNamespace()
        self.dofs.tst_z = DOFDefinition(f"{self.name}.dofs.tst_z", None, self.tst.z, 1)
        self.dofs.tst_F_z = DOFDefinition(
            f"{self.name}.dofs.tst_F_z", None, self.tst.F_z, 1
        )
        self.dofs.pum_F_z = DOFDefinition(
            f"{self.name}.dofs.pum_F_z", None, self.pum.F_z, 1
        )
        self.dofs.gnd_z = DOFDefinition(f"{self.name}.dofs.gnd_z", None, self.gnd.z, 1)

    @property
    def ss(self):
        return self._ss

    def input_output_indices(self, input_node, output_node):
        name_map = {n.port.name: "tst" for n in self.tst.nodes}
        idx = self.inputs[node_2_ligo_node("in", input_node, name_map)]
        odx = self.outputs[node_2_ligo_node("out", output_node, name_map)]
        return idx, odx

    def bode_plot(self, input_node, output_node, omega=None, Hz=True, **kwargs):
        import control

        if isinstance(input_node, str):
            input_node = reduce_getattr(self, input_node)
        if isinstance(output_node, str):
            output_node = reduce_getattr(self, output_node)

        i, o = self.input_output_indices(input_node, output_node)
        # Reduce numberof inputs/outputs in SS
        A = self.ss.A
        B = self.ss.B[:, i]
        C = self.ss.C[o, :]
        D = self.ss.D[o, i]
        ss = control.ss(A, B, C, D)
        return control.bode_plot(ss, omega=omega, Hz=Hz, **kwargs)

    def _get_workspace(self, sim):
        if sim.signal:
            import control

            refill = sim.model.fsig.f.is_changing  # Need to recompute H(f)
            idxs = []
            odxs = []
            N = 0
            for j, (i, o) in enumerate(self._registered_connections.values()):
                if i in sim.signal.nodes and o in sim.signal.nodes:
                    i = self.nodes[i]
                    o = self.nodes[o]
                    idx, odx = self.input_output_indices(i, o)
                    idxs.append(idx)
                    odxs.append(odx)
                    N += 1

            if N > 0:
                ws = MIMOSSWorkspace(self, sim)
                ws.QUAD_ss_cache = {}
                ws.signal.add_fill_function(self._signal_fill, refill)
                ws.N = N
                ws.iselect = tuple(set(idxs))
                ws.oselect = tuple(set(odxs))
                ws.idxs = tuple((ws.iselect.index(_) for _ in idxs))
                ws.odxs = tuple((ws.oselect.index(_) for _ in odxs))
                # Here we select a subset of inputs/outputs that we need
                # from the SS, otherwise we compute a frequency matrix with
                # a bunch of information we do not need
                ws.ss = control.ss(
                    self.ss.A,
                    self.ss.B[:, ws.iselect],
                    self.ss.C[ws.oselect, :],
                    self.ss.D[np.ix_(ws.oselect, ws.iselect)],
                )
                return ws
            else:
                return None
        else:
            return None

    def _signal_fill(self, ws):
        """There might be smarter more efficient ways to calcuate this:

        A note on shifted Hessenberg systems and frequency response computation
            https://dl.acm.org/doi/10.1145/2049673.2049676
            In this article, we propose a numerical algorithm for efficient
            and robust solution of a sequence of shifted Hessenberg linear systems.
            In particular, we show how the frequency response 𝒢(σ) = d-C(A-σ I)-1b in
            the single input case can be computed more efficiently than with other
            state-of-the-art methods. We also provide a backward stability analysis
            of the proposed algorithm.
        """
        s = 2j * np.pi * ws.sim.model_settings.fsig
        H = ws.ss(s)

        for i in range(ws.N):
            with ws.sim.signal.component_edge_fill3(ws.owner_id, i, 0, 0) as mat:
                mat[:] = H[ws.odxs[i], ws.idxs[i]]


class MIMOSSWorkspace(ConnectorWorkspace):
    pass


class LIGOTripleSuspension(Connector):
    """A mechanics element that represents a LIGO Triple suspension.

    LIGO Triple version 20140304TMproductionTM
    generate_TRIPLE_Model_Production.m
    SVN REV 10312
    https://redoubt.ligo-wa.caltech.edu/svn/sus/trunk/QUAD/Common/MatlabTools

    The Matlab code above was run to generate the state space model which
    was exported to Python. The Python Controls toolbox was then used
    to generate the transfer-function coefficients and stored in a Pickled
    file which this object accesses.

    The component being suspended must have a mechanical port with
    nodes z, pitch, and yaw and forces F_z, F_pitch, and F_yaw.

    This mechanics element provides access to the ground (`gnd` port)
    and penultimate (`pum` port) mass stages for injecting in
    displacement noise or feedback signals for controlling the test
    (`tst` port) mass.
    """

    def __init__(self, name, connect_to):
        super().__init__(name)
        mech_port = get_mechanical_port(connect_to)
        # Add motion and force nodes to mech port.
        # Here we duplicate the already created mechanical
        # nodes in some other connector element
        self._add_port("tst", NodeType.MECHANICAL)
        self.tst._add_node("z", None, mech_port.z)
        self.tst._add_node("yaw", None, mech_port.yaw)
        self.tst._add_node("pitch", None, mech_port.pitch)
        self.tst._add_node("F_z", None, mech_port.F_z)
        self.tst._add_node("F_yaw", None, mech_port.F_yaw)
        self.tst._add_node("F_pitch", None, mech_port.F_pitch)
        # Suspension point ground port
        self._add_port("gnd", NodeType.MECHANICAL)
        self.gnd._add_node("z", NodeDirection.BIDIRECTIONAL)
        self.gnd._add_node("yaw", NodeDirection.BIDIRECTIONAL)
        self.gnd._add_node("pitch", NodeDirection.BIDIRECTIONAL)
        # Penultimate mass port
        self._add_port("pum", NodeType.MECHANICAL)
        self.pum._add_node("F_z", NodeDirection.BIDIRECTIONAL)
        self.pum._add_node("F_yaw", NodeDirection.BIDIRECTIONAL)
        self.pum._add_node("F_pitch", NodeDirection.BIDIRECTIONAL)

        global TRIPLE_DATA
        if TRIPLE_DATA is None:
            import bz2
            import control
            import pickle
            from . import data

            # Load some data in and process it
            ss = pickle.loads(
                bz2.decompress(
                    pkg_resources.read_binary(data, "ligo_triple_suspension_ss.pbz2")
                )
            )
            tfs = control.ss2tf(
                ss["A"],
                ss["B"],
                ss["C"],
                ss["D"],
            )
            TRIPLE_DATA = (tfs, ss["inputs"], ss["outputs"])

        self.tfs, self.inputs, self.outputs = TRIPLE_DATA

        # Add in connections for GND/PUM coupling into TST
        for i in self.gnd.nodes + self.pum.nodes:
            for o in self.tst.nodes:
                # Sus model computes how PUM/GND couple
                # into TST displacement
                if not o.name.startswith("F_"):
                    self._register_node_coupling(
                        f"{i.full_name}__{o.full_name}".replace(".", "_"), i, o
                    )
        # Add in TST drives to TST displacements
        # coupling and cross-coupling
        for i in self.tst.nodes:
            if i.name.startswith("F_"):  # drives only
                for o in self.tst.nodes:
                    if not o.name.startswith("F_"):  # disp only
                        self._register_node_coupling(
                            f"{i.full_name}__{o.full_name}".replace(".", "_"), i, o
                        )

        # Define typical degrees of freedom for this component
        import types

        self.dofs = types.SimpleNamespace()
        self.dofs.tst_z = DOFDefinition(f"{self.name}.dofs.tst_z", None, self.tst.z, 1)
        self.dofs.tst_F_z = DOFDefinition(
            f"{self.name}.dofs.tst_F_z", None, self.tst.F_z, 1
        )
        self.dofs.pum_F_z = DOFDefinition(
            f"{self.name}.dofs.pum_F_z", None, self.pum.F_z, 1
        )
        self.dofs.gnd_z = DOFDefinition(f"{self.name}.dofs.gnd_z", None, self.gnd.z, 1)

    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing  # Need to recompute H(f)
            N = len(self._registered_connections)
            ws = MIMOTFWorkspace(self, sim, refill, N)
            ws.set_denominator(self.tfs.den[0][0])
            name_map = {n.port.name: "tst" for n in self.tst.nodes}

            # Setup the TFs for filling
            for j, (i, o) in enumerate(self._registered_connections.values()):
                i = self.nodes[i]
                o = self.nodes[o]
                idx = self.inputs[node_2_ligo_node("in", i, name_map)]
                odx = self.outputs[node_2_ligo_node("out", o, name_map)]
                ws.add_numerator(self.tfs.num[odx][idx])

            return ws
        else:
            return None
