from __future__ import print_function
from typing import Optional
import grpc
from ..modules import bot_pb2_grpc, bot_pb2
from datetime import datetime
from ..converter import datetime_to_timestamp
import json

class Client:
    def __init__(self, address: str = "guardian", port: str = "50065"):
        self.address = address
        self.port = port
        self.channel = grpc.insecure_channel(self.address + ":" + self.port)
        self.stub = bot_pb2_grpc.EchoStub(self.channel)

    def __string_to_datetime(self, date: str):
        date = datetime.strptime(date, "%Y-%m-%d")
        time = datetime.now().time()

        date_class = datetime_to_timestamp(datetime.combine(date, time))
        return date_class

    def create_bot(
        self,
        ticker: str,
        spot_date: str,
        investment_amount: float,
        price: float,
        bot_id: float,
        margin: int = 1,
        fraction: bool = False,
    ):

        response = self.stub.CreateBot(
            bot_pb2.Create(
                ticker=ticker,
                spot_date=self.__string_to_datetime(spot_date),
                investment_amount=investment_amount,
                price=price,
                bot_id=bot_id,
                margin=margin,
                fraction=fraction,
            )
        )
        return json.loads(response.message)

    def hedge(
        self,
        bot_id: str,
        ticker: str,
        current_price: float,
        entry_price: float,
        last_share_num: float,
        last_hedge_delta: float,
        investment_amount: float,
        bot_cash_balance: float,
        stop_loss_price: float,
        take_profit_price: float,
        expiry: str,
        strike: Optional[float] = None,
        strike_2: Optional[float] = None,
        margin: Optional[int] = 1,
        fraction: Optional[bool] = False,
        option_price: Optional[float] = None,
        barrier: Optional[float] = None,
        current_low_price: Optional[float] = None,
        current_high_price: Optional[float] = None,
        ask_price: Optional[float] = None,
        bid_price: Optional[float] = None,
        trading_day: Optional[str] = datetime.strftime(datetime.now().date(), "%Y-%m-%d")
    ):
        response = self.stub.HedgeBot(
            bot_pb2.Hedge(
                ric=ticker,
                expiry=self.__string_to_datetime(expiry),
                investment_amount=investment_amount,
                current_price=current_price,
                bot_id=bot_id,
                margin=margin,
                entry_price=entry_price,
                last_share_num=last_share_num,
                last_hedge_delta=last_hedge_delta,
                bot_cash_balance=bot_cash_balance,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                option_price=option_price,
                strike=strike,
                strike_2=strike_2,
                barrier=barrier,
                current_low_price=current_low_price,
                current_high_price=current_high_price,
                ask_price=ask_price,
                bid_price=bid_price,
                fraction=fraction,
                trading_day=self.__string_to_datetime(trading_day)
            )
        )
        return json.loads(response.message)
    
    def stop(
        self,
        bot_id: str,
        ticker: str,
        current_price: float,
        entry_price: float,
        last_share_num: float,
        last_hedge_delta: float,
        investment_amount: float,
        bot_cash_balance: float,
        stop_loss_price: float,
        take_profit_price: float,
        expiry: str,
        strike: Optional[float] = None,
        strike_2: Optional[float] = None,
        margin: Optional[int] = 1,
        fraction: Optional[bool] = False,
        option_price: Optional[float] = None,
        barrier: Optional[float] = None,
        current_low_price: Optional[float] = None,
        current_high_price: Optional[float] = None,
        ask_price: Optional[float] = None,
        bid_price: Optional[float] = None,
        trading_day: Optional[str] = datetime.strftime(datetime.now().date(), "%Y-%m-%d")
    ):
        response = self.stub.StopBot(
            bot_pb2.Stop(
                ric=ticker,
                expiry=self.__string_to_datetime(expiry),
                investment_amount=investment_amount,
                current_price=current_price,
                bot_id=bot_id,
                margin=margin,
                entry_price=entry_price,
                last_share_num=last_share_num,
                last_hedge_delta=last_hedge_delta,
                bot_cash_balance=bot_cash_balance,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                option_price=option_price,
                strike=strike,
                strike_2=strike_2,
                barrier=barrier,
                current_low_price=current_low_price,
                current_high_price=current_high_price,
                ask_price=ask_price,
                bid_price=bid_price,
                fraction=fraction,
                trading_day=self.__string_to_datetime(trading_day)
            )
        )
        return json.loads(response.message)
        
