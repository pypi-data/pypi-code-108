import logging
from broker_clients.quantfury_proxy.broker.client import Utils
logger = logging.getLogger(__name__)


class ExtendedAccount:

    def __init__(self, name, symbol):
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
            pass
        except Exception as e:
            logger.error('func=ExtendedAccount.market, account_name={}, trade_id={}, symbol={},'
                         'side={}, quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quantity, e))
            raise e

    def limit_buy(self, trade_id, symbol, quote_order_quantity, price):
        try:
            pass
        except Exception as e:
            logger.error('func=ExtendedAccount.limit_buy, account_name={}, trade_id={}, symbol={}, '
                         'quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, quote_order_quantity, e))
            raise e

    def limit_sell(self, trade_id, symbol, quote_order_quantity, price):
        try:
            pass
        except Exception as e:
            logger.error('func=ExtendedAccount.limit_sell, account_name={}, trade_id={}, symbol={},'
                         'side={}, quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, side, quote_order_quantity, e))
            raise e

    def take_profit_limit(self, symbol, side, quote_order_quantity, price, stop_price):
        try:
            pass

        except Exception as e:
            logger.error('func=ExtendedAccount.take_profit_limit, symbol={}, quote_order_quantity={}, price={}, '
                         'msg={}'.format(symbol, quote_order_quantity, price, e))
            raise e

    def market_with_stop_loss(self, balance_name, side):
        stage = 'API.read_price'
        try:
            pass
        except Exception as e:
            logger.critical('func=ExtendedAccount.market_with_stop_loss, account_name={}, symbol={}, stage={}, '
                            'msg={}'.format(self.name, self.symbol, stage, e))


    def OCO_buy(self, trade_id, symbol, quote_order_quantity, buy_price, target_price, stop_price):
        try:
            symbol = Utils.reformat_symbol(symbol)

        except Exception as e:
            logger.error('func=ExtendedAccount.limit_buy, account_name={}, trade_id={}, symbol={}, '
                         'quote_order_quantity={}, msg={}'.format(
                          self.name, trade_id, symbol, quote_order_quantity, e))
            raise e