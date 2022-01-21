import pandas as _pd
import numpy as _np


def read_in_tsf(fileName, addType=True, sep=""):
    """
    Import a TSF pandas dataframe from a GEOS extract
    """
    
    #extract first row with names
    header = _np.array(_pd.read_csv(fileName, sep=";", nrows=1), dtype = str)
    if addType:
        #extract second row with types and join
        header2 = _np.array(_pd.read_csv(fileName, sep=";", nrows=1, skiprows=1, low_memory=False), dtype = str)
        
        header = _np.core.defchararray.add(_np.core.defchararray.add(header, sep), header2)
        
    #combine header names
    header = header.flatten().tolist()
    
    #read all data
    return _pd.read_csv(fileName, sep=";", skiprows=8, header=None, names=header, decimal=",", low_memory=False)


def apply(df, tasks):
    """
    apply a set of datatransforms (tasks) on the dataframe (df)
    """
    for t in tasks:
        globals()["_apply_" + t["typ"]](df = df, **t)


#start toolfunctions

def _apply_addDates(df, inputColumn, targetColumns = {"CW": "CW", "MON": "Month", "YEAR": "Year", "DAYS": "Days"}, inDateFormat='%Y%m%d', **kwargs):
    if "CW" in targetColumns:
        print("Append CW (var name:{1}) from input {0}".format(inputColumn, targetColumns["CW"]))
        df[targetColumns["CW"]] = _pd.to_datetime(df[inputColumn],format=inDateFormat).dt.strftime('%Y-%U')
    if "DAY" in targetColumns:
        print("Append DAY (var name:{1}) from input {0}".format(inputColumn, targetColumns["DAY"]))
        df[targetColumns["DAY"]] = _pd.to_datetime(df[inputColumn],format=inDateFormat).dt.strftime('%Y-%m-%d')
    if "DAYS" in targetColumns:
        print("Append DAYS (var name:{1}) from input {0}".format(inputColumn, targetColumns["DAYS"]))
        df[targetColumns["DAYS"]] = (_pd.Timestamp.now() - _pd.to_datetime(df[inputColumn],format=inDateFormat)).dt.days
    if "MON" in targetColumns:
        print("Append Month (var name:{1}) from input {0}".format(inputColumn, targetColumns["MON"]))
        df[targetColumns["MON"]] = _pd.to_datetime(df[inputColumn],format=inDateFormat).dt.strftime('%Y-%m')
    if "YEAR" in targetColumns:
        print("Append Year (var name:{1}) from input {0}".format(inputColumn, targetColumns["YEAR"]))
        df[targetColumns["YEAR"]] = _pd.to_datetime(df[inputColumn],format=inDateFormat).dt.strftime('%Y')
        
        
        
def _apply_rename(df, columns, **kwargs):
    print("Apply rename: {0}".format(columns))
    df.rename(index=str, columns=columns, inplace=True)
        

def _apply_substring(df, inputColumn, outputColumn, start, stop, **kwargs):
    print("Append {1} as substring(start={2},stop={3}) from {0}".format(inputColumn, outputColumn, start, stop))
    df[outputColumn] = df[inputColumn].str.slice(start, stop)

    
def _apply_mapping(df, inputColumn, outputColumn, mapping, notNanFill=False, **kwargs):
    print("Append {1} as mapping from {0}".format(inputColumn, outputColumn))
    if notNanFill:
        df[outputColumn] = df[inputColumn].map(mapping).fillna(df[outputColumn])
    else:
        df[outputColumn] = df[inputColumn].map(mapping)
        
        
def _apply_dropColumns(df, inputColumns, **kwargs):
    print("Drop columns {0}".format(inputColumns))
    df.drop(columns=inputColumns, inplace=True)
    
    
def _apply_conditionalEval(df, outputColumn, cases, default=_np.nan, **kwargs):
    print("Apply conditional eval of {0}".format(outputColumn))
    df[outputColumn] = default

    for s in cases:
        
        if "filter" in s:
            print(" * if {} then {}".format(s["filter"], s["expr"]))
            if type(default) == str:
                mask = df.eval("{} == '{}' and ({})".format(outputColumn, default, s["filter"]))
            elif _np.isnan(default):
                mask = df.eval("{}.isna() and ({})".format(outputColumn, s["filter"]))
            else:
                mask = df.eval("{} == {} and ({})".format(outputColumn, default, s["filter"]))
        else:
            print(" * else {}".format(s["expr"]))
            if type(default) == str:
                mask = df.eval("{} == '{}'".format(outputColumn, default))
            elif _np.isnan(default):
                mask = df[outputColumn].isna()
            else:
                mask = df.eval("{} == {}".format(outputColumn, default))
            
        values = df[outputColumn].values
        values[mask] = df[mask].eval(s["expr"])
        df[outputColumn] =  values
    
        
def _apply_firstNonNull(df, inputColumns, targetColumn, **kwargs):
    print("Append {1} from first {0}".format(inputColumns, targetColumn))
    
    def mapfirst(x):
        if x.first_valid_index() is None:
            return None
        else:
            return x[x.first_valid_index()]

    #remove not known cols and keep the order of input cols
    possibleCols = [el for el in inputColumns if el in df.columns]
    
    df[targetColumn] = df[possibleCols].apply(mapfirst, axis=1)
    
#end toolfunctions



