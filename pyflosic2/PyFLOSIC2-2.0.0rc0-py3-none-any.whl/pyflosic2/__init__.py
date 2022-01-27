"""

PyFLOSIC2
------------
| Open-Source Python Fermi-Löwdin orbital self-interaction correction
| development tool-box.
| https://opensic.gitlab.io/pyflosic2/
| 
| by S. Schwalbe, K. Trepte
| and co-workers
| The OpenSIC project 
| https://opensic.gitlab.io/opensic/

How to use
----------

    >>> from pyflosic2 import Atoms, WORKFLOW
    >>> # Nuclei
    >>> sym = ['C']+4*['H']
    >>> p0 = [+0.00000000,+0.00000000,+0.00000000]
    >>> p1 = [+0.62912000,+0.62912000,+0.62912000]
    >>> p2 = [-0.62912000,-0.62912000,+0.62912000]
    >>> p3 = [+0.62912000,-0.62912000,-0.62912000]
    >>> p4 = [-0.62912000,+0.62912000,-0.62912000]
    >>> pos = [p0,p1,p2,p3,p4]
    >>> atoms = Atoms(sym,pos,spin=0,charge=0)
    >>> # Workflow
    >>> wf = WORKFLOW(atoms, 
    >>>               tier_name='tier1',
    >>>               flevel=0,
    >>>               log_name='UWF.log',
    >>>               mode='unrestricted')
    >>> wf.kernel() 
    >>> print(wf.p.atoms,wf.etot) 

"""
from pyflosic2.version.version import version_name
__version__ = version_name
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.sic.workflow import WORKFLOW
from pyflosic2.sic.run import RUN
from pyflosic2.atoms.atoms import Atoms
from pyflosic2.gui.view import GUI
from pyflosic2.utils import systems_from_xyz
__all__ = ['Atoms','WORKFLOW','GUI']
