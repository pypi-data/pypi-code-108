import os
import dask.dataframe as dd
import pandas as pd

from datupapi.configure.config import Config
from datupapi.prepare.format import Format

class FormatDask(Config):

    DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
    #DOCKER_CONFIG_PATH = os.path.join('./', 'config.yml')
    fmt = Format(config_file=DOCKER_CONFIG_PATH, logfile='data_extraction', log_path='output/logs')

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def resample_dataset(self, df, date_col_=None, item_col_=None, frequency_=None, agg_dict_=None, meta_dict_=None):
        """
        Return a dataframed resampling the date dimension to the specified frequency

        :param df: Dataframe to be resampled
        :param date_col_: Name of date column in the input dataframe
        :param item_col_: Name of item column in the item dataframe
        :param frequency_: Target frequency to resample the data
        :param agg_dict_: Aggregation dictionary including column as key and operation as value
        :param meta_dict_: Metadata dictionary including column as key and datatype as value
        :return df_out: Dataframe resampled

        >>> df_out = resample_dataset(df, date_col_='date', item_col_='item_id', frequency_='W', agg_dict_={'demand': 'sum', 'cantidad': 'sum'}, meta_dict_={'demand': 'float64', 'cantidad': 'float64'})
        >>> df_out =
                                var1    var2    var3
                        idx0     1       2       3
        """
        def datup_resample(partition):
            return partition.resample(frequency_).agg(agg_dict_)

        try:
            df_out = df.set_index(date_col_) \
                       .groupby(item_col_) \
                       .apply(datup_resample, meta=meta_dict_) \
                       .compute() \
                       .reset_index()
            df_out = self.fmt.reorder_cols(df_out, first_cols=[date_col_, item_col_])
        except KeyError as err:
            self.logger.exception(f'Columns for index, item or qty not found. Please check spelling: {err}')
            raise
        return df_out


    def resample_dataset_with_location(self, df, date_col_=None, item_col_=None, location_col_=None, frequency_=None, agg_dict_=None, meta_dict_=None):
        """
        Return a dataframed resampling the date dimension to the specified frequency

        :param df: Dataframe to be resampled
        :param date_col_: Name of date column in the input dataframe
        :param item_col_: Name of item column in the input dataframe
        :param location_col_: Name of location in the input dataframe
        :param frequency_: Target frequency to resample the data
        :param agg_dict_: Aggregation dictionary including column as key and operation as value
        :param meta_dict_: Metadata dictionary including column as key and datatype as value
        :return df_out: Dataframe resampled

        >>> df_out = resample_dataset_with_location(df, date_col_='date', item_col_='item_id', location_col_='location', frequency_='W', agg_dict_={'demand': 'sum', 'cantidad': 'sum'}, meta_dict_={'demand': 'float64', 'cantidad': 'float64'})
        >>> df_out =
                                var1    var2    var3
                        idx0     1       2       3
        """
        def datup_resample_with_location(partition):
            return partition.resample(frequency_).agg(agg_dict_)
        try:
            df_out = df.set_index(date_col_) \
                       .groupby([location_col_, item_col_]) \
                       .apply(datup_resample_with_location, meta=meta_dict_)\
                       .compute() \
                       .reset_index()
            df_out = self.fmt.reorder_cols(df_out, first_cols=[date_col_, item_col_, location_col_])
        except KeyError as err:
            self.logger.exception(f'Columns for index, item or qty not found. Please check spelling: {err}')
            raise
        return df_out
