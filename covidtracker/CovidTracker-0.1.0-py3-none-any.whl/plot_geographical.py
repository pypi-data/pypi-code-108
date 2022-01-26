from CovidTracker.get_covid_data import get_covid_data 
import geopandas as gpd
import matplotlib.pyplot as plt
import re
import pandas as pd

import importlib.resources as pkg_resources
from . import templates 


def plot_geographical(covid_df,metric):
    """Creates a chloropleth map showing the number 
       of covid cases or other metric in each province of Canada

    Parameters
    ----------
    covid_df : pd.core.frame.DataFrame
        Pandas dataframe containing covid data to plot.

    metric : str
        column in the dataframe to plot 

    Returns
    -------
    plot : matplotlib.figure
        Cloropleth map of Covid metric numbers

    Examples
    --------
    >>> plot_geographical(covid_df,'cases')
    """

    if type(metric) != str:
        raise Exception("The value of the argument 'metric' must be of type string")

    if type(covid_df) != pd.DataFrame:
        raise Exception("The value of the argument 'covid_df' must be of type dataframe.")

    if metric not in covid_df.columns:
        raise ValueError(f"Chosen metric must be a column in the dataframe.\nPlease choose one from: {list(covid_df.columns)}")

    if re.match(r'^date', metric) or re.match(r'^province', metric) :
        raise ValueError("Chosen metric must not be date or province column.")

    if metric == 'testing_info':
        raise ValueError("Please choose a different metric with non null values.")

    # read in and tidy geodataframe containing Canada geography data
    with pkg_resources.path(templates, 'lpr_000b16a_e.shp') as fp:
        map_df = gpd.read_file(fp)[['PRENAME','geometry']]
        
        
    map_df = gpd.read_file(fp)[['PRENAME','geometry']]
    map_df = map_df.replace({'PRENAME' : {'Newfoundland and Labrador' : 'NL', 'Prince Edward Island' : 'PEI', 'British Columbia' : 'BC' ,'Northwest Territories' :'NWT'}})

    # data wranging if cumulative metric is chosen
    if re.match(r'^cumulative', metric):
        for met in list(covid_df.columns): # find date column 
            if met.startswith('date'):
                date_metric = met
                break

        covid_df[date_metric] = pd.to_datetime(covid_df[date_metric]) # convert date column to datetime
        covid_df=covid_df[(covid_df[date_metric] == covid_df[date_metric].max())] # filter for most recent date
        merged = map_df.set_index('PRENAME').join(covid_df.set_index('province'))

    # data wrangling for non cumulative columns
    else:
        covid_df = covid_df.groupby('province').sum()
        merged = map_df.set_index('PRENAME').join(covid_df)

    # Plot Cloropleth map
    fig, ax = plt.subplots(1, figsize=(10, 6))
    
    plt.close()
    merged.plot(column=metric, cmap='Reds', linewidth=0.8, ax=ax, edgecolor='0.8')
    ax.axis('off')

    vmin = merged[metric].min()
    vmax = merged[metric].max()

    sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm)
    cbar.set_label(f'Number of {metric.capitalize().replace("_", " ")}',labelpad=20)

    ax.set_title(f'Covid Numbers Across Canada: {metric.capitalize().replace("_", " ")}', fontdict={'fontsize': '15', 'fontweight' : '3'})

    return fig 
