from pltflow.utils.colors import colors

style = {
    "rcParams": {
        # Background color
        "axes.facecolor": "black",
        "figure.facecolor": "black",
        # Labels settings
        "axes.labelcolor": "white",
        "axes.labelsize": 20,
        "axes.labelpad": 25,
        # XY line axis color
        "axes.edgecolor": "white",
        # XY line width
        "axes.linewidth": 3,
        # XY line remove top/right
        "axes.spines.right": False,
        "axes.spines.top": False,
        # Change xy axis color
        "xtick.color": "white",
        "ytick.color": "white",
        "xtick.major.size": 6,
        "xtick.major.width": 2,
        "ytick.major.size": 6,
        "ytick.major.width": 2,
        # Y grid
        "grid.color": "lightgray",
        "grid.alpha": 0.2,
        "axes.grid": True,
        "axes.grid.axis": "y",
        # Savefig properties
        "savefig.facecolor": "black",
        "savefig.edgecolor": "black",
        "legend.loc": "best",
        "legend.fontsize": "medium",
        "legend.facecolor": "white",
        "legend.framealpha": 0.5,
    },
    "styleParams": {
        "xticks": {"fontsize": 11, "fontweight": "bold"},
        "yticks": {"fontsize": 11, "fontweight": "bold"},
        "ylabel": {
            "fontsize": 15,
            "fontweight": "bold",
            "labelpad": 14,
        },
        "xlabel": {
            "fontsize": 15,
            "fontweight": "bold",
            "labelpad": 14,
        },
        "title": {
            "fontsize": 19,
            "color": "white",
            "fontweight": "bold",
            "xy": (0.00, 1.16),
            "xycoords": "axes fraction",
        },
        "subtitle": {
            "color": "red",
            "fontsize": 16,
            "xy": (0.00, 1.085),
            "xycoords": "axes fraction",
        },
        "scatter": {"s": 30, "alpha": 0.8},
        "lines": {"linewidth": 1.5},
        "kde": {"linewidth": 0.1, "fill": True, "alpha": 0.6},
        "hist": {"linewidth": 0.1, "bins": 40, "alpha": 0.6},
    },
    "colors": {
        "lines": colors["mkbhd_palette"],
        "hist": colors["mkbhd_palette"],
        "kde": colors["mkbhd_palette"],
        "scatter": colors["mkbhd_palette"],
    },
}
