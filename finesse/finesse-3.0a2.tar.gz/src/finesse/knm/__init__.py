"""Library of coupling coefficient data structures and calculations.

Much of the code in this sub-package exists in a Cythonised form which
should only be used internally for calculating modal scattering during
simulations.

For the user, the :mod:`.tools` sub-module provides Python facing functions
for calculating certain types of coupling coefficients, and scattering
matrices of these, directly. The :mod:`.bayerhelms` module also contains
Python exposed functions for calculating Bayer-Helms :cite:`BayerHelms`
coefficients directly.

A data structure, :class:`.KnmMatrix`, representing a scattering matrix is
documented in :mod:`.matrix`. Objects of this type are returned whenever using
functions in this library which compute coupling coefficient matrices.

See :ref:`arbitrary_scatter_matrices` for details and examples on using some
of the Python-facing tools in this library.

Note that these tools use the same internal C code as that which gets executed
during simulations, and so will be very efficient off-the-shelf.
"""

from .maps import Map

__all__ = ("Map",)
