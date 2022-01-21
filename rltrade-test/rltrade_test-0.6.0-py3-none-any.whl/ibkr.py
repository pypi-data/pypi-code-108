import time
import threading
import pandas as pd
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.id_to_stock = {}
        self.stock_dict = {}
        self.data = []
        self.tick_data = []
    
    def historicalData(self, reqId, bar):
        self.data.append([bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume])
    
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)
    
    def historicalTicks(self, reqId: int, ticks:list, done: bool):
        for i,tick in enumerate(ticks):
            self.tick_data.append([i,tick.time,tick.price])
    
    def historicalTicksLast(self, reqId: int, ticks: list, done: bool):
        for i,tick in enumerate(ticks):
            self.tick_data.append([i,tick.time,tick.price])
    
    def historicalTicksBidAsk(self, reqId: int, ticks: list, done: bool):
        for i,tick in enumerate(ticks):
            self.tick_data.append([i,tick.time,tick.price])

    def get_df(self):
        return pd.DataFrame(self.data,columns=['date','open','high','low','close','volume'])
    
    def get_tic_df(self):
        return pd.DataFrame(self.tick_data,columns=['tick_no','time','price'])
    
    def reset_df(self):
        self.data = []
        self.tick_data = []

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    def updatePortfolio(self, contract: Contract, position: int, marketPrice: float, marketValue: float, averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
        print("Symbol:", contract.symbol,"Position:", position, "MarketPrice:", marketPrice)
        if contract.secType in ['STK','FUT']:
            self.stock_dict[contract.symbol] = [marketPrice,position]
    
    def tickPrice(self, reqId, tickType, price, attrib):
        self.stock_dict[self.id_to_stock[reqId]] = [price,0]
    
    def setStockId(self,i,tic):
        self.id_to_stock[i] = tic

    def getStockData(self):
        return self.stock_dict


def stock_contract(symbol, secType='STK', exchange='SMART', currency='USD'):
	''' custom function to create stock contract '''
	contract = Contract()
	contract.symbol = symbol
	contract.secType = secType
	contract.exchange = exchange
	contract.currency = currency
	return contract

def future_contract(symbol,secType="FUT",exchange="GLOBEX",currency="USD"):
    ''' custom function to create future contract '''
    contract = Contract()
    contract.localSymbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = currency
    return contract

def contfuture_contract(symbol,secType="CONTFUT",exchange="GLOBEX",currency="USD"):
    ''' custom function to create future contract '''
    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = currency
    return contract

def api_connect(demo=True):
    app = IBapi()
    app.nextorderId = None
    if demo:
        app.connect('127.0.0.1', 7497, 123)
    else:
        app.connect('127.0.0.1', 7496, 123)
    time.sleep(1)
    return app


def buy_stock(app,ticker:str,sectype:str,exchange:str,quantity:int):
    
    def run_loop():
        app.run()

    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderid
    while True:
        if isinstance(app.nextorderId, int):
            break
        else:
            print('waiting for connection')
            time.sleep(1)

    #Create order object
    order = Order()
    order.action = 'BUY'
    order.totalQuantity = quantity
    order.orderType = 'MKT'

    #Place order
    if sectype == 'STK':
        cont = stock_contract(ticker,secType=sectype,exchange=exchange)
    elif sectype == 'FUT':
        cont = future_contract(ticker,secType=sectype,exchange=exchange)
    elif sectype == 'CONTFUT':
        cont = contfuture_contract(ticker,secType=sectype,exchange=exchange)

    app.placeOrder(app.nextorderId, cont, order)
    app.nextorderId += 1
    time.sleep(2)

def sell_stock(app,ticker:str,sectype:str,exchange:str,quantity:int):
    def run_loop():
        app.run()

    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderid
    while True:
        if isinstance(app.nextorderId, int):
            break
        else:
            print('waiting for connection')
            time.sleep(1)

    #Create order object
    order = Order()
    order.action = 'SELL'
    order.totalQuantity = quantity
    order.orderType = 'MKT'

    #Place order
    if sectype == 'STK':
        cont = stock_contract(ticker,secType=sectype,exchange=exchange)
    elif sectype == 'FUT':
        cont = future_contract(ticker,secType=sectype,exchange=exchange)
    elif sectype == 'CONTFUT':
        cont = contfuture_contract(ticker,secType=sectype,exchange=exchange)

    app.placeOrder(app.nextorderId, cont, order)
    app.nextorderId += 1
    time.sleep(2)

def get_stock_info(app:IBapi,ticker_list:list,sec_types:list,exchanges:list,accountid:str,demo=True):
    def run_loop():
        app.run()

    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via
    while True:
        if isinstance(app.nextorderId, int):
            break
        else:
            print('waiting for connection')
            time.sleep(1)

    acc_type = 2 if demo else -1
    for i,tic in enumerate(ticker_list):
        exchange = exchanges[i]
        sectype = sec_types[i]
        if sectype == 'STK':
            contract = stock_contract(tic,secType=sectype,exchange=exchange)
            app.setStockId(i,tic)
        elif sectype == 'FUT':
            contract = future_contract(tic,secType=sectype,exchange=exchange)
            app.setStockId(i,tic[:-2])
        elif sectype == 'CONTFUT':
            contract = contfuture_contract(tic,secType=sectype,exchange=exchange)
            app.setStockId(i,tic)

        app.reqMarketDataType(acc_type)
        app.reqMktData(i, contract, '', True, False, [])
        time.sleep(3)

    #get information for stocks currently in the portfolio
    app.reqAccountUpdates(True,accountid)
    time.sleep(5)

    return app.getStockData()