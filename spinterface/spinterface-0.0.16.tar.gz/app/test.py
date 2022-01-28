from spinterface.inputs.CWriteInputs import CWriteInput
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from pathlib import Path
import numpy as np

lattice = CWriteInput(name='lattice.in', Nsize=f'20 20 1', alat='2.0 1.0 10.0',
                      lines=['lattice', '1.0 0.0 0.0', '0.0 1.0 0.0', '0.0 0.0 1.0',
                             'motif 2 atoms', f'0.0 0.0 0.0 {2.5}', '0.5 0.5 0.5 2.0'])
lattice(where=Path.cwd())

#latt = CLattice(source='STM',path=Path.cwd()/'SpinSTMi.dat')
latt = CLattice(magdir=np.array([1.0,0.0,0.0]))

latt.add_skyrmiontube(c=7.0,w=7.5)

latt.write()
print(latt.skradius)

visualizer = CVisualPyVista(lattice=latt)
#, cam=[(83.05595689117641, 66.51948874605938, 7.739481461469535),
# (19.499999448657036, 9.749999903142452, 0.24698486924171448),
# (-0.05425875800911427, -0.07071068929493245, 0.9960200728894695)])
visualizer.show()
#visualizer()