__version__ = '0.0.1'


import requests
import requests
from datetime import date
import folium 
import shapefile as shp  # Requires the pyshp package
import matplotlib as mpl
from matplotlib import cm
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from wwo_hist import retrieve_hist_data
from pmdarima.arima import auto_arima
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error 
import datetime 


from .habitat_fydp_package import *