import numpy as np
import pandas as pd
import pyvista as pv
from pathlib import Path
from spinterface.visualizations.energylandscapes.i2dfunction import I2DFunction
from spinterface.visualizations.energylandscapes.cvisualpyvista import CVisualPyVista
from spinterface.algorithms.spineapple.minimizer.cnewton_2d import CNewton2D
from spinterface.algorithms.spineapple.gneb.cneb2d import CNEB2D,CciNEB2d
from spinterface.algorithms.spineapple.modefollowing.cmodefollowing_2d import CModeFollowing2D


class Clandscape(I2DFunction):
    r"""

    """

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        omega_x = 1 / 4 * np.pi  # should produce minimum for x=+-4
        omega_y = 1 / 3 * np.pi  # should produce minimum for y=+-3
        return 1.0 * np.cos(1.0 * (omega_x * x)) + np.cos((omega_y * y)) + \
            self.gauss(x,y,x0=-4, y0=5, a=2.0, sigmax=3.0, sigmay=2) + \
            self.gauss(x,y,x0=-4, y0=-1, a=2.0, sigmay=2, sigmax=3.0)


x = np.linspace(-6, 6.0, 500)
y = np.linspace(0, 6, 500)

func = Clandscape()
visualizer = CVisualPyVista(x=x, y=y, function=func, cam= [(-13.331663532588744, -12.24130749359373, 22.990028902008252),
 (-0.7079845672515099, 2.2874402754346983, 1.3990931175195231),
 (0.3748579064849082, 0.6527011506467436, 0.6583788862730705)])


image = 4

point_size_big = 80 #8ß
point_size_small = 50 #50
# guess points near the minimum based on a view from the top===================================

# start point to minimize into the a state:
newton_minimizer = CNewton2D(f=func, initial=np.array([-4, 1]))
Astate = newton_minimizer()
if image in [1,2,3,4,5]:
    visualizer.placepointonsurface(xypoint=Astate[-1], color='red', point_size=point_size_big)

#visualizer.placepointonsurface(xypoint=np.array([-4, 1]), point_size=point_size_big, color='k')

#.............................................................

#visualizer.placepointonsurface(xypoint=np.array([4, 2]), point_size=point_size_big, color='k')
# start point to minimize into the b state:
newton_minimizer = CNewton2D(f=func, initial=np.array([4, 2]))
Bstate = newton_minimizer()
if image in [1,2,3,4,5]:
    visualizer.placepointonsurface(xypoint=Bstate[-1], color='red', point_size=point_size_big)
#.............................................................
# GNEB A to M
nebber = CNEB2D(f=func,initial=Astate[-1],final=Bstate[-1],nim=15)
#path_AB = nebber(i_write_out=True, write_out=Path.cwd() / 'path_AM.dat')
path_AB = nebber.read_convergedpath_fromfile(Path.cwd() / 'path_AM.dat')
ci_nebber = CciNEB2d(function=func, file=Path.cwd() / 'path_AM.dat')
#path_ABsp, sp = ci_nebber(i_write_out=True,write_out=Path.cwd() / 'path_AB_ci.dat')
path_ABsp = ci_nebber.read_convergedpath_fromfile(Path.cwd() / 'path_AB_ci.dat')
ci = ci_nebber.find_ci()
if image in [1,2,3]:
    visualizer.placepointsequenceonsurface(path_ABsp, color_points='blue', point_size=point_size_small,tuberadius=0.05)
    visualizer.placepointonsurface(xypoint=path_ABsp[ci], color='green', point_size=point_size_big)
#.............................................................

# construct transition state
if image in [2,3]:
    bx = pv.Box(bounds=[0.0,0.1,0.0,6.0,0,3.0])
    visualizer.add_mesh(bx,color='gray',opacity=0.5)

if image in [3]:
    mf = CModeFollowing2D(f=func,initial=Astate[-1])
    # points, evals, evecs = mf(mode_index=0,i_write_out=True,write_out=Path.cwd() / 'mf_0.dat')
    visualizer.create_eigenvalue_parabola(Astate[-1],evals=mf.eigenvalues_initial,evecs=mf.eigenvectors_initial,point_distance_xy=0.1,point_size=30, y_offset=1.5)
    mf = CModeFollowing2D(f=func,initial=path_ABsp[ci])
    # points, evals, evecs = mf(mode_index=0,i_write_out=True,write_out=Path.cwd() / 'mf_0.dat')
    visualizer.create_eigenvalue_parabola(path_ABsp[ci],evals=mf.eigenvalues_initial,evecs=mf.eigenvectors_initial,point_distance_xy=0.1,point_size=30,x_width=2,y_width=2,y_offset=1.5)

if image in [4]:
    mf = CModeFollowing2D(f=func, initial=path_ABsp[ci],mf_steps=20)
    points, evals, evecs = mf(mode_index=0,i_write_out=True,write_out=Path.cwd() / 'mode1.dat')
    visualizer.placepointsequenceonsurface(seq_xypoint=np.asarray(points),color_points='tab:orange')
    points, evals, evecs = mf(mode_index=1,i_write_out=True,write_out=Path.cwd() / 'mode2.dat')
    visualizer.placepointsequenceonsurface(seq_xypoint=np.asarray(points),color_points='tab:orange')


visualizer.show()
visualizer(outpath=Path.cwd() / f'method_1sp{image}.png')
