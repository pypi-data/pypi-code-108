import pandas as pd

import bluebelt.styles
import bluebelt.core.helpers

import warnings

def area(series, ax, **kwargs):

    # handle kwargs
    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{series.name} area plot')

    # area plot
    ax.stackplot(series.index, series.values, **style.graphs.area.stackplot)
    ax.plot(series, **style.graphs.area.plot)
    
    # labels
    ax.set_title(title, **style.graphs.area.title)
    
    # set x axis locator
    bluebelt.core.helpers._axisformat(ax, series)
    ax.set_ylim(0,)

def hist(series, ax, **kwargs):

    # handle kwargs
    xstyle = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{series.name} histogram')
    fit_normal_distribution = kwargs.pop('fit_normal_distribution', False)

    # histogram
    ax.hist(series, **style.graphs.hist.hist)
    ax.set_yticks([])

    # fit a normal distribution to the data
    if fit_normal_distribution:
        norm_mu, norm_std = stats.norm.fit(series.dropna())
        xlims = ax.get_xlim()
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        ax.plot(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), **style.graphs.hist.plot)

    # labels
    ax.set_title(title, **style.graphs.area.title)

def boxplot(series, ax, **kwargs):

    # get data
    if isinstance(series, (pd.Series, pd.DataFrame))and series.isnull().values.any():
        warnings.warn('the series contains Null values which will be removed', Warning)
        series = series.dropna()

    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', None)


        
    boxplot = ax.boxplot(series)

    for n, box in enumerate(boxplot['boxes']):
        # add style if any is given
        box.set(**style.graphs.boxplot.boxplot.get('boxes', {}))
        
    # title
    ax.set_title(title, **style.graphs.boxplot.title)