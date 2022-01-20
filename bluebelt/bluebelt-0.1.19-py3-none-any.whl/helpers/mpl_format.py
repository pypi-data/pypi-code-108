import pandas as pd
import matplotlib.dates as mdates

def axisformat(ax, series):

    if isinstance(series.index, pd.DatetimeIndex):
        rng = series.index.max() - series.index.min()

        if rng > pd.Timedelta('365 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('183 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('31 days'):
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%V'))
            ax.set_xlabel('week')
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            ax.set_xlabel('date')
    else:
        ax.set_xlabel(series.name)

    return ax
