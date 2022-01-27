import os
import pandas as pd
import re

from bs4 import BeautifulSoup
from datupapi.configure.config import Config

class Format(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def extract_item_metadata(self, df, item_col, metadata_cols):
        """
        Return a dataframe containing items with metadata columns

        :param df: Dataframe panel type with items and metadata
        :param item_col: Column name for items ids
        :param metadata_cols: Metadata columns to extract
        :return df_metadata: Output dataframe with items and their corresponding metadata

        >>> df = extract_item_metadata(df, item_col='Item', metadata_cols=['Description', 'Category'])
        >>> df =
                        sku1    sku2    sku3
                idx1    23      543      123
        """
        try:
            agg_dict = {e: 'first' for e in metadata_cols}
            df_metadata = df.groupby([item_col], as_index=False).agg(agg_dict)
            df_metadata = df_metadata.rename(columns={item_col: 'Item'})
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_metadata


    def concat_item_metadata(self, df, df_metadata, item_col):
        """
        Return a dataframe including metadata

        :param df: Dataframe pending to attach metadata
        :param df_metadata: Dataframe with items and their corresponding metadata
        :param item_col: Column name for items ids
        :return df: Output dataframe adding

        >>> df = concat_item_metadata(df, df_metadata, item_col='Item')
        >>> df =
                        sku1    sku2    sku3
                idx1    23      543      123
        """
        try:
            df[item_col] = df[item_col].astype(str)
            df_metadata[item_col] = df_metadata[item_col].astype(str)
            df_out = pd.merge(df, df_metadata, on=item_col, how='left')
        except ValueError as err:
            self.logger.exception(f'No valid values. Please check timeseries: {err}')
            raise
        return df_out


    def concat_item_metadata_with_location(self, df, df_metadata, item_col, location_col):
        """
        Return a dataframe including metadata
        :param df: Dataframe pending to attach metadata
        :param df_metadata: Dataframe with items and their corresponding metadata
        :param item_col: Column name for items ids
        :param location_col: Column name for location ids
        :return df: Output dataframe adding
        >>> df = concat_item_metadata_with_location(df, df_metadata, item_col='Item',location_col='Location')
        >>> df =
                        sku1    sku2    sku3
                idx1    23      543      123
        """
        try:
            df[item_col] = df[item_col].astype(str)
            df_metadata[item_col] = df_metadata[item_col].astype(str)
            df[location_col] = df[location_col].astype(str)
            df_metadata[location_col] = df_metadata[location_col].astype(str)
            df_out = pd.merge(df, df_metadata, on=[item_col, location_col], how='left')
        except ValueError as err:
            print(f'No valid values. Please check timeseries: {err}')
        return df_out


    def get_active_items(self, df, min_periods, ascending=True):
        """
        Return a dataframe with actives items according to recent activity

        :param df: Dataframe to be filtered for active items
        :param min_periods: Minimum number of time periods to check no activity
        :param ascending: Determine whether the timeseries is increasing or decreasing dates. Default True
        :return df_out: Output dataframe with active items

        >>> df = get_active_items(df=df, min_periods=4, ascending=True)
        >>> df =
                        sku1    sku2    sku3
                idx1    23      543      123
        """
        try:
            if ascending:
                df_sample = df.iloc[-min_periods:, :]
            else:
                df_sample = df.iloc[:min_periods, :]
            df_out = df.loc[:, (df_sample != 0).all()]
        except ValueError as err:
            self.logger.exception(f'No valid values. Please check timeseries: {err}')
            raise
        return df_out


    def parse_week_to_date(self, df, week_col, date_col, drop_cols=None):
        """
        Return a dataframe parsing the year's week column to datetime column

        :param df: Dataframe to parse
        :param week_col: Column name containing year's week number
        :param date_col: Column name of output datetime column
        :param drop_cols: List related columns to drop after parsing. Default None
        :return: Dataframe with parsed week to datetime column

        >>> df = parse_week_to_date(df, week_col='Weeks', date_col='Date', drop_cols=['Weeks'])
        >>>
        """
        try:
            df[week_col] = df[week_col].astype(str).str.replace('[^\w\s]', '', regex=True).astype('int64')
            df[date_col] = pd.to_datetime((df[week_col] - 0).astype(str) + "1", format="%Y%W%w")
            if drop_cols is not None:
                df = df.drop(columns=drop_cols, axis=1)
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df


    def pivot_dates_vs_items(self, df, date_col, item_col, qty_col):
        """
        Return a dataframe with dates as rows and SKUs as columns from stacked columns

        :param df: Dataframe with stacked SKUs in one column, subjecto to pivot
        :param date_col: Column name storing dates
        :param item_col: Column name storing SKUs
        :param qty_col: Column name storing quantity to forecast
        :return df: Dataframe with dates as index, SKUs as columns and quantities as records

        >>> df = pivot_dates_vs_items(df, date_col='Date', sku_col='Codes', qty_col='Volume')
        >>> df
                          A102    B205    C451
            2020-01-02      85     905      23
            2020-02-02     102     487      95
        """
        try:
            df[item_col] = df[item_col].astype(str)
            df_out = df.groupby([date_col, item_col], as_index=False).agg({qty_col: sum})
            df_out = df_out.pivot(index=date_col, columns=item_col, values=qty_col)\
                           .fillna(0)
        except KeyError as err:
            self.logger.exception(f'Columns for index, sku or qty not found. Please check spelling: {err}')
            raise
        return df_out


    def reorder_cols(self, df, first_cols):
        """
        Return a dataframe with columns specified in first_col at the leading positions

        :param df: Dataframe to reorder
        :param first_cols: Leading columns to appear in the dataframe
        :return df: Dataframe reordered

        >>> df = reorder_cols(df, first_cols)
        >>> df =
                        var1    var2    var3
                idx0     1       2       3
        """
        cols = list(df.columns)
        for col in reversed(first_cols):
            cols.remove(col)
            cols.insert(0, col)
            df = df[cols]
        return df


    def resample_dataset(self, df, date_col=None, item_col=None, frequency=None, agg_dict=None):
        """
        Return a dataframed resampling the date dimension to the specified frequency

        :param df: Dataframe to be resampled
        :param frequency: Target frequency to resample the data
        :param agg_dict: Aggregation dictionary including column as key and operation as value
        :return df_out: Dataframe resampled

        >>> df_out = resample_dataset()
        >>> df_out =
                                var1    var2    var3
                        idx0     1       2       3
        """
        #df_out = pd.DataFrame()
        try:
            #for item in df[item_col].unique():
            #    df_tmp = df[df[item_col] == item]
            #    df_tmp = df_tmp.set_index(date_col).resample(frequency).agg(agg_dict).reset_index(drop=False)
            #    df_tmp[item_col] = item
            #    df_out = pd.concat([df_out, df_tmp], axis='rows').drop_duplicates()
            #df_out = df_out.drop_duplicates()
            df_out = df.groupby(item_col) \
                       .resample(frequency, on=date_col) \
                       .agg(agg_dict) \
                       .reset_index()
            df_out = self.reorder_cols(df_out, first_cols=[date_col, item_col])
        except KeyError as err:
            self.logger.exception(f'Columns for index, item or qty not found. Please check spelling: {err}')
            raise
        return df_out


    def resample_dataset_with_location(self, df, date_col_=None, item_col_=None, location_col_=None, frequency_=None, agg_dict_=None):
        """
        Return a dataframed resampling the date dimension to the specified frequency

        :param df: Dataframe to be resampled
        :param frequency: Target frequency to resample the data
        :param agg_dict: Aggregation dictionary including column as key and operation as value
        :return df_out: Dataframe resampled

        >>> df_out = resample_dataset()
        >>> df_out =
                                var1    var2    var3
                        idx0     1       2       3
        """
        #df_out = pd.DataFrame()
        try:
            #for location in df[location_col_].unique():
            #    df_loc = df[df[location_col_]==location]
            #    df_loc_resample = self.resample_dataset(df_loc, date_col=date_col_, item_col=item_col_, frequency=frequency_, agg_dict=agg_dict_)
            #    df_loc_resample[location_col_] = location
            #    df_out = pd.concat([df_out, df_loc_resample], axis='rows').drop_duplicates()
            #df_out = df_out.drop_duplicates()
            df_out = df.set_index(date_col_) \
                       .groupby([location_col_, item_col_]) \
                       .resample(frequency_) \
                       .agg(agg_dict_) \
                       .reset_index()
            df_out = self.reorder_cols(df_out, first_cols=[date_col_, item_col_, location_col_])
        except KeyError as err:
            self.logger.exception(f'Columns for index, item or qty not found. Please check spelling: {err}')
            raise
        return df_out


    def xml_to_dataframe(self, text_=None, tag_=None):
        """
        Return a dataframe containing data from xml text file

        :param text_: Plain text with xml data
        :param tag_: Tag to search the name of columns
        :return df: Output dataframe with data from xml file

        >>> df = xml_to_dataframe(contents,'xs:element')
        >>> df =
                              sku1    sku2    sku3
                      idx1    23      543      123
        """
        try:
            list_names = []
            df = pd.DataFrame()
            soup = BeautifulSoup(text_, 'xml')
            for element in soup.find_all(tag_, minOccurs="0"):
                list_names.append(element['name'])
            for name in list_names:
                col = soup.find_all(name)
                data = []
                for i in range(0, len(col)):
                    rows = col[i].get_text()
                    data.append(rows)
                tmp = pd.DataFrame(data, columns=[name])
                df = pd.concat([df, tmp], axis=1)
        except ValueError as err:
            self.logger.exception(f'No valid values. Please check xml file: {err}')
            raise
        return df

    def title_to_pascalcase(self, df_,list_cols): 
        """
        Return a dataframe with columns names free of special characters in camel case

        :param df: Dataframe to clean columns names
        :param list_cols: Dataframe columns names
        :return df_out: Dataframe with columns names without spaces and normalized

        >>> df = title_to_pascalcase(df, df.columns)
        >>> df
                   Item    DescriptionItem   Categoria
           idx1    123       Azul             Postres
        """
        try:
            for name_col in list_cols:
              df_ = df_.rename(columns={name_col: name_col.replace("_", " ").title().replace(" ", "")})
        except ValueError as err:
            self.logger.exception(f'No valid column name : {err}')
            raise
        return df_