import os
import logging
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Unicode, Numeric, ForeignKey, DateTime, Boolean, Enum, event
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.encrypted.encrypted_type import StringEncryptedType
import enum
from broker_clients import Base, session
# no delete
from broker_clients.binance_proxy.storage.models import Orders, Fills, SymbolMetadata
from broker_clients.quantfury_proxy.storage.models import QuantfuryPositionType, QuantfuryPositions, QuantfuryOrders

load_dotenv()
logger = logging.getLogger(__name__)
cypher_key = os.getenv("CYPHER_KEY")


class TradeInTrend(enum.Enum):
    none = 'none'
    first_upper_scale = 'first_upper_scale'
    second_upper_scale = 'second_upper_scale'
    both_upper_scales = 'both_upper_scales'
    any_upper_scales = 'any_upper_scales'
    second_any_upper_scales = 'second_any_upper_scales'


class Trades(Base):
    __tablename__ = 'trades'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode, nullable=False)
    symbol = Column(String, nullable=False)
    time_frame = Column(String, nullable=False)

    entry_date = Column(DateTime, nullable=False)
    amount = Column(Numeric, nullable=True)  # must be same on Orders.quote_order_quantity
    stop_loss = Column(Numeric, nullable=True)  # must be same on Orders.stop_price
    buy_price = Column(Numeric, nullable=True)  # must be same on Orders.price
    sell_price = Column(Numeric, nullable=True)  # must be same on Orders.price
    profit = Column(Numeric, nullable=True)  # must be same on Orders.price
    side = Column(String, nullable=False)
    low_moment_price = Column(Numeric, default=0, nullable=False)
    quantity = Column(Numeric, nullable=True)
    exit_date = Column(DateTime, nullable=True)

    now = datetime.utcnow()
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=datetime.utcnow())

    balance_id = Column(Integer, ForeignKey('balances.balance_id'), nullable=False)
    balance = relationship("Balances", back_populates="trades")
    orders = relationship("Orders", back_populates="trade")
    quantfury_position = relationship("QuantfuryPositions", back_populates="trade", uselist=False)

    def __repr__(self):
        return "<Trades(name={}, symbol={}, time_frame={}, date={})>".format(
            self.name, self.symbol, self.time_frame, self.entry_date)

    def is_stop_loss_reached(self, prices):
        # low si no estoy en la misma vela
        # close y low_moment_price si estoy en la misma vela
        log_template = 'func=Trades.is_stop_loss_reached, is_reached={}, stage={}, price={}, stop_loss={}, low={}, '\
                       'low_moment_price={}, trade_id={}, name={}, symbol={}, time_frame={}, entry_date={}, diff={}'
        for date, row in prices.items():
            row['Low'] = Decimal(row['Low'])
            row['Close'] = Decimal(row['Close'])
            entry_date = self.entry_date.strftime("%Y/%m/%d, %H:%M:%S")
            if row['date'] == entry_date:
                if self.low_moment_price > row['Low']:
                    # TODO error in if due to presicion
                    logger.info(log_template.format(self.stop_loss >= row['Low'], 'same candle new low', row['Close'],
                                                    self.stop_loss, row['Low'], self.low_moment_price,
                                                    self.trade_id, self.name, self.symbol, self.time_frame,
                                                    entry_date.replace(',', ''), self.low_moment_price - row['Low']))
                    return self.stop_loss >= row['Low']
                else:
                    logger.info(log_template.format(self.stop_loss >= row['Close'], 'same candle same low',
                                                    row['Close'], self.stop_loss, row['Low'], self.low_moment_price,
                                                    self.trade_id, self.name, self.symbol, self.time_frame,
                                                    entry_date.replace(',', ''), self.low_moment_price - row['Low']))
                    return self.stop_loss >= row['Close']

            else:
                if self.stop_loss >= row['Low']:
                    logger.info(log_template.format('True', 'different candle', row['Close'], self.stop_loss,
                                                    row['Low'], self.low_moment_price,
                                                    self.trade_id, self.name, self.symbol, self.time_frame,
                                                    entry_date.replace(',', ''), self.stop_loss - row['Low']))
                    return True
        logger.info(log_template.format('False', 'last ', row['Close'], self.stop_loss, row['Low'],
                                        self.low_moment_price, self.trade_id, self.name, self.symbol, self.time_frame,
                                        entry_date.replace(',', ''), row['Close'] - self.stop_loss))
        return False

    @classmethod
    def timestamp_to_time_frame(cls, timestamp, time_frame):
        timestamp = timestamp.replace(second=0, microsecond=0)
        if time_frame == '15':
            return timestamp.replace(minute=timestamp.minute//15 * 15)
        elif time_frame == '60':
            return timestamp.replace(minute=0)
        elif time_frame == '240':
            return timestamp.replace(hour=timestamp.hour//4 * 4, minute=0)
        elif time_frame == '1D':
            return timestamp.replace(hour=0, minute=0)
        else:
            raise ValueError('Invalid time_frame')

    def has_open_order(self):
        return self.sell_price is None and self.profit is None


class Balances(Base):
    __tablename__ = 'balances'

    balance_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    name = Column(Unicode, nullable=False, unique=True)
    symbol = Column(String, nullable=False)
    time_frame = Column(String, nullable=False)
    free = Column(Numeric, nullable=False)
    locked = Column(Numeric, nullable=False)

    stop_loss_percentage = Column(Numeric, nullable=False)
    profit_percentage = Column(Numeric, nullable=False)
    trade_in_trend = Column(Enum(TradeInTrend), nullable=False, default=False)
    second_scale_from_database = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=False), default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=False), default=datetime.utcnow(), onupdate=datetime.utcnow())
    account = relationship("Accounts", back_populates="balances")
    trades = relationship("Trades", back_populates="balance")

    @classmethod
    def balances_by_strategy(cls, symbol, time_frame):
        records = session.query(Balances).filter(
            Balances.symbol == symbol, Balances.time_frame == time_frame,
            Balances.profit_percentage != 0).all()
        return records

    @classmethod
    def balances_by_stop_loss_percentage(cls, symbol, time_frame, stop_loss_percentage):
        records = session.query(Balances).filter(
            Balances.symbol == symbol, Balances.time_frame == time_frame, Balances.stop_loss_percentage == stop_loss_percentage,
            Balances.profit_percentage != 0).all()
        return records

    @property
    def delay_to_open_a_position(self):
        if self.time_frame.isdigit():
            return int(self.time_frame)
        elif self.time_frame == '1D':
            return 1440
        elif self.time_frame == '1W':
            return 10080
        else:
            raise ValueError('Invalid time_frame')

    def __repr__(self):
        return "<Balances(name={}, symbol={}, time_frame={}, free={})>".format(
            self.name, self.symbol, self.time_frame, self.free)


class Accounts(Base):
    __tablename__ = 'accounts'
    if not cypher_key:
        raise ValueError('CYPHER_KEY environment variable is required')
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(StringEncryptedType(String, cypher_key), unique=True, nullable=False)
    api_key = Column(StringEncryptedType(String, cypher_key), unique=True, nullable=False)
    secret_key = Column(StringEncryptedType(String, cypher_key), nullable=False)
    token = Column(StringEncryptedType(String, cypher_key), nullable=True)
    broker_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    #__table_args__ = (UniqueConstraint('api_key', name='api_key_unique'),)
    balances = relationship("Balances", back_populates="account")

    def masked_api_key(self):
        prefix = len(self.name)//3 * '*'
        return "{}{}{}".format(prefix, self.name[len(self.name)//3:len(self.name)//3*2], prefix)

    def __repr__(self):
        return "<Accounts(account_id={}, name={}, api_key={})>".format(
            self.account_id, self.name, self.api_key)


@event.listens_for(QuantfuryPositions.position_open_price, 'set')
def sync_open_price(target, value, old_value, initiator):
    if target.trade:
        target.trade.buy_price = value


@event.listens_for(QuantfuryPositions.close_price, 'set')
def sync_close_price(target, value, old_value, initiator):
    if target.trade:
        target.trade.sell_price = value


@event.listens_for(QuantfuryPositions.limit_stop_order, 'set')
def sync_stop_order(target, value, old_value, initiator):
    if target.trade:
        target.trade.stop_loss = value
