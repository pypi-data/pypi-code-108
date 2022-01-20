from urllib3 import PoolManager


URL_TW_Stock = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date=20210801&stockNo=2330"

http = PoolManager()
response = http.request(method="GET", url=URL_TW_Stock, headers={"Content-Type": "application/json;charset=UTF-8"})
print("response.data: ", response.data)
print("response.data.decode('utf-8'): ", response.data.decode('utf-8'))
print("response.read: ", response.read())
