import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot = {
    'marker': 'o',
    'zorder': 20,
}

# median axhline | pyplot.axhline
median_axhline = {
    'color': defaults.grey,
    'linestyle': 'dashed',
    'linewidth': 1,
}

# longest runs about fill_between | pyplot.fill_between
longest_runs_about_fill_between = {
    'color': None,
    'hatch': '//',
    'linestyle': 'dashed',
    'linewidth': 0.5,
}

# longest runs up or down fill_between | pyplot.fill_between
longest_runs_up_or_down_fill_between = {
    'color': None,
    'hatch': '//',
    'linestyle': 'dashed',
    'linewidth': 0.5,
}

# median text | pyplot.text
median_text = {
    'ha': 'left',
    'va': 'center',
    'zorder': 50,
}

# longest runs about text | pyplot.text
longest_runs_about_text = {
    'ha': 'left',
    'va': 'bottom',
    'zorder': 50,
}

# longest runs up or down text | pyplot.text
longest_runs_up_or_down_text = {
    'ha': 'left',
    'va': 'top',
    'zorder': 50,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}