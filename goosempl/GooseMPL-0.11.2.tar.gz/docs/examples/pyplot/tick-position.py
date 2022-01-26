import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["goose", "goose-latex"])

n = 5
x = np.arange(n)
y = np.sin(np.linspace(-3, 3, n))
xlabels = ["Long ticklabel %i" % i for i in range(n)]

fig, ax = plt.subplots()

ax.plot(x, y, "o-")

ax.set_xticks(x)

labels = ax.set_xticklabels(xlabels)

for i, label in enumerate(labels):
    label.set_y(label.get_position()[1] - (i % 2) * 0.075)

plt.savefig("tick-position.svg")
plt.close()
