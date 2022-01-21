import decimal

from broker_clients.emulator_proxy import Broker
import logging
from broker_clients import session
from broker_clients import Balances, Trades

MINIMUM_TRADE_AMOUNT = 0
logger = logging.getLogger(__name__)


class BrokerEmulator(Broker):
    def __init__(self, symbol, time_frame, name, trade_in_trend):
        super().__init__(symbol, time_frame)
        self.name = name
        self.trade_in_trend = trade_in_trend
        self.balance_id = self.get_balance_id()
        if self.trading_budget() is None:
            self.set_trading_budget(100)

    @ property
    def stop_loss(self):
        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()
        if trade:
            return trade.stop_loss

    @ stop_loss.setter
    def stop_loss(self, value):
        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()
        if trade:
            trade.stop_loss = value
            session.commit()
            self._stop_loss = value

    @property
    def trade_id(self):
        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()
        if trade:
            return trade.trade_id
        return None

    def get_balance_id(self):
        balance = session.query(Balances).filter_by(name=self.name).first()
        if balance is None:
            raise ValueError('No Balance found with name: {}'.format(self.name))
        return balance.balance_id

    def trading_budget(self):
        balance = session.query(Balances).filter_by(name=self.name).first()
        if balance:
            return balance.free

    def set_trading_budget(self, value):
        if not self.trading_budget():

            balance = Balances(name=self.name, symbol=self._symbol, time_frame=self._time_frame, free=value, locked=0)
            session.add(balance)
        else:
            balance = session.query(Balances).filter_by(name=self.name).first()
            balance.free = value
        session.commit()

    def get_opened_trades(self):
        count = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).count()
        return count

    def init_broker_object(self):
        count = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).count()
        if count > 1:
            message = 'The balance {} has {} trades opened'.format(self.name, count)
            logger.error('func=init_broker_object, name={}, time_frame={}, symbol, msg={}'.format(
                self.name, self._time_frame, self._symbol, message))
            raise ValueError(message)

        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()
        if trade:
            self._price, self._stop_loss = trade.buy_price, trade.stop_loss
            self._amount, self.created_at = trade.amount, trade.created_at

    def market(self, side, amount, stop_loss=None, stop_loss_percentage=None, emulated_time=None):
        if side not in ['BUY', 'SELL'] or amount <= MINIMUM_TRADE_AMOUNT:
            raise ValueError('Invalid side: {} or amount: {} in market order'.format(side, amount))
        if stop_loss is None and stop_loss_percentage is None:
            raise ValueError('Stop loss must be set')
        if self.get_opened_trades() >= 1:
            raise ValueError('There are {} opened trades'.format(side))

        if side == 'BUY':
            self.price = decimal.Decimal(emulated_time['Close'])
            if not stop_loss:
                calculated_stop_loss = self.price - (self.price * stop_loss_percentage)
            self._amount = amount

            trade = Trades(name=self.name,
                           symbol=self._symbol,
                           time_frame=self._time_frame,
                           entry_date=emulated_time['date'],
                           amount=amount,
                           stop_loss=calculated_stop_loss,
                           buy_price=self.price,
                           sell_price=None,
                           profit=None,
                           side=side,
                           low_moment_price=emulated_time['Low'],
                           balance_id=self.balance_id)
            session.add(trade)
            session.commit()

    def take_profit(self, row=None):
        current_price = decimal.Decimal(row['Close'])
        delta = current_price - self.price
        profit_percentage = delta / current_price
        profit_amount = self._amount * profit_percentage
        self.set_sell_price(current_price, self._amount + profit_amount, row)
        self.clean_order()
        return {
            "profit_percentage": profit_percentage,
            "profit_amount": profit_amount
        }

    def set_sell_price(self, sell_price, profit, row):
        balance = session.query(Balances).filter_by(name=self.name).first()
        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()

        trade.sell_price = sell_price
        trade.profit = profit
        trade.exit_date = row['date']
        balance.free = profit
        session.commit()

    def has_open_order(self):
        return self.get_opened_trades() == 1

    def is_stop_loss_reached(self, prices):
        trade = session.query(Trades).filter_by(name=self.name, sell_price=None, profit=None).first()
        return trade.is_stop_loss_reached(prices)


if __name__ == '__main__':
    symbol, time_frame, name = 'BTCUSDT:BINANCE', '15', 'BTC'
    broker = BrokerEmulator(symbol, time_frame, name, None)
    side, amount, stop_loss, stop_loss_percentage, emulated_time = 'BUY', 100, 145, None, {
        "Close": 150, "date": "2021/01/14, 14:30:00"}
    broker.market(side, amount, stop_loss=stop_loss, emulated_time=emulated_time)
