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
    'linestyle': 'dotted',
    'linewidth': 1,
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

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}