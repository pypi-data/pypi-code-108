import os

import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import seasonal_decompose


def _clean_file_name(file_name):
    return file_name.strip().replace(" ", "_").replace("/", "_")


def seasonal_all(df, col_name, col_display, date_col_name, folder=None, orig_color="blue", trend_color="red",
                 legend_position="best", legend_bbox_to_anchor=None, x_label_rotation=0, period=2, plot_trends=True,
                 plot_seasonal=True, plot_residual=True, file_name=None):
    temp_df = df.copy()

    temp_df.index = pd.to_datetime(temp_df[date_col_name])
    series = temp_df[col_name]

    decompose_data = seasonal_decompose(series, model="additive", period=period)

    trend_estimate = decompose_data.trend
    periodic_estimate = decompose_data.seasonal
    residual = decompose_data.resid

    if plot_trends:
        fig, ax = plt.subplots()

        trend_estimate = trend_estimate.fillna(0)
        plt.xlim(min(temp_df[date_col_name]), max(temp_df[date_col_name]))
        plt.ylim(min(trend_estimate), max(trend_estimate))

        plt.plot(series, label='Original data', color=orig_color)
        plt.plot(trend_estimate, label='Trend', color=trend_color)
        plt.xticks(rotation=x_label_rotation)
        plt.legend(loc=legend_position, bbox_to_anchor=legend_bbox_to_anchor)
        fig.tight_layout()
        if folder is not None:
            if not os.path.exists(folder):
                os.mkdir(folder)
            saved_file = file_name if file_name is not None else "Trend_" + _clean_file_name(col_display) + ".png"
            fig.savefig(os.path.join(folder, saved_file))

    if plot_seasonal:
        fig, ax = plt.subplots()
        periodic_estimate = periodic_estimate.fillna(0)
        plt.xlim(min(temp_df[date_col_name]), max(temp_df[date_col_name]))
        plt.ylim(min(periodic_estimate), max(periodic_estimate))
        plt.plot(periodic_estimate, label='Seasonality', color=orig_color)
        plt.xticks(rotation=x_label_rotation)
        fig.tight_layout()
        if folder is not None:
            saved_file = file_name if file_name is not None else "Seasonality_" + _clean_file_name(col_display) + ".png"
            fig.savefig(os.path.join(folder, saved_file))

    if plot_residual:
        fig, ax = plt.subplots()
        residual = residual.fillna(0)
        plt.xlim(min(temp_df[date_col_name]), max(temp_df[date_col_name]))
        plt.ylim(min(residual), max(residual))
        plt.plot(residual, label='Residuals', color=orig_color)
        plt.xticks(rotation=x_label_rotation)
        fig.tight_layout()
        if folder is not None:
            saved_file = file_name if file_name is not None else "Residuals_" + _clean_file_name(col_display) + ".png"
            fig.savefig(os.path.join(folder, saved_file))


def trends(df, col_names, col_displays, date_col_name, folder=None, file_name=None, colors=None, legend_position="best",
           legend_bbox_to_anchor=None, x_label_rotation=0, period=2, method='plot'):
    if colors is None:
        colors = ["blue", "red", "green", "yellow"]
    temp_df = df.copy()

    temp_df.index = pd.to_datetime(temp_df[date_col_name])

    min_val = None
    max_val = None
    fig, ax = plt.subplots()
    for idx in range(len(col_names)):
        series = temp_df[col_names[idx]]

        decompose_data = seasonal_decompose(series, model="additive", period=period)
        trend_estimate = decompose_data.trend

        trend_estimate = trend_estimate.fillna(0)
        if min_val is None:
            min_val = min(trend_estimate)
        elif min_val > min(trend_estimate):
            min_val = min(trend_estimate)

        if max_val is None:
            max_val = max(trend_estimate)
        elif max_val < max(trend_estimate):
            max_val = max(trend_estimate)

        if method == 'plot':
            plt.plot(trend_estimate, label=col_displays[idx], color=colors[idx])
        elif method == 'scatter':
            plt.scatter(temp_df[date_col_name], trend_estimate, label=col_displays[idx], color=colors[idx])

    plt.xlim(min(temp_df[date_col_name]), max(temp_df[date_col_name]))
    plt.ylim(min_val, max_val)
    plt.xticks(rotation=x_label_rotation)
    plt.legend(loc=legend_position, bbox_to_anchor=legend_bbox_to_anchor)
    fig.tight_layout()
    if folder is not None:
        if not os.path.exists(folder):
            os.mkdir(folder)
        if file_name is None:
            file_name = ""
            for idx in range(len(col_names)):
                file_name += " " + col_displays[idx]
            file_name = _clean_file_name(file_name)
        fig.savefig(os.path.join(folder, file_name))
