"""

PyFLOSIC_dev
------------
Python Fermi-Loewdin orbital self-interaction correction

by S. Schwalbe, K. Trepte
and co-workers

How to use
----------

    >>> from ase.atoms import Atoms
    >>> from pyflosic2 import WORKFLOW
    >>> # Nuclei
    >>> sym = 'C'+4*'H'
    >>> p0 = [+0.00000000,+0.00000000,+0.00000000]
    >>> p1 = [+0.62912000,+0.62912000,+0.62912000]
    >>> p2 = [-0.62912000,-0.62912000,+0.62912000]
    >>> p3 = [+0.62912000,-0.62912000,-0.62912000]
    >>> p4 = [-0.62912000,+0.62912000,-0.62912000]
    >>> pos = [p0,p1,p2,p3,p4]
    >>> ase_atoms = Atoms(sym,pos)
    >>> # Workflow
    >>> wf = WORKFLOW(ase_atoms,
                      spin=0,
                      charge=0,
                      mode='unrestricted')
    >>> wf.kernel()
    >>> print(wf.etot)
"""
from pyflosic2.version.version import version_name
__version__ = version_name
from pyflosic2.sic.workflow import WORKFLOW
from pyflosic2.atoms.atoms import Atoms
