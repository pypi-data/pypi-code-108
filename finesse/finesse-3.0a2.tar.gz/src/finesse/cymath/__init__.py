"""Fast C functions providing common mathematical routines for the Cython level code in
Finesse.

Note that the functions and classes provided by this library
are generally only for developers or those extending the code
via additional Cython extensions.

Unless otherwise stated, the functions here do **not** work on
:class:`numpy.ndarray` objects. Instead, they operate on scalar
C types as they are primarily intended for use in low-level code.
"""
