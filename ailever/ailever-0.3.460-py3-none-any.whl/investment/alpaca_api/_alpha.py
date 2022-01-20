from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime
import _config

TRADE_BASE_URL = _config.ENDPOINT_URL
DATA_BASE_URL = _config.DATA_URL
APCA_API_KEY_ID = _config.API_KEY_ID
APCA_API_SECRET_KEY =_config.SECRET_KEY

"""
Paper Trading BASE URL operates on Account URL
"""
trade_api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, TRADE_BASE_URL)
account = trade_api.get_account()

"""
Data viewing URL operates on DATA BASE URL
"""

data_api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, DATA_BASE_URL)
bars = data_api.get_bars("ARE", TimeFrame.Day, "2021-01-01", "2021-07-30", limit=10, adjustment='raw').df

if __name__ == "__main__":
    print(bars)
    print(account)
