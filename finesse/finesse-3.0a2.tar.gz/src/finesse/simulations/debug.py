# import logging
# import numpy as np
# import re

# from finesse.components.node import NodeType
# from finesse.simulations.base import BaseSimulation

# LOGGER = logging.getLogger(__name__)


# class DebugSimulation(BaseSimulation):
#     def active(self):
#         return self._M is not None

#     def print_matrix(self):
#         self._M.print_matrix()

#     def solve(self):
#         self.out = None
#         return

#     def __enter__(self):
#         """
#         When entered the Simulation object will create the matrix to be used in
#         the simulation.

#         This is where the matrix gets allocated and constructed. It will expect
#         that the model structure does not change after this until it has been
#         exited.
#         """
#         # Initialising the simulation expects there to be a self._M class that handles the
#         # matrix build/memory/etc. This must be set before initialising.

#         self._initialise()
#         self.initial_fill()
#         return self

#     def _initialise_submatrices(self):
#         from finesse.components import FrequencyGenerator

#         # Add in the diagonal elements of the matrix
#         # for n, node_inf in self._node_info.items():
#         #     Nsm = node_inf["nfreqs"]
#         #     Neq = node_inf["nhoms"]
#         #     for freq in range(Nsm):
#         #         fidx = self.findex(n, freq)  # Get index for this submatrix
#         #         comment = f"I,node={n.full_name},f={freq},fidx={fidx},Neq={Neq}"
#         #         self.M().declare_equations(Neq, fidx, comment)
#         #         Not building the diagonal currently

#         _done = {}
#         # Loop over every edge in the network which represents a bunch of
#         # connections between frequencies and HOMs between two nodes
#         for owner in self._edge_owners:
#             if owner in _done:
#                 continue

#             couples_f = isinstance(owner, FrequencyGenerator)

#             # For each connection this element wants...
#             for name in owner._registered_connections:
#                 # convert weak ref (input, output)
#                 nio = tuple(
#                     (owner.nodes[_] for _ in owner._registered_connections[name])
#                 )

#                 # If we are a carrier matrix only compute optics, no AC electronics or mechanics
#                 if not self.is_audio:
#                     if (
#                         nio[0].type is not NodeType.OPTICAL
#                         or nio[1].type is not NodeType.OPTICAL
#                     ):
#                         continue

#                 # Loop over all the frequencies we can couple between and add
#                 # submatrixes to the overall model
#                 for ifreq in self.frequencies:
#                     for ofreq in self.frequencies:
#                         # For each input and output frequency check if our
#                         # element wants to couple them at this
#                         if couples_f and not owner._couples_frequency(
#                             self, name, ifreq, ofreq
#                         ):
#                             continue
#                         elif not couples_f and ifreq != ofreq:
#                             # If it doesn't couple frequencies and the
#                             # frequencies are different then ignore
#                             continue

#                         iodx = []  # submatrix indices
#                         tags = []  # descriptive naming tags for submatrix key
#                         key_name = re.sub(r"^[^.]*\.", "", name)
#                         key_name = re.sub(r">[^.]*\.", ">", key_name)
#                         key = [owner, key_name]

#                         # Get simulation unique indices for submatrix
#                         # position. How we get these depends on the type of
#                         # the nodes involved
#                         for freq, node in zip((ifreq, ofreq), nio):
#                             if node.type is NodeType.OPTICAL:
#                                 iodx.append(self.findex(node, freq.index))
#                                 tags.append(freq.name)
#                                 key.append(freq)
#                             else:
#                                 # Mechanical and electrical don't have multiple
#                                 # freqs, so always use the zeroth frequency index
#                                 iodx.append(self.findex(node, 0))
#                                 tags.append("AC")
#                                 key.append(None)

#                         assert len(iodx) == 2
#                         assert len(key) == 4

#                         if tuple(key) not in self._submatrices:
#                             # smname = "{}__{}__{}".format(name, *tags)

#                             # print("Requesting:", *iodx, self.name, smname, i, j, nio)
#                             # Then we get a view of the underlying matrix which we set the values
#                             # with. Store one for each frequency. By requesting this view we are
#                             # telling the matrix that these elements should be non-zero in the
#                             # model.
#                             n1size = self._node_info[node]["nhoms"]
#                             n2size = self._node_info[node]["nhoms"]
#                             self._submatrices[tuple(key)] = np.zeros(
#                                 (n1size, n2size), dtype=complex
#                             )
#                         else:
#                             # Check if we've just requested the same submatrix.
#                             sm = self._submatrices[tuple(key)]
#                             if sm.from_idx != iodx[0] or sm.to_idx != iodx[1]:
#                                 raise Exception(
#                                     "Requested submatrix has already been requested,"
#                                     "but new one has different indices"
#                                 )
#                             else:
#                                 continue

#             _done[owner] = True

#     def __exit__(self, type_, value, traceback):
#         return

#     def _clear_rhs(self):
#         return None

#     def set_source(self, field_idx, vector):
#         return None
