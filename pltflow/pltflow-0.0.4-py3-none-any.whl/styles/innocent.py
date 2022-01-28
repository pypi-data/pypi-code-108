from pltflow.utils.colors import colors

MAIN_FONT = "monofur for powerline"

style = {
    "rcParams": {
        # Background color
        "axes.facecolor": "#F3F0E0",
        "figure.facecolor": "#F3F0E0",
        # Labels settings
        "axes.labelcolor": "black",
        "axes.labelsize": 20,
        "axes.labelpad": 25,
        # XY line axis color
        "axes.edgecolor": "black",
        # XY line width
        "axes.linewidth": 0.5,
        # XY line remove top/right
        "axes.spines.right": False,
        "axes.spines.top": False,
        # Change xy axis color
        "xtick.color": "black",
        "ytick.color": "black",
        "xtick.major.size": 7,
        "xtick.major.width": 1,
        "ytick.major.size": 7,
        "ytick.major.width": 1,
        # Y grid
        "axes.grid": True,
        "axes.grid.axis": "both",
        "grid.linestyle": "--",
        "grid.linewidth": 1,
        "grid.alpha": 0.2,
        "grid.color": "#9e9d9d",
        # Savefig properties
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "legend.loc": "best",
        "legend.fontsize": "medium",
        "legend.facecolor": "white",
        "legend.framealpha": 0.5,
    },
    "styleParams": {
        "xticks": {"fontsize": 13, "fontweight": "normal", "fontname": MAIN_FONT},
        "yticks": {"fontsize": 13, "fontweight": "normal", "fontname": MAIN_FONT},
        "ylabel": {"fontsize": 17, "fontname": MAIN_FONT, "labelpad": 14},
        "xlabel": {"fontsize": 17, "fontname": MAIN_FONT, "labelpad": 14},
        "title": {
            "fontsize": 20,
            "fontweight": "bold",
            "xy": (0.00, 1.17),
            "xycoords": "axes fraction",
            "fontname": MAIN_FONT,
        },
        "subtitle": {
            "fontsize": 16,
            "color": "#696969",
            "xy": (0.00, 1.09),
            "xycoords": "axes fraction",
            "fontname": "monofur for powerline",
        },
        "scatter": {"s": 20, "alpha": 0.8},
        "lines": {"linewidth": 2},
        "kde": {"linewidth": 0.1, "fill": True, "alpha": 0.6},
        "hist": {"linewidth": 0.1, "bins": 40, "alpha": 0.6},
    },
    "colors": {
        "lines": colors["innocent_palette"],
        "hist": colors["innocent_palette"],
        "kde": colors["innocent_palette"],
        "scatter": colors["innocent_palette"],
    },
}
