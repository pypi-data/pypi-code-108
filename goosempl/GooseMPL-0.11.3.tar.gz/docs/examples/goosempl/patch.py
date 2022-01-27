import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex"])

coor = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0]])

conn = np.array([[0, 1, 4, 3], [1, 2, 5, 4]])

value = np.array([-1, +1])

fig, ax = plt.subplots()

im = gplt.patch(coor=coor, conn=conn, cindex=value, clim=[-2, 2], cmap="RdBu_r")

plt.xlim([-0.1, 2.1])
plt.ylim([-0.1, 1.1])

ax.set_aspect("equal")

div = make_axes_locatable(ax)
cax = div.append_axes("right", size="5%", pad=0.1)
cbar = plt.colorbar(im, cax=cax)

plt.savefig("patch.svg")
plt.close()
