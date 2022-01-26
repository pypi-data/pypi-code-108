import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.style.use(["goose", "goose-latex"])

# create colormap
# ---------------

# create a colormap that consists of
# - 1/5 : custom colormap, ranging from white to the first color of the colormap
# - 4/5 : existing colormap

# set upper part: 4 * 256/4 entries
upper = mpl.cm.jet(np.arange(256))

# set lower part: 1 * 256/4 entries
# - initialize all entries to 1 to make sure that the alpha channel (4th column) is 1
lower = np.ones((int(256 / 4), 4))
# - modify the first three columns (RGB):
#   range linearly between white (1,1,1) and the first color of the upper colormap
for i in range(3):
    lower[:, i] = np.linspace(1, upper[0, i], lower.shape[0])

# combine parts of colormap
cmap = np.vstack((lower, upper))

# convert to matplotlib colormap
cmap = mpl.colors.ListedColormap(cmap, name="myColorMap", N=cmap.shape[0])

# show some example
# -----------------

# open a new figure
fig, ax = plt.subplots()

# some data to plot: distance to point at (50,50)
x, y = np.meshgrid(np.linspace(0, 99, 100), np.linspace(0, 99, 100))
z = (x - 50) ** 2.0 + (y - 50) ** 2.0

# plot data, apply colormap, set limit such that our interpretation is correct
im = ax.imshow(z, cmap=cmap, clim=(0, 5000))

# add a colorbar to the bottom of the image
div = make_axes_locatable(ax)
cax = div.append_axes("bottom", size="5%", pad=0.4)
cbar = plt.colorbar(im, cax=cax, orientation="horizontal")

# save/show the image
plt.savefig("colormap.svg")
plt.close()
