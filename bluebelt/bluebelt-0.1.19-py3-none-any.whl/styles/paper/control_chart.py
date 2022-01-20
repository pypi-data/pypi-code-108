import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot = {
    'marker': 'o',
    'zorder': 50, 
}

# main plot background (used to create space in UCL and LCL area) | pyplot.plot
plot_background = {
    'marker': None,
    'color': defaults.white,
    'linewidth': 11,
    'zorder': 30, 
}

# ucl axhline | pyplot.axhline
ucl_axhline = {
    'color': defaults.grey,
    'linestyle': 'dashed',
    'linewidth': 1,
    'zorder': 1, 
}

# lcl axhline | pyplot.axhline
lcl_axhline = {
    'color': defaults.grey,
    'linestyle': 'dashed',
    'linewidth': 1,
    'zorder': 1, 
}

# mean axhline | pyplot.axhline
mean_axhline = {
    'color': defaults.grey,
    'linestyle': 'dashed',
    'linewidth': 1,
    'zorder': 40, 
    
}

# ucl fill_between | pyplot.fill_between
ucl_fill_between = {
    'color': None,
    'hatch': '//',
    'linestyle': 'solid',
    'linewidth': 0,
    'zorder': 10, 
}

# lcl fill_between | pyplot.fill_between
lcl_fill_between = {
    'color': None,
    'hatch': '//',
    'linestyle': 'solid',
    'linewidth': 0,
    'zorder': 10, 
}

# outlier background | pyplot.plot
outlier_background = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 17,
    'markerfacecolor': defaults.white,
    'zorder': 40, 
}

# outlier marker | pyplot.plot
outlier = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 9,
    'markerfacecolor': defaults.white,
    'markeredgecolor': defaults.black+(1,),
    'markeredgewidth': 1,
    'zorder': 45, 
}

# mean text | pyplot.text
mean_text = {
    'ha': 'left',
    'va': 'center',
    'zorder': 50,
}

# ucl text | pyplot.text
ucl_text = {
    'ha': 'left',
    'va': 'center',
    'zorder': 50,
}

# lcl text | pyplot.text
lcl_text = {
    'ha': 'left',
    'va': 'center',
    'zorder': 50,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}