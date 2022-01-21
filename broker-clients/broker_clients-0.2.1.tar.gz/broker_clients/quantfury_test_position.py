from broker_clients import Base, session
from broker_clients import Balances, Trades
from broker_clients.binance_proxy.storage.models import SymbolMetadata
from broker_clients.quantfury_proxy.broker.client import Utils
from broker_clients.quantfury_proxy.storage.models import QuantfuryPositions

balance_name = 'BTC_15_no_trend_2_no_break_even'
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

order = QuantfuryPositions(trade_id=trade.trade_id, symbol=SymbolMetadata.to_currency_pair_format(balance.symbol),
        limit_id=trade.amount, limit_price=trade.buy_price, limit_quantity=45000,
                           limit_amount_instrument=10, limit_amount_system=10, limit_stop_order=44500)

session.add(order)
session.commit()
print(order)