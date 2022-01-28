import os
import numpy as np
import pandas as pd
import re

from datupapi.configure.config import Config
from unidecode import unidecode

class Cleanse(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def clean_metadata(self, df):
        """
        Return a dataframe with columns names free of special characters in camel case

        :param df: Dataframe to clean metadata
        :return df_out: Dataframe with cleaned metadata

        >>> df = clean_metadata(df)
        >>> df
                   Codigo    Linea    Categoria
           idx1    123       Azul     Postres
        """
        try:
            cols = {col: re.sub('[^A-Za-z0-9 ]+', '', unidecode(col)).title() for col in df.columns}
            df_out = df.rename(columns=cols)
        except ValueError as err:
            self.logger.exception(f'No valid column name : {err}')
            raise
        return df_out


    def clean_data(self, df):
        """
        Return a dataframe with records free of special characters in camel case

        :param df: Dataframe to clean metadata
        :return df_out: Dataframe with cleaned metadata

        >>> df = clean_data(df)
        >>> df
                   City    Linea    Categoria
           idx1    Lima    Azul     Postres
        """
        try:
            df_cat = df.select_dtypes(include='object')
            df_cat = df_cat.applymap(lambda x: re.sub('[^A-Za-z0-9 ]+', '', unidecode(x)).title())
            df_num = df.select_dtypes(include='number')
            df_num = df_num.applymap(lambda x: 0 if np.isnan(x) else x)
            df_out = pd.concat([df_cat, df_num], axis='columns')
        except ValueError as err:
            self.logger.exception(f'No valid column name : {err}')
            raise
        return df_out




