import bluebelt.styles.defaults as defaults

# histogram | pyplot.hist
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

# plot used for normal distribution | pyplot.plot
normal_plot = {
    'color': defaults.blue,
    'linestyle': 'dashed',
    'linewidth': 1,
}

# standard deviation fill_between | pyplot.fill_between
std_fill_between = {
    'alpha': 1,
    #'color': None,
    'edgecolor': defaults.blue,
    'facecolor': None, # color name, hex or None
    'hatch': '\\\\\\\\\\',
    'linewidth': 0,
}

# standard deviation axvline | pyplot.plot
std_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# standard deviation axhline (line behind the text) | pyplot.plot
std_axhline = {
    'color': defaults.blue,
    'linestyle': 'solid',
    'linewidth': 1,
}

# standard deviation text | pyplot.text
std_text = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'center', 
}

# boxplot | pyplot.boxplot
boxplot = {
    'boxes': {
        'hatch': '//',
        },
}

# drop axvline (used for drop lines from ax 1 to ax 4) | pyplot.axvline
drop_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# ci mean horizontal line | pyplot.plot
ci_mean_plot = {
    'color': defaults.black,
}

# ci mean vertical lines (whiskers) | pyplot.plot
ci_mean_axvline = {
    'color': defaults.black,
}

# ci mean scatter (mean point) : pyplot.scatter
ci_mean_scatter = {
    'color': defaults.black,
}

# ci median horizontal line | pyplot.plot
ci_median_plot = {
    'color': defaults.black,
}

# ci median vertical lines (whiskers) | pyplot.plot
ci_median_axvline = {
    'color': defaults.black,
}

# ci median scatter (mean point) : pyplot.scatter
ci_median_scatter = {
    'color': defaults.black,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}