from pltflow.utils.colors import colors

MAIN_FONT = "Roboto mono for powerline"

style = {
    "rcParams": {
        # Background color
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        # Labels settings
        "axes.labelcolor": "black",
        "axes.labelsize": 20,
        "axes.labelpad": 23,
        # XY line axis color
        "axes.edgecolor": "gray",
        # XY line width
        "axes.linewidth": 1,
        # XY line remove top/right
        "axes.spines.right": False,
        "axes.spines.top": False,
        # Change xy axis color
        "xtick.color": "black",
        "ytick.color": "black",
        "xtick.major.size": 6,
        "xtick.major.width": 1,
        "ytick.major.size": 7.2,
        "ytick.major.width": 1,
        # Y grid
        "grid.color": "lightgray",
        "grid.alpha": 0.3,
        "axes.grid": False,
        # Savefig properties
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "legend.loc": "best",
        "legend.fontsize": "medium",
        "legend.facecolor": "white",
        "legend.framealpha": 0.5,
    },
    "styleParams": {
        "xticks": {"fontsize": 11, "fontname": MAIN_FONT},
        "yticks": {"fontsize": 11, "fontname": MAIN_FONT},
        "ylabel": {
            "fontsize": 13,
            "fontname": MAIN_FONT,
            "fontweight": "bold",
            "labelpad": 14,
        },
        "xlabel": {
            "fontsize": 13,
            "fontname": MAIN_FONT,
            "labelpad": 14,
            "fontweight": "bold",
        },
        "title": {
            "fontsize": 16,
            "fontweight": "bold",
            "xy": (0.00, 1.16),
            "xycoords": "axes fraction",
            "fontname": MAIN_FONT,
        },
        "subtitle": {
            "fontsize": 12,
            "color": "#696969",
            "xy": (0.00, 1.09),
            "xycoords": "axes fraction",
            "fontname": MAIN_FONT,
        },
        "scatter": {"s": 40, "alpha": 0.8},
        "lines": {"linewidth": 1},
        "kde": {"linewidth": 0.1, "fill": True, "alpha": 0.6},
        "hist": {"linewidth": 0.1, "bins": 40, "alpha": 0.6},
    },
    "colors": {
        "lines": colors["base_palette"],
        "hist": colors["base_palette"],
        "kde": colors["base_palette"],
        "scatter": colors["base_palette"],
    },
}
