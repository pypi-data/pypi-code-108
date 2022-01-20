import bluebelt.styles.defaults as defaults


histogram = {
    'density': True, 
    'alpha': 1, # alpha fraction 0-1
    'edgecolor': None, # color name, hex or None
    'facecolor': defaults.blue, # color name, hex or None
    'fill': False, #True, False
    'hatch': '//', # '/', '\', '|', '-', '+', 'x', 'o', 'O', '.' or '*'
    'linestyle': 'solid', # '-', '--', '-.', ':', '', (offset, on-off-seq), ...
    'linewidth': 1, # float
}

# histogram patches that need to be split; in range specs | pyplot.hist
histogram_fill_in_range = {
    'hatch': '//', # '/', '\', '|', '-', '+', 'x', 'o', 'O', '.' or '*'
}

# histogram patches that need to be split; out of range specs | pyplot.hist
histogram_fill_out_of_range = {
    'edgecolor': defaults.red, # color name, hex or None
    'linewidth': 0,
    'hatch': '////', # '/', '\', '|', '-', '+', 'x', 'o', 'O', '.' or '*'
}

histogram_patch_edge_color = defaults.red
histogram_patch_edge_hatch = '////'

# plot used for normal distribution | pyplot.plot
normal_plot_overall = {
    'color': defaults.blue,
    'linestyle': 'dashed',
    'linewidth': 1,
}
normal_plot_within = {
    'color': defaults.red,
    'linestyle': 'dashed',
    'linewidth': 1,
}

# target axvline | pyplot.axvline
target_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# USL, LSL axvline | pyplot.axvline
sl_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# USL, LSL, target text | pyplot.text
sl_text = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'center', 
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}