"""Actions to compute noise projections and budgets."""

import logging
from collections import defaultdict

import numpy as np

from ...env import warn
from ...detectors.compute.quantum import QShot0Workspace, QShotNWorkspace
from ...solutions import BaseSolution
from .base import Action
from .lti import FrequencyResponse

LOGGER = logging.getLogger(__name__)


class NoiseProjectionSolution(BaseSolution):
    def plot(self, output_node=None, lower=0.1, upper=3, *, ax=None, **kwargs):
        import matplotlib.pyplot as plt

        if output_node is None:
            output_node = self.output_nodes[0]

        if ax is None:
            fig = plt.gcf()
            if len(fig.axes) == 0:
                fig.subplots(1, 1)
            ax = fig.axes[0]

        total = np.sqrt((self.out[output_node] ** 2).sum(1))
        rng = lower * total.min(), upper * total.max()
        noises_to_plot = np.any(self.out[output_node] > rng[0], 0)
        if any(noises_to_plot):
            ax.loglog(self.f, self.out[output_node][:, noises_to_plot])
            ax.loglog(self.f, total, c="k", ls="-.", lw=2)
            ax.legend((*np.array(self.noises)[noises_to_plot], "Total"))
            ax.set_ylim(*rng)
        else:
            warn("No noise data to plot in this solution")

        ax.set_ylabel(
            f"ASD [{output_node if not self.scaling else self.scaling}/$\\sqrt{{\\mathrm{{Hz}}}}$]"
        )
        ax.set_xlabel("Frequency [Hz]")


class NoiseProjection(Action):
    def __init__(self, f, *output_nodes, scaling=None, name="loop"):
        if len(output_nodes) == 0:
            raise ValueError(
                "At least one output node must be specified to compute noise projection to"
            )
        super().__init__(name)
        process = lambda x: x.full_name if type(x) is not str else x

        self.f = f
        self.scaling = process(scaling) if scaling is not None else None
        self.output_nodes = tuple(process(o) for o in output_nodes)

        if len(self.output_nodes) > len(set(self.output_nodes)):
            raise ValueError(
                f"The same output node has been requested multiple times {self.output_nodes}"
            )

    def _do(self, state):
        sol = NoiseProjectionSolution(self.name)
        sol.f = self.f
        sol.output_nodes = self.output_nodes
        sol.scaling = self.scaling
        # create a list of callables func(fsig) to get the ASD noises
        noise_ASDs = {
            name: el.ASD.lambdify(state.model.fsig.f)
            for name, el in state.model.noises.items()
        }
        # labels for noises
        sol.noises = list(el.name for _, el in state.model.noises.items())
        # Keep track of which nodes have what noise injected into them
        noise_node_map = defaultdict(list)
        for name, el in state.model.noises.items():
            noise_node_map[el.node.full_name].append(el.name)
        # Collect any extra outputs that should be calculated during the fsig sweep. This
        # is to make efficient use of the filling and solving that this is already doing
        # to extract quantum noise, or others, as needed. Some of these outputs will be
        # signal frequency independant, such as standard shot-noise calculations, so just
        # compute them once.
        # TODO eventually handle qnoised detectors, which are frequency dependant
        fsig_indep_output = []
        for dws in state.sim.readout_workspaces:
            if isinstance(dws, (QShot0Workspace, QShotNWorkspace)):
                added = 0  # don't calculate anything if we aren't modelling the nodes
                # The quantum shot noise detectors will be on the optiical
                # input node, which we can't inject a signal into for computing
                # the noise propagation. Here we need to get the electrical outputs
                # of the readout and just put the noise in there
                for n in dws.owner.signal_nodes:
                    if n.full_name in state.sim.signal.nodes:
                        noise_node_map[n.full_name].append(dws.oinfo.name)
                        added += 1
                if added:
                    fsig_indep_output.append(dws)
        # Compute all the required transfer functions for noise propagation
        # NOTE: We use _do directly here because we just want to call the action
        # on this state, rather than `run` which will try and create a new state.
        # This is fine, as long as we have requested all the options it needs in
        # _requests. We can't make this frequency response in the init as we do
        # not have the model to grab all the various noise and shot-noise nodes
        self.input_nodes = tuple(noise_node_map.keys())
        sol.freqresp = FrequencyResponse(
            self.f, self.input_nodes, self.output_nodes
        )._do(state, fsig_indep_output)
        # Get any shot noise outputs from the solution
        for dws in fsig_indep_output:
            # Make a simple callable to work wiht the noise ASD functions
            noise_ASDs[dws.oinfo.name] = lambda f: sol.freqresp.extra_outputs[
                dws.oinfo.name
            ]
            sol.noises.append(dws.oinfo.name)
        # get a map from nodes->noise, for noise->node index in output
        inv_noise_node_map = {}
        for k, v in noise_node_map.items():
            for n in v:
                inv_noise_node_map[n] = self.input_nodes.index(k)
        # Convert all the ASDs into PSDs
        sol.PSDs = np.array(
            tuple(np.ones_like(self.f) * fn(self.f) ** 2 for fn in noise_ASDs.values())
        ).T
        # Use this to broadcast from the frequency response output to get the right
        # transfer function for each noise source
        out_indices = tuple(inv_noise_node_map[name] for name in noise_ASDs.keys())
        # Here we can compute some projection for calculating equivalent noise budgets
        if self.scaling:
            sol.scaling_solution = FrequencyResponse(
                self.f, self.scaling, self.output_nodes, open_loop=True
            )._do(state)
        sol.out = {}
        # compute abs(H)**2 for noise projection of PSDS
        HH = np.zeros(
            (len(self.f), len(out_indices), len(self.output_nodes)), dtype=float
        )
        np.abs(sol.freqresp.out[:, out_indices, :], out=HH)
        np.multiply(HH, HH, out=HH)
        # The final index of HH is the output node index, so we can quickly iterate over
        # them here to project the noises
        for i, output_node in enumerate(self.output_nodes):
            # sqrt(output**2/node**2 * node**2/Hz) => output/rtHz
            sol.out[output_node] = np.sqrt(HH[:, :, i] * sol.PSDs)
            if self.scaling:
                # output / scaling
                # sqrt(output**2/node**2 * node**2/Hz) => scaling/rtHz
                sol.out[output_node] /= np.abs(sol.scaling_solution.out[:, :, 0])
        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend(self.output_nodes)
        if self.scaling:
            memo["keep_nodes"].append(self.scaling)
        memo["keep_nodes"].extend((el.node.full_name for n, el in model.noises.items()))
