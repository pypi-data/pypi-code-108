import bluebelt.styles.defaults as defaults

# boxplot | pyplot.boxplot
boxplot = {
    'boxes': {
        'hatch': '//',
        },
}

# mean axvline | pyplot.axvline
mean_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# population mean axvline | pyplot.axvline
popmean_axvline = {
    'color': defaults.red,
    'linestyle': 'dashed',
    'linewidth': 1,
    'zorder': 99,
}

# ci mean horizontal line | pyplot.plot
ci_mean_plot = {
    'color': defaults.black,
    'zorder': 90,
}

# ci mean vertical lines (whiskers) | pyplot.plot
ci_mean_axvline = {
    'color': defaults.black,
    'zorder': 90,
}

# ci mean scatter (mean point) : pyplot.scatter
ci_mean_scatter = {
    'color': defaults.black,
    'zorder': 90,
}

# result text | pyplot.text
result_text = {
    'backgroundcolor': defaults.white,
    'va': 'top',
    'ha': 'left', 
}

# text | pyplot.text
text = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'center',
    'zorder': 10,
}

# text | pyplot.text
text_ci_min = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'right',
    'zorder': 0,
}

# text | pyplot.text
text_ci_max = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'left',
    'zorder': 0, 
}


ci_fill_between = {
    'alpha': 1,
    #'color': None,
    'edgecolor': defaults.blue,
    'facecolor': None, # color name, hex or None
    'hatch': '\\\\\\\\',
    'linewidth': 0,
}

# standard deviation axvline | pyplot.plot
ci_axvline = {
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
    'zorder': 10,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
    'size': defaults.small
}

# plot title | pyplot.set_title
suptitle = {
    'ha': 'left',
    'size': defaults.medium
}
