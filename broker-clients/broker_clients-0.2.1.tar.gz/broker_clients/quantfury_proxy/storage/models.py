import enum
import logging
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import relationship, validates
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from broker_clients import Base, session
from broker_clients.binance_proxy.broker import UtilsAPI
from broker_clients.emulator_proxy.storage.models import SymbolMetadata
from broker_clients.quantfury_proxy.broker.client import Utils, Quantfury
from broker_clients.quantfury_proxy.broker.client import REVERTED_POSITION_TYPES, REVERTED_ORDER_TYPES


load_dotenv()
logger = logging.getLogger(__name__)


class QuantfuryOrderStatus(enum.Enum):
    hold = 'hold'
    open = 'open'
    close = 'close'
    cancel = 'cancel'
    target = 'target'


class QuantfuryOrderType(enum.Enum):
    stop_order = 'stop_order'
    target_order = 'target_order'
    limit_order = 'limit_order'


class QuantfuryPositionType(enum.Enum):
    long = 'long'
    short = 'short'


class QuantfuryPositions(Base):
    __tablename__ = 'quantfury_positions'

    quantfury_order_id = Column(Integer, primary_key=True, nullable=False)
    trade_id = Column(Integer, ForeignKey('trades.trade_id'), nullable=False)

    symbol = Column(String, nullable=False)

    limit_id = Column(String, nullable=False, unique=True)
    limit_price = Column(Numeric, nullable=True)
    limit_quantity = Column(Numeric, nullable=False)
    limit_amount_instrument = Column(Numeric, nullable=False)
    limit_amount_system = Column(Numeric, nullable=False)
    limit_stop_order = Column(Numeric, nullable=False)
    limit_create_date = Column(DateTime, nullable=True)
    limit_execution_type = Column(Numeric, nullable=True)

    api_position_id = Column(String, nullable=True, unique=True)
    position_open_price = Column(Numeric, nullable=True)
    position_quantity = Column(Numeric, nullable=True)
    position_amount_instrument = Column(Numeric, nullable=True)
    position_amount_system = Column(Numeric, nullable=True)
    position_open_date = Column(DateTime, nullable=True)
    position_order = Column(Integer, nullable=True)
    position_session_currency = Column(String, nullable=True)
    position_session_id = Column(String, nullable=True)
    position_spread_adjustment_end_date = Column(DateTime, nullable=True)

    profit_and_loss_instrument = Column(Numeric, nullable=True)
    profit_and_loss_system = Column(Numeric, nullable=True)
    profit_and_loss_account = Column(Numeric, nullable=True)
    close_price = Column(Numeric, nullable=True)
    close_date = Column(DateTime, nullable=True)

    #_position_type = Column("position_type", Enum(QuantfuryPositionType), nullable=True)
    position_type = Column(Enum(QuantfuryPositionType), nullable=True)
    status = Column(Enum(QuantfuryOrderStatus), nullable=False, default=QuantfuryOrderStatus.open)  # hold, open, close, cancel

    trade = relationship("Trades", back_populates="quantfury_position", uselist=False)
    quantfury_orders = relationship("QuantfuryOrders", back_populates="position", uselist=True)

    @property
    def stop_order(self):
        order = session.query(QuantfuryOrders).filter_by(
            api_position_id=self.api_position_id, order_type=QuantfuryOrderType.stop_order).first()
        return order

    @property
    def target_order(self):
        order = session.query(QuantfuryOrders).filter_by(
            api_position_id=self.api_position_id, order_type=QuantfuryOrderType.target_order).first()
        return order

    @validates('limit_create_date')
    def validate_limit_create_date(self, key, limit_create_date):
        return datetime.fromtimestamp(limit_create_date)

    @validates('position_spread_adjustment_end_date')
    def validate_position_spread_adjustment_end_date(self, key, position_spread_adjustment_end_date):
        return datetime.fromtimestamp(position_spread_adjustment_end_date)

    @validates('position_open_date')
    def validate_position_open_date(self, key, position_open_date):
        return datetime.fromtimestamp(position_open_date)

    @validates('close_date')
    def validate_close_date(self, key, close_date):
        return datetime.fromtimestamp(close_date)

    def __repr__(self):
        return "<QuantfuryPositions(symbol={}, limit_quantity={}, limit_price={}, position_type={})>".format(
            self.symbol, self.limit_quantity, self.limit_price, self.position_type)

    def update(self, data):
        key_errors = []

        def set_value(key, value):
            try:
                if not hasattr(self, key):
                    raise AttributeError(key)
                setattr(self, key, value)
            except Exception as e:
                key_errors.append(e.__str__())

        for key, value in data.items():
            set_value(key, value)

        if key_errors:
            raise KeyError(';'.join(key_errors))
        try:
            session.commit()
        except Exception as e:
            logger.info('func=QuantfuryOrders.update, msg={}'.format(e))

    def cancel(self, client):
        self.cancel_limit_order(client, self.limit_id)

    def close_with_earnings(self, client, target_price, entry_price, attempt):
        stage, code = 'self.fix_decimals_attempt_{}'.format(attempt), None
        try:
            symbol_metadata = session.query(SymbolMetadata).filter(
                SymbolMetadata.currency_pair == self.symbol).first()
            if not symbol_metadata:
                raise ValueError('Not SymbolMetadata for symbol {}'.format(self.symbol))
            limit_amount_system = symbol_metadata.quote_quantity(self.limit_amount_system)
            lower, upper = symbol_metadata.get_price_range(target_price)
            upper_target_price = symbol_metadata.fix_price_precision(upper)
            lower_target_price = symbol_metadata.fix_price_precision(lower)

            if Decimal(lower_target_price) <= entry_price:
                raise ValueError('Cannot close position with loss')

            stage = 'API.first_update_target_position_attempt_{}'.format(attempt)
            target_json_result = client.upsert_position(
                self.api_position_id, self.symbol, QuantfuryOrderType.target_order.value,
                upper_target_price, limit_amount_system)
            target_code = target_json_result.get('code', None)

            if target_code != 'Success':
                if attempt <= 1:
                    latest_price = Decimal(Utils.get_latest_price(self.symbol))
                    return self.close_with_earnings(client, latest_price, entry_price, attempt + 1)
                raise ConnectionError('Target Update failed')

            stage = 'API.update_stop_loss_position_attempt_{}'.format(attempt)
            stop_json_result = client.upsert_position(
                self.api_position_id, self.symbol, QuantfuryOrderType.stop_order.value,
                lower_target_price, limit_amount_system)
            stop_code = stop_json_result.get('code', None)

            if stop_code != 'Success':
                if attempt <= 1:
                    latest_price = Decimal(Utils.get_latest_price(self.symbol))
                    return self.close_with_earnings(client, latest_price, entry_price, attempt + 1)
                raise ConnectionError('Second Update failed')

            stage = 'SQL.update_quantfury_positions_attempt_{}'.format(attempt)
            self.status = QuantfuryOrderStatus.target
            session.commit()

            logger.info('func=QuantfuryPositions.close_with_earnings, trade_id={}, balance_id={}, '
                        'lower_target_price={}, upper_target_price={}'.format(
                self.trade.trade_id, self.trade.balance.balance_id, lower_target_price, upper_target_price))
        except Exception as e:
            logger.critical('func=QuantfuryPositions.close_with_earnings, trade_id={}, balance_id={}, '
                            'target_price={}, stage={}, code={}, entry_price={}, msg={}'.format(
                self.trade.trade_id, self.trade.balance.balance_id,
                target_price, stage, code, entry_price, e))

    def update_limit_order(self, client, stop_order=None, limit_price=None):
        stage = 'API.update_limit_order'
        try:
            response = client.update_order(
                self.limit_id, self.symbol, limit_price or self.limit_price, stop_order or self.limit_stop_order,
                None, self.limit_quantity, self.position_type)
            response = UtilsAPI.convert_keys_to_snake_case(response)
            return response
        except Exception as e:
            logger.critical('func=QuantfuryPositions.update_limit_order, limit_id={}, '
                            'stop_order={}, limit_price={}, stage={}, msg={}'.format(
                self.limit_id, stop_order, limit_price, stage, e))

    @classmethod
    def register_order(cls, client, trade_id, **kwargs):
        order_id = None
        stage = 'API.create_order'  # for error control
        try:
            active_trade_id = client.active_trade(kwargs['symbol'])
            if active_trade_id:
                raise ConnectionError('Active trade with id: {}'.format(active_trade_id))
            symbol_metadata = session.query(SymbolMetadata).filter(
                SymbolMetadata.currency_pair == kwargs['symbol']).first()
            if symbol_metadata:
                kwargs['quote_order_quantity'] = symbol_metadata.quote_quantity(kwargs['quote_order_quantity'])
                kwargs['buy_price'] = symbol_metadata.fix_price_precision(kwargs['buy_price'])
                if 'stop_price' in kwargs:
                    kwargs['stop_price'] = symbol_metadata.fix_price_precision(kwargs['stop_price'])
                if 'target_price' in kwargs:
                    kwargs['target_price'] = symbol_metadata.fix_price_precision(kwargs['target_price'])
            else:
                logger.warning('func=QuantfuryOrders.register_order, order_id={}, trade_id={}, '
                               'stage={}, msg=No able to round price or quantity'.format(order_id, trade_id, stage))

            create_order_response = client.create_OCO_long_order(**kwargs)
            if 'data' not in create_order_response and create_order_response.get('code') != 'Success':
                raise ConnectionError(create_order_response.get('code', 'Empty Response'))
            clean_create_order_response = create_order_response['data']
            clean_create_order_response = UtilsAPI.convert_keys_to_snake_case(clean_create_order_response)
            order_id = clean_create_order_response.get('id')

            clean_create_order_response = QuantfuryPositions.rename_fields_from_response(clean_create_order_response)
            clean_create_order_response['trade_id'] = trade_id
            clean_create_order_response['status'] = 'hold'
            clean_create_order_response['position_type'] = REVERTED_POSITION_TYPES[
                clean_create_order_response['position_type']]
            clean_create_order_response['symbol'] = clean_create_order_response.pop('limit_short_name')

            stage = 'SQL.create_order'
            order = QuantfuryPositions(**clean_create_order_response)
            session.add(order)
            session.commit()
            logger.info('func=QuantfuryOrders.register_order, trade_id={}, balance_id={}, '
                        'limit_price={}, limit_stop_order={}'.format(
                order.trade.trade_id, order.trade.balance.balance_id, order.limit_price, order.limit_stop_order))
            return order
        except Exception as e:
            logger.error('func=QuantfuryOrders.register_order, order_id={}, trade_id={}, stage={}, msg={}'.format(
                order_id, trade_id, stage, e))

            raise e

    @classmethod
    def is_equal_price(cls, price_1, price_2, symbol):
        symbol_metadata = session.query(SymbolMetadata).filter_by(currency_pair=symbol).first()
        return abs(price_1 - price_2) <= Decimal(symbol_metadata.minimum_price_filter) * 250

    @classmethod
    def match_limit_with_position(cls, limit, open_positions):
        for position in open_positions:
            position['open_price'] = Decimal(str(position['open_price']))
            if limit.symbol == position['short_name'] and limit.limit_amount_instrument == position['amount_instrument']:
                if len(position.get('stop_orders', [])) > 0 and limit.limit_stop_order is not None:
                    if cls.is_equal_price(Decimal(position['stop_orders'][0]['price']), limit.limit_stop_order, limit.symbol) and \
                            position['stop_orders'][0]['amount_instrument'] == limit.limit_amount_instrument:
                        return position
                else:
                    logger.warning(
                        'func=QuantfuryOrders.match_limit_with_position, symbol={}, limit_price={}, '
                        'limit_stop_order={}, msg=Found position but without stop loss'.format(
                            limit.symbol, limit.limit_price, limit.limit_stop_order))
                    return position
            logger.error(
                'func=QuantfuryOrders.match_limit_with_position, symbol={}, limit_price={}, limit_stop_order={}, '
                'msg=No position Found'.format(limit.symbol, limit.limit_price, limit.limit_stop_order))

    @classmethod
    def is_there_mismatches(cls, open_positions):
        null_position = session.query(QuantfuryOrders).filter_by(position_id=None).all()

        position_ids = [i['id'] for i in open_positions]

        orders_with_positions = session.query(
            QuantfuryOrders).filter(QuantfuryOrders.position_id.in_(position_ids)).all()

        unmatched_position = set(position_ids).difference(set([i.position_id for i in orders_with_positions]))
        unmatched_orders = set(set([i.position_id for i in orders_with_positions])).difference(position_ids)

        if unmatched_orders:
            logger.critical(
                'func=QuantfuryOrders.is_there_mismatches, unmatched_position={}, unmatched_position={}, '
                'msg=Found unmathced orders'.format(';'.join(unmatched_position), ';'.join(unmatched_position)))
            return False

        if unmatched_position:
            logger.critical(
                'func=QuantfuryOrders.is_there_mismatches, unmatched_position={}, unmatched_position={}, '
                'msg=Found unmathced orders'.format(';'.join(unmatched_position), ';'.join(unmatched_position)))
            return False
        return True

    @classmethod
    def sync_orders(cls, client):
        orders = client.list_orders().get('data', [])
        orders = UtilsAPI.convert_keys_to_snake_case(orders)
        orders_with_null_position = session.query(QuantfuryPositions).filter_by(api_position_id=None).all()

        for position in orders_with_null_position:
            new_position = cls.match_limit_with_position(position, orders['open_positions'])
            if new_position:
                stop_orders = new_position.pop('stop_orders')
                #new_position['order_type'] = REVERTED_ORDER_TYPES[new_position.pop('order_type')]
                #stop_orders = UtilsAPI.rename_keys_with_prefix(stop_orders, 'order_')
                stop_orders[0]['api_order_id'] = stop_orders[0].pop('id')
                stop_orders[0]['api_position_id'] = stop_orders[0].pop('trading_position_id')
                stop_orders[0]['order_type'] = REVERTED_ORDER_TYPES[stop_orders[0].pop('order_type')]

                new_position = UtilsAPI.rename_keys_with_prefix(new_position, 'position_')
                new_position['api_position_id'] = new_position.pop('position_id')
                new_position['position_type'] = REVERTED_POSITION_TYPES[new_position.pop('position_position_type')]
                new_position['status'] = QuantfuryOrderStatus.open.value
                del new_position['position_short_name']
                del new_position['position_target_orders']
                position.update(new_position)
                position.trade.buy_price = position.position_open_price
                position.trade.stop_loss = position.limit_stop_order
                stop_order = QuantfuryOrders(**stop_orders[0])
                session.add(stop_order)
                session.commit()
                logger.info('func=QuantfuryPositions.sync_orders, balance_id={}, trade_id={}, symbol={}, '
                            'position_open_price={}'.format(position.trade.balance_id, position.trade_id,
                                                            position.symbol, new_position['position_open_price']))

    @classmethod
    def sync_closed_positions(cls, client):
        closed_positions = client.list_closed_positions()
        closed_positions = closed_positions.get('data')
        closed_positions = UtilsAPI.convert_keys_to_snake_case(closed_positions)
        closed_positions = [{
            "api_position_id": i.get('id'),
            "close_price": i.get('close_price'),
            "close_date": i.get("close_date"),
            "profit_and_loss_instrument": i.get("pnl_instrument"),
            "profit_and_loss_system": i.get("pnl_system"),
            "profit_and_loss_account": i.get("pnl_account"),
        } for i in closed_positions]
        for close_position in closed_positions:
            stored_position = session.query(QuantfuryPositions).filter_by(
                api_position_id=close_position['api_position_id']).first()
            if stored_position and stored_position.status != QuantfuryOrderStatus.close:
                stored_position.update(close_position)
                stored_position.status = QuantfuryOrderStatus.close
                session.commit()
                logger.info(
                    'func=QuantfuryPositions.sync_closed_positions, balance_id={}, trade_id={}, close_price={}, '
                    'profit_and_loss_instrument={}'.format(
                        stored_position.trade.balance_id, stored_position.trade_id,
                        close_position['close_price'], close_position['profit_and_loss_instrument']))

    @classmethod
    def update_order(cls, order_response):
        order_id = order_response.get('orderId', None)
        try:
            cleaned_response = UtilsAPI.clean_response(order_response)
            cleaned_response['update_time'] = datetime.utcfromtimestamp(
                cleaned_response['update_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            cleaned_response['time'] = datetime.utcfromtimestamp(
                cleaned_response['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

            session.query(QuantfuryOrders).filter_by(order_id=order_id).update(dict(**cleaned_response))
            session.commit()

        except Exception as e:
            order_response_str = ';'.join(
                ['{}:{}'.format(k, v) for k, v in cleaned_response.items() or order_response.items()])
            logger. error('func=Orders.update_order, order_id={}, order_response_str={}, msg={}'.format(
                order_id, order_response_str, e))

    @classmethod
    def cancel_limit_order(cls, client, position_id):
        order_id = None
        stage = 'API.cancel_order'  # for error control
        try:
            create_order_response = client.cancel(position_id)
            if 'data' not in create_order_response and create_order_response.get('code') != 'Success':
                raise ConnectionError('Empty Response')
            stage = 'SQL.update_order'
            order = session.query(QuantfuryPositions).filter_by(limit_id=position_id).first()
            order.status = QuantfuryOrderStatus.cancel
            session.commit()

            return order
        except Exception as e:
            logger.error('func=QuantfuryOrders.cancel_order, api_order_id={}, stage={}, msg={}'.format(
                order_id, stage, e))

            raise e

    @classmethod
    def rename_fields_from_response(cls, limit_response):
        new_response = {'limit_' + k: v for k, v in limit_response.items()}
        new_response['position_type'] = new_response.pop('limit_position_type')
        return new_response


class QuantfuryOrders(Base):
    __tablename__ = 'quantfury_orders'
    quantfury_order_id = Column(Integer, primary_key=True, nullable=False)
    api_order_id = Column(String, primary_key=True, nullable=False)
    api_position_id = Column(String, ForeignKey('quantfury_positions.api_position_id'), nullable=False)

    order_type = Column(Enum(QuantfuryOrderType), nullable=True)
    price = Column(Numeric, nullable=False)
    quantity = Column(Numeric, nullable=False)
    amount_instrument = Column(Numeric, nullable=False)
    amount_system = Column(Numeric, nullable=False)

    position = relationship("QuantfuryPositions", back_populates="quantfury_orders", uselist=False)


if __name__ == '__main__':
    #from broker_clients import Balances, Trades

    balance_name = 'BTC_15_no_trend_1_no_break_even'
    balance = session.query(Balances).filter_by(name=balance_name).first()
    close_price, stop_loss, target_price = Utils.get_test_limit_stop_target_prices(
        SymbolMetadata.to_currency_pair_format(balance.symbol))


    trade = Trades(name=balance.name,
                   symbol=balance.symbol,
                   time_frame=balance.time_frame,
                   entry_date='2021-03-27 21:45:00.000000',
                   amount=10,
                   quantity=None,
                   stop_loss=stop_loss,
                   buy_price=close_price,
                   sell_price=None,
                   profit=None,
                   side='long',
                   low_moment_price=close_price,
                   balance_id=balance.balance_id)
    session.add(trade)
    session.commit()
    #login_result = Quantfury.login(balance.account.api_key, balance.account.secret_key)
    #client = Quantfury(login_result['data']['token'])
    client = Quantfury(balance.account.token)
    position = session.query(QuantfuryPositions).filter_by(api_position_id='52dd4715-961c-4a69-9693-bc0b07e65d22').first()
    #position.close_with_earnings(client, 49100)
    QuantfuryPositions().sync_closed_positions(client)
    QuantfuryPositions().sync_orders(client)
    order = QuantfuryPositions.register_order(
        client, trade_id=trade.trade_id, symbol=SymbolMetadata.to_currency_pair_format(balance.symbol),
        quote_order_quantity=trade.amount, buy_price=trade.buy_price, stop_price=trade.stop_loss,
        target_price=trade.sell_price, position_type=trade.side)

    print(order)

    QuantfuryPositions().cancel_limit_order(client, order.limit_id)
