from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

Base = declarative_base()
BROKER_DB = os.getenv("BROKER_DB")
engine = create_engine(BROKER_DB, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

from broker_clients.emulator_proxy.storage.models import Accounts, Balances, Trades
#from broker_clients.binance_proxy.storage.models import Orders, Fills, SymbolMetadata
#from broker_clients.quantfury_proxy.storage.models import QuantfuryPositionType, QuantfuryPositions, QuantfuryOrders
