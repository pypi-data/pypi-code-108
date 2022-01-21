from spinterface.inputs.lattice.CLattice import CLattice
from pathlib import Path
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista

latt = CLattice(source='evec',path=Path.cwd() / 'vec_4_skyr.dat')

visual = CVisualPyVista(lattice=latt,cam=[(53.486631523554976, 28.986632387822333, 28.986613940184775),
 (24.49999913573265, 0.0, -1.84476375579834e-05),
 (0.0, 0.0, 1.0)])
visual.show()
visual(outpath=Path.cwd() / 'vec_4_skyr.png')