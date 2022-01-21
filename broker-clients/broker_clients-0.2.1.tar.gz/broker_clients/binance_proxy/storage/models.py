import os
import re
import logging
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from broker_clients import Base, session
from broker_clients.binance_proxy.broker import UtilsAPI


load_dotenv()
logger = logging.getLogger(__name__)
cypher_key = os.getenv("CYPHER_KEY")


class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, nullable=False)
    trade_id = Column(Integer, ForeignKey('trades.trade_id'), nullable=False)
    symbol = Column(String, nullable=False)
    order_list_id = Column(Integer, nullable=False)
    client_order_id = Column(String, nullable=False)
    transact_time = Column(DateTime, nullable=False)
    price = Column(Numeric, nullable=True)
    # original_quantity, original_quantity and cumulative_quote_quantity should be equal
    original_quantity = Column(Numeric, nullable=False)  # quantity requested
    executed_quantity = Column(Numeric, nullable=False)  # quantity filled
    cumulative_quote_quantity = Column(Numeric, nullable=False)

    status = Column(String, nullable=False)
    time_in_force = Column(String, nullable=False)
    type = Column(String, nullable=False)
    side = Column(String, nullable=False)

    stop_price = Column(Numeric, nullable=True)
    iceberg_quantity = Column(Numeric, nullable=True)  # For hiding the actual order quantity on big orders
    time = Column(DateTime, nullable=True)
    update_time = Column(DateTime, nullable=True)
    is_working = Column(Boolean, nullable=True)
    original_quote_order_quantity = Column(Numeric, nullable=True)  # quote quantity requested
    binance_trade_id = Column(Integer, nullable=True)
    commission_asset = Column(String, nullable=True)
    commission = Column(Numeric, nullable=True)

    fills = relationship("Fills")
    trade = relationship("Trades", back_populates="orders", uselist=False)

    def __repr__(self):
        return "<Orders(symbol={}, cumulative_quote_quantity={}, executed_quantity={}, type={}, side={})>".format(
            self.symbol, self.cumulative_quote_quantity, self.executed_quantity, self.type, self.side)

    @classmethod
    def register_order(cls, client, trade_id, **kwargs):
        list_fills = None
        order_id = None
        stage = 'API.create_order'  # for error control
        try:
            create_order_response = client.create_order(**kwargs)
            if not create_order_response:
                raise ConnectionError('Empty Response')
            create_order_response['trade_id'] = trade_id
            cleaned_create_order_response = UtilsAPI.clean_response(create_order_response)
            if cleaned_create_order_response.get('status') == 'EXPIRED':
                raise ValueError('Expired order')
            list_fills = cleaned_create_order_response.get('fills', [])
            if 'fills' in cleaned_create_order_response:
                del cleaned_create_order_response['fills']
            stage = 'API.read_order'

            read_order_response = client.get_order(symbol=kwargs['symbol'], orderId=cleaned_create_order_response['order_id'])
            cleaned_read_order_response = UtilsAPI.clean_response(read_order_response)
            cleaned_create_order_response.update(cleaned_read_order_response)
            if cleaned_read_order_response.get('status') == 'EXPIRED':
                raise ValueError('Expired order')

            stage = 'SQL.create_order'
            order = Orders(**cleaned_create_order_response)
            session.add(order)
            session.commit()
            stage = 'SQL.create_fills'

            for f in list_fills:
                f['order_id'] = cleaned_create_order_response['order_id']
            fills = [Fills(**f) for f in list_fills]
            session.bulk_save_objects(fills)
            session.commit()
            return order
        except Exception as e:
            order_response_str = None
            if 'cleaned_response' in vars():
                order_response_str = ';'.join([
                    '{}:{}'.format(k, v) for k, v in cleaned_create_order_response.items() or create_order_response.items()])
            logger.error('func=Orders.register_order, order_id={}, order_response_str={}, stage={}, msg={}'.format(
                order_id, order_response_str, stage, e))
            if type(list_fills) is list:
                for f in list_fills:
                    fill_str = ';'.join(['{}:{}'.format(k, v) for k, v in f.items()])
                    logger.error('func=Orders.register_order, order_id={}, fill_str={}, stage={}, msg={}'.format(
                        order_id, fill_str, stage, e))
            raise e

    def price_from_fills(self):
        mean_price = sum(
            [float(f.price) * float(f.quantity) / float(self.executed_quantity) for f in
             self.fills])
        return mean_price

    def commission_from_fills(self):
        commission = sum([float(f.commission) for f in self.fills])
        return commission

    @classmethod
    def update_order(cls, order_response):
        order_id = order_response.get('orderId', None)
        try:
            cleaned_response = UtilsAPI.clean_response(order_response)
            cleaned_response['update_time'] = datetime.utcfromtimestamp(
                cleaned_response['update_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            cleaned_response['time'] = datetime.utcfromtimestamp(
                cleaned_response['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

            session.query(Orders).filter_by(order_id=order_id).update(dict(**cleaned_response))
            session.commit()

        except Exception as e:
            order_response_str = ';'.join(
                ['{}:{}'.format(k, v) for k, v in cleaned_response.items() or order_response.items()])
            logger. error('func=Orders.update_order, order_id={}, order_response_str={}, msg={}'.format(
                order_id, order_response_str, e))

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        session.commit()

    def fill_empty_price(self, my_trade):
        columns_to_update = ["id", "order_list_id", "price", "quantity", "quote_quantity", "commission",
                             "commission_asset"]
        stage = 'SQL.update_order'
        try:

            my_trade = {k: v for k, v in my_trade.items() if k in columns_to_update}
            my_trade['binance_trade_id'] = my_trade.pop('id')
            self.update(my_trade)
            stage = 'SQL.update_trade'

            self.trade.buy_price = self.price
            self.trade.quantity = self.executed_quantity
            self.trade.amount = self.price * self.executed_quantity
            session.commit()
        except Exception as e:
            logger.critical('func=Orders.fill_empty_price, order_id={}, stage={}, msg={}'.format(
                self.order_id, stage, e))
            raise e


class Fills(Base):
    __tablename__ = 'fills'

    fill_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    price = Column(Numeric, nullable=False)
    quantity = Column(Numeric, nullable=False)
    commission = Column(Numeric, nullable=False)
    commission_asset = Column(String, nullable=False)
    trade_id = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Fills(order_id={}, quantity={}, commission={}, commission_asset={})>".format(
            self.order_id, self.quantity, self.commission, self.commission_asset)


def infer_currency_pair(context):
    symbol = context.get_current_parameters()['symbol']
    prefixes = ['BTC']
    suffixes = ['USDT']
    for sub in suffixes:
        matches = re.search(r'(?P<first>^.+?)(?P<second>{}$)'.format(sub), symbol)
        if matches:
            return '{}/{}'.format(matches.groupdict()['first'], matches.groupdict()['second'])

    for pre in prefixes:
        matches = re.search(r'(?P<first>^{})(?P<second>.+)'.format(pre), symbol)
        if matches:
            return '{}/{}'.format(matches.groupdict()['first'], matches.groupdict()['second'])
    return None


class SymbolMetadata(Base):
    __tablename__ = 'symbol_metadata'

    symbol_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, unique=True)
    minimum_quantity_lot_size = Column(String, nullable=False)
    minimum_price_filter = Column(String, nullable=False)
    minimum_notional = Column(String, nullable=False)
    quote_precision = Column(Integer, nullable=False)
    currency_pair = Column(String, nullable=True, default=infer_currency_pair)

    @validates('currency_pair')
    def validate_create_date(self, key, currency_pair):
        assert '/' in currency_pair
        return currency_pair

    def __repr__(self):
        return "<SymbolMetadata(symbol_id={}, symbol={}, minimum_quantity_lot_size={})>".format(
            self.symbol_id, self.symbol, self.minimum_quantity_lot_size)

    def has_quantity_error(self, quantity):
        if quantity < Decimal(self.minimum_quantity_lot_size):
            return 'Quantity to low'

    def has_price_error(self, price):
        if price < Decimal(self.minimum_price_filter):
            return 'Price to low'

    def has_price_quantity_error(self, price, quantity):
        quantity = Decimal(quantity)
        if price < Decimal(self.minimum_price_filter):
            return 'Price to low {} < {}'.format(price, self.minimum_price_filter)
        elif quantity < Decimal(self.minimum_quantity_lot_size):
            return 'Quantity to low'.format(quantity, self.minimum_quantity_lot_size)
        elif price * quantity < Decimal(self.quote_precision):
            return 'Price Quantity to low {} < {}'.format(price*quantity, self.quote_precision)

    def fix_price_precision(self, price):
        if price is None:
            return price
        price = Decimal(price) - Decimal(price) % Decimal(self.minimum_price_filter)
        return "{:0.0{}f}".format(price, self.quote_precision).rstrip('0')

    def calculate_stop_from_limit(self, limit):
        delta_1 = Decimal(limit) * Decimal('0.0001')
        delta_2 = Decimal(self.minimum_quantity_lot_size) * Decimal('10')
        #return max(limit+delta_1, limit+delta_2)
        return limit + delta_2

    def quote_quantity(self, quantity):
        quoted = quantity - quantity % Decimal(self.minimum_quantity_lot_size)
        # return quoted.normalize().__str__()
        return quoted.to_integral_value().__str__()

    def quantity_from_quote(self, quote_order_quantity, price):
        try:
            quantity = quote_order_quantity/price
            quoted_quantity = self.quote_quantity(quantity)
            return quoted_quantity
        except Exception as e:
            logger.error('func=ExtendedAccount.quantity_from_quote, quote_order_quantity={}, price={}, '
                         'quote_precision={}, msg={}'.format(quote_order_quantity, price, self.quote_precision, e))
            raise e

    @classmethod
    def to_currency_pair_format(cls, symbol):
        symbol = symbol.split(':')[1] if symbol.find(':') > 0 else symbol
        symbol_metadata = session.query(SymbolMetadata).filter_by(symbol=symbol).first()
        if not symbol_metadata:
            raise ValueError('Not metadata for symbol {}'.format(symbol))
        return symbol_metadata.currency_pair

    @classmethod
    def get_threshold(cls, price):
        return price * Decimal('0.001')

    def get_price_range(self, limit_price):
        threshold = self.get_threshold(limit_price)
        upper = self.fix_price_precision(limit_price + threshold)
        lower = self.fix_price_precision(limit_price - threshold)
        return lower, upper
