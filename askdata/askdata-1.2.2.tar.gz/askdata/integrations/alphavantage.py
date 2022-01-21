import requests
import pandas as pd

''' Create a function that get TIME_SERIES_DAILY_ADJUSTED for a particular symbol as input '''
def get_daily_adjusted(symbol):
    # create the endpoint
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={apikey}"
    # request the data
    response = requests.get(url)
    # parse the JSON data into a python dictionary
    data = response.json()
    # return the dictionary
    return data

''' Parse returned data in a denormalized pandas dataframe '''
def parse_daily_adjusted_in_a_dataframe(data):
    # extract the time series
    time_series = data["Time Series (Daily)"]
    # extract the columns to keep
    columns = ["5. adjusted close", "6. volume", "7. dividend amount", "8. split coefficient"]
    # create an empty list to store daily stock price
    rows = []
    # iterate over time_series
    for date, daily_prices in time_series.items():
        # create a dictionary for each date
        row = {key: value for key, value in daily_prices.items() if key in columns}
        # add a date column using the date string from the time_series
        row["date"] = date
        # add the symbol column
        row["symbol"] = data["Meta Data"]["2. Symbol"]
        # append the row to the rows list
        rows.append(row)
    # create a pandas dataframe from the rows list
    df = pd.DataFrame(rows)
    # reorder the columns
    df = df[["date", "symbol", "5. adjusted close", "6. volume", "7. dividend amount", "8. split coefficient"]]
    df.columns = ["Date", "Symbol", "Adjusted Close", "Volume", "Dividend amount", "Split coefficient"]
    # return the dataframe
    return df


''' 
Write a function that get as input a list of symbols and for earch symbol get get_daily_adjusted() and parse_daily_adjusted() returning a combination of the individual dataframes
'''

def get_daily_adjusted_df(symbols, apikey=None):

    if apikey=None:
        print("You need to request an Alpha Vantage API key from here: https://www.alphavantage.co/support/#api-key")

    # create an empty list to store dataframes
    dfs = []
    # iterate over symbols
    for symbol in symbols:
        # get the data for the symbol
        data = get_daily_adjusted(symbol, apikey)
        # parse the data into a dataframe
        df = parse_daily_adjusted_in_a_dataframe(data)
        # add the dataframe to the list
        dfs.append(df)
    # concatenate the list of dataframes
    df = pd.concat(dfs)

    # Casting the Volume type as float
    df["Volume"] = df["Volume"].astype(float)

    # return the concatenated dataframe
    return df