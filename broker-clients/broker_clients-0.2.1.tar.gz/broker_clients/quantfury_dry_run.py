from broker_clients import Accounts
from broker_clients.binance_proxy.broker.account import ExtendedAccount
from broker_clients.emulator_proxy.storage.models import SymbolMetadata
from broker_clients import Base, session
from broker_clients import Balances
a = Accounts(name='quantfury_test', api_key='5583198120', secret_key='Dando&perdiend0',
             token='z4Ti3RS6JwhnP7eShTo7ZSYk4s2PrfovzK7-EPAbhJ-Z5agupaICLdQoS-b8skEBpAEzcJHgaQbrS6I6nL7NcM27cZZNecXec6QmvsIW-UNwuFr_62sjsY4KpuPRPcVyF6kMWQJatcUw4240vx2cMtddyAj94i9X9mx_i6v5rYYWyvOJgzNFp8jRnEJmI9PzAM7vb8z9IKPNGGTznZBOwORwJ1heDdXKqlQT8WcoJ5YYtosBO6rWQ5dqjvKUye5QFSBteIFS-OSAOTZMCWTntmBCZxvdV81Jes1joaOZkqBfNjmnDVsvD5ZtOPJT8LgXqXAttkooAdYxUzhnDaxcIHvunznX8eYJx8nJTG_U6xLd4Kma7IOoICcYdF19lxP0orz0VmNykgbPbjdZjyxxBLzHJnOz2AP8M8YavWGyKrq9ewZEu2fAxlAuNUt_f7jfHp7mdyZ0Wp5u9dsIXQGPnG888KjmjDw11x2XRDU8RwCL-ti1', broker_name='quantfury')
session.add(a)
session.commit()

ea = ExtendedAccount('quantfury_test', 'BINANCE:BTCUSDT')
ea.update_symbol_metadata()

session.query(SymbolMetadata).filter_by(symbol='BTCUSDT').update({"currency_pair": "BTC/USDT"})
session.query(Balances).filter_by(name='BTC_15_no_trend_1_no_break_even').update({"account_id": 2})
session.commit()