import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.style.use(["goose", "goose-latex"])

np.random.seed(1)
data = np.sort(np.random.rand(8, 12))

fig, axes = plt.subplots(figsize=(16, 8), ncols=2)

cmap = mpl.cm.jet(np.linspace(0, 1, 20))
cmap = mpl.colors.ListedColormap(cmap[10:, :-1])

ax = axes[0]
c = ax.pcolor(data, edgecolors="k", linewidths=4, cmap=cmap, vmin=0.0, vmax=1.0)
div = make_axes_locatable(ax)
cax = div.append_axes("right", size="5%", pad=0.1)
cbar = plt.colorbar(c, cax=cax)

cmap = mpl.cm.jet(np.linspace(0, 1, 20))
cmap = mpl.colors.LinearSegmentedColormap.from_list("test", [cmap[10, :-1], cmap[-1, :-1]], N=10)

ax = axes[1]
c = ax.pcolor(data, edgecolors="k", linewidths=4, cmap=cmap, vmin=0.0, vmax=1.0)
div = make_axes_locatable(ax)
cax = div.append_axes("right", size="5%", pad=0.1)
cbar = plt.colorbar(c, cax=cax)

plt.savefig("colormap-part.svg")
plt.close()
