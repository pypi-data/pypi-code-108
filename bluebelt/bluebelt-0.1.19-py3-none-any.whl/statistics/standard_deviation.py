import numpy as np
import bluebelt.helpers.constants as constants

# standard deviation
def short_term_std(series, observations=2):
    """
    Calculate the average moving range, or short term standard deviation.
    """
    periods = observations - 1
    series_length = series.shape[0]
    if observations >= series_length:
        raise InputError(f'The number of observations ({observations}) must be lower then the length of the series({series_length})')

    return sum(series.diff(periods=periods).apply(abs)[periods:]) / ((len(series) - observations + 1) * constants.d2(observations))

average_moving_range = short_term_std

def pooled_std(df, columns=None, **kwargs):
        """
        Calculate poolded standard deviation for pandas DataFrame columns.
        Pass kwargs for numpy.std (like ddof)
        pooled_std = (((n1-1)*std1**2 + (n2-1)*std2**2 +...+ (nk-1)*stdk**2) / (n1+n2+...+nk-k))**0.5
        """
        # have the entire dataframe or just some columns
        df = df if columns is None else df[columns]

        #alt = (sum(((df[column]-df[column].mean())**2).sum() for column in df) / (df.shape[0]-df.shape[1]))**0.5
        return (sum((len(df[column].values)-1)*np.std(df[column].values, **kwargs)**2 for column in df) / (sum(len(df[column].values) for column in df) - len(df.columns)))**0.5
        