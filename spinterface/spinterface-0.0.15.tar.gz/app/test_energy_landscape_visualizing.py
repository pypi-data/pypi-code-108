import numpy as np
import pandas as pd
import pyvista as pv
from pathlib import Path
from spinterface.visualizations.energylandscapes.i2dfunction import I2DFunction
from spinterface.visualizations.energylandscapes.cvisualpyvista import CVisualPyVista
from spinterface.algorithms.spineapple.minimizer.cnewton_2d import CNewton2D
from spinterface.algorithms.spineapple.gneb.cneb2d import CNEB2D,CciNEB2d


class Clandscape(I2DFunction):
    r"""

    """

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        omega_x = 1 / 4 * np.pi  # should produce minimum for x=+-4
        omega_y = 1 / 3 * np.pi  # should produce minimum for y=+-3
        return 1.0 * np.cos(1.0 * (omega_x * x)) + np.cos((omega_y * y)) + \
               self.gauss(x, y, x0=4, y0=3, a=4.0, sigmax=5, sigmay=5) + \
               self.gauss(x, y, x0=-4, y0=-3, a=4.0, sigmax=5, sigmay=5) + \
               self.gauss(x, y, x0=0, y0=-8, a=2.0, sigmax=5, sigmay=5) + \
               self.gauss(x, y, x0=1.5, y0=-3, a=1.5, sigmax=1, sigmay=2) + \
               self.gauss(x, y, x0=4, y0=-6, a=3.0, sigmax=3, sigmay=3) + \
               self.gauss(x, y, x0=4.0, y0=4.0, a=2.0, sigmax=3.2, sigmay=3.2)


x = np.linspace(-6, 5.0, 500)
y = np.linspace(-6, 4, 500)

func = Clandscape()
visualizer = CVisualPyVista(x=x, y=y, function=func, cam=[(9.094746928770046, 16.863633966086084, 29.17188311757661),
 (0.0, 0.0, -0.1160760797235747),
 (-0.35791776521192226, -0.7568231363882767, 0.5469128025317338)])


image = 5
point_size_big = 80
point_size_small = 50
# guess points near the minimum based on a view from the top===================================
#visualizer.show_grid_topview()

# start point to minimize into the a state:
newton_minimizer = CNewton2D(f=func, initial=np.array([2, -4]))
Astate = newton_minimizer()
if image in [1]:
    visualizer.placepointonsurface(xypoint=np.array([2, -4]), point_size=point_size_big, color='k')
    A_initial_projected = visualizer.projectosurface(np.array([2,-4]))
    A_projected=visualizer.projectosurface(Astate[-1])
    minimization_vector = pv.Arrow(start=A_initial_projected,direction=A_projected-A_initial_projected)
    visualizer.add_mesh(mesh=minimization_vector, color='k')
if image in [1,2,3,4,5]:
    visualizer.placepointonsurface(xypoint=Astate[-1], color='red', point_size=point_size_big)
#.............................................................

# start point to minimize into the m state
newton_minimizer = CNewton2D(f=func, initial=np.array([-1, -4]))
Mstate = newton_minimizer()
if image in [4]:
    M_initial_projected = visualizer.projectosurface(np.array([0,-1.8]))
    M_projected=visualizer.projectosurface(Mstate[-1])
    minimization_vector = pv.Arrow(start=M_initial_projected,direction=M_projected-M_initial_projected)
    visualizer.add_mesh(minimization_vector, color='k')
if image in [4,5]:
    visualizer.placepointonsurface(xypoint=Mstate[-1], color='red', point_size=point_size_big)

#visualizer.placepointonsurface(xypoint=Mstate[-1], color='red')
#.............................................................

# start point to minimize into the b state
newton_minimizer = CNewton2D(f=func, initial=np.array([-4, 2]))
Bstate = newton_minimizer()
if image in [1]:
    visualizer.placepointonsurface(xypoint=np.array([-4, 2]), point_size=point_size_big, color='k')
    B_initial_projected = visualizer.projectosurface(np.array([-4,2]))
    B_projected=visualizer.projectosurface(Bstate[-1])
    minimization_vector = pv.Arrow(start=B_initial_projected,direction=B_projected-B_initial_projected)
    visualizer.add_mesh(minimization_vector, color='k')
if image in [1,2,3,4,5]:
    visualizer.placepointonsurface(xypoint=Bstate[-1], color='red', point_size=point_size_big)
#.............................................................

# direct connection between A and B:
initial_path = visualizer.create_sequence_between_points(initial=Astate[-1], final=Bstate[-1], nr=15)
if image in [2]:
    visualizer.placepointsequenceonsurface(initial_path, color_points='gray', point_size=point_size_small, tuberadius=0.05)
#.............................................................

# constructed result after short NEB calculations
cut_point = np.array([0,-1.8])
initial_path_AM = visualizer.create_sequence_between_points(initial=Astate[-1], final=cut_point, nr=10)
initial_path_MB = visualizer.create_sequence_between_points(initial=cut_point, final=Bstate[-1], nr=10)
if image in [3,4]:
    if image in [3]:
        visualizer.placepointsequenceonsurface(initial_path_AM, color_points='gray', point_size=point_size_small, tuberadius=0.05)
        visualizer.placepointsequenceonsurface(initial_path_MB, color_points='gray', point_size=point_size_small, tuberadius=0.05)
    visualizer.placepointonsurface(xypoint=cut_point, point_size=point_size_big, color='k')
#.............................................................

# GNEB A to M
nebber = CNEB2D(f=func,initial=Astate[-1],final=Mstate[-1],nim=12)
#path_AM = nebber(i_write_out=True, write_out=Path.cwd() / 'path_AM.dat')
path_AM = nebber.read_convergedpath_fromfile(Path.cwd() / 'path_AM.dat')
ci_nebber = CciNEB2d(function=func, file=Path.cwd() / 'path_AM.dat')
#path_AMsp, sp = ci_nebber(i_write_out=True,write_out=Path.cwd() / 'path_AM_ci.dat')
path_AMsp = ci_nebber.read_convergedpath_fromfile(Path.cwd() / 'path_AM_ci.dat')
ci = ci_nebber.find_ci()

if image in [5]:
    visualizer.placepointsequenceonsurface(path_AMsp, color_points='blue', point_size=point_size_small,tuberadius=0.05)
    visualizer.placepointonsurface(xypoint=path_AMsp[ci], color='green', point_size=point_size_big)
#.............................................................

# GNEB M to B
nebber = CNEB2D(f=func,initial=Mstate[-1],final=Bstate[-1],nim=12)
#path_MB = nebber(i_write_out=True, write_out=Path.cwd() / 'path_MB.dat')
path_MB = nebber.read_convergedpath_fromfile(Path.cwd() / 'path_MB.dat')
ci_nebber = CciNEB2d(function=func, file=Path.cwd() / 'path_MB.dat')
#path_MBsp, sp = ci_nebber(i_write_out=True,write_out=Path.cwd() / 'path_MB_ci.dat')
path_MBsp = ci_nebber.read_convergedpath_fromfile(Path.cwd() / 'path_MB_ci.dat')
ci = ci_nebber.find_ci()
if image in [5]:
    visualizer.placepointsequenceonsurface(path_MBsp, color_points='blue', point_size=point_size_small,tuberadius=0.05)
    visualizer.placepointonsurface(xypoint=path_MBsp[ci], color='green', point_size=point_size_big)
#.............................................................

visualizer.show()
visualizer(outpath=Path.cwd() / f'method{image}.png')
