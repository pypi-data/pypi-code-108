# A collection of functions

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
from sklearn.metrics import (
    median_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
)
import datetime


def plotMovingAverage(
    series, window, plot_intervals=False, scale=1.96, plot_anomalies=False
):

    """
    Description: Given a time series "smooth" the data to reduce noise given a specfic window size to
    preform the averaging over. This function uses basic stats to additonally show anomolous points
    by setting plot_anomalies to True. This function can also provide a confidence interval over the average
    given plot_interval = True. A point is considered an anomaly if outside this range.

        series - dataframe with timeseries
        window - rolling window size
        plot_intervals - show confidence intervals
        plot_anomalies - show anomalies

    """
    rolling_mean = series.rolling(window=window).mean()

    plt.figure(figsize=(15, 5))
    plt.title("Moving average\n window size = {}".format(window))
    plt.plot(rolling_mean, "g", label="Rolling mean trend")

    # Plot confidence intervals for smoothed values
    if plot_intervals:
        mae = mean_absolute_error(series[window:], rolling_mean[window:])
        deviation = np.std(series[window:] - rolling_mean[window:])
        lower_bond = rolling_mean - (mae + scale * deviation)
        upper_bond = rolling_mean + (mae + scale * deviation)
        plt.plot(upper_bond, "r--", label="Upper Bond / Lower Bond")
        plt.plot(lower_bond, "r--")

        # Having the intervals, find abnormal values
        if plot_anomalies:
            anomalies = pd.DataFrame(index=series.index, columns=series.columns)
            anomalies[series < lower_bond] = series[series < lower_bond]
            anomalies[series > upper_bond] = series[series > upper_bond]
            plt.plot(anomalies, "ro", markersize=10)

    plt.plot(series[window:], label="Actual values", lw=0.5)
    plt.legend(loc="upper left")
    plt.grid(True)
    return rolling_mean


def list_stations():
    """
    This function lists all the stations available in the GLOS dataset. Preforms an API call to return
    (for each station available), its name, id, latitude and longitude coordinates, and platform id.

    Returns these details as a dictionary object, indexed by station name.
    """
    response = requests.get("https://seagull-api.glos.org/api/v1/obs-dataset-summaries")
    platform_details = {}

    for i in response.json():
        if i["deployment_site"]["body_of_water"] == "lake-erie":
            platform_details[i["platform_name"]] = [
                {"dataset_id": i["obs_dataset_id"]},
                {"latitude": i["deployment_site"]["latitude"]},
                {"longitude": i["deployment_site"]["longitude"]},
                {
                    "platform_id": i["obs_dataset_platform_assignment"][
                        "obs_dataset_platform_assignment_id"
                    ]
                },
                {"org_platform_id": i["org_platform_id"]},
            ]
    return platform_details


def list_station_measurment_types(station_name):
    """
    Given a station name from GLOS (input), return all time series measurement
    types available at this station. Returns a list of these names.
    """
    response = requests.get("https://seagull-api.glos.org/api/v1/obs-datasets.geojson")
    platform_info = []

    for i in response.json()["features"]:
        if i["properties"]["platform_name"] == station_name:
            return i["properties"]


def list_measurement_defintion(measurement=None):
    """
    Given a measurment type from one of the available GLOS stations return its defintion ie. what is it?
    to the user.
    """
    response = requests.get(
        "https://seagull-api.glos.org/api/v1/parameter-configurations"
    )
    data_types = {}

    for i in response.json():
        data_types[i["display_name"]["en"]] = i

    if measurement != None:
        return data_types[measurement]

    return data_types


def get_most_recent_measurement(station_name, measurement):
    """
    Given a GLOS station name, and a measurement type available at the station,
    return the most recent value of that measurement.

    ie. surface temperature at toledo site is 10 degree Celcius
    """
    station = list_stations()
    station_dataset_id = station[station_name][0]["dataset_id"]
    standard_name = list_measurement_defintion()[measurement]["standard_name"]

    response1 = requests.get("https://seagull-api.glos.org/api/v1/parameters")
    measurement_id = []

    for i in response1.json():
        if i["standard_name"] == standard_name:
            measurement_id.append(i["parameter_id"])

    response2 = requests.get(
        "https://seagull-api.glos.org/api/v1/obs-latest?startDate="
        + date.today().strftime("%Y-%m-%d")
    )
    for i in response2.json():
        if i["obs_dataset_id"] == int(station_dataset_id):
            for j in i["parameters"]:
                if j["parameter_id"] in measurement_id:
                    return j["observations"]


def get_historical_measurements(station_name, measurement, start_date, end_date):
    """
    Given a GLOS station, a measurement available at that station, a start_date,
    and end_date, return the measurement values over that window.

    Returns timeseries as a pandas dataframe object.
    """
    station = list_stations()
    station_dataset_id = station[station_name][0]["dataset_id"]
    standard_name = list_measurement_defintion()[measurement]["standard_name"]
    response1 = requests.get("https://seagull-api.glos.org/api/v1/parameters")
    measurement_id = []

    for i in response1.json():
        if i["standard_name"] == standard_name:
            measurement_id.append(i["parameter_id"])

    response2 = requests.get(
        "https://seagull-api.glos.org/api/v1/obs?obsDatasetId="
        + str(station_dataset_id)
        + "&startDate="
        + start_date
        + "&endDate="
        + end_date
    )
    for i in response2.json()[0]["parameters"]:
        if i["parameter_id"] in measurement_id:
            data = i["observations"]
            rows = []
            for row in data[::-1]:
                rows.append(pd.DataFrame.from_dict(row, orient="index").T)
            timeseries = pd.concat(rows)
            timeseries.timestamp = pd.to_datetime(timeseries.timestamp)
            timeseries.value = timeseries.value.astype(np.float)
            timeseries.reset_index(inplace=True, drop=True)
            return timeseries


def plot_stations():
    """
    Plot all stations on an interactive map that are providing user data to help monitor
    variables cotributing to HAB development.

    Returns a folium map object focused on lake erie.
    """
    stations = list_stations()
    erie_map = folium.Map(
        width=550,
        height=350,
        location=[42.4106739458553, -81.0343768809182],
        zoom_start=7.3,
    )
    for key in stations.keys():
        lat = stations[key][1]["latitude"]
        lon = stations[key][2]["longitude"]
        folium.Marker(
            location=[lat, lon], popup="Default popup Marker1", tooltip=key
        ).add_to(erie_map)

    folium.Marker(
        location=[42.906788, -79.616806],
        popup="Default popup Marker1",
        tooltip="Dunnville Site",
    ).add_to(erie_map)
    return erie_map


def plot_lake_depth(
    path_to_contour_file="/Users/nicholascalen/downloads/Lake_Erie_Contours/Lake_Erie_Contours.dbf",
):
    """
    Given a path to the stored contour depth file of lake erie (this is available from the sdk), plot it.
    User can provide a path input to the locations of the file optionally.
    """
    fig = plt.figure()
    ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])
    cmap = cm.get_cmap("hsv", 64)  # visualize with the new_inferno colormaps

    cb = mpl.colorbar.ColorbarBase(
        ax,
        orientation="horizontal",
        cmap=cmap,
        norm=mpl.colors.Normalize(0, 64),  # vmax and vmin
        label="Depth (m)",
        ticks=[0, 16, 32, 48, 64],
    )

    sf = shp.Reader(path_to_contour_file)
    plt.figure(figsize=(5, 5))
    zs = []
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        z = shape.record[1]
        plt.plot(x, y, color=cmap(z), label=z if z not in zs else "")
        zs.append(z)
    plt.xlabel("Longitude")
    plt.ylabel("Lattitude")
    plt.grid(True)
    plt.show()


def univariate_forecast_arima(series, horizon, frequency_of_obvs):
    """
    Using a simple ARIMA model provide a forecasr for one time series variable
    series: time series to forecast
    horizon: units in advance to forecast
    frequency_of_obvs: days, months, seconds, e.t.c

    returns: predictions, lower bound, upper bound confidence interval
    """
    model = auto_arima(
        series.value,
        start_p=1,
        start_q=1,
        test="adf",  # use adftest to find optimal 'd'
        max_p=3,
        max_q=3,  # maximum p and q
        m=1,  # frequency of series
        d=None,  # let model determine 'd'
        seasonal=False,  # No Seasonality
        start_P=0,
        D=0,
        trace=True,
        error_action="ignore",
        suppress_warnings=True,
        stepwise=True,
    )
    # Forecast
    fc, confint = model.predict(n_periods=horizon, return_conf_int=True)
    index_of_fc = pd.date_range(
        start=series.index[-1] + datetime.timedelta(hours=5), periods=horizon, freq="5H"
    )
    # make series for plotting purpose
    fc_series = pd.Series(fc, index=index_of_fc)
    lower_series = pd.Series(confint[:, 0], index=index_of_fc)
    upper_series = pd.Series(confint[:, 1], index=index_of_fc)
    return fc_series, lower_series, upper_series


cols = [
    "date_time",
    "maxtempC",
    "mintempC",
    "totalSnow_cm",
    "sunHour",
    "uvIndex",
    "DewPointC",
    "HeatIndexC",
    "WindChillC",
    "WindGustKmph",
    "cloudcover",
    "humidity",
    "precipMM",
    "pressure",
    "tempC",
    "visibility",
    "winddirDegree",
    "windspeedKmph",
    "location",
]


def get_weather_variables(
    start_date, end_date, station_name, freq, api_key="503fb7ba855e47a0b15154154222701"
):
    """
    Function to retrieve the weather data available. Returns weather from the location of the station
    through satilite.

    start_date: first data point from this date
    end_date: last data point from this date
    station_name: station of interest
    freq: frequency of the observations ie. 1 min, 1 hr, 1 day, e.t.c
    api_key: api_key to access open weather api

    returns: pandas df with the weather data
    """
    stations = list_stations()
    lat = stations[station_name][1]["latitude"]
    lon = stations[station_name][2]["longitude"]
    hist_weather_data = retrieve_hist_data(
        api_key,  # setup for lat, lon
        [str(lat) + "," + str(lon)],
        start_date,
        end_date,
        freq,
        location_label=False,
        export_csv=False,
        store_df=True,
    )
    return hist_weather_data[0][cols]


def aggregate_habnet_data(
    station_name,
    measurement,
    start_date,
    end_date,
    freq,
    path_to_contour_file="/Users/nicholascalen/downloads/Lake_Erie_Contours/Lake_Erie_Contours.dbf",
):
    """
    Function to aggregate all available data into one frame.

    measurement: measurement of interest that is available at the station
    start_date: first data point from this date
    end_date: last data point from this date
    station_name: station of interest
    freq: frequency of the observations ie. 1 min, 1 hr, 1 day, e.t.c
    path_to_contour_file: path to the bathemetry shap file.

    returns: pandas df indexed by timestamp with all the data
    """
    # 1. GLOS
    glos = get_historical_measurements(
        station, measurement, start_date, end_date  # start date  # end date
    )
    glos.set_index("timestamp", inplace=True)
    glos = glos.resample(freq).mean().ffill()
    glos.columns = [measurement]
    # 2. Weather
    weather = get_weather_variables(start_date, end_date, station, freq)
    weather.set_index("date_time", inplace=True)
    weather = weather.resample(freq).mean().ffill()
    weather.index = glos.index
    # 3. Depth
    stations = list_stations()
    lat = round(stations[station_name][1]["latitude"], 3)
    lon = round(stations[station_name][2]["longitude"], 3)
    sf = shp.Reader(path_to_contour_file)
    zs = []
    for shape in sf.shapeRecords():
        x = [round(i[0], 3) for i in shape.shape.points[:]]
        y = [round(i[1], 3) for i in shape.shape.points[:]]
        z = shape.record[1]
        if (lon in x) and (lat in y):
            break
    df = glos.join(weather)
    df["depth (m)"] = z
    return df
