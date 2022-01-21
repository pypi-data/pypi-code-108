import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

BROKER_DATABASE_NAME = os.getenv("BROKER_DATABASE_NAME")
MINIMUM_TRADE_AMOUNT = 0


class Broker:
    def __init__(self, symbol, time_frame):
        self._symbol = symbol
        self._time_frame = time_frame
        self._price = None
        self._stop_loss = None
        self._amount = None

    def clean_order(self):
        self._price = None
        self._stop_loss = None
        self._amount = None

    def market(self, side, amount, stop_loss=None, stop_loss_percentage=None, emulated_time=None):
        pass

    def has_open_order(self):
        return self._price is not None

    def has_earning(self, emulated_time=None):
        return self._price < emulated_time['Low']

    def take_profit(self, row=None):
        pass

    def has_opened_position(self):
        return self.price is not None and self.stop_loss is not None and self.price > self.stop_loss

    @property
    def stop_loss(self):
        return self._stop_loss

    @stop_loss.setter
    def stop_loss(self, value):
        self._stop_loss = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    def set_sell_price(self, sell_price):
        pass


class BrokerMemoryEmulator(Broker):

    def market(self, side, amount, stop_loss=None, stop_loss_percentage=None, emulated_time=None):
        if side not in ['BUY', 'SELL'] or amount <= MINIMUM_TRADE_AMOUNT:
            raise ValueError('Invalid side: {} or amount: {} in market order'.format(side, amount))
        if stop_loss is None and stop_loss_percentage is None:
            raise ValueError('Stop loss must be set')

        if side == 'BUY':
            self._price = (emulated_time['Close'] + emulated_time['Open']) / 2
            if not stop_loss:
                self.stop_loss = self.price - (self.price * stop_loss_percentage)
            self._amount = amount

    def take_profit(self, row=None):
        delta = row['Low'] - self._price
        profit_percentage = delta / row['Low']
        profit_amount = self._amount * profit_percentage
        self.clean_order()
        return {
            "profit_percentage": profit_percentage,
            "profit_amount": profit_amount
        }


class BrokerDiskEmulator(Broker):
    def __init__(self, symbol, time_frame, database_name=BROKER_DATABASE_NAME):
        self.conn = sqlite3.connect(database_name)
        super().__init__(symbol, time_frame)
        self._create_table()
        if self.trading_budget() is None:
            self.set_trading_budget(100)

    def _create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS trades(
        date text,
        side text,
        symbol text,
        time_frame text,
        amount real,
        stop_loss real,
        buy_price real,
        sell_price real,
        profit real
        )''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS balances(
                symbol text,
                time_frame text,
                free real,
                locked real
                )''')

    def trading_budget(self):
        result_set = self.conn.execute("""SELECT free FROM balances WHERE symbol=? and time_frame=?""", (self._symbol, self._time_frame))
        row = result_set.fetchone()
        if row:
            return row[0]

    def set_trading_budget(self, value):
        if not self.trading_budget():
            trade = [(self._symbol, self._time_frame, value, 0)]
            self.conn.executemany('INSERT INTO balances VALUES (?,?,?,?)', trade)
        else:
            self.conn.execute("""UPDATE balances
            SET free = ?
            WHERE symbol=? and time_frame=?""", (value, self._symbol, self._time_frame))
        self.conn.commit()

    def init_broker_object(self):
        result_set = self.conn.execute("""
           SELECT buy_price, stop_loss, amount 
           FROM trades WHERE symbol=? and time_frame=? and sell_price is NULL""", (self._symbol, self._time_frame))
        row = result_set.fetchone()
        if row:
            self._price, self._stop_loss, self._amount = row[0], row[1], row[2]

    def market(self, side, amount, stop_loss=None, stop_loss_percentage=None, emulated_time=None):
        if side not in ['BUY', 'SELL'] or amount <= MINIMUM_TRADE_AMOUNT:
            raise ValueError('Invalid side: {} or amount: {} in market order'.format(side, amount))
        if stop_loss is None and stop_loss_percentage is None:
            raise ValueError('Stop loss must be set')

        if side == 'BUY':
            self.price = emulated_time['Close']
            if not stop_loss:
                self.stop_loss = self.price - (self.price * stop_loss_percentage)
            self._amount = amount
            trade = [(emulated_time['date'], side, self._symbol, self._time_frame, amount, self.stop_loss, self.price, None, None)]
            self.conn.executemany('INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?)', trade)
            self.conn.commit()

    def take_profit(self, row=None):
        current_price = row['Close']
        delta = current_price - self.price
        profit_percentage = delta / current_price
        profit_amount = self._amount * profit_percentage
        self.set_sell_price(current_price, self._amount + profit_amount)
        self.clean_order()
        return {
            "profit_percentage": profit_percentage,
            "profit_amount": profit_amount
        }

    def set_sell_price(self, sell_price, profit):
        self.conn.execute("begin")
        update_query = """UPDATE trades SET sell_price = ?, profit = ? 
        WHERE symbol=? and time_frame=? and sell_price is NULL"""
        self.conn.execute(update_query, (sell_price, profit, self._symbol, self._time_frame))
        self.set_trading_budget(profit)


if __name__ == '__main__':
    broker = BrokerDiskEmulator('BINANCE:BTCUSDT', '60')
    budget = broker.trading_budget()
    print(budget)
    #broker.market('BUY', 100, None, 0.03, {'date': '2020/10/28, 18:00:00', 'Close': 5000})
