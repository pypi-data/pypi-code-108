import matplotlib.pyplot as plt

plt.style.use(["goose", "goose-latex"])

fig, ax = plt.subplots()

for i in range(10):
    x = [0, 1]
    y = [i / 10, (i + 10) / 10]
    ax.plot(x, y, label=fr"$i = {i:d}$")

ax.legend(loc="center right", facecolor="white", framealpha=1)

plt.savefig("legend_background.svg")
plt.close()
