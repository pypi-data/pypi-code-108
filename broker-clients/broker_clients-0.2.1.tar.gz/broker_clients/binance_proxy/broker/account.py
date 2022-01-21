from decimal import Decimal

from broker_clients.binance_proxy.broker import UtilsAPI
from broker_clients import session
from broker_clients.emulator_proxy.storage.models import Orders, SymbolMetadata
from broker_clients import Accounts, Trades, Balances
from binance.client import Client
import logging

logger = logging.getLogger(__name__)


class ExtendedAccount:

    def __init__(self, name, symbol):
        self.name = name
        account = session.query(Accounts).filter(Accounts.name == name).first()
        self.client = Client(api_key=account.api_key, api_secret=account.secret_key, tld='vision')
        self.symbol = symbol
        self.symbol_metadata = session.query(SymbolMetadata).filter(SymbolMetadata.symbol == self.symbol).first()

    def calculate_precise_quantity(self, quote_order_quantity, price):
        quantity = self.quantity_from_quote(quote_order_quantity, price, self.minimum_quantity_lot_size)
        quantity = "{:0.0{}f}".format(quantity, self.quote_precision)
        return quantity

    def update_buy_price(self, trade_id, order):
        pass

    def market(self, trade_id, symbol, side, quote_order_quantity):
        try:
            order = Orders.register_order(self.client, trade_id, symbol=symbol, side=side,
                                          quoteOrderQty=quote_order_quantity, type=self.client.ORDER_TYPE_MARKET)
            return order
        except Exception as e:
            logger.error('func=ExtendedAccount.market, account_name={}, trade_id={}, symbol={},'
                         'side={}, quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quote_order_quantity, e))
            raise e

    def market_quantity(self, trade_id, symbol, side, quantity):
        try:
            order = Orders.register_order(self.client, trade_id, symbol=symbol, side=side,
                                          quantity=quantity, type=self.client.ORDER_TYPE_MARKET)
            return order
        except Exception as e:
            logger.error('func=ExtendedAccount.market, account_name={}, trade_id={}, symbol={},'
                         'side={}, quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quantity, e))
            raise e

    def limit_buy(self, trade_id, symbol, quote_order_quantity, price):
        try:
            quantity = self.calculate_precise_quantity(quote_order_quantity, price)
            res = Orders.register_order(self.client, trade_id, symbol=symbol, quantity=quantity, price=price,
                                        side=self.client.SIDE_BUY, type=self.client.ORDER_TYPE_LIMIT)
            return res
        except Exception as e:
            logger.error('func=ExtendedAccount.limit_buy, account_name={}, trade_id={}, symbol={},'
                         'side={}, quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quote_order_quantity, e))
            raise e

    def limit_sell(self, trade_id, symbol, quote_order_quantity, price):
        try:
            quantity = self.calculate_precise_quantity(quote_order_quantity, price)

            res = Orders.register_order(self.client, trade_id, symbol=symbol, quantity=quantity,
                                        price=price, side=self.client.SIDE_SELL, type=self.client.ORDER_TYPE_LIMIT)
            return res
        except Exception as e:
            logger.error('func=ExtendedAccount.limit_sell, account_name={}, trade_id={}, symbol={},'
                         'side={}, quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quote_order_quantity, e))
            raise e

    def update_limit_orders(self):
        records = session.query(Orders.order_id, Orders.symbol).filter(Orders.status != 'FILLED').all()
        for row in records:
            order_id, symbol = row[0], row[1]
            order_response = self.client.get_order(symbol=symbol, orderId=order_id)
            Orders.update_order(order_response)

    def take_profit_limit(self, symbol, side, quote_order_quantity, price, stop_price):
        try:
            quantity = self.calculate_precise_quantity(quote_order_quantity, price)

            order_response = self.client.create_order(symbol=symbol, side=side, quantity=quantity, price=price,
                                                      stopPrice=stop_price, type=self.client.ORDER_TYPE_STOP_LOSS_LIMIT,
                                                      timeInForce=self.client.TIME_IN_FORCE_GTC)
            res = Orders.register_order(order_response)
            return res

        except Exception as e:
            logger.error('func=ExtendedAccount.take_profit_limit, symbol={}, quote_order_quantity={}, price={}, '
                         'msg={}'.format(symbol, quote_order_quantity, price, e))
            raise e

    def test_order(self, symbol, side, quote_order_quantity):
        klines = self.client.get_historical_klines(symbol, self.client.KLINE_INTERVAL_15MINUTE, "1 hour ago UTC")
        close_price = Decimal(klines[0][4])
        # a = limit_buy(symbol, quote_order_quantity, close_price)

        limit_price = close_price * Decimal('0.97')
        stop_price = close_price - Decimal('0.96')
        b = self.stop_loss_limit(symbol, side, quote_order_quantity, limit_price, stop_price)

    def fill_empty_prices(self, symbol):
        filled_orders = session.query(Orders).filter_by(status=self.client.ORDER_STATUS_FILLED, price=0)
        zero_price_trades = session.query(Orders).join(Trades).filter(Trades.buy_price == 0)
        orders = list(filled_orders) + list(zero_price_trades)

        my_trades = self.client.get_my_trades(symbol=symbol)
        for order in orders:
            my_trade = self.find_by_order_id(my_trades, order.order_id)
            if my_trade:
                order.fill_empty_price(UtilsAPI.clean_response(my_trade))
            else:
                logger.critical('func=ExtendedAccount.fill_empty_prices, order_id={}, symbol={}, '
                                'msg=No trade found'.format(order.order_id, symbol))

    @classmethod
    def find_by_order_id(cls, my_trades, order_id):
        for t in my_trades:
            if t['orderId'] == order_id:
                return t

    def update_symbol_metadata(self):
        symbols = session.query(Balances.symbol).distinct(Balances.symbol)
        for row in symbols:
            symbol_text = row[0].split(':')[1]
            symbol_metadata = session.query(SymbolMetadata).filter_by(symbol=symbol_text).first()

            info = self.client.get_symbol_info(symbol_text)
            minimum_quantity_lot_size = Decimal(
                [i for i in info['filters'] if 'LOT_SIZE' == i['filterType']][0]['minQty'])
            minimum_price_filter = Decimal(
                [i for i in info['filters'] if 'PRICE_FILTER' == i['filterType']][0]['minPrice'])
            minimum_notional = Decimal(
                [i for i in info['filters'] if 'MIN_NOTIONAL' == i['filterType']][0]['minNotional'])
            quote_precision = info['quotePrecision']

            if not symbol_metadata:
                symbol_metadata = SymbolMetadata(
                    symbol=symbol_text, minimum_quantity_lot_size=minimum_quantity_lot_size,
                    quote_precision=quote_precision, minimum_price_filter=minimum_price_filter,
                    minimum_notional=minimum_notional)
                session.add(symbol_metadata)
                session.commit()
                self.symbol_metadata = symbol_metadata
            else:
                symbol_metadata.minimum_quantity_lot_size = minimum_quantity_lot_size
                symbol_metadata.minimum_price_filter = minimum_price_filter
                symbol_metadata.minimum_notional = minimum_notional
                symbol_metadata.minimum_notional = minimum_notional
                symbol_metadata.quote_precision = quote_precision
                session.commit()

    def market_with_stop_loss(self, balance_name, side):
        stage = 'API.read_price'
        try:
            ############################################################################################################
            # Block of code only for test net
            # In real escenario Trades tables records are created by the strategy
            self.update_symbol_metadata()
            klines = self.client.get_historical_klines(
                self.symbol, self.client.KLINE_INTERVAL_15MINUTE, "1 hour ago UTC")
            close_price = Decimal(klines[0][4])

            stage = 'SQL.create_trade'
            balance = session.query(Balances).filter_by(name=balance_name).first()
            quantity = self.symbol_metadata.quantity_from_quote(balance.free, close_price)

            trade = Trades(name=balance.name,
                           symbol=balance.symbol,
                           time_frame=balance.time_frame,
                           entry_date='2021-03-27 21:45:00.000000',
                           amount=balance.free,
                           quantity=quantity,
                           stop_loss=close_price*Decimal('0.97'),
                           buy_price=close_price,
                           sell_price=None,
                           profit=None,
                           side='Buy',
                           low_moment_price=close_price,
                           balance_id=balance.balance_id)
            session.add(trade)
            session.commit()
            ############################################################################################################
            stage = 'ExtendedAccount.create_order'

            self.market_quantity(
                trade.trade_id, self.symbol, side, self.symbol_metadata.fix_price_precision(trade.quantity))

            stage = 'API.read_entry_price'
            self.fill_empty_prices(self.symbol)

            stage = 'ExtendedAccount.register_order'

            stop = self.symbol_metadata.calculate_stop_from_limit(trade.stop_loss)
            Orders.register_order(
                self.client, trade.trade_id, symbol=symbol, side=self.client.SIDE_SELL, quantity=trade.quantity,
                price=self.symbol_metadata.fix_price_precision(trade.stop_loss),
                timeInForce=self.client.TIME_IN_FORCE_GTC, stopPrice=self.symbol_metadata.fix_price_precision(stop),
                type=self.client.ORDER_TYPE_STOP_LOSS_LIMIT)

            print(trade)
            print(trade.orders)
        except Exception as e:
            logger.critical('func=ExtendedAccount.market_with_stop_loss, account_name={}, symbol={}, stage={}, '
                            'msg={}'.format(self.name, self.symbol, stage, e))


if __name__ == '__main__':
    symbol = 'BTCUSDT'
    side = 'BUY'
    #quote_order_quantity = Decimal(100)
    balance_name = 'BTC_1D_no_trend_4_testnet'
    balance = session.query(Balances).filter_by(name=balance_name).first()
    if not balance:
        balance = Balances(
                 account_id=1,
                    name=balance_name,
                    symbol='BINANCE:BTCUSDT',
                    time_frame='1D',
                    free=500,
                    locked=0,
                    stop_loss_percentage=0.04,
                    profit_percentage=0.04,
                    trade_in_trend='none',
                    second_scale_from_database=False
        )
        session.add(balance)
        session.commit()
    account = ExtendedAccount('testnet', symbol)
    account.market_with_stop_loss(balance_name, side)






