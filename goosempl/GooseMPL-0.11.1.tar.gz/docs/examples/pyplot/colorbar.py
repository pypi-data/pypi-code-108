import matplotlib as mpl
import matplotlib.pyplot as plt

plt.style.use(["goose", "goose-latex"])

fig, ax = plt.subplots(figsize=(8, 2))

cbar = mpl.colorbar.ColorbarBase(
    ax,
    cmap=mpl.cm.get_cmap("RdBu_r"),
    norm=mpl.colors.Normalize(vmin=5, vmax=10),
    orientation="horizontal",
)

cbar.set_label("Some Units")

plt.savefig("colorbar.svg")
plt.close()
