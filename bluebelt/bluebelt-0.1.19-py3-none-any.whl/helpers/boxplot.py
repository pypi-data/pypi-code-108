import numpy as np

def get_boxplot_quantiles(series, whis=1.5):
    # get the matplotlib boxplot quantiles
    # sort of direct copy from the matplotlib library

    q1, median, q3 = np.percentile(series, [25, 50, 75])

    if np.isscalar(whis):
        iqr = q3 - q1
        loval = q1 - (whis * iqr)
        hival = q3 + (whis * iqr)
    else:
        loval, hival = np.percentile(series, sorted(whis))

    # get high extreme
    wiskhi = series[series <= hival]
    if len(wiskhi) == 0 or np.max(wiskhi) < q3:
        high = q3
    else:
        high = np.max(wiskhi)

    # get low extreme
    wisklo = series[series >= loval]
    if len(wisklo) == 0 or np.min(wisklo) > q1:
        low = q1
    else:
        low = np.min(wisklo)
    
    return [low, q1, q3, high]

def get_boxplot_outliers(series, whis=1.5):
    low, q1, q3, high = get_boxplot_quantiles(series=series, whis=whis)

    return series[series < low].append(series[series > high]).values
