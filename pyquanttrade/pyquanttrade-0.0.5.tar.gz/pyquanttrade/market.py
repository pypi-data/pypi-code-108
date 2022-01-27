# -*- coding: utf-8 -*-
"""Class for get Market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import pandas as pd
import numpy as np
import altair as alt
import scipy.stats as stats
import scipy.spatial.distance as distance
import time, quandl
from decouple import config
class marketData(object):

    @staticmethod
    def get_data(ticker, init_date, end_date):
        quandl.ApiConfig.api_key=config("QUANDL_API_KEY")
        table_name = 'SHARADAR/SEP'
        filter_date = { 'gte': init_date, 'lte':end_date}
        source = quandl.get_table(table_name,  date = filter_date, ticker=ticker, paginate=True)
        source = pd.DataFrame(source).drop_duplicates("date")
        source["date"] = pd.to_datetime(source["date"])
        source = source.sort_values(by="date")
        source = source.set_index("date")
        return source

    @staticmethod
    def get_data_n_tries(ticker, init_date, end_date, n_tries = 5):
        tried = 0
        completed = False
        while tried<n_tries and completed == False:
            try:
                data = marketData.get_data(ticker, init_date, end_date)
                completed = True
            except:
                time.sleep(2000)
                tried += 1
        assert tried<n_tries, 'The data could not be retrieved after ' + str(n_tries) + ' tries'
        return data

    @staticmethod
    def get_data_lt(ticker, init_date):
        quandl.ApiConfig.api_key=config("QUANDL_API_KEY")
        table_name = 'SHARADAR/SEP'
        filter_date = {'gte':init_date}
        source = quandl.get_table(table_name,  date = filter_date, ticker=ticker, paginate=True)
        source = pd.DataFrame(source).drop_duplicates("date")
        source["date"] = pd.to_datetime(source["date"])
        source = source.sort_values(by="date")
        source = source.set_index("date")
        return source

    @staticmethod
    def get_data_and_visualize(
        ticker, init_date, end_date, moving_averages=[], ribbons=False
    ):
        # Get the data from ElasticSearch

        source = marketData.get_data(ticker, init_date, end_date)
        # visualize
        open_close_color = alt.condition(
            "datum.open < datum.close", alt.value("#06982d"), alt.value("#ae1325")
        )
        rule = (
            alt.Chart(source.reset_index())
            .mark_rule()
            .encode(
                alt.X(
                    "yearmonthdate(date):T",
                ),
                alt.Y("low", scale=alt.Scale(zero=False), axis=alt.Axis(title="Price")),
                alt.Y2("high"),
                color=open_close_color,
            )
            .properties(width=1000, height=400)
        )
        bar = (
            alt.Chart(source.reset_index())
            .mark_bar()
            .encode(
                x="yearmonthdate(date):T", y="open", y2="close", color=open_close_color
            )
        )
        vis = rule + bar
        colors = [
            "blue",
            "grey",
            "orange",
            "brown",
            "yellow",
            "pink",
            "black",
            "violet",
            "red",
            "cyan",
        ]
        for idx, m in enumerate(moving_averages):
            field = "mean_" + str(m)
            source[field] = source["close"].rolling(m, min_periods=1).mean()
            color_line = colors[idx]
            mean = (
                alt.Chart(source.reset_index())
                .mark_line()
                .encode(
                    alt.X("yearmonthdate(date):T"),
                    alt.Y(field),
                    color=alt.value(color_line),
                )
            )
            vis = vis + mean

        source["mean_30"] = source["close"].rolling(10, min_periods=1).mean()
        source["std_dev"] = source["close"].rolling(10, min_periods=1).std()
        source["std_dev_up"] = source["mean_30"] + 2 * source["std_dev"]
        source["std_dev_down"] = source["mean_30"] - 2 * source["std_dev"]

        area = (
            alt.Chart(source.reset_index())
            .mark_area(opacity=0.3)
            .encode(x="yearmonthdate(date):T", y=alt.Y("std_dev_up"), y2="std_dev_down")
        )

        vis = vis + area
        if ribbons:
            rolling_means = {}
            for i in np.linspace(10, 100, 10):
                X = source["close"].rolling(window=int(i), min_periods=1).mean()
                rolling_means[i] = X

            rolling_means = pd.DataFrame(rolling_means).dropna()

            scores = pd.Series(index=source.index)

            for date in rolling_means.index:
                mavg_values = rolling_means.loc[date]
                ranking = stats.rankdata(mavg_values.values)
                d = distance.hamming(ranking, range(1, 11))
                scores[date] = d

            # Normalize the  score
            source["ribbon"] = scores.rolling(50, min_periods=1).mean()
            source["ribbon_velocity"] = source["ribbon"].diff()
            ribbon1 = (
                alt.Chart(source.reset_index())
                .mark_line()
                .encode(
                    alt.X("yearmonthdate(date):T"),
                    alt.Y("ribbon"),
                    color=alt.value("blue"),
                )
            )

            ribbon2 = (
                alt.Chart(source.reset_index())
                .mark_line()
                .encode(
                    alt.X("yearmonthdate(date):T"),
                    alt.Y("ribbon_velocity"),
                    color=alt.value("red"),
                )
            )
            ribbon = ribbon1 + ribbon2
            vis = alt.layer(vis, ribbon).resolve_scale(y="independent")

        return vis, source


