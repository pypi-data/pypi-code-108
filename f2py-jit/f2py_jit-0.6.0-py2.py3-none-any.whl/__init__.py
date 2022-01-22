"""
f2py_jit is a just-in-time extension module builder for Fortran 90
code. It improves and extends the `compile()` function available in
`f2py`, through a simple interface.

Features:
--------

- caching of modules builds across executions
- tagging of modules via arbitrary metadata
- interprocedural optimizations not triggered by f2py

This last feature is experimental, please check your results.

Examples:
--------
Compile the code, import it and execute it

>>> from f2py_jit import jit
>>> f90 = jit('code.f90')
>>> f90.hello()

Optionally inline internal subroutines in the Fortran 90 code

>>> from f2py_jit import jit, inline
>>> f90 = jit(inline('code.f90'))

The `jit` function also accepts Fortran code as string. See `docs/` for more examples.
"""


from .f2py_jit import *
from .finline import *
