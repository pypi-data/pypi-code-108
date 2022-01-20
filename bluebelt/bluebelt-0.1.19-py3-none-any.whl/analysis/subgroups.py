import pandas as pd
import numpy as np

def get_subgroups(series, subgroups=None, subgroup_size=None):
    if subgroups is not None:
        subgroup_size = subgroups.value_counts().max()
        s = pd.Series(index=subgroups, data=series.values)
        groups = [(s[group].append(pd.Series((subgroup_size - len(s[group])) * [np.nan], dtype=float), ignore_index=True)) for group in np.unique(subgroups)]
        return pd.DataFrame(groups).T
    elif subgroup_size is not None:
        series = series.append(pd.Series(((subgroup_size - series.size) % subgroup_size) * [np.NaN], dtype=float), ignore_index=True)
        return pd.DataFrame(series.values.reshape(subgroup_size, int(series.size/subgroup_size)))
    else:
        return series