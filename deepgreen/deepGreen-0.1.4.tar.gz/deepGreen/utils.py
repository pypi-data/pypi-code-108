import numpy as np
import pandas as pd
from scipy import spatial
from termcolor import cprint

def p_header(text):
    return cprint(text, 'cyan', attrs=['bold'])

def p_hint(text):
    return cprint(text, 'grey', attrs=['bold'])

def p_success(text):
    return cprint(text, 'green', attrs=['bold'])

def p_fail(text):
    return cprint(text, 'red', attrs=['bold'])

def p_warning(text):
    return cprint(text, 'yellow', attrs=['bold'])

def find_closest_loc(lat, lon, target_lat, target_lon, mode=None, verbose=False):
    ''' Find the closet model sites (lat, lon) based on the given target (lat, lon) list

    Args:
        lat, lon (array): the model latitude and longitude arrays
        target_lat, target_lon (array): the target latitude and longitude arrays
        mode (str):
        + latlon: the model lat/lon is a 1-D array
        + mesh: the model lat/lon is a 2-D array

    Returns:
        lat_ind, lon_ind (array): the indices of the found closest model sites

    '''
    if mode is None:
        if len(np.shape(lat)) == 1:
            mode = 'latlon'
        elif len(np.shape(lat)) == 2:
            mode = 'mesh'
        else:
            raise ValueError('ERROR: The shape of the lat/lon cannot be processed !!!')

    if mode is 'latlon':
        # model locations
        mesh = np.meshgrid(lon, lat)

        list_of_grids = list(zip(*(grid.flat for grid in mesh)))
        model_lon, model_lat = zip(*list_of_grids)

    elif mode is 'mesh':
        model_lat = lat.flatten()
        model_lon = lon.flatten()

    elif mode is 'list':
        model_lat = lat
        model_lon = lon

    model_locations = []

    for m_lat, m_lon in zip(model_lat, model_lon):
        model_locations.append((m_lat, m_lon))

    # target locations
    if np.size(target_lat) > 1:
        #  target_locations_dup = list(zip(target_lat, target_lon))
        #  target_locations = list(set(target_locations_dup))  # remove duplicated locations
        target_locations = list(zip(target_lat, target_lon))
        n_loc = np.shape(target_locations)[0]
    else:
        target_locations = [(target_lat, target_lon)]
        n_loc = 1

    lat_ind = np.zeros(n_loc, dtype=int)
    lon_ind = np.zeros(n_loc, dtype=int)

    # get the closest grid
    for i, target_loc in enumerate(target_locations):
        X = target_loc
        Y = model_locations
        distance, index = spatial.KDTree(Y).query(X)
        closest = Y[index]
        nlon = np.shape(lon)[-1]

        if mode == 'list':
            lat_ind[i] = index % nlon
        else:
            lat_ind[i] = index // nlon
        lon_ind[i] = index % nlon

    if np.size(target_lat) > 1:
        return lat_ind, lon_ind
    else:
        if verbose:
            print(f'Target: ({target_lat}, {target_lon}); Found: ({lat[lat_ind[0]]:.2f}, {lon[lon_ind[0]]:.2f})')
        return lat_ind[0], lon_ind[0]

def rotate_lon(field, lon):
    ''' Make lon to be sorted with range (0, 360)

    Args:
        field (ndarray): the last axis is assumed to be lon
        lon (1d array): the longitude axis

    Returns:
        field (ndarray): the field with longitude rotated
        lon (1d array): the sorted longitude axis with range (0, 360)
    '''
    if np.min(lon) < 0:
        lon = np.mod(lon, 360)

    sorted_lon = sorted(lon)
    idx = []
    for lon_gs in sorted_lon:
        idx.append(list(lon).index(lon_gs))
    lon = lon[idx]
    field = field[..., idx]

    return field, lon

def monthly_to_df(monthly_array_1d, years=None):
    ''' Convert a monthly array of data into a DataFrame 
    '''
    nt = np.size(monthly_array_1d)
    ny = int(nt // 12) if nt % 12 == 0 else int(nt // 12) + 1
    monthly_array_2d = np.reshape(monthly_array_1d, (ny, 12))

    df = pd.DataFrame(monthly_array_2d, columns=np.arange(1, 13), index=years)
    return df

def gen_pseudoTRW(df_monthly_tas, df_monthly_pr, season_tas, season_pr,
                  weights_tas, weights_pr, coeff_tas=1, coeff_pr=1):
    ''' Generate pseudoTRW
    '''
    year_tas = df_monthly_tas.index.values
    year_pr = df_monthly_pr.index.values
    assert year_tas == year_pr, 'Inconsistent number of years for tas and pr!'
    n_year = np.size(year_tas)

    seasonal_tas = df_monthly_tas[season_tas].mean(axis=1)
    seasonal_pr = df_monthly_pr[season_pr].mean(axis=1)
    n_lag_tas = np.size(weights_tas)
    n_lag_pr = np.size(weights_pr)
    assert n_lag_tas == n_lag_pr, 'Inconsistent degree of lags for tas and pr!'
    n_lag = n_lag_tas

    n_TRW = n_year - n_lag + 1
    value_TRW = np.zeros()
    for i in range(n_TRW):
        value_TRW[i] = coeff_tas*np.dot(
            np.array([k for k in seasonal_tas.values[i:i+n_lag]]),
            weights_tas/np.sum(weights_tas),
        ) + coeff_pr*np.dot(
            np.array([k for k in seasonal_pr.values[i:i+n_lag]]),
            weights_pr/np.sum(weights_pr),
        )

    year_TRW = year_tas[n_lag-1:]
    return year_TRW, value_TRW