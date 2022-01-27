import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["goose", "goose-latex"])

x, y = np.meshgrid(np.linspace(0, 1, 100), np.linspace(0, 1, 100))
d = np.sqrt(x ** 2 + y ** 2)

fig, ax = plt.subplots()

cax = ax.imshow(d)

cbar = fig.colorbar(cax, aspect=10)
cbar.set_ticks([0, np.sqrt(2.0)])
cbar.set_ticklabels(["0", r"$\sqrt{2}$"])

ax.xaxis.set_ticks(range(0, 101, 20))
ax.yaxis.set_ticks(range(0, 101, 20))

ax.set_xlim([0, 100])
ax.set_ylim([0, 100])

ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")

plt.savefig("image.svg")
plt.close()
