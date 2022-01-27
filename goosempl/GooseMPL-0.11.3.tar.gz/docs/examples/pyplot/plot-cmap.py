import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["goose", "goose-latex"])

x = np.linspace(0, 5, 100)
N = 21
cmap = plt.get_cmap("jet", N)

fig, ax = plt.subplots()

for i, n in enumerate(np.linspace(0, 2, N)):
    y = np.sin(x) * x ** n
    ax.plot(x, y, color=cmap(i))

ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(vmin=0, vmax=N))
sm.set_array([])

ticks = np.linspace(0, N - 1, int((N + 1) / 2))
labels = np.linspace(0, 2, int((N + 1) / 2))
boundaries = np.linspace(0, N, N + 1) - 0.5
cbar = plt.colorbar(sm, ticks=ticks, boundaries=boundaries)
cbar.ax.set_yticklabels([f"{i:.1f}" for i in labels])

plt.savefig("plot-cmap.svg")
plt.close()
