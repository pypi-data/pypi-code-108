import pandas as pd
import requests
import json

""" 
Read google sheet as dataframe
Usage example: read_gsheet("https://sheet.google.com/45qwd3533")
"""


def read_gsheet(url, credentials=None, sheet=None):
    import gspread

    if credentials != True:
        gc = gspread.service_account(credentials)

    if sheet != None:

        wks = gc.open_by_url(url).worksheet(sheet)

    else:

        wks = gc.open_by_url(url).get_worksheet(0)

    data = wks.get_values(value_render_option='UNFORMATTED_VALUE', date_time_render_option="FORMATTED_STRING")

    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)

    # else:

    # df = ##chiamata API

    return df


""" 
Read hubspot contacts as dataframe
Usage example: read_hubspot_contacts(api_key)
"""


def read_hubspot_contacts(api_key, offset=100):
    from askdata.integrations import hubspot
    return hubspot.get_contacts_df(api_key, offset)


""" 
Read alpha vantage api
Usage example: read_alphavantage_stock(api_key, symbols)
"""


def read_alphavantage_stock(symbols, api_key):
    from askdata.integrations import alphavantage
    return alphavantage.get_daily_adjusted_df(symbols, api_key)


def normalize_columns(df: pd.DataFrame):
    problematicChars = [",", ";", ":", "{", "}", "(", ")", "=", ">", "<", "."]
    new_cols = {}
    for column in df.columns:

        columnName = column.lower()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        columnName = columnName.replace(" ", "_")
        columnName = columnName.replace("-", "_")
        columnName = columnName.strip()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        new_cols[column] = columnName

    return df.rename(columns=new_cols)


def read(type, settings):
    if type == "CSV":
        return __read_csv(settings)
    if type == "EXCEL":
        return __read_excel(settings)
    if type == "PARQUET":
        return __read_parquet(settings)
    if type == "GSHEET":
        return __read_gsheet(settings)
    if type == "Hubspot":
        return __read_hubspot(settings)
    else:
        raise TypeError("Dataset type not supported yet")


def __read_csv(settings: dict):
    
    # Handle thousands
    if settings["thousands"] == "None":
       settings["thousands"] = None

    # Read source file
    df = pd.read_csv(filepath_or_buffer=settings["path"], sep=settings["separator"], encoding=settings["encoding"], thousands=settings["thousands"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    # Exec custom post-processing
    if "processing" in settings and settings["processing"] != "" and settings["processing"] != None:
        exec(settings["processing"])

    return df

def __read_parquet(settings: dict):
    
    df = pd.read_parquet(path=settings["path"])

    return df

def __read_excel(settings: dict):
    df = pd.read_excel(settings["path"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    return df

def __read_gsheet(settings: dict):
    df = read_gsheet(settings["url"])

    return df

def __read_hubspot(settings: dict):
    df = read_hubspot_contacts(settings["fields"]["token"])

    return df