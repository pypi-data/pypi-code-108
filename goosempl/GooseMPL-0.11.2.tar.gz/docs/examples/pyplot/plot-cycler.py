import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

plt.style.use(["goose", "goose-latex"])

x = np.linspace(0, 5, 100)
N = 21
cmap = plt.get_cmap("jet", N)
custom_cycler = cycler(color=[cmap(i) for i in range(N)])
plt.rc("axes", prop_cycle=custom_cycler)

fig, ax = plt.subplots()

for n in np.linspace(0, 2, N):
    y = np.sin(x) * x ** n
    ax.plot(x, y)

ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")

plt.savefig("plot-cycler.svg")
plt.close()
