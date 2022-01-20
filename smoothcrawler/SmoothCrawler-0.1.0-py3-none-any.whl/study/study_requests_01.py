import requests


URL_TW_Stock = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date=20210801&stockNo=2330"

response = requests.get(url=URL_TW_Stock, headers={"Content-Type": "application/json;charset=UTF-8"})
print("response.text: ", response.text)
print("response.content: ", response.content)
