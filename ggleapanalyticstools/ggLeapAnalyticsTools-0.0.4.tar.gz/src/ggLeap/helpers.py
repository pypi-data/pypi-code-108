import pandas as pd

from datetime import datetime, date

def remove_date_datetime(dt: date) -> date:
    """ Remove a date from a datetime. """
    dt = dt.replace(year=1, month=1, day=1)
    return dt


def remove_week_datetime(dt: date) -> date:
    """ Change dates to the following:
        01/01/01 for a Monday
        02/01/01 for a Tuesday
        03/01/01 for a Wednesday
        04/01/01 for a Thursday
        05/01/01 for a Friday
        06/01/01 for a Saturday
        07/01/01 for a Sunday """

    day = dt.weekday()
    dt = dt.replace(year=1, month=1, day=(day + 1))
    return dt


def ggLeap_str_to_datetime(string: str) -> date:
    date = datetime.strptime(string,
                             '%m/%d/%Y %I:%M:%S %p')
    return date


def ggLeap_datetime_to_str(string: str) -> date:
    date = datetime.strftime(string,
                             '%m/%d/%Y %I:%M:%S %p')
    return date


def ggLeap_str_to_datetime_no_time(string: str) -> date:
    date = datetime.strptime(string,
                             '%m/%d/%Y')
    return date


def ggLeap_get_weekday(string: str) -> int:
    date = ggLeap_str_to_datetime(string)
    return date.weekday()


def ggLeap_get_weekday_no_time(string: str) -> int:
    date = ggLeap_str_to_datetime_no_time(string)
    return date.weekday()


def read_csv(path: str) -> pd.DataFrame:
    """ Function to replace pandas.read_csv() because
    ggLeap data is screwy to start with so this function
    cleans the data and then loads it into a pandas
    dataframe """

    # First make sure that we actually don't have a valid CSV
    # because pandas is way more efficient than whatever I'm writing
    try:
        cleaned_df = pd.read_csv(path)
        return cleaned_df
    except:
        pass

    f = open(path, 'r')
    raw_rows = f.readlines()

    columns = raw_rows.pop(0)
    columns = columns.split(',')

    #####################################################################
    # Break this down into two stages                                   #
    # 1: pre-comma-breaking                                             #
    # 2: post-comma-breaking                                            #
    # Functions pre-comma-breaking take a list and return a list        #
    # Functions post-comma-breaking take a 2D list and return a 2D list #
    #####################################################################

    pre_comma_br_cleaning_functions = [remove_escapes]
    post_comma_br_cleaning_functions = [fix_RemoveOffers]

    for f in pre_comma_br_cleaning_functions:
            raw_rows = f(raw_rows)

    raw_rows = break_commas(raw_rows)

    for f in post_comma_br_cleaning_functions:
        raw_rows = f(raw_rows)

    cleaned_df = pd.DataFrame(raw_rows)
    cleaned_df.columns = columns
    return cleaned_df


def break_commas(raw_rows: list) -> list:
    new_rows = []
    for row in raw_rows:
        new_rows.append(row.split(','))

    return new_rows


def fix_RemoveOffers(raw_rows: list) -> list:
    """ If ggLeap returns records which have a 'RemoveOffer' action, then another 
    of the columns will have a comma in it meaning that reading it as a CSV doesn't work
    properly. This function fixes that """

    # There's definitely a more efficent way of doing this.
    new_df_vals = []
    for row in raw_rows:
        if 'RemovedOffer' in row:
            index = row.index('RemovedOffer')
            offer_name = row[index + 1]
            reason = row[index + 2]

            new_val = offer_name + "; " + reason

            row.pop(index + 2)
            row.pop(index + 1)
            row.insert(index + 1, new_val)

        new_df_vals.append(row)

    return new_df_vals


def remove_escapes(raw_rows: list) -> list:
    """ On initially loading the data, a number of escape characters
        don't get removed. This function removes them """
    escapes = ['\n']

    new_rows = []
    for row in raw_rows:
        for escape in escapes:
            row.replace(escape, '')

        new_rows.append(row)
    
    return new_rows
