import pandas_datareader as datar


class priceData():
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = self.get_price()

    def get_price(self, source='yahoo'):
        """ give a symobl -> get a price """

        price = datar.DataReader(self.symbol, source)
        price = price["Close"][price.last_valid_index()]
        return price
