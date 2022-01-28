import numpy as np

from finesse.element import ModelElement
from finesse.parameter import float_parameter
from finesse.solutions.base import BaseSolution


@float_parameter("ASD", "Amplitude spectral density", units="ASD")
class ClassicalNoise(ModelElement):
    def __init__(self, name, node, ASD):
        super().__init__(name)
        self._add_to_model_namespace = True
        self._namespace = (".noises",)
        self.node = node
        self.ASD = ASD

    def _on_add(self, model):
        if model is not self.node._model:
            raise Exception(
                f"{repr(self)} is using a node {self.node} from a different model"
            )


class NoiseSolution(BaseSolution):
    def __init__(self, name, f, output_nodes, noises, parents=None):
        super().__init__(name, parents)
        self.f = f
        self.dtype = np.dtype([(n.name, float) for n in noises])
        self.noises = {
            onode: np.zeros(f.shape, dtype=self.dtype) for onode in output_nodes
        }

    def total_ASD(self, output_node):
        return np.sqrt(sum(v ** 2 for v in self.noises[output_node].values()))

    def plot(
        self,
        output_node,
        noises=None,
        show_total=True,
        figsize_scale=1,
        ax=None,
    ):
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots()
        if not isinstance(output_node, str):
            output_node = output_node.full_name

        if output_node not in self.noises:
            raise Exception(
                f"The noise at {output_node} was not calculated, please recalculate."
            )

        for k, v in self.noises[output_node].items():
            if noises is not None and k not in noises:
                continue
            if hasattr(v, "shape"):
                ax.loglog(self.f, v, label=k)
            else:
                ax.loglog(self.f, v * np.ones_like(self.f), label=k)

        if (noises is not None and len(noises) > 1) or (show_total and noises is None):
            ax.loglog(
                self.f, self.total_ASD(output_node), c="k", ls=":", lw=3, label="Total"
            )

        ax.legend()
        ax.set_title(f"Noise at {output_node}")
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("ASD [UNIT/rtHz]")
        plt.gcf().tight_layout()
        return ax


def get_loop_network(model):
    import networkx
    import sympy
    from finesse.components import NodeType, Wire

    net = networkx.digraph.DiGraph()

    def is_electric(x):
        return all(p.type == NodeType.ELECTRICAL for p in x.ports)

    optics_in = set()  # nodes going into the optics
    optics_out = set()  # nodes coming out of the optics
    Omega = sympy.var("Omega")
    noise_nodes = tuple(n.node.full_name for n in model.noises)

    for i, o, d in model.network.edges(data=True):
        # Keep any edge going into an electronic element
        if (
            d["out_ref"]().type == NodeType.ELECTRICAL
            or d["in_ref"]().type == NodeType.ELECTRICAL
        ):
            if d["in_ref"]().connection or i in noise_nodes or o in noise_nodes:
                # Store the nodes that inject into an optical node
                # and those optical nodes that feed into the electronics
                if d["in_ref"]().type == NodeType.OPTICAL:
                    optics_out.add(d["out_ref"]())
                elif d["out_ref"]().type == NodeType.OPTICAL:
                    optics_in.add(d["in_ref"]())
                else:
                    el = d["owner"]()
                    sym = sympy.var(el.name)
                    if type(el) is Wire:
                        if not el.delay.is_changing:
                            sym = sympy.exp(-sympy.I * Omega * float(el.delay))
                        elif el.delay == 0:
                            sym = 1
                    net.add_edge(i, o, symbol=sym)
        elif d["in_ref"]().type == NodeType.MECHANICAL and i in noise_nodes:
            # Mechanical noise inputs need to be included so we can project them
            # These are really just inputs into the optical system.
            # I guess we could also have mechanical to electrical sensors...
            optics_in.add(d["in_ref"]())

    optic_couplings = {}
    # Add in placeholds for any opto-mechanic coupling
    for i in optics_in:
        for o in optics_out:
            sym = sympy.var(
                f"{i.full_name.replace('.','')}__{o.full_name.replace('.','')}"
            )
            net.add_edge(i.full_name, o.full_name, symbol=sym)
            optic_couplings[sym] = (i, o)
    return net, optic_couplings


def nx_to_coo_sparse(G, nodelist=None):
    from itertools import chain

    if nodelist is None:
        nodelist = list(G)
    nlen = len(nodelist)

    if nlen == 0:
        raise Exception("Graph has no nodes or edges")

    if len(nodelist) != len(set(nodelist)):
        raise Exception("Ambiguous ordering: `nodelist` contained duplicates.")

    index = dict(zip(nodelist, range(nlen)))
    # build I-M sparse matrix
    coefficients = zip(
        *chain(
            # Add in I matrix
            ((i, i, 1) for i in range(nlen)),
            # negative off-diagonal elements
            (
                (index[u], index[v], -d["symbol"])
                for u, v, d in G.edges(nodelist, data=True)
                if u in index and v in index
            ),
        )
    )

    try:
        row, col, data = coefficients
    except ValueError:
        # there is no edge in the subgraph
        row, col, data = [], [], []

    return row, col, data


# class NoiseAnalysis(Action):
#     def __init__(
#         self,
#         name,
#         mode,
#         start,
#         stop,
#         steps,
#         output_node,
#         *opt_output_nodes,
#         noises=None,
#     ):
#         super().__init__(name)
#         if mode not in ("lin", "log"):
#             raise Exception("mode must be lin or log")

#         if mode == "lin":
#             self.f = np.linspace(start, stop, steps)
#         else:
#             self.f = np.geomspace(start, stop, steps)

#         if noises is None:
#             self.noises = tuple(n.name for n in output_node.component._model.noises)
#         else:
#             self.noises = tuple(n.name for n in noises)

#         self.output_nodes = tuple(
#             (output_node.full_name, *(o.full_name for o in opt_output_nodes))
#         )
#         self._info.parameters_changing = tuple(("fsig.f",),)
#         self._info.makes_solution = True

#     def fill_info(self, p_info):
#         info = self.copy_info()
#         p_info.add(info)

#     def setup(self, s_prev, model: finesse.model.Model):
#         import sympy
#         from sympy.matrices import SparseMatrix
#         from sympy import Matrix

#         ws = NoiseAnalysisWorkspace(s_prev, model)
#         ws.s_prev = s_prev
#         ws.model = model
#         ws.info = self.copy_info()
#         ws.fn_do = self.do
#         ws.params = tuple(
#             finesse.analysis.actions.get_param(model, p)
#             for p in self._info.parameters_changing
#         )
#         for p in ws.params:
#             if not p.is_tunable:
#                 raise ParameterLocked(
#                     f"{repr(p)} must set as tunable " "before building the simulation"
#                 )
#         # Setup the symbolic sparse matrix for solving noise propagations
#         ws.loop_network, oc = get_loop_network(model)
#         ws.noises = tuple(n for n in model.noises if n.name in self.noises)
#         assert len(ws.noises) > 0
#         # returns a I-M matrix for solving
#         rcv = nx_to_coo_sparse(ws.loop_network)
#         ws.M_nodes = nodes = tuple(ws.loop_network.nodes)
#         M = SparseMatrix(
#             None, {k: v for k, v in zip(tuple(zip(rcv[0], rcv[1])), rcv[2])}
#         )
#         # Always ensure that the Signal frequency variable
#         # is present as we always fill that
#         ws.Omega = sympy.var("Omega")
#         ws.syms = M.free_symbols | set((ws.Omega,))
#         ws.Minv = Matrix(M).inv()
#         # Fill up a dict of how each noise
#         # couples into each output node
#         ws.TF = tuple([] for i in range(len(self.output_nodes)))
#         for i, onode in enumerate(self.output_nodes):
#             for j, noise in enumerate(ws.noises):
#                 noise_tf = ws.Minv[
#                     nodes.index(noise.node.full_name), nodes.index(onode)
#                 ].expand()
#                 ws.TF[i].append(
#                     sympy.lambdify(ws.syms, abs(noise_tf) ** 2, "numpy", dummify=False)
#                 )
#         ws.values = {s: 0 for s in ws.syms}
#         ws.OMEGA = ws.values[ws.Omega] = 2 * np.pi * self.f
#         ws.lambdas = tuple(noise.ASD.lambdify(ws.model.fsig.f) for noise in ws.noises)
#         # Get the simulations to do some calculations with in the do step
#         ws.carrier = model.carrier_simulation
#         try:
#             ws.signal = model.signal_simulation
#             ws.optical_couplings = {}
#             ins = []
#             outs = []
#             # Store optical coulpings node indices for injecting later
#             for key, (inode, onode) in oc.items():
#                 idx = ws.signal.field(inode, 0, 0)
#                 odx = ws.signal.field(onode, 0, 0)
#                 if idx in ins:
#                     x = ins.index(idx)
#                 else:
#                     ins.append(idx)
#                     x = len(ins) - 1
#                 if odx in outs:
#                     y = outs.index(odx)
#                 else:
#                     outs.append(odx)
#                     y = len(outs) - 1
#                 ws.optical_couplings[key] = (x, y)
#             ws.input_rhs_indices = np.array((tuple(ins)), dtype=int)
#             ws.output_rhs_indices = np.array((tuple(outs)), dtype=int)
#             ws.out_fsig_sweep = np.zeros(
#                 (len(ins), len(self.f), len(outs)), dtype=np.complex128
#             )
#         except AttributeError:
#             raise Exception(
#                 "Noise analysis requires a signal simulation to work, please set the model fsig.f frequency"
#             )

#         return ws

#     def update_symbolic_values(self, ws):
#         run_fsig_sweep(
#             ws.carrier,
#             ws.signal,
#             self.f,
#             ws.input_rhs_indices,
#             ws.output_rhs_indices,
#             ws.out_fsig_sweep,
#             True,
#         )
#         for sym in ws.syms:
#             if sym is ws.Omega:
#                 continue
#             el = ws.model.elements.get(str(sym))
#             if el:
#                 ws.values[sym] = el.eval(ws.OMEGA)
#             else:
#                 # Now we loop over the actual simulation and run each point
#                 i, o = ws.optical_couplings[sym]
#                 ws.values[sym] = ws.out_fsig_sweep[i, :, o]

#     def do(self, ws):
#         ws.sol = NoiseSolution(
#             self.name, self.f, self.output_nodes, ws.noises, ws.s_prev
#         )
#         ws.sol.Minv = ws.Minv
#         ws.sol.Minv_nodes = ws.M_nodes
#         self.update_symbolic_values(ws)
#         ws.sol.optical_tfs = ws.out_fsig_sweep
#         v = ws.values.values()
#         for i, onode in enumerate(self.output_nodes):
#             ws.sol.noises[onode] = {}
#             for j, noise in enumerate(ws.noises):
#                 y_noise = ws.lambdas[j](self.f) * ws.TF[i][j](*v)
#                 ws.sol.noises[onode][noise.name] = y_noise
