from pathlib import Path
from spinterface.visualizations.lattices.cvisualpyvistabilayer import CVisualPyvistaBilayer
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista

latt = CLattice(source='STM', path = Path.cwd() / 'sp_J_AA0.0_im.dat')

# visualizer = CVisualPyVista(lattice=latt)
visualizer = CVisualPyvistaBilayer(lattice=latt,cmap='coolwarm',filter_around_layercenter=7, filter_half=True, dist_bot=15, dist_top=15)
#visualizer()
visualizer.show()