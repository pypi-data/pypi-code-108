import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from pagexdata.database import Base
from pydantic import BaseModel
from typing import Optional


class RedditHits(Base):
    __tablename__ = 'reddit_hits'

    date = Column(DateTime, primary_key=True)
    ticker_symbol = Column(String, primary_key=True)
    subreddit = Column(String, primary_key=True)
    hits = Column(Integer)
    positive_hits = Column(Boolean)
    rank = Column(Integer, nullable=True)
    previous_rank = Column(Integer, nullable=True)
    change_rank = Column(Integer, nullable=True)
    change_hits_one_day = Column(Integer, nullable=True)
    change_hits_two_days = Column(Integer, nullable=True)
    change_hits_three_days = Column(Integer, nullable=True)
    change_hits_one_week = Column(Integer, nullable=True)
    change_hits_two_weeks = Column(Integer, nullable=True)
    change_hits_four_weeks = Column(Integer, nullable=True)
    hits_volatility_one_week = Column(Float, nullable=True)
    hits_volatility_two_weeks = Column(Float, nullable=True)


class StockData(Base):
    __tablename__ = 'stockdata'

    date = Column(DateTime, primary_key=True)
    ticker_symbol = Column(String, primary_key=True)
    price = Column(Float)
    volume = Column(Integer)


class ImportLog(Base):
    __tablename__ = 'importlog'

    log_datetime = Column(DateTime, primary_key=True)
    type = Column(String, primary_key=True)
    state = Column(String)
    message = Column(String, nullable=True)
    extra = Column(String, nullable=True)


# pagination entities for rest api
class RedditHitsPage(BaseModel):
    date: datetime.datetime
    ticker_symbol: str
    subreddit: str
    hits: int
    rank: Optional[int] = None
    previous_rank: Optional[int] = None
    change_rank: Optional[int] = None
    change_hits_one_day: Optional[int] = None
    change_hits_two_days: Optional[int] = None
    change_hits_three_days: Optional[int] = None
    change_hits_one_week: Optional[int] = None
    change_hits_two_weeks: Optional[int] = None
    change_hits_four_weeks: Optional[int] = None
    hits_volatility_one_week: Optional[float] = None
    hits_volatility_two_weeks: Optional[float] = None

    class Config:
        orm_mode = True


class StockDataPage(BaseModel):
    date: datetime.datetime
    ticker_symbol: str
    price: float
    volume: int

    class Config:
        orm_mode = True


class ImportLogPage(BaseModel):
    log_datetime: datetime.datetime
    type: str
    state: str
    message: Optional[str] = None
    extra: Optional[str] = None

    class Config:
        orm_mode = True
