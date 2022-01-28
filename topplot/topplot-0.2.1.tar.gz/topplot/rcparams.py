import matplotlib as mpl

# -----------------------------------------------------------------------------


def override_rcParams():
    """Customize MatPlotLib rcParams for topplot."""
    mpl.rcParams["legend.facecolor"] = "white"  # Doesn't work
    mpl.rcParams["legend.fancybox"] = True
    mpl.rcParams["legend.shadow"] = True
    # Disable keystrokes for toggling log scales
    mpl.rcParams["keymap.xscale"] = []
    mpl.rcParams["keymap.yscale"] = []
    # Remove clashes with topplot's keymap
    mpl.rcParams["keymap.back"] = filter(
        lambda x: x != "c", mpl.rcParams["keymap.back"]
    )


# -----------------------------------------------------------------------------


def rcParams():
    """Dump MatPlotLib rcParams."""
    # Override defaults
    override_rcParams()

    # Dump state
    for k, v in mpl.rcParams.items():
        print(f"mpl.rcParams['{k}'] = {v}")


# -----------------------------------------------------------------------------
