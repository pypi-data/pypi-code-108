import pandas as pd
import requests
import json
import re

def get_covid_data(data_type='cases', loc='', date=''):

    """Acquires Canada Covid Data of specified type
    and for an optionally provided date
    
    Parameters
    ----------
    data_type : str, default='cases'
        Type of data to be returned
    loc : str, optional
        Location (province) filter to search
        If none provided, will search all provinces in Canada
    date : str, optional
        Date to search, specified as 'DD-MM-YYYY'
        By default will return data for all available dates

    Examples
    --------
    >>> get_covid_data('cases', 'BC', '13-01-2021')
    >>> get_covid_data()
    """

    stat_types = ['cases', 'mortality', 'recovered', 'testing', 'active',
                  'dvaccine', 'avaccine', 'cvaccine']

    provinces = ['AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT', 'RP', '']

    if data_type not in stat_types:
        raise ValueError("Stat type must be within pre-defined options.\n Choose from: ['cases', 'mortality', 'recovered', 'testing', 'active', 'dvaccine', 'avaccine', 'cvaccine']")

    if loc not in provinces:    
        raise ValueError("Provines must be within pre-defined options or left empty.\n Choose from: ['AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT', 'RP', '']")

    pattern = r'(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}|$^'

    if not re.match(pattern, date):
        raise ValueError("Input date must follow DD-MM-YYY format")

    params = {
        'stat': data_type,
        'loc': loc,
        'date': date
    }

    res = requests.get('https://api.opencovid.ca/timeseries',
                      params=params)
    data = json.loads(res.text)

    return pd.DataFrame(data[data_type])