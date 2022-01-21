import pandas as _pd
import numpy as _np
from datetime import date as _date
from datetime import timedelta as _timedelta


class DfStitcher:

    def __init__(self, 
        id_col="WAFER_TADOS_553_15_553_15_TADOS_WAFER_NR_text",
        date_col="WAFER_TADOS_553_15_553_15_MEAS_DATE_date",
        date_col_format='%Y%m%d',
        buffer_file="/cache/data.csv",
        maxage = 370):
        
        self._buffer_file = buffer_file
        self._id_col = id_col
        date_threshold = _pd.Timestamp(_date.today() - _timedelta(maxage))
        
        try:
            print("import old data from {}".format(buffer_file))
            self.df = _pd.read_csv(buffer_file)
        
            #remove old rows
            oldrows = _pd.to_datetime(self.df[date_col],format=date_col_format) < date_threshold
            print("drop {} rows with date older than {} days".format(_np.sum(oldrows), maxage))
            self.df.drop(self.df[oldrows].index, axis=0, inplace=True)
        except:
            print("start with empty dataframe")
            self.df = None
        
    def append(self, newdata):
        """append newdata to the dataframe
        """
        
        if self.df is not None:
            
            new_ids = set(newdata[self._id_col].values)
            duplicate_rows = self.df[self._id_col].isin(new_ids)
            print("remove {} matching ids".format(_np.sum(duplicate_rows)))
            self.df.drop(self.df[duplicate_rows].index, axis=0, inplace=True)
            
            self.df = self.df.append(newdata, sort=True)
        
        else:
            print("take as new data")
            self.df = newdata
            
            
    def save(self):
        """Save as csv file for the next import
        """
        if self.df is not None:

            #remove unnamed columns
            self.df = self.df.drop([c for c in self.df.columns if "Unnamed" in c], axis=1)

            print("save data to {}".format(self._buffer_file))
            self.df.to_csv(self._buffer_file, chunksize=10000)

