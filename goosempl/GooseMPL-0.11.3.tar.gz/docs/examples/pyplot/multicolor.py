import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["goose", "goose-latex"])

x = np.linspace(0, 2 * np.pi, 1000)
y = np.sin(x)

fig, ax = plt.subplots()

ax.plot(x, y, linestyle=(0, (10, 20)), color="r")
ax.plot(x, y, linestyle=(10, (10, 20)), color="g")
ax.plot(x, y, linestyle=(20, (10, 20)), color="b")

plt.savefig("multicolor.svg")
