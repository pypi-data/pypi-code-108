import requests
import json
import pandas as pd
import datetime
    
def retrieve_data(symbol:str="BTC-USDT",
                  time_period:str="1day",
                  start_date:str="2018-01-01",
                  end_date:str="2022-01-10",
                 ):
    """
    Retrieves historical data from the KuCoin API.
    Using open API adress "https://openapi-v2.kucoin.com/api/v1/market/history/trade"
    
    Parameters
    ----------
    name : array-like
        Inputted cryptocurrency symbol.
    time_period : str
        Inputted time period.
        1min, 3min, 5min, 15min, 30min, 1hour,
        2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
    start_date : string "%Y-%m-%d"
        Inputted datetime. Minimum is 2018-01-01
    end_date : string "%Y-%m-%d"
        Inputted time frame.
    
    Returns
    -------
    pandas.DataFrame
        Historical data of the cryptocurrency.
    """
    
    if not isinstance(symbol, str):
        raise TypeError("The input symbol must be of string type")

    date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    start_date = int(datetime.datetime.timestamp(date))
    
    date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    end_date = int(datetime.datetime.timestamp(date))
    

    # Define the API URL
    urllink = f"https://api.kucoin.com/api/v1/market/candles?type={time_period}&symbol={symbol}&startAt={start_date}&endAt={end_date}"
    
    # Make the API call and convert the JSON response to a Python dictionary
    response = requests.get(urllink).json()
    
    assert type(response) == dict, "It is not a dictionary response"
    
    # Convert the JSON response to a Python dictionary
    data = response["data"]
    
    # Create a pandas dataframe from the Python dictionary
    cols = ["Date", "Open", "Close", "High",  "Low", "Volume", "Turnover"]
    df = pd.DataFrame(data, columns=cols)
    df['Symbol'] = symbol
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    
    df['Close'] = df['Close'].astype(float)
    
    assert len(df) >= 1, "Empty dataframe"
    
    # Test whether output data is of pd.DataFrame type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The output dataframe must be of pd.DataFrame type")
    
    # Return the dataframe
    return df[['Symbol','Date','Close']]
