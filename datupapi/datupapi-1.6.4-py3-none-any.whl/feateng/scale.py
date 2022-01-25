import math
import os
import pandas as pd

from datupapi.configure.config import Config
from scipy.fft import rfft, rfftfreq
from scipy.signal import boxcar
from sklearn.preprocessing import MinMaxScaler, PowerTransformer, RobustScaler, StandardScaler

class Scale(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def extract_frequency(self, ts, frequency):
        """Return the dominant frequency or time series seasonality

        :param ts: Input timeseries
        :param frequency: Timeseries frequency, either 'D', 'W-SUN', 'W-MON', 'SM' and 'M'
        :return freq: Dominant frequency or seasonality

        >>> freq = extract_frequency(ts, duration=2)
        >>> freq = 12
        """
        SAMPLES = len(ts)
        if frequency == 'D':
            duration = SAMPLES/365
        elif frequency == 'W-SUN' or frequency == 'W-MON':
            duration = SAMPLES/52
        elif frequency == 'SM':
            duration = SAMPLES/26
        elif frequency == 'M':
            duration = SAMPLES/12
        else:
            self.logger.exception(f'No valid timeseries frequency. Please check again: {err}')
        SAMPLE_RATE = SAMPLES/duration
        try:
            if ts.max() == 0:
                ts_norm = ts/1.0
            else:
                ts_norm = ts/ts.max()
            window = boxcar(SAMPLES)
            amplitude = rfft(ts_norm*window)
            freqs = rfftfreq(SAMPLES, 1/SAMPLE_RATE)
            # Start on 1 to remove the central frequency effect
            result = pd.Series(data=abs(amplitude[1:]), index=freqs[1:])
            freq = math.ceil(result.idxmax())
            if freq <= 1:
                freq = 2
        except ValueError as err:
            self.logger.exception(f'Inconsistent numeric values. Please check again: {err}')
            raise
        return freq


    def scale_dataset(self, df, scaler='minmax'):
        """Return a dataframe with scaled data using box-cox, min-max, robust or standard.
        Return the scale object to perform inverse scaling.

        :param df: Dataframe to scale
        :param scaler: Scaling algorithm to apply on the input dataframe. Default 'minmax'.
        :return df_scaled: Dataframe scaled using the chosen scaling algorithm
        :return scaler_obj: Scale object fitted to the input dataframe to reverse the scaling later on.

        >>> df_scaled, scaler_obj = scale_dataset(df=df, scaler='minmax')
        >>> df_scaled
        idx0     0.333       0.666       1
        """
        try:
            if scaler == 'minmax':
                scaler_obj = MinMaxScaler().fit(df)
                data_scaled = scaler_obj.transform(df)
            elif scaler == 'robust':
                scaler_obj = RobustScaler().fit(df)
                data_scaled = scaler_obj.transform(df)
            elif scaler == 'zscore':
                scaler_obj = StandardScaler().fit(df)
                data_scaled = scaler_obj.transform(df)
            elif scaler == 'boxcox':
                scaler_obj = PowerTransformer(method='box-cox', standardize=False).fit(df)
                data_scaled = scaler_obj.transform(df)
            else:
                self.logger.debug(f'No valid scaler option. Try again...')
            df_scaled = pd.DataFrame(data_scaled, index=df.index, columns=df.columns)
        except ValueError as err:
            self.logger.exception(f'Inconsistent numeric errors. Please check data types: {err}')
            raise
        return df_scaled, scaler_obj


    def inverse_scale_dataset(self, df_scaled, scaler_obj):
        """Return a dataframe with scaled data using min-max and standard

        :param df_scaled: Dataframe to reverse scaling
        :param scaler_obj: Scale object used in scale_dataset method
        :return df: Dataframe with unscaled/original values

        >>> df = inverse_scale_dataset(df_scaled=df_scaled, scaler_obj=my_scaler)
        >>> df
        idx0     1       2       3
        """
        try:
            data = scaler_obj.inverse_transform(df_scaled)
            df = pd.DataFrame(data, index=df_scaled.index, columns=df_scaled.columns)
        except ValueError as err:
            self.logger.exception(f'Inconsistent numeric errors. Please check data types: {err}')
            raise
        return df