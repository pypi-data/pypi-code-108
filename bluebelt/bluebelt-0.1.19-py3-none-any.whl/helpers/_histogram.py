import numpy as np
import pandas as pd
from decimal import Decimal

def bins(series, points, min_bins=10, max_bins=20):

    if not isinstance(series, pd.Series):
        raise ValueError('series is not a Pandas Series')

    if not isinstance(points, (tuple, list)):
        raise ValueError('points is not a tuple or a list')

    if not isinstance(min_bins, int):
        raise ValueError('min_bins is not an integer')
    else:
        if min_bins < 1:
            min_bins = 1
    
    if not isinstance(max_bins, int):
        raise ValueError('max_bins is not an integer')
    else:
        if max_bins < 5:
            max_bins = 5
    
    
    # decimal places for points
    decimal_places = -min([Decimal(str(x)).as_tuple().exponent for x in points])
    
    gcd_factor = 10**decimal_places
    bin_size = np.gcd.reduce([int(round(x*gcd_factor)) for x in points]) / gcd_factor
    
    # adjust bin_size
    series_range = series.max() - series.min()

    ## min_bins
    range_factor = np.ceil(min_bins/(series_range/bin_size))
    bin_size = bin_size / range_factor
    
    ## max_bins
    range_factor = np.ceil((series_range/bin_size)/max_bins)
    bin_size = bin_size * range_factor

    # new decimal places
    decimal_places = -Decimal(str(bin_size)).as_tuple().exponent
    
    # get start and end
    start = round(series.min() - (series.min() % bin_size), decimal_places)
    end = round(series.max() - (series.max() % bin_size) + bin_size, decimal_places)

    return np.arange(start, end, bin_size)