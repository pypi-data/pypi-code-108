import logging
import pandas as pd
import pandas.io.sql as sqlio
import psycopg2 as p
from typing import Literal

logger = logging.getLogger("preprocessing_helper")

class RawDataLoader:
    """Call for handling the loading of raw files or database tables depending 
    on the input
    """
    
    __valid_extensions = ["csv", "txt"]
    __type_lookup = {"integer":int, "float":float, "string":str}
    
    def __init__(self, read_mode:Literal["db", "file"]) -> None:
        """Init for class

        Args:
            read_mode (Literal["db", "file"]): Determines whether the class 
            should read from files or a database.
        """
        if read_mode not in ["db", "file"]:
            raise ValueError("read_mode should be one of db or file")
        self.read_mode = read_mode   
    
    def __read_file(self, file_name:str, **kwargs)->pd.DataFrame:
        """Reads an input file

        Args:
            file_name (str): Full directory of the file including extension

        Returns:
            pd.DataFrame: File imported as a dataframe
        """
        raw_file = pd.read_csv(file_name, dtype=str, **kwargs)
        return raw_file
    
    def __read_db_table(self, table_name:str, **kwargs)->pd.DataFrame:
        """Reads a table from a database

        Args:
            table_name (str): Name of the table in the database

        Returns:
            pd.DataFrame: Table imported as a dataframe
        """
        conn = p.connect("")
        sql_state = "SELECT * FROM {};".format(table_name)
        raw_table = sqlio.read_sql_query(sql_state, conn, **kwargs)
        return raw_table
    
    def read_file_table(self, file_table_name:str, 
                        type_conversions:dict=None)->pd.DataFrame:    
        """Wrapper function to read a raw file or a table from a database

        Args:
            file_table_name (str): Full path of file (including extension) or
            table name in the database
            type_conversions (dict): A dictionary of column and associated 
            types to convert. Refer to __type_conversions for more info

        Raises:
            ValueError: Raised if the import option is set to file and a file
            path without a valid extension is provided

        Returns:
            pd.DataFrame: Table/file imported as a dataframe
        """
        if self.read_mode == "file":
            # Check for valid extension
            if file_table_name.split(".")[-1] not in self.__valid_extensions:
                raise ValueError(
                    "File does not have valid extension. Must be one of {}".format(
                        ", ".join(self.__valid_extensions)))
            else:
                ret = self.__read_file(file_table_name)
                ret = self.__type_conversions(ret, type_conversions)
        elif self.read_mode == "db":
            ret = self.__read_db_table(file_table_name)
        return ret
    
    def __type_conversions(self, pandas_df:pd.DataFrame, 
                           type_conversions:dict)->pd.DataFrame:
        """Converts the columns of an input dataframe to the specified type

        Args:
            pandas_df (pd.DataFrame): Input dataframe to convert
            type_conversions (dict): Dictionary of the form:
            {"column_name": type}. If type is "date" the type should be a 
            another dictionary of the form: {"date": "date_format"}

        Returns:
            pd.DataFrame: pandas_df with converted columns
        """
        for i in type_conversions.keys():
            if not isinstance(type_conversions[i], dict):
                pandas_df[i] = pandas_df[i].astype(
                    self.__type_lookup[type_conversions[i]])
            elif "date" in type_conversions[i].keys():
                pandas_df[i] = pd.to_datetime(
                    pandas_df[i], format=type_conversions[i]["date"])
            else: 
                raise ValueError
        return pandas_df
        
                
    
    


